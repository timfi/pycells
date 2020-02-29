from itertools import product
from configparser import ConfigParser
import os
import sys

import click
from PIL import Image

from .yaml import load_yaml
from .simulations import SIM_METHODS
from .render import DIM_TO_FORMAT, FORMATS


__all__ = ("cli",)


DIR = os.path.dirname(os.path.realpath(__file__))
PRESETS = {
    file[:-4]: os.path.join(DIR, "presets", file)
    for file in os.listdir(os.path.join(DIR, "presets"))
}


REQURIED_SET = ("dimensions", "method", "rule", "iterations")
DEFAULTS = {
    "neighborhood_radius": 1,
    "initial_state": -1,
    "scaling": 4,
    "out": "out",
    "parallelize": False,
}


class CustomCommand(click.Command):
    def __init__(self, *args, params=None, **kwargs):
        super().__init__(
            *args,
            params=[
                click.Option(
                    param_decls=("-p", "--preset"),
                    type=click.Choice(PRESETS),
                    help="simulation preset to run",
                    multiple=True,
                ),
                click.Option(
                    param_decls=("-f", "--file"),
                    type=click.File(mode="r"),
                    help="file to load simulation config from",
                    multiple=True,
                ),
            ]
            + (params or []),
            **kwargs,
        )

    def invoke(sefl, ctx):

        data = {**DEFAULTS}

        preset = ctx.params.pop("preset")
        if preset:
            click.echo("Loading presets...")
            for p in preset:
                data = {**data, **load_yaml(open(PRESETS[p]))}

        file = ctx.params.pop("file")
        if file:
            click.echo("Loading simulation parameters from file...")
            for f in file:
                f_data = load_yaml(f)
                preset = PRESETS.get(f_data.pop("preset", None))
                if preset is not None:
                    with open(preset, "r") as p:
                        p_data = load_yaml(p)
                        f_data = {
                            **p_data,
                            **f_data,
                        }
                data = {**data, **f_data}

        data = {
            **data,
            **{
                param: value for param, value in ctx.params.items() if value is not None
            },
        }

        if any(param not in data for param in REQURIED_SET):
            return cli(["--help"])

        ctx.params = data

        return super().invoke(ctx)


@click.command("simulate", cls=CustomCommand)
@click.option(
    "-d",
    "--dimensions",
    type=str,
    help="dimensions of the simulation, format: N[xN[xN[...]]",
)
@click.option(
    "-m", "--method", type=click.Choice(SIM_METHODS), help="simulation method"
)
@click.option("-r", "--rule", type=int, help="rule to simulate")
@click.option("-i", "--iterations", type=int, help="iterations to simulate")
@click.option(
    "-n", "--neighborhood-radius", type=int, help="neighborhood radius to use"
)
@click.option(
    "-o",
    "--out",
    type=click.Path(dir_okay=False, writable=True),
    help="path to save the output to",
)
@click.option("--initial-state", type=int, help="initial simulation state")
@click.option(
    "--parallelize",
    is_flag=True,
    default=None,
    help="enabled parallel calculation of cells per state transition",
)
@click.option("--scaling", type=int, help="scaling to apply to output")
@click.option(
    "--format",
    type=click.Choice(FORMATS),
    help="format to output as, this skips the default which is to simply use the most suitable for the given number of dimensions",
)
def cli(
    dimensions,
    method,
    rule,
    iterations,
    neighborhood_radius,
    initial_state,
    parallelize,
    scaling,
    out,
    format=None,
    **draw_options,
):
    """
    Simulate n-dimensional cellular automata using some of
    the most common methods.
    """
    sim_method = SIM_METHODS.get(method)
    if sim_method is None:
        raise click.BadParameter(
            f'unkown simulation method, options are {", ".join(SIM_METHODS)}'
        )

    try:
        dimensions = tuple(int(dim) for dim in dimensions.split("x"))
    except BaseException:
        raise click.BadParameter("dimensions should be supplied as: N[xN[xN[...]]")

    if format is None:
        if len(dimensions) + 1 > len(DIM_TO_FORMAT):
            raise click.BadParameter(
                f"can only render simulations with up to {len(DIM_TO_FORMAT) - 1} dimensions"
            )
        else:
            draw_method = DIM_TO_FORMAT[len(dimensions)]
    else:
        if format not in FORMATS:
            raise click.BadParameter(
                f'unkown output format, options are {", ".join(FORMATS)}'
            )
        else:
            draw_method = FORMATS[format]

    with click.progressbar(
        sim_method(
            dimensions,
            rule,
            neighborhood_radius=neighborhood_radius,
            initial_state=initial_state,
            iterations=iterations,
            parallel=parallelize,
        ),
        label="Simulating...",
        show_pos=True,
        length=iterations + 1,
    ) as bar:
        draw_method(
            iterations,
            dimensions,
            scaling,
            f"{out}.{draw_method.__name__}",
            bar,
            **draw_options,
        )

    click.echo("done")

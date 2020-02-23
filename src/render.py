from typing import Iterator, Tuple
from itertools import product as iter_product

from PIL import Image
import numpy as np

from .simulations import product


__all__ = ("gif", "png", "DIM_TO_FORMAT", "FORMATS")


FORMATS = {}


def gif(
    iterations: int,
    dimensions: Tuple[int, ...],
    scaling: int,
    path: str,
    simulation: Iterator[int],
    tpf: int = 50,
    loop: bool = True,
    **kwargs,
):
    imgs = []
    width, height = dimensions
    for state in simulation:
        img = Image.new("RGB", dimensions, (255, 255, 255))
        data = img.load()
        for x, y in iter_product(range(width), range(height)):
            if state >> y * width + x & 1:
                data[x, y] = (0, 0, 0)
        imgs.append(img.resize((scaling * width, scaling * height), Image.NEAREST))
    imgs[0].save(
        path,
        format="GIF",
        save_all=True,
        append_images=imgs[1:],
        duration=tpf,
        loop=int(not loop),
    )


FORMATS["gif"] = gif


def png(
    iterations: int,
    dimensions: Tuple[int, ...],
    scaling: int,
    path: str,
    simulation: Iterator[int],
    **kwargs,
):
    (width,) = dimensions
    img = Image.new("RGB", (width, iterations + 1), (255, 255, 255))
    data = img.load()
    for y, state in enumerate(simulation):
        for x in range(width):
            if state >> x & 1:
                data[x, y] = (0, 0, 0)
    img.resize((scaling * width, scaling * (iterations + 1)), Image.NEAREST).save(
        path, format="PNG"
    )


FORMATS["png"] = png


DIM_TO_FORMAT = [None, png, gif]


def state_to_array(dimensions: Tuple[int, ...], state: int):
    arr = np.ndarray(dimensions, np.bool)
    for coords in iter_product(*map(range, dimensions)):
        arr[(*coords,)] = bool(
            state >> sum(c * product(*dimensions[:j]) for j, c in enumerate(coords)) & 1
        )
    return arr


def npy(
    iterations: int,
    dimensions: Tuple[int, ...],
    scaling: int,
    path: str,
    simulation: Iterator[int],
    **kwargs,
):
    data = np.ndarray((iterations + 1, *dimensions), np.bool)
    for i, state in enumerate(simulation):
        data[i] = state_to_array(dimensions, i)
    with open(path, "wb+") as f:
        np.save(f, data)


FORMATS["npy"] = npy


def txt(
    iterations: int,
    dimensions: Tuple[int, ...],
    scaling: int,
    path: str,
    simulation: Iterator[int],
    **kwargs,
):
    state_format = f"{{state:0>{product(*dimensions)}b}}\n"
    with open(path, "w+") as f:
        f.write("d=" + "x".join(map(str, dimensions)) + "\n")
        for state in simulation:
            f.write(state_format.format(state=state))


FORMATS["txt"] = txt

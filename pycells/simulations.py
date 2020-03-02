from typing import Iterator, Tuple, Callable, List, Dict
from random import randrange
from functools import reduce
from itertools import product as iter_product
from multiprocessing import cpu_count, Pool
from functools import partial


__all__ = ("count", "pattern", "SIM_METHODS")


def _get_pool(workers: int):
    """Build dummy process pool for 1 worker to avoid cpu context switches."""
    if workers == 1:

        class cls:
            def __init__(self, *args, **kwargs):
                ...

            def imap_unordered(self, f, iterable, **kwargs):
                return map(f, iterable)

            def __enter__(self, *args, **kwargs):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                if (
                    exc_type is not None
                    and exc_value is not None
                    and traceback is not None
                ):
                    raise exc_type(exc_value).with_traceback(traceback)

    else:
        cls = Pool

    return cls(processes=workers)


def product(*scalars: int) -> int:
    return reduce(lambda acc, scalar: acc * scalar, scalars, 1)


Simulation = Callable[[Tuple[int, ...], int, int, int, int, bool, bool], Iterator[int]]
SetupFunc = Callable[[Tuple[int, ...], int, int], Tuple]
WorkerFunc = Callable[[Tuple[int, ...], List[int], Tuple, int, int], int]


# Simulation method registry
SIM_METHODS: Dict[str, Simulation] = {}


def make_simulation(
    name: str,
    setup_func: SetupFunc,
    worker_func: WorkerFunc,
) -> Simulation:
    """Constructor for creating simulations from a setup and a worker function.

    Parameters
    ----------
    name : str
        The name to register the simulation method as.
    setup_func : SetupFunc
        The function that parses the rule integer into something useful
        to the worker.
    worker_func : WorkerFunc
        The function that gets executed for each cell for each iteration.

    Returns
    -------
    simulation : Simulation
        A function that when called results in an iterator that yields
        the state of each iteration sequentially.

    """
    def simulation(
        dimensions: Tuple[int, ...],
        rule: int,
        neighborhood_radius: int = 1,
        initial_state: int = -1,
        iterations: int = -1,
        parallel: bool = False,
        skip_initial_state: bool = False,
    ):
        worker_args = setup_func(dimensions, rule, neighborhood_radius)

        state_size = product(*dimensions)
        slice_sizes = [product(*dimensions[:j]) for j in range(len(dimensions))]
        max_state = 2 ** state_size

        if initial_state < 0:
            initial_state = randrange(max_state)

        iteration, state = 0, initial_state
        if not skip_initial_state:
            yield state

        n_workers = max(1, cpu_count() - 1) if parallel else 1
        worker = partial(worker_func, dimensions, slice_sizes, neighborhood_radius, *worker_args)
        with _get_pool(n_workers) as pool:
            while iterations < 0 or iteration < iterations:
                iteration += 1
                state = sum(
                    pool.imap_unordered(
                        partial(worker, state), range(state_size), chunksize=state_size // n_workers
                    )
                )
                yield state
    SIM_METHODS[name] = simulation
    simulation.__name__ = name
    return simulation


"""====================================================================================

Simulate nD cellular automata based on neighbor counting rules.

Parameters
----------
dimensions : Tuple[int, ...]
    The dimensions of the state to simulate.
rule : int
    The rule to simulate.
neighborhood_radius : int
    The radius of the Moors-Neighborhood to count the neighbors in. (the default is 1)
initial_state : int
    The state to start the simulation with. (the default is -1, which forces the
    random generation of an initial state)
iterations : int
    The number of iterations to simulate. (the default is -1, which causes the
    simulation to run indefinitely)
parallel : bool
    Flag to enabled parallel calculation of cells per stat transition. (the default is
    False)

Yields
------
state : int
    The current state of the simulation.
"""

def count_setup(dimensions: Tuple[int, ...], rule: int, neighborhood_radius: int):
    n_neighbors = ((2 * neighborhood_radius + 1) ** len(dimensions)) - 1
    b = rule >> 0 & (2 ** (n_neighbors + 2)) - 1
    s = rule >> (n_neighbors + 1) & (2 ** (n_neighbors + 2)) - 1

    return b, s


def count_worker(dimensions, slice_sizes, neighborhood_radius, b, s, state, i):
    return (
        b * (~state >> i & 1) + s * (state >> i & 1)
        >> sum(
            state
            >> sum(
                (i // slice_sizes[j] + offset) % dimensions[j] * slice_sizes[j]
                for j, offset in enumerate(offsets)
            )
            & any(offset != 0 for offset in offsets)
            for offsets in iter_product(
                *(
                    range(-neighborhood_radius, neighborhood_radius + 1)
                    for _ in dimensions
                )
            )
        )
        & 1
    ) << i


count = make_simulation("count", count_setup, count_worker)


"""====================================================================================

Simulate nD cellular automata based on neighbor pattern rules.

Parameters
----------
dimensions : Tuple[int, ...]
    The dimensions of the state to simulate.
rule : int
    The rule to simulate.
neighborhood_radius : int
    The radius of the Moors-Neighborhood to match the patterns in. (the default is 1)
initial_state : int
    The state to start the simulation with. (the default is -1, which forces the
    random generation of an initial state)
iterations : int
    The number of iterations to simulate. (the default is -1, which causes the
    simulation to run indefinitely)
parallel : bool
    Flag to enabled parallel calculation of cells per stat transition. (the default is
    False)


Yields
------
state : int
    The current state of the simulation.
"""


def pattern_setup(dimensions: Tuple[int, ...], rule: int, neighborhood_radius: int = 1):
    return ({
        i: rule >> i & 1
        for i in range(2 ** ((2 * neighborhood_radius + 1) ** len(dimensions)))
    },)


def pattern_worker(dimensions, slice_sizes, neighborhood_radius, patterns, state, i):
    return (
        patterns[
            sum(
                (
                    state
                    >> sum(
                        (i // slice_sizes[k] + offset) % dimensions[k] * slice_sizes[k]
                        for k, offset in enumerate(offsets)
                    )
                    & 1
                )
                << j
                for j, offsets in enumerate(
                    iter_product(
                        *(
                            range(-neighborhood_radius, neighborhood_radius + 1)
                            for _ in dimensions
                        )
                    )
                )
            )
        ]
        << i
    )


pattern = make_simulation("pattern", pattern_setup, pattern_worker)

# PyCells

Whilst being very bored recently I started playing around with simulating cellular automata once again.
But to challenge myself a bit more than usual I set three specific limitations that made this a bit harder
than I was used to:
1. The simulation functions should be able to handle n-dimensional rules and states.
2. The rules should be given as integers.
3. The state should be represented as an integer, making use of the fact that the whole state consists of
   a n-dimensional array of booleans that can be flattened.
   
Another additional burden I put on to myself was to implement multiple unique styles of rules:
1. Pattern based rules, such as the popular 110 or 30.
2. Neighbor count based rules, such as Conway's Game of Life.


## Usage

### From PyPi
1. run `pip install pycells`
2. run `pycells` and check what options you have

### From source
1. clone this repo
2. setup virtualenv using python `> 3.7` and `./requirements.txt`
3. run `python simulate.py`


I implemented both a cli and a file-based simulation configuration system. The cli is structured
as follows:

```
$ python simulation.py

Usage: simulate.py [OPTIONS]

  Simulate n-dimensional cellular automata using some of the most common
  methods.

Options:
  -p, --preset [conway|elementary]
                                  simulation preset to use
  -f, --file FILENAME             file to load simulation config from
  -d, --dimensions TEXT           dimensions of the simulation, format:
                                  N[xN[xN[...]]
  -m, --method [count|pattern]    simulation method
  -r, --rule INTEGER              rule to simulate
  -i, --iterations INTEGER        iterations to simulate
  -n, --neighborhood-radius INTEGER
                                  neighborhood radius to use
  -o, --out FILE                  path to save the output to
  --initial-state INTEGER         initial simulation state
  --parallelize                   enabled parallel calculation of cells per
                                  state transition
  --scaling INTEGER               scaling to apply to output
  --format [gif|png|npy|txt]      format to output as, this skips the default
                                  which is to simply use the most suitable for
                                  the given number of dimensions
  --help                          Show this message and exit.
```

To make use of file based configuration options simply write a YAML file that contains all
the necessary parameters. For some examples have a look in the `./examples` directory.
If you want to write binary numbers in these files I've added two tags to the yaml-parser
`!b` and `!br` (reverse). Using these files is as simple as running:

```
python simulate.py -f examples/glider.yml
```

Using the predefined presets is also similar, to use them simply make use of the `-p` option
and fill in the rest of the undefined parameters:

```
python simulate.py -p conway -d 64x64 -i 32
```

## Notice
Though this implementation can handle n-dimensional states as of now I have only implemented
graphical visualizations for 1D and 2D automata. If you want to create your own visualization
you can specify one of the text based formats (e.g. `txt`, `npy`).

## Examples

_1D pattern rule 772 radius=2_<br>
![772](https://raw.githubusercontent.com/tim-fi/pycells/master/images/772.png)

_Conway's Game of Life (2D count rule 6152 radius=1)_<br>
![conway](https://raw.githubusercontent.com/tim-fi/pycells/master/images/long_conway.gif)



# Examples

_1D pattern rule 772 radius=2_<br>
`pycells -m pattern -r 772 -n 2 -d 128 -i 127`<br>
![772](https://media.githubusercontent.com/media/timfi/pycells/master/images/772.png)

---

_2D pattern rule 12345678 radius=1_<br>
`pycells -m pattern -r 12345678 -d 100x100 -i 1024 --parallelize --skip-initial-state`<br>
![12345678](https://media.githubusercontent.com/media/timfi/pycells/master/images/12345678.gif)

---

_Conway's Game of Life (2D count rule 6152 radius=1)_<br>
`pycells -p conway -d 128x128 -i 1024 --parallelize --skip-initial-state`<br>
![conway](https://media.githubusercontent.com/media/timfi/pycells/master/images/long_conway.gif)
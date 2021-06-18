# monospace
An android Python3 game project, using desper + SDL2

### The game
A modern reinterpretation of the great classic space invaders. Destroy aliens until the target score is 0, receive a powerup, repeat.

### Why
Mainly an experiment, testing SDL on android coupled with my library [desper](https://github.com/Ball-Man/desper).

### Build and play
The game can be found on Google Play ([here](https://play.google.com/store/apps/details?id=org.ball.monospace)), but you are free to test the game on your local machine by first of all installing the requirements:
```bash
python -m pip install -r requirements.txt
```
And finally running the game with:
```bash
python main.py
```
Note that private instances of the game will not be able to submit scores to the public leaderboard (but should be able to fetch the already existing ones).

#### Android builds
Exporting private android builds is also possible, and is done via [buildozer](https://buildozer.readthedocs.io/en/latest/), a project developed by the kivy team to export kivy apps to android.
If you buildozer is correctly installed, a debug build should be obainable by simply:
```bash
buildozer android debug
```
In order to deploy and test the game on a connected device a combination of commands can be used:
```bash
buildozer android debug deploy run logcat
```

#### Requirements
In general:
* Python 3.8 >=
* SDL2 (on Windows machines, install pysdl2-dll via `python -m pip install pysdl2-dll`)
* A bunch of Python packages that can be installed via `python -m pip install -r requirements.txt`

For android builds:
* Buildozer
* Cython
* Jnius

Android requirements can easily be satisfied with `python -m pip install -r android_requirements.txt`

### Contributing and more
Honestly, I don't know if a complete documentation will ever exist for this game. Docstrings are there, hence a trivial sphinx doc is not to be excluded, but it's certainly not my main focus. Also, I don't expect anyone to be contributing due to the nature of the project (a game published under my name, certainly not an interesting tool), but just in case, I will give a few pointers to anyone willing to do so:

This repository is trunk-like based, meaning that most of the development takes place on `master`. Other branches are used for releases and no direct commit should take place there (only merges and cherry picking). Please do not create new releases, aim all your PRs to `master`. Branches with a `b` in front of the name (eg. `b0.2.3`) are for beta releases. The first stable release is `0.4.0`.

### Special thanks
To everyone who believes in my work and to [gmiscores](https://gmiscores.altervista.org/), a simple service for leaderboards maintained by a dear friend. I developed a Python binding for his API that can be found [here](https://github.com/Ball-Man/pygmiscores).


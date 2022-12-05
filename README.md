# rbgcraft

## Fishing

### Overview

Automatic fishing in WoW, using a combination of: mouse/keyboard automation, audio processing, and computer vision.

![Alt text](images/status_blurred.png?raw=true)
![Alt text](images/status.png?raw=true) 

### Running the project

Setup the game as follows:
* Default UI scale
* Options -> Enable Sound -> Effects on 100% (all other sub volumes on 0%)
* Keybind fish to 9, alternatively change the keybind on [config](fishing/config.py).

Install via
```commandline
python setup.py install
```

Run via:
```commandline
python -c "import fishing; fishing.fish()"
```
or
```python
import fishing
fishing.fish()
```
Then click on the game window to begin.

### Dependencies
* [Open CV](https://pypi.org/project/opencv-python/)
* [SoundCard](https://pypi.org/project/SoundCard/)
* [PyAutoGUI](https://pypi.org/project/PyAutoGUI/)

### Task List

- [ ] Audio signal inference to use only game sound, currently it listens to all desktop sounds.
- [ ] Work in background, so that user can run other applications actively.
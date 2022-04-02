# fake_piano
Play any piece on the piano with no musical knowledge.

The notes played on the piano will be replaced in realtime by those specified in a MIDI file previously configured, allowing you to playback the original melody pressing random keys.

Although the program has been designed to use a digital piano as input device and a MIDI port as output, it is possible to use any input or output providing its implementation.

## Installation
### Minimum requirements
*Python3* is required to execute the scripts. Aditionally, you may need to install these tools for proper functioning.

* [Mido](https://pypi.org/project/mido/) - MIDI file and message handling
```
pip install mido
```
* [python-rtmidi](https://pypi.org/project/python-rtmidi/) - Realtime MIDI input / output communication
```
pip install python-rtmidi
```

### Optional requirements
To extend compatibility with other input/output devices it may be necessary to install their corresponding third party drivers or libraries.

* [pyFluidSynth](https://github.com/nwhitehead/pyfluidsynth) - Necessary for FluidSynthOutput to work.
```
pip install pyFluidSynth
```
* [pynput](https://pypi.org/project/pynput/) - Necessary for KeyboardOutput to work.
```
pip install pynput
```
* [pyPS4Controller](https://pypi.org/project/pyPS4Controller/) - Necessary for DS4Input (DualShock 4) to work.
```
pip install pyPS4Controller
```

## Usage

The program consists of two basic parts, the reading of MIDI files and their playback. The classes corresponding to each main task are Reader and Player respectively.

The Reader object is used to read a MIDI file and create a Playable object which the Player is able to play.

The Player object is responsible for reading the messages sent by the chosen input device and modifying them before sending them to the configured output device.

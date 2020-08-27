# fake_piano
Play MIDI files by randomly pressing keys on a digital piano or any other input device.
The idea is to play the next note or chord in the MIDI file every time a key is pressed on the specified input device.

Although the initial purpose was to act between MIDI ports, listening from a digital piano and sending messages to an output port,
the input/ouptut system is fully customizable, so you can adapt it to work with any device you want.

## Requirements
You need Python 3 to run fake_piano.

* [Mido](https://pypi.org/project/mido/) - To work with MIDI files
```
pip install mido
```
* [python-rtmidi](https://pypi.org/project/python-rtmidi/) - To work with MIDI ports
```
pip install python-rtmidi
```

### Optional dependencies
You can optionally install other packages to be able to run some of the included examples

* [pyFluidSynth](https://github.com/nwhitehead/pyfluidsynth) - To use FluidSynth as the ouptut.
```
pip install pyFluidSynth
```
* [pynput](https://pypi.org/project/pynput/) - To use the computer's keyboard as the input device.
```
pip install pynput
```
* [pyPS4Controller](https://pypi.org/project/pyPS4Controller/) - To use the DualShock 4 controller as the input device.
```
pip install pyPS4Controller
```

## Usage
Pyton package or GUI.
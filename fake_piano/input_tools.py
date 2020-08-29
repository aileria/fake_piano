from .player import Player
import rtmidi
from rtmidi.midiutil import open_midiinput
from datetime import datetime

DEFAULT_INPUTS = (DigitalPianoInput)

def available_inputs() -> list:
    return rtmidi.MidiIn().get_ports() + (DEFAULT_INPUTS)

class Input:
    """Interface that input devices must implement to comunicate with the Player object."""

    def start(self): ...
    def stop(self): ...

class DigitalPianoInput(Input):
    """Implementation of Input for a digital piano"""

    def __init__(self):
        #self.midi_in = rtmidi.MidiIn(b'in')
        self.midi_in = rtmidi.MidiIn()
        i = 0
        for port in self.midi_in.get_ports():
            if 'Piano' in port:
                self.midi_in, port_name = open_midiinput(port=i)
                break
            i += 1
        else:
            raise ValueError("Unable to find Piano")

    def __str__(self):
        return 'Digital Piano'

    def start(self):
        data = self.callback # data to be used by rtmidi inside the callback function
        self.midi_in.set_callback(self.process, data)

    def stop(self):
        self.midi_in.close_port()

    def process(self, message_and_delta, callback):
        # Receive message
        message = message_and_delta[0]
        delta_time = message_and_delta[1]

        # Process
        if message:
            # noteon or noteoff
            if len(message) >= 3 and message[0] == 144:
                print(message, delta_time)
                # noteoff
                if message[2] == 0:
                    msg = {
                        'type': Player.NOTE_OFF,
                        'note': message[1]
                    }
                # noteon
                else:
                    msg = {
                        'type': Player.NOTE_ON,
                        'note': message[1],
                        'vel': message[2]
                    }
            # sustain
            elif message[0] == 176:
                msg = {
                    'type': Player.CONTROL,
                    'ctrl': message[1],
                    'val': message[2]
                }
            # Send message to Player
            callback(msg, delta_time)
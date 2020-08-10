import player
import rtmidi_python as rtmidi
from rtmidi.midiutil import open_midiinput
from threading import Thread
from datetime import datetime
# Keyboard
from pynput.keyboard import Listener, Key
# DS4
from pyPS4Controller.controller import Controller

class Input:
    """Interface that input devices must implement to comunicate with the Player object."""

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        pass
    
    def stop(self):
        pass

class KeyboardInput(Input):
    """Implementation of Input for a computer keyboard. Every key will be interpreted
    as a noteon message except the shift keys (right or left), which can be used as the 
    sustain pedal."""

    INPUT_VELOCITY = 60

    def __init__(self):
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.t0 = datetime.now()
        self.active_keys = {}

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def fake_key_generator(self):
        for i in iter(int, 1):
            yield i%89

    def on_press(self, key):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        # Process
        if key == Key.shift or key == Key.shift_r:
            msg = {
                'type': player.Player.CONTROL,
                'ctrl': 64,
                'val': 0
            }
        else:
            # Validate and update active_keys
            try:
                key = key.char.lower()
            except AttributeError:
                return

            if key in self.active_keys.keys():
                return
            else:
                self.active_keys[key] = next(self.fake_key_generator())

            # Build message
            msg = {
                'type': player.Player.NOTE_ON,
                'note': self.active_keys[key],
                'vel': self.INPUT_VELOCITY
            }
        self.callback(msg, self.delta_time.total_seconds())

    def on_release(self, key):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        # Process
        if key == Key.shift or key == Key.shift_r:
            msg = {
                'type': player.Player.CONTROL,
                'ctrl': 64,
                'val': 0
            }
        else:
            # Validate
            try:
                key = key.char.lower()
            except AttributeError:
                return
                
            # Build message
            msg = {
                'type': player.Player.NOTE_OFF,
                'note': self.active_keys.pop(key)
            }
        self.callback(msg, self.delta_time.total_seconds())

class DigitalPianoInput(Input):
    """Implementation of Input for a Yamaha P-45."""

    def __init__(self):
        self.midi_in = rtmidi.MidiIn(b'in')
        i = 0
        for port in self.midi_in.ports:
            if b'Piano' in port:
                self.midi_in, port_name = open_midiinput(i)
                break
            i += 1
        else:
            raise ValueError("Unable to find Piano")

    def available_midi_in(self):
        """Returns all available midi input port names"""

        return tuple(rtmidi.MidiIn(b'in').ports)
    
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
                        'type': player.Player.NOTE_OFF,
                        'note': message[1]
                    }
                # noteon
                else:
                    msg = {
                        'type': player.Player.NOTE_ON,
                        'note': message[1],
                        'vel': message[2]
                    }
            # sustain
            elif message[0] == 176:
                msg = {
                    'type': player.Player.CONTROL,
                    'ctrl': message[1],
                    'val': message[2]
                }
            # Send message to Player
            callback(msg, delta_time)

class DS4Input(Input):
    """Implementation of Input for a DualShock4 controller."""

    INPUT_VELOCITY = 60

    def __init__(self):
        self.controller = DS4PianoController(self.on_press, self.on_release, self.on_sustain)
        self.active_buttons = {}
        self.t0 = datetime.now()

    def start(self):
        self.controller.listen(timeout=860)

    def stop(self):
        del self.controller

    def fake_key_generator(self):
        for i in iter(int, 1):
            yield i%89

    def on_press(self, button):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        if button in self.active_buttons.keys():
            return
        else:
            self.active_buttons[button] = next(self.fake_key_generator())

        # Build message
        msg = {
            'type': player.Player.NOTE_ON,
            'note': self.active_buttons[button],
            'vel': self.INPUT_VELOCITY
        }
        self.callback(msg, self.delta_time.total_seconds())

    def on_release(self, button):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        if button not in self.active_buttons.keys(): return
        
        # Build message
        msg = {
            'type': player.Player.NOTE_OFF,
            'note': self.active_buttons.pop(button)
        }
        self.callback(msg, self.delta_time.total_seconds())

    def on_sustain(self, value):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        msg = {
            'type': player.Player.CONTROL,
            'ctrl': 64,
            'val': value
        }
        self.callback(msg, self.delta_time.total_seconds())

class DS4PianoController(Controller):

    def __init__(self, on_press, on_release, on_sustain):
        Controller.__init__(self, interface="/dev/input/js0", event_format="3Bh2b", connecting_using_ds4drv=False)
        self.on_press = on_press
        self.on_release = on_release
        self.on_sustain = on_sustain

    # Normal keys
    def on_x_press(self):
       self.on_press("x")

    def on_x_release(self):
       self.on_release("x")

    def on_triangle_press(self):
       self.on_press("t")

    def on_triangle_release(self):
       self.on_release("t")

    def on_square_press(self):
       self.on_press("t")

    def on_square_release(self):
       self.on_release("t")

    def on_circle_press(self):
       self.on_press("t")

    def on_circle_release(self):
       self.on_release("t")

    def on_left_arrow_press(self):
        self.on_press("lr_arrow")

    def on_right_arrow_press(self):
        self.on_press("lr_arrow")

    def on_left_right_arrow_release(self):
        self.on_release("lr_arrow")

    def on_up_arrow_press(self):
        self.on_press("ud_arrow")

    def on_down_arrow_press(self):
        self.on_press("ud_arrow")

    def on_up_down_arrow_release(self):
        self.on_release("ud_arrow")

    def on_R1_press(self):
        self.on_press("r1")

    def on_L1_press(self):
        self.on_press("l1")

    def on_R1_release(self):
        self.on_release("r1")

    def on_L1_release(self):
        self.on_release("l1")

    # Sustain
    def on_R2_press(self, value):
        value = int((value + 32767)/65534 * 127)
        self.on_sustain(value)
    
    def on_R2_release(self):
        self.on_sustain(0)
    
    def on_L2_press(self, value):
        value = int((value + 32767)/65534 * 127)
        self.on_sustain(value)
    
    def on_L2_release(self):
        self.on_sustain(0)

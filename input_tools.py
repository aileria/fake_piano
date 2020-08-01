from player import Player
import rtmidi_python as rtmidi
from threading import Thread
from datetime import datetime
# Keyboard
from pynput.keyboard import Listener, Key
# DS4
from pyPS4Controller.controller import Controller

class Input():
    """Interface that input devices must implement to comunicate with the Player object."""

    def __init__(self, player: Player):
        self.player = player

    def start(self):
        pass
    
    def stop(self):
        pass

class KeyboardInput(Input):
    """Implementation of Input for a computer keyboard. Every key will be interpreted
    as a noteon message except the shift keys (right or left), which can be used as the 
    sustain pedal."""

    INPUT_VELOCITY = 60

    def __init__(self, player: Player):
        super().__init__(player)
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
                'type': Player.CONTROL,
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
                'type': Player.NOTE_ON,
                'note': self.active_keys[key],
                'vel': self.INPUT_VELOCITY
            }
        self.player.process(msg, self.delta_time.total_seconds())

    def on_release(self, key):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        # Process
        if key == Key.shift or key == Key.shift_r:
            msg = {
                'type': Player.CONTROL,
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
                'type': Player.NOTE_OFF,
                'note': self.active_keys.pop(key)
            }
        self.player.process(msg, self.delta_time.total_seconds())

class DigitalPianoInput(Input):
    """Implementation of Input for a Yamaha P-45."""

    def __init__(self, player: Player):
        super().__init__(player)
        self.midi_in = rtmidi.MidiIn(b'in')
        i = 0
        for port in self.midi_in.ports:
            if b'Piano' in port:
                self.midi_in.open_port(i)
                break
            i += 1
        else:
            raise ValueError("Unable to find Piano")

    def available_midi_in(self):
        """Returns all available midi input port names"""

        return tuple(rtmidi.MidiIn(b'in').ports)
    
    def start(self):
        self.stop_thread = False
        self.thread = Thread(target=self.loop, args=(lambda : self.stop_thread))
        self.thread.start()

    def stop(self):
        self.midi_in.close_port()
        self.stop_thread = True
        self.thread.join()

    #TODO fix sustain_on/off distinction in piano
    def loop(self, stop_thread):
        while True:
            # Exit condition
            if stop_thread: break

            # Receive message
            message, delta_time = self.midi_in.get_message()

            # Process
            if message:
                # noteon or noteoff
                if len(message) >= 3 and message[0] == 144:
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
                self.player.process(msg, delta_time)

class DS4Input(Input):
    """Implementation of Input for a DualShock4 controller."""

    INPUT_VELOCITY = 60

    def __init__(self, player: Player):
        super().__init__(player)
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
            'type': Player.NOTE_ON,
            'note': self.active_buttons[button],
            'vel': self.INPUT_VELOCITY
        }
        self.player.process(msg, self.delta_time.total_seconds())

    def on_release(self, button):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        # Build message
        msg = {
            'type': Player.NOTE_OFF,
            'note': self.active_buttons.pop(button)
        }
        self.player.process(msg, self.delta_time.total_seconds())

    def on_sustain(self, value):
        # Calculate delta_time
        self.t1 = datetime.now()
        self.delta_time = self.t1 - self.t0
        self.t0 = datetime.now()

        msg = {
            'type': Player.CONTROL,
            'ctrl': 64,
            'val': value
        }
        self.player.process(msg, self.delta_time.total_seconds())

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
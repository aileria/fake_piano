from pynput.keyboard import Listener, Key
from player import Player
import rtmidi_python as rtmidi
from threading import Thread
from datetime import datetime

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
                'mode': Player.CONTROL,
                'ctrl': 64,
                'val': 0
            }
        else:
            # Update active_keys
            self.active_keys[key] = next(self.fake_key_generator())
            msg = {
                'mode': Player.NOTE_ON,
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
                'mode': Player.CONTROL,
                'ctrl': 64,
                'val': 0
            }
        else:
            msg = {
                'mode': Player.NOTE_OFF,
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
                            'mode': Player.NOTE_OFF,
                            'note': message[1]
                        }
                    # noteon
                    else:
                        msg = {
                            'mode': Player.NOTE_ON,
                            'note': message[1],
                            'vel': message[2]
                        }
                # sustain
                elif message[0] == 176:
                    msg = {
                        'mode': Player.CONTROL,
                        'ctrl': message[1],
                        'val': message[2]
                    }

                # Send message to Player
                self.player.process(msg, delta_time)
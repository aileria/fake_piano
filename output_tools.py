try:
    import fluidsynth
except:
    print("NO FLUIDSYNTH")
#import rtmidi_python as rtmidi #linux
import rtmidi #windows
from threading import Thread

class Output:
    """Interface that output devices must implement to be used by the Player object."""

    def note_on(self, key, velocity):
        pass
    
    def note_off(self, key):
        pass

    def control(self, ctrl, value):
        pass

class FluidSynthOutput(Output):
    """Implementation of Output for FluidSynth."""

    def __init__(self, sf2_path, driver='alsa', gain=1, volume=127):
        super().__init__()
        self.synth = fluidsynth.Synth(gain=gain)
        self.synth.start(driver)
        sfid = self.synth.sfload(sf2_path)
        self.synth.program_select(0, sfid, 0, 0)
        self.synth.cc(0, 7, volume)

    def note_on(self, key, velocity):
        self.synth.noteon(0, key, velocity)

    def note_off(self, key):
        self.synth.noteoff(0, key)

    def control(self, ctrl, value):
        self.synth.cc(0, ctrl, value)

class DigitalPianoOutput(Output):
    """Implementation of Output for a Yamaha P-45."""

    def __init__(self):
        self.midi_out = rtmidi.MidiOut(b'out')
        i = 0
        for port_name in self.midi_out.ports:
            if b'Piano' in port_name:
                self.midi_out.open_port(i)
                break
            i += 1
        else:
            raise Exception("Unable to detect Piano")
    
    def note_on(self, key, velocity):
        self.midi_out.send_message([0x90, key, velocity])

    def note_off(self, key):
        self.midi_out.send_message([0x80, key, 0])

    def control(self, ctrl, value):
        self.midi_out.send_message([0xb0, ctrl, value])

class VirtualPortOutput(Output):
    """Implementation of Output for a virtual MIDI port."""

    def __init__(self, port_name='fake_piano'):
        self.midi_out = rtmidi.MidiOut()
        # Try to open virtual port (not compatible with windows)
        try:
            self.midi_out.open_virtual_port(name=port_name)
        except Exception:
            print("Virtual port couldn't be opened")

        # Workaround for windows with loopMidi or similar
        i = 0
        for port in self.midi_out.get_ports():
            if port_name in port:
                self.midi_out.open_port(i)
                break
            i += 1

    def note_on(self, key, velocity):
        self.midi_out.send_message([0x90, key, velocity])

    def note_off(self, key):
        self.midi_out.send_message([0x80, key, 0])

    def control(self, ctrl, value):
        self.midi_out.send_message([0xb0, ctrl, value])
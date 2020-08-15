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

class MidiPortOutput(Output):
    """Implementation of Output for a MIDI port."""

    def __init__(self, port_name='fake_piano', virtual=False):
        self.midi_out = rtmidi.MidiOut()

        # Open virtual port (not compatible with windows)
        if virtual:
            self.midi_out.open_virtual_port(name=port_name)
            return
            
        # Open existing port
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

class DigitalPianoOutput(MidiPortOutput):
    """Implementation of Output for a Yamaha P-45."""

    def __init__(self, port_name='fake_piano', virtual=False):
        super().__init__(port_name='Piano')
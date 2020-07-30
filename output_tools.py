import fluidsynth

class Output():
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

if __name__=='__main__':
    fsout = FluidSynthOutput("soundfonts/AA_piano_cola.sf2")
    fsout.note_on(60,30)
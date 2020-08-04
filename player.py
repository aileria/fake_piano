import rtmidi_python as rtmidi
import fluidsynth
import mido
import time
from playable import Playable
from reader import Reader
import input_tools
from sequencer import Sequencer

class Player:

    NOTE_ON = 0
    NOTE_OFF = 1
    CONTROL = 2
    SUSTAIN_ON = 3
    SUSTAIN_OFF = 4

    def __init__(self, sf2_path, driver='alsa', channel=0, synth_gain=1, volume=127, input_threshold=0.02):
        # Synth
        self._synth = fluidsynth.Synth(gain=synth_gain)
        self._synth.start(driver)
        sfid = self._synth.sfload(sf2_path)
        self._synth.program_select(0, sfid, 0, 0)
        self._synth.cc(0, 7, volume)
        self.breakpoint_note = -1
        # Threshold
        self._threshold = input_threshold
        # Midi input port
        self.midi_in = None 
        # Active keys list
        self._active_notes = {} # {real_note: fake_note}
        # Sequencer for accompaniment
        self.sequencer = Sequencer(self._synth) #TODO change initialization to set_output method when implemented

    def set_playable(self, playable: Playable):
        self.playable = playable

    @property
    def active_notes(self):
        return self._active_notes

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, t):
        self._threshold = t

    # Breakpoint note
    def set_breakpoint_note(self, note):
        self.breakpoint_note = note
    
    def read_breakpoint_note(self, time_limit=5):
        """Reads the breakpoint note from the connected MIDI input device"""

        breakpoint_note = -1
        print('Enter breakpoint note:')
        start_time = time.perf_counter()
        while breakpoint_note<=0:
            # Check time limit
            if time.perf_counter() - start_time >= time_limit:
                break
            # Read note
            message = self.midi_in.get_message()[0]
            if message:
                if message[0] == 144:
                    breakpoint_note = message[1]
                    print("Breakpoint note = "+str(breakpoint_note)+"\n")
        self.breakpoint_note = breakpoint_note

    # Threshold
    def set_threshold(self, threshold):
        self.threshold = threshold

    def set_playback_speed(self, speed):
        self.playback_speed = speed

    def process(self, message, delta_time):
        threshold = self._threshold     # Minimum time (seconds) between inputs
        time = 0.0                      # Elapsed time between inputs
        
        # Update time
        if delta_time:
            time += delta_time

        # Process message
        if message:
            # NOTEON
            if message['type'] == Player.NOTE_ON:
                # validate
                if time < threshold or message['note'] < self.breakpoint_note:
                    return

                mel_block, acc_block = self.playable.next()
                real_note = message['note']

                # add entry to active_notes and play notes
                self.active_notes[real_note] = mel_block
                for note in mel_block: # turn on all notes in the block
                    self._synth.noteon(0, note.value, message['vel'])

                # add accompaniment to sequencer
                if acc_block:
                    self.sequencer.add(acc_block, self.playback_speed) # playback_speed changes the accomp playback speed
                    
                # Debug
                print(message, delta_time)

            # NOTEOFF
            elif message['type'] == Player.NOTE_OFF:
                real_note = message['note']
                if real_note in self.active_notes.keys():
                    for n in self.active_notes.pop(real_note): # turn off all notes linked to the real one
                        self._synth.noteoff(0, n.value)
            # CONTROL
            else:
                self._synth.cc(0, message['ctrl'], message['val'])

    def start(self):
        self.sequencer.add(self.playable.initial_accomp(), 1)

    def stop(self):
        pass

if __name__ == '__main__':
    ply = Player("soundfonts/FluidR3_GM.sf2", synth_gain=1, input_threshold=0)
    reader = Reader(0)
    reader.load_midi("midi_files/fur_elise.mid")
    reader.load_melody("right_hand")
    reader.load_accomp("left_hand")
    ply.set_playable(reader.create_playable())
    ply.set_playback_speed(1)
    ply.start()
    input_device = input_tools.KeyboardInput(ply)
    input_device.start()
    while True: pass
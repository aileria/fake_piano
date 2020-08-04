import time
from playable import Playable
from reader import Reader
from input_tools import *
from output_tools import *
from sequencer import Sequencer

class Player:

    NOTE_ON = 0
    NOTE_OFF = 1
    CONTROL = 2
    SUSTAIN_ON = 3
    SUSTAIN_OFF = 4

    def __init__(self, input_threshold=0.02):
        self.breakpoint_note = -1
        self.threshold = input_threshold
        self.active_notes = {} # {real_note: fake_note}

    # Playable
    def set_playable(self, playable: Playable):
        self.playable = playable

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

    # Input and output
    def set_input(self, input_device):
        input_device.set_callback(self.process)

    def set_output(self, output):
        self.output = output
        self.sequencer = Sequencer(output)

    # Process message
    def process(self, message, delta_time):
        threshold = self.threshold     # Minimum time (seconds) between inputs
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
                    self.output.note_on(note.value, message['vel'])

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
                        self.output.note_off(n.value)
            # CONTROL
            else:
                self.output.control(message['ctrl'], message['val'])

    def start(self):
        self.sequencer.add(self.playable.initial_accomp(), 1)

    def stop(self):
        pass

if __name__ == '__main__':

    ply = Player(input_threshold=0)

    reader = Reader(0)
    reader.load_midi("midi_files/nocturne.mid")
    reader.load_melody("right_hand")
    reader.load_accomp("left_hand")
    ply.set_playable(reader.create_playable())
    ply.set_playback_speed(1)

    output_device = FluidSynthOutput("soundfonts/FluidR3_GM.sf2")
    ply.set_output(output_device)
    input_device = DigitalPianoInput()
    ply.set_input(input_device)

    ply.start()
    input_device.start()
    while True: pass
from playable import Playable
from sequencer import Sequencer

class Player:

    NOTE_ON = 0
    NOTE_OFF = 1
    CONTROL = 2
    SUSTAIN_ON = 3
    SUSTAIN_OFF = 4

    def __init__(self, input_threshold=0):
        self.breakpoint_note = -1
        self.threshold = input_threshold
        self.active_notes = {} # {real_note: fake_notes}

    # Playable
    def set_playable(self, playable: Playable):
        self.playable = playable

    # Threshold
    def set_threshold(self, threshold):
        self.threshold = threshold

    # Input and output
    def set_input(self, input_device):
        self.input = input_device
        self.input.set_callback(self.process)

    def set_output(self, output_device):
        self.output = output_device
        self.sequencer = Sequencer(self.output)

    # Process messages
    def process(self, message, delta_time):
        print(message, delta_time)

    def start(self):
        self.input.start()

    def stop(self):
        self.input.stop()

class AdaptativePlayer(Player):
    
    def __init__(self, memory_size=5, initial_speed=1):
        super().__init__()
        self.memory_size = memory_size
        self.rel_speed_avg = 0
        self.last_speed_ratios = []
        self.initial_speed = initial_speed

    def start(self):
        super().start()
        self.sequencer.add(self.playable.initial_accomp(), self.initial_speed)

    def process(self, message, delta_time):
        threshold = self.threshold     # Minimum time (seconds) between inputs
        time = 0.0
        
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

                # update average time between inputs
                self.last_speed_ratios.insert(0, mel_block[0].duration / time)
                if len(self.last_speed_ratios) > self.memory_size:
                    self.last_speed_ratios.pop()

                self.rel_speed_avg = sum(self.last_speed_ratios) / len(self.last_speed_ratios) # Make exponential (EMA)
                cur_speed = self.rel_speed_avg

                # add entry to active_notes and play notes
                self.active_notes[real_note] = mel_block
                for note in mel_block: # turn on all notes in the block
                    self.output.note_on(note.value, message['vel'])

                # add accompaniment to sequencer
                if acc_block:
                    self.sequencer.add(acc_block, cur_speed) # playback_speed changes the accomp playback speed
                    
                time = 0.0

            # NOTEOFF
            elif message['type'] == Player.NOTE_OFF:
                real_note = message['note']
                if real_note in self.active_notes.keys():
                    for n in self.active_notes.pop(real_note): # turn off all notes linked to the real one
                        self.output.note_off(n.value)
            # CONTROL
            else:
                self.output.control(message['ctrl'], message['val'])

class FixedSpeedPlayer(Player):

    def __init__(self, playback_speed=1):
        super().__init__()
        self.playback_speed = playback_speed

    def start(self):
        super().start()
        self.sequencer.add(self.playable.initial_accomp(), self.playback_speed)

    def process(self, message, delta_time):
        threshold = self.threshold     # Minimum time (seconds) between inputs
        time = 0.0
        
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
                    
                time = 0.0

            # NOTEOFF
            elif message['type'] == Player.NOTE_OFF:
                real_note = message['note']
                if real_note in self.active_notes.keys():
                    for n in self.active_notes.pop(real_note): # turn off all notes linked to the real one
                        self.output.note_off(n.value)
            # CONTROL
            else:
                self.output.control(message['ctrl'], message['val'])

class MelodyPlayer(Player):
    def process(self, message, delta_time):
        threshold = self.threshold     # Minimum time (seconds) between inputs
        time = 0.0
        
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

                mel_block = self.playable.next()[0]
                real_note = message['note']

                # add entry to active_notes and play notes
                self.active_notes[real_note] = mel_block
                for note in mel_block: # turn on all notes in the block
                    self.output.note_on(note.value, message['vel'])
                    
                time = 0.0

            # NOTEOFF
            elif message['type'] == Player.NOTE_OFF:
                real_note = message['note']
                if real_note in self.active_notes.keys():
                    for n in self.active_notes.pop(real_note): # turn off all notes linked to the real one
                        self.output.note_off(n.value)
            # CONTROL
            else:
                self.output.control(message['ctrl'], message['val'])
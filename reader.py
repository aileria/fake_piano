from playable import Playable, Note
from mido import MidiFile

class Reader():
    def __init__(self, read_threshold=1):
        self.threshold = read_threshold
        self.melody = None
        self.accomp = None

    def load_midi(self, path):
        """Loads the MIDI file of the specified path"""

        self.midi = MidiFile(path)

    def available_midi_tracks(self):
        """Returns a list with the available tracks in the MIDI file"""

        return tuple([track.name for track in self.midi.tracks])

    def load_melody(self, name):
        """Loads the MIDI track which name contains the given name"""

        # Check if MIDI is loaded
        if not self.midi:
            raise ValueError("MIDI file not loaded")
        for track in self.midi.tracks:
            if name in track.name:
                mel_track = track
                break
        else:
            raise ValueError("MIDI track not found")
        
        # Create new MIDI file from track
        midi = MidiFile()
        midi.tracks.append(mel_track)

        # Read melody from MIDI
        elapsed_time = 0
        last_note_time = 0
        completed_pointer = 0
        melody_notes = []
        aux_block = []

        for msg in midi:
            elapsed_time += msg.time
            if msg.type == 'note_on':
                if last_note_time == 0:
                    last_note_time = elapsed_time
                if elapsed_time - last_note_time > self.threshold:
                    melody_notes.append(aux_block.copy())
                    aux_block.clear()
                    last_note_time = elapsed_time
                aux_block.append(Note(msg.note, elapsed_time))

            if msg.type == 'note_off':
                completed_block = True  # prevents completed_pointer from advancing
                # Search note in melody_notes
                for i in range(completed_pointer,len(melody_notes)):
                    for note in melody_notes[i]:
                        if note.duration == 0:
                            if note.value == msg.note:
                                note.set_end_time(elapsed_time)
                                break
                            completed_block = False
                    if completed_block:
                        completed_pointer += 1
                # Search note in aux_block
                for note in aux_block:
                    if note.duration == 0:
                        if note.value == msg.note:
                            note.set_end_time(elapsed_time)
                            break
        
        self.melody = melody_notes
        for notes in melody_notes:
            for note in notes:
                print(note.value, note.start_time, note.duration)
    
    def load_accomp(self, name):

        # Check if MIDI is loaded
        if not self.midi:
            raise ValueError("MIDI file not loaded")
        for track in self.midi.tracks:
            if name in track.name:
                acc_track = track
                break
        else:
            raise ValueError("MIDI track not found")
        
        # Create new MIDI file from track
        midi = MidiFile()
        midi.tracks.append(acc_track)

        # Read accompaniment from MIDI
        elapsed_time = 0
        completed_pointer = 0
        accomp_notes = [[] for i in range(len(self.melody)+1)]
        melody_position = 0
        last_mel_start = 0

        for msg in midi:
            elapsed_time += msg.time

            # adjust position relative to self.melody
            while melody_position < len(self.melody) and elapsed_time >= self.melody[melody_position][0].start_time:
                melody_position += 1
                last_mel_start = self.melody[melody_position-1][0].start_time

            if msg.type == 'note_on':
                accomp_notes[melody_position].append(
                    Note(msg.note, elapsed_time - last_mel_start, msg.velocity))

            if msg.type == 'note_off':
                completed_block = True
                for i in range(completed_pointer,len(accomp_notes)):
                    notes = accomp_notes[i]
                    for note in notes:
                        if note.duration == 0:
                            if note.value == msg.note:
                                note.set_end_time(elapsed_time)
                                break
                            completed_block = False
                    if completed_block:
                        completed_pointer += 1
        
        # Remove useless time at the beginning
        for note in accomp_notes[0]:
            note.set_start_time(note.start_time - accomp_notes[0][0].start_time)

        self.accomp = accomp_notes

    def create_playable(self):
        return Playable(self.melody, self.accomp)
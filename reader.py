import mido
from playable import Playable, Note

from output_tools import FluidSynthOutput
from mido import MidiFile
import time
from sequencer import Sequencer

class Reader():
    def __init__(self, read_threshold=1):
        self.threshold = read_threshold
        self.melody = None
        self.accomp = None

    def load_midi(self, path):
        """Loads the MIDI file of the specified path"""

        self.midi = mido.MidiFile(path)

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
        completed_pointer = 0
        melody_notes = []
        untracked_flag = False      # prevents completed_pointer from advancing

        # melody (list of simple notes, not grouping in chords yet)
        for msg in midi:
            elapsed_time += msg.time
            if msg.type == 'note_on':
                melody_notes.append([Note(msg.note, elapsed_time)])
            if msg.type == 'note_off':
                for i in range(completed_pointer,len(melody_notes)):
                    for note in melody_notes[i]:
                        if note.duration == 0:
                            untracked_flag = True
                            if note.value == msg.note:
                                note.set_duration(elapsed_time)
                                untracked_flag = False
                                break
                        else:
                            if not untracked_flag:
                                completed_pointer += 1
        
        self.melody = melody_notes
    
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
                accomp_notes[melody_position].append(Note(msg.note, elapsed_time - last_mel_start, msg.velocity))

            if msg.type == 'note_off':
                for i in range(completed_pointer,len(accomp_notes)):
                    notes = accomp_notes[i]
                    for note in notes:
                        if note.duration == 0:
                            untracked_flag = True
                            if note.value == msg.note:
                                note.set_duration(elapsed_time)
                                untracked_flag = False
                                break
                        else:
                            if not untracked_flag:
                                completed_pointer += 1
        
        self.accomp = accomp_notes

    def create_playable(self):
        return Playable(self.melody, self.accomp)
import mido
from playable import Playable

class Reader():
    def __init__(self, read_threshold=1):
        self.threshold = read_threshold
        self.noteon_seq = []

    def load_midi(self, path):
        """Loads the MIDI file of the specified path"""

        self.midi = mido.MidiFile(path)

    def available_midi_tracks(self):
        """Returns a list with the available tracks in the MIDI file"""

        return tuple([track.name for track in self.midi.tracks])

    def load_track(self, name):
        """Loads the MIDI track which name contains the given name"""

        if not self.midi:
            raise ValueError("MIDI file not loaded")
        for track in self.midi.tracks:
            if name in track.name:
                play_track = track
                break
        else:
            raise ValueError("MIDI track not found")
        
        # Generate sequence from note_on  messages. Every element
        # will be a block of notes (to be played simultaneously)
        threshold = self.threshold      # minimum time (tics) between blocks of notes
        tics_on = 0                     # tics from last note_on
        aux_on = []                     # current block of note_on messages

        for msg in play_track:
            if msg.type == 'note_on':
                tics_on += msg.time
                if tics_on < threshold:             # Add note to current block
                    aux_on.append(msg.note)
                else:                               # Add note to new block
                    if aux_on:
                        self.noteon_seq.append(aux_on.copy())
                    tics_on = 0
                    aux_on.clear()
                    aux_on.append(msg.note)
    
    def create_playable(self):
        return Playable(self.noteon_seq)

    def save_playable(self):
        pass
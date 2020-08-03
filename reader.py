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
        last_mel_start = self.melody[0][0].start_time

        for msg in midi:
            elapsed_time += msg.time

            # adjust position relative to self.melody
            while melody_position < len(self.melody) and elapsed_time >= self.melody[melody_position][0].start_time:
                melody_position += 1
                last_mel_start = self.melody[melody_position-1][0].start_time

            if msg.type == 'note_on':
                accomp_notes[melody_position].append(Note(msg.note, elapsed_time - last_mel_start, msg.velocity)) #FIXME start_time is negative in first block (maybe initialize to 0 before loop)

            if msg.type == 'note_off':
                for i in range(completed_pointer,len(accomp_notes)):
                    notes = accomp_notes[i]
                    for note in notes:
                        if note.duration == 0:
                            untracked_flag = True
                            if note.value == msg.note:
                                note.set_duration(elapsed_time)
                                #note.start_time -= last_mel_start
                                untracked_flag = False
                                break
                        else:
                            if not untracked_flag:
                                completed_pointer += 1
        
        self.accomp = accomp_notes

    def create_playable(self):
        return Playable(self.melody, self.accomp)

    def save_playable(self):
        pass

if __name__=='__main__':
    reader = Reader()
    reader.load_midi("midi_files/fantaisie.mid")
    reader.load_melody("right_hand")

    mid_right = MidiFile()
    mid_left = MidiFile()
    mid0 = MidiFile("midi_files/moonlight_sonata.mid")

    for track in mid0.tracks:
        if "right" in track.name:
            play_track = track
        if "left" in track.name:
            acc_track = track
    mid_right.tracks.append(play_track)
    mid_left.tracks.append(acc_track)

    # Crear listas de objetos Note para melody y accomp
    elapsed_time = 0
    duration = 0
    completed_pointer = 0
    melody_notes = []
    untracked_flag = False      # prevents completed_pointer from advancing

    # melody (list of simple notes, not grouping in chords yet)
    for msg in mid_right:
        elapsed_time += msg.time
        if msg.type == 'note_on':
            melody_notes.append(Note(msg.note, elapsed_time))
        if msg.type == 'note_off':
            for i in range(completed_pointer,len(melody_notes)):
                note = melody_notes[i]
                if note.duration == 0:
                    untracked_flag = True
                    if note.value == msg.note:
                        note.set_duration(elapsed_time)
                        untracked_flag = False
                        break
                else:
                    if not untracked_flag:
                        completed_pointer += 1

    # accomp
    elapsed_time = 0
    duration = 0
    completed_pointer = 0
    accomp_notes = [[] for i in range(len(melody_notes)+1)]
    melody_position = 0
    last_mel_start = melody_notes[0].start_time

    for msg in mid_left:
        elapsed_time += msg.time

        # adjust position relative to melody_notes
        while melody_position < len(melody_notes) and elapsed_time >= melody_notes[melody_position].start_time:
            melody_position += 1
            last_mel_start = melody_notes[melody_position-1].start_time

        if msg.type == 'note_on':
            accomp_notes[melody_position].append(Note(msg.note, elapsed_time, msg.velocity))

        if msg.type == 'note_off':
            for i in range(completed_pointer,len(accomp_notes)):
                notes = accomp_notes[i]
                for note in notes:
                    if note.duration == 0:
                        untracked_flag = True
                        if note.value == msg.note:
                            note.set_duration(elapsed_time)
                            #note.start_time -= last_mel_start
                            untracked_flag = False
                            break
                    else:
                        if not untracked_flag:
                            completed_pointer += 1

    print(accomp_notes)
    exit()

    fsout = FluidSynthOutput("soundfonts/FluidR3_GM.sf2")
    seq = Sequencer(fsout)

    last_noteon = 0
    position = 0
    for note in melody_notes:
        seq.add(accomp_notes[position])
        position += 1
        time.sleep(note.start_time - last_noteon)
        last_noteon = note.start_time
        last_noteon = note.start_time
        print(note.value, note.start_time)
        fsout.note_on(note.value, 60)

    print(accomp_notes)
    for block in accomp_notes:
        print(block)
        seq.add(block)
        print("_________DONE__________")

    exit()

    for note in melody_notes:
        print(note.value, note.duration, note.start_time)

    fsout = FluidSynthOutput("soundfonts/FluidR3_GM.sf2")

    last_noteon = 0
    for note in melody_notes:
        time.sleep(note.start_time-last_noteon)
        last_noteon = note.start_time
        print(note.value, note.start_time)
        fsout.note_on(note.value, 60)

    while True: pass
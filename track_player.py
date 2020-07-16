import time
import mido
from mido import MidiFile, MidiTrack, MetaMessage

def main(fs, track):
    midi = mido.MidiFile()
    new_track = MidiTrack()
    new_track.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    new_track.append(MetaMessage('set_tempo', tempo=1500000, time=0))
    midi.tracks.append(new_track)
    for msg in track:
        new_track.append(msg)

    # Play
    for msg in midi.play():
        if msg.type == 'note_on':
            fs.noteon(0, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            fs.noteoff(0, msg.note)
        elif msg.type == 'control_change':
            fs.cc(0, msg.control, msg.value)
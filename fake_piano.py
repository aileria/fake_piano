import rtmidi_python as rtmidi
import fluidsynth
import mido

midi_path = 'midi_files/fantaisie.mid'
sf2_path = 'soundfonts/FluidR3_GM.SF2'

# Initialize MIDI input
midi_in = rtmidi.MidiIn(b'in')
i=0
for port_name in midi_in.ports:
    if b'Piano' in port_name:
        midi_in.open_port(i)
    i = i+1

# Initialize synth
fs = fluidsynth.Synth()
fs.start('alsa')
sfid = fs.sfload(sf2_path)
fs.program_select(0, sfid, 0, 0)

# Create noteon and noteoff sequences
noteon_seq = []
noteoff_seq = []
midi = mido.MidiFile(midi_path)

for track in midi.tracks:       # get right hand track from midi
    if 'right' in track.name:
        rhand_track = track
        break
else:
    rhand_track = midi

for msg in rhand_track:         # create sequences
    if msg.type == 'note_on':
        noteon_seq.insert(0, msg.note)
    elif msg.type == 'note_off':
        noteoff_seq.insert(0, msg.note)

# Handle messages
fs.noteon(0, 60, 60)
while True:
    message, delta_time = midi_in.get_message()
    if message:
        if message[0] == 144 and len(message) >= 3:     # noteon & noteoff
            print(message)
            if message[2] == 0: # noteoff
                fs.noteoff(0, noteoff_seq.pop())
            else: # noteon
                fs.noteon(0, noteon_seq.pop(), message[2])

        elif message[0] == 176:                         # sustain
            fs.cc(0, message[1], message[2])
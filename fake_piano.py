import rtmidi_python as rtmidi
import fluidsynth
import mido

midi_path = 'midi_files/fantaisie.mid'
sf2_path = 'soundfonts/FluidR3_GM.SF2'

# MIDI input
midi_in = rtmidi.MidiIn(b'in')
i=0
for port_name in midi_in.ports:
    if b'Piano' in port_name:
        midi_in.open_port(i)
    i = i+1

# Synth and sf2
fs = fluidsynth.Synth()
fs.start('alsa')
sfid = fs.sfload(sf2_path)
fs.program_select(0, sfid, 0, 0)

# Create noteon and noteoff sequences
noteon_seq = []
noteoff_seq = []
midi = mido.MidiFile(midi_path)
for msg in midi:
    if msg.type == 'note_on':
        if msg.velocity == 0: # noteoff
            noteoff_seq.append(msg.note)
        else: # noteon
            noteon_seq.append(msg.note)

# Handle messages
fs.noteon(0, 60, 60)
while True:
    message, delta_time = midi_in.get_message()
    if message:
        if message[0] == 144:
            print(message)
            if message[2] == 0: # noteoff
                fs.noteoff(0, noteoff_seq.pop(0))
            else: # noteon
                fs.noteon(0, noteon_seq.pop(0), message[2])
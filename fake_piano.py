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


threshold = 0   # Time threshold
tics_on = 0     # tics_from reference on
tics_off = 0    # tics_from reference off
aux_on = []
aux_off = []

for msg in rhand_track:         # create sequences
    if msg.type == 'note_on':
        if tics_on + msg.time < threshold:      # Notes played at same time
            aux_on.append(msg.note)
            tics_on = tics_on + msg.time
        else:                                   # Notes played at different time
            noteon_seq.insert(0, aux_on)
            tics_on = 0
            aux_on.clear()
        
    elif msg.type == 'note_off':
        if tics_off + msg.time < threshold:  
            aux_off.append(msg.note)
            tics_off = tics_off + msg.time
        else:
            noteoff_seq.insert(0, aux_off)
            tics_off = 0
            aux_off.clear()


# Set breakpoint note
note_crit = -1
print('Enter breakpoint note:')
while note_crit<0:
    message, delta_time = midi_in.get_message()
    if message[0] == 144:
        note_crit = message.note
    print("Breakpoint note = "+str(note_crit)+"\n")

# Handle messages
fs.noteon(0, 60, 60)
len_off_seq = len(noteoff_seq)
len_on_seq = len(noteon_seq)
while True:
    message, delta_time = midi_in.get_message()

    if message:
        if message[0] == 144 and len(message) >= 3:     # noteon & noteoff
            if message[1] >= note_crit:

                if delta_time < threshold:  # message is simultaneous note
                    continue

                print(message)   # debug

                # message is not simultaneous note
                if message[2] == 0: # noteoff
                    if len_off_seq > 0:
                        for note in noteoff_seq.pop():
                            fs.noteoff(0, note)
                        len_off_seq = len_off_seq - 1
                else: # noteon
                    if len_on_seq > 0:
                        for note in noteon_seq.pop():
                            fs.noteon(0, note, message[2])  # TODO: check multiple note velocity
                        len_on_seq = len_on_seq - 1

        elif message[0] == 176:                         # sustain
            fs.cc(0, message[1], message[2])
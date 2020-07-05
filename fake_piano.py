import rtmidi_python as rtmidi
import fluidsynth
import mido
import time
import track_player
import threading

MIDI_PATH = 'midi_files/fur_padre/fur_elise.mid'
SF2_PATH = 'soundfonts/FluidR3_GM.SF2'

# Open piano midi input port
midi_in = rtmidi.MidiIn(b'in')
i = 0
for port_name in midi_in.ports:
    if b'Piano' in port_name:
        midi_in.open_port(i)
        break
    i += 1
else:
    print("Unable to detect Piano")
    exit()

# Initialize synth
fs = fluidsynth.Synth()
fs.start('alsa')
sfid = fs.sfload(SF2_PATH)
fs.program_select(0, sfid, 0, 0)    # channel = 0

# Extract right and left hand tracks from midi
midi = mido.MidiFile(MIDI_PATH)
rhand_track = None
lhand_track = None
for track in midi.tracks:
    if 'right' in track.name:
        rhand_track = track
    if 'left' in track.name:
        lhand_track = track
if not rhand_track:
    rhand_track = midi
if not lhand_track:
    lhand_track = midi

# Generate sequences from note_on and note_off messages. Every element
# of each sequence will be a block of notes (to allow chords).
threshold = 1           # minimum time (tics) between blocks of notes
tics_on = 0             # tics from last note_on
tics_off = 0            # tics from last note_off
aux_on = []             # current block of note_on messages
aux_off = []            # current block of note_off messages
noteon_seq = []         # final note_on sequence
noteoff_seq = []        # final note_off sequence

for msg in rhand_track:     # Create sequences from right hand track
    
    if msg.type == 'note_on':
        tics_on += msg.time
        tics_off += msg.time
        if tics_on < threshold:             # Add note to current block
            aux_on.append(msg.note)
        else:                               # Add note to new block
            if aux_on:
                noteon_seq.insert(0, aux_on.copy())
            tics_on = 0
            aux_on.clear()
            aux_on.append(msg.note)

    elif msg.type == 'note_off':
        tics_on += msg.time
        tics_off += msg.time
        if tics_off < threshold:            # Add note to current block
            aux_off.append(msg.note)
            tics_off = tics_off + msg.time
        else:                               # Add note to new block
            if aux_off:
                noteoff_seq.insert(0, aux_off.copy())
            tics_off = 0
            aux_off.clear()
            aux_off.append(msg.note)

# Set breakpoint note. Every note lower than this will be ignored.
breakpoint_note = -1
print('Enter breakpoint note:')
start_time = time.perf_counter()
while breakpoint_note<=0:
    # Check time limit
    if time.perf_counter() - start_time >= 5:
        break
    # Read note
    message, delta_time = midi_in.get_message()
    if message:
        if message[0] == 144:
            breakpoint_note = message[1]
            print("Breakpoint note = "+str(breakpoint_note)+"\n")

# Play left hand in background
t = track_player.main
a = [fs, lhand_track]
lhand_thread = threading.Thread(target=t, args=a)
#lhand_thread.start()

# Handle messages
threshold = 0.005        # Minimum time (seconds) between inputs
time = 0.0              # Elapsed time between inputs

while True:
    #Receive message
    message, delta_time = midi_in.get_message()

    # Update time
    if delta_time is None:
        delta_time = 0
    time += delta_time

    # Process message
    if message:
        if len(message) >= 3 and message[0] == 144:     # noteon or noteoff
            
            # Debug
            print(message, delta_time)
            
            # Invalid input
            if message[1] < breakpoint_note or time < threshold:
                continue
            
            # Valid input
            time = 0
            if message[2] == 0:     # noteoff
                try:
                    for note in noteoff_seq.pop():
                        fs.noteoff(0, note)
                except: break
            else:                   # noteon
                try:
                    for note in noteon_seq.pop():
                        # TODO: check block notes velocity
                        fs.noteon(0, note, message[2])
                except: pass

        elif message[0] == 176:                         # sustain
            fs.cc(0, message[1], message[2])

print('\nImpressive!')
if lhand_thread:
    lhand_thread._stop()
    lhand_thread._delete()
import rtmidi_python as rtmidi
import time

midi_out = rtmidi.MidiOut(b'out')
i = 0
for port_name in midi_out.ports:
    if b'Piano' in port_name:
        midi_out.open_port(i)
        break
    i += 1
else:
    print("Unable to detect piano")
    exit()


volume_up = [0xb0, 7, 127]
note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
note_off = [0x80, 60, 0]
midi_out.send_message(volume_up)
midi_out.send_message(note_on)
time.sleep(0.5)
midi_out.send_message(note_off)
time.sleep(0.1)

print(note_on)
time.sleep(2)
while True:
    volume_up = [7, 0, 127]
    midi_out.send_message(volume_up)

del midi_out
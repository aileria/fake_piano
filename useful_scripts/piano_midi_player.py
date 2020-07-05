import mido
import time
import fluidsynth

file_path = 'midi_files/fur_padre/guardian_faro.mid'
port_name = 'Digital Piano:Digital Piano MIDI 1 24:0'

# Reproducir MIDI
outport = mido.open_output(port_name)
mid = mido.MidiFile(file_path)
for msg in mid.play():
    outport.send(msg)
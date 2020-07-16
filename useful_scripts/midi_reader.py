import mido

midi_path = 'midi_files/fly.mid'
output_file = 'notas_fly.txt'

mid = mido.MidiFile(midi_path)
with open(output_file, "w") as f:
    for msg in mid:
        if msg.type == 'note_on':
            f.write(str(msg.note)+"\n")
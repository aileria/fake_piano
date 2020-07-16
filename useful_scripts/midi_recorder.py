import mido
from mido.ports import MultiPort

file_path = 'notas_prueba.txt'
port_name = 'Digital Piano:Digital Piano MIDI 1 24:0'

with mido.open_input(port_name) as inport:
    for msg in inport:
        with open(file_path, "w") as f:
            if msg.type == 'note_on':
                f.write(str(msg.note)+"\n")
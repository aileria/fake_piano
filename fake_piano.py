import mido
from fake_player import fake_player

midi_path = 'midi_files/fantaisie.mid'
sf2_path = '/home/aitor/Proyectos/fake_piano/soundfonts/FluidR3_GM.sf2'
port_name = 'Digital Piano:Digital Piano MIDI 1 24:0'

# Bucle principal
with mido.open_input(port_name) as inport, fake_player(midi_path, sf2_path) as player:
    for msg in inport:
        if not player.send(msg): exit()
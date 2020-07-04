import mido, fluidsynth

# Inicializar sintetizador
fs = fluidsynth.Synth()
fs.start(driver='alsa') # linux
#fs.start(driver='dsound') # windows

sfid = fs.sfload("/home/aitor/Proyectos/fake_piano/soundfonts/FluidR3_GM.SF2")
fs.program_select(0, sfid, 0, 0)

# Reproducir MIDI
mid = mido.MidiFile('midi_files/fantaisie.mid')
for msg in mid.play():
    if msg.type == 'note_on':
        fs.noteon(msg.channel, msg.note, msg.velocity)
    elif msg.type == 'note_off':
        fs.noteoff(msg.channel, msg.note)
    elif msg.type == 'control_change':
        fs.cc(msg.channel, msg.control, msg.value)

fs.delete()
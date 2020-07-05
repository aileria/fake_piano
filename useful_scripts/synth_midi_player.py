import mido, fluidsynth

def main(midi, driver='alsa'):
    """Plays midi file in the computer. Driver 'alsa' for linux, 'dsound' for windows"""

    # Inicializar sintetizador
    fs = fluidsynth.Synth()
    fs.start(driver) # linux
    #fs.start(driver='dsound') # windows

    sfid = fs.sfload("soundfonts/FluidR3_GM.SF2")
    fs.program_select(0, sfid, 0, 0)

    # Reproducir MIDI
    for msg in midi.play():
        if msg.type == 'note_on':
            fs.noteon(msg.channel, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            fs.noteoff(msg.channel, msg.note)
        elif msg.type == 'control_change':
            fs.cc(msg.channel, msg.control, msg.value)

    fs.delete()
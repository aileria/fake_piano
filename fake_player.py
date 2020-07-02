import fluidsynth, mido

class fake_player:
    def __init__(self, midi_path, sf2_path, driver='alsa'):
        #Inicializar sintetizador
        self.fs = fluidsynth.Synth()
        self.fs.start(driver)

        #Cargar notas del MIDI en una lista
        midi = mido.MidiFile(midi_path)
        self.stack = []
        for msg in midi:
            if msg.type == 'note_on':
                self.stack.append(msg.note)

        #Cargar instrumento
        sfid = self.fs.sfload(sf2_path)
        self.fs.program_select(0, sfid, 0, 0)
        
        #Declarar lista de notas pendientes por finalizar
        self.pending_off = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fs.delete()
        
    def send(self, msg):
        #Comprobar si quedan notas por tocar
        if not self.stack: return False

        #Enviar mensaje al sintetizador
        if msg.type == 'note_on':
            next_note = self.stack.pop(0)
            self.pending_off.append(next_note)
            self.fs.noteon(msg.channel, next_note, msg.velocity)
        elif msg.type == 'note_off':
            self.fs.noteoff(msg.channel, self.pending_off.pop(0))
        elif msg.type == 'control_change':
            self.fs.cc(msg.channel, msg.control, msg.value)
        return True
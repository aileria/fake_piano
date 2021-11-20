import fake_piano

class FakePianoConsole():
    def __init__(self):
        self.options = {
            1 : 'Play midi file',
            2 : 'Exit'
        }
        self.functions = {
            1: self.fake_play,
            2: exit
        }

    def showMenu(self):
        for option, desc in self.options.items():
            print(str(option)+'.', desc)

    def run(self):
        while True:
            self.showMenu()
            print('Option:', end=' ')
            selected = int(input())
            if(0 < selected <= len(self.options)):
                self.functions[selected]()
                break
        while True:
            pass

    def fake_play(self):
        player = fake_piano.FixedSpeedPlayer(playback_speed=1)
        reader = fake_piano.Reader(read_threshold=0.02)
        print('Midi file name:', end=' ')
        reader.load_midi('midi/'+input()+'.mid')
        print('----- Midi tracks -----')
        print(*reader.available_midi_tracks(), sep='\n')
        print('-----------------------')
        print('Midi melody track:', end=' ')
        reader.load_melody(input())
        print('Midi accomp track:', end=' ')
        reader.load_accomp(input())
        player.set_playable(reader.create_playable())
        player.set_input(fake_piano.input_tools.KeyboardInput())
        player.set_output(fake_piano.output_tools.MidiPortOutput())
        player.start()
        print('\n+ Playing... Press CTRL+C to stop')

if __name__=='__main__':
    try:
        FakePianoConsole().run()
    except KeyboardInterrupt:
        print('\nInterrupted')
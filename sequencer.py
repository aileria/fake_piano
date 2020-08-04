import time
from threading import Thread

class Sequencer():

    VELOCTIY = 60

    def __init__(self, output):
        self.output = output
        self.thread = None

    def add(self, accompaniment_block, playback_speed):
        self.stop()
        self.thread = Thread(target=self.play, args=[accompaniment_block, playback_speed])
        self.thread.start()

    def play(self, accompaniment_block, playback_speed):
        for note in accompaniment_block:
            time.sleep(note.start_time / playback_speed)
            self.output.note_on(note.value, Sequencer.VELOCTIY)
            #self.output.noteon(0, note.value, Sequencer.VELOCTIY) # fsout testing

    def stop(self):
        pass
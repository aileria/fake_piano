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
        last_note_start = 0
        for note in accompaniment_block:
            time.sleep((note.start_time - last_note_start) / playback_speed)
            last_note_start = note.start_time
            self.output.note_on(note.value, note.velocity)

    def stop(self):
        pass
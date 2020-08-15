import asyncio
import time
from threading import Thread

class SyncSequencer():

    VELOCTIY = 60

    def __init__(self, output):
        self.output = output
        self.thread = None

    def add(self, notes, playback_speed):
        self.stop()
        self.thread = Thread(target=self.play, args=[notes, playback_speed])
        self.thread.start()

    def play(self, notes, playback_speed):
        last_note_start = 0
        for note in notes:
            time.sleep((note.start_time - last_note_start) / playback_speed)
            last_note_start = note.start_time
            self.output.note_on(note.value, Sequencer.VELOCTIY)

    def stop(self):
        pass

class Sequencer():

    VELOCTIY = 60

    def __init__(self, output):
        self.output = output
        self.thread = None
        self.tasks = None

    def add(self, notes, playback_speed):
        self.stop()
        self.thread = Thread(target=self.play, args=[notes, playback_speed])
        self.thread.start()

    def play(self, notes, playback_speed):
        self.playback_speed = playback_speed
        self.last_note_start = 0
        try:
            asyncio.run(self.process(notes))
        except asyncio.exceptions.CancelledError:
            pass

    async def process(self, notes):
        self.stop()
        self.tasks = asyncio.gather(*[self.play_note(n) for n in notes])
        await self.tasks

    async def play_note(self, note):
        await asyncio.sleep((note.start_time - self.last_note_start) / self.playback_speed)
        self.last_note_start = note.start_time
        self.output.note_on(note.value, Sequencer.VELOCTIY)
        await asyncio.sleep(note.duration)
        self.output.note_off(note.value)

    def stop(self):
        if self.tasks:
            self.tasks.cancel()
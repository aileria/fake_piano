class Note():
    def __init__(self, value, start_time, velocity=0):
        self.value = value
        self.duration = 0
        self.velocity = velocity
        self.start_time = start_time

    def set_duration(self, end_time):
        self.duration = end_time - self.start_time

    def set_velocity(self, velocity):
        self.velocity = velocity

class Playable():
    """Contains the necessary information for a Player object to play its content"""

    def __init__(self, notes_on, accompaniment_blocks):
        """`notes_on`: list of block of notes to be played each input iteration\n
        `accompaniment_blocks`: list (same size than notes_on) of AccompanimentNote lists to be played after each note_on"""

        self.notes_on = notes_on
        self.accompaniment = accompaniment_blocks
        self.reset()
    
    def initial_accomp(self) -> list:
        """Returns the list of Note objects to play before the first melody note"""
        
        return self.accompaniment[0]

    def next(self) -> (list, list):
        """Returns the current block of notes in the queue and points to the next one"""

        self.position += 1
        return self.notes_on[self.position-1], self.accompaniment[self.position]
    
    def back(self) -> (list, list):
        """Returns the previous block of notes in the queue"""

        self.position -= 1
        return self.notes_on[self.position+1], self.accompaniment[self.position]

    def peek(self, position=0) -> (list, list):
        """Returns a block of notes at `position` distance from the current one, 
        without changing the internal pointer"""

        return self.notes_on[self.position+position], self.accompaniment[self.position+position+1]

    def reset(self):
        self.position = 0
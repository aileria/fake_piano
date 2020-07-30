class Playable():
    """Contains the necessary information for a Player object to play its content"""

    def __init__(self, notes_on):
        self.notes_on = notes_on
        self.reset()
    
    def next(self) -> list:
        """Returns the current block of notes in the queue and points to the next one"""

        self.position += 1
        return self.notes_on[self.position-1]
    
    def back(self) -> list:
        """Returns the previous block of notes in the queue"""

        self.position -= 1
        return self.notes_on[self.position+1]

    def peek(self, position=0) -> list:
        """Returns a block of notes at `position` distance from the current one, 
        without changing the internal pointer"""

        return self.notes_on[self.position+position]

    def reset(self):
        self.position = 0
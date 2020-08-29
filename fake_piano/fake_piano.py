from .player import Player
from .reader import Reader
from .input_tools import Input
from .output_tools import Output

class FakePiano():

    def __init__(self):
        self.player = Player()
        self.reader = Reader()
        self.input = Input()
        self.output = Output()

    def get_available_inputs(self) -> list: ...
    def get_available_outputs(self) -> list: ...
    def set_input(self, input: Input) -> None: ...
    def set_output(self, output: Output) -> None: ...
    
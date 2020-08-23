import tkinter as tk
from tkinter import ttk

class FakePiano(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('FakePiano')
        self.geometry('500x300')
        #self.resizable(False, False)

        # Tabs
        tab_control = ttk.Notebook(self)
        playback_tab = ttk.Frame(tab_control)
        midi_tab = ttk.Frame(tab_control)
        io_tab = ttk.Frame(tab_control)
        tab_control.add(playback_tab, text='Playback')
        tab_control.add(midi_tab, text='Midi')
        tab_control.add(io_tab, text='Input/Output')
        tab_control.pack(expand=True, fill="both")
        
        # Playback tab
        # Midi tab
        # IO tab

if __name__=='__main__':
    app = FakePiano()
    app.mainloop()
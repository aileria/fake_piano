import tkinter as tk
from tkinter import ttk, StringVar, filedialog
#from ttkthemes import ThemedTk
#class FakePiano(ThemedTk):

class FakePiano(tk.Tk):

    CORRECT_COLOR = 'green4'
    ERROR_COLOR = 'red'
    TTK_THEME = 'vista'
    WINDOW_TITLE = 'FakePiano'
    DEFAULT_SIZE = '500x300'

    def __init__(self):
        super().__init__()
        self.title(self.WINDOW_TITLE)
        self.geometry(self.DEFAULT_SIZE)
        #self.resizable(False, False)

        # Attributes
        self.midi_file = None
        self.input_threshold = 0
        self.read_threshold = 0

        # Style
        style = ttk.Style()
        style.theme_use(self.TTK_THEME)
        style.layout("Tab",
            [('Notebook.tab', {'sticky': 'nswe', 'children':
                [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
                        [('Notebook.label', {'side': 'top', 'sticky': ''})],
                })],
            })]
        )

        # Tabs
        tab_control = ttk.Notebook(self)
        playback_tab = ttk.Frame(tab_control)
        midi_tab = ttk.Frame(tab_control)
        io_tab = ttk.Frame(tab_control)
        tab_control.add(playback_tab, text='{:^25}'.format('Playback'))
        tab_control.add(midi_tab, text='{:^25}'.format('Midi'))
        tab_control.add(io_tab, text='{:^25}'.format('Input/Output'))
        tab_control.pack(expand=True, fill="both")
        
        self.init_playback_tab(playback_tab)
        self.init_midi_tab(midi_tab)
        self.init_io_tab(io_tab)
    
    def init_playback_tab(self, tab):
        # Create components
        #   Buttons
        start_btn = ttk.Button(tab, text='Start', command=self.start)
        stop_btn = ttk.Button(tab, text='Stop', command=self.stop)
        undo_btn = ttk.Button(tab, text='Undo', command=self.undo)
        
        #   Input threshold
        threshold_lbl = ttk.Label(tab, text='Input threshold (ms)')
        input_threshold = StringVar()
        input_threshold.set(0)
        input_threshold_entry = tk.Entry(tab, textvariable=input_threshold)
        input_threshold.trace('w', lambda name, index, mode, string_var=input_threshold: 
            self.change_threshold(self.input_threshold, string_var.get(), input_threshold_entry))

        # Place components in the frame
        start_btn.grid(row=0, column=0)
        stop_btn.grid(row=0, column=1)
        undo_btn.grid(row=0, column=2)
        threshold_lbl.grid(row=1, column=0)
        input_threshold_entry.grid(row=1, column=1)

    def init_midi_tab(self, tab):
        # Create components
        #   Labels
        lbl1 = ttk.Label(tab, text='MIDI file', anchor="w")
        lbl2 = ttk.Label(tab, text='Melody track', anchor="w")
        lbl3 = ttk.Label(tab, text='Accomp. track', anchor="w")
        lbl4 = ttk.Label(tab, text='Read threshold (ms)', anchor="w")

        #   Midi file
        self.midi_file = StringVar()
        midi_entry = tk.Entry(tab, textvariable=self.midi_file)

        #   Read threshold
        read_threshold = StringVar()
        read_threshold.set(0)
        read_threshold_entry = tk.Entry(tab, textvariable=read_threshold)
        read_threshold.trace('w', lambda name, index, mode, string_var=read_threshold: 
            self.change_threshold(self.read_threshold, string_var.get(), read_threshold_entry))
            
        #   Tracks
        midi_tracks = ['left_hand', 'right_hand']
        melody_track_combo = ttk.Combobox(tab, values=midi_tracks)
        accomp_track_combo = ttk.Combobox(tab, values=midi_tracks)

        #   Buttons
        browse_btn = ttk.Button(tab, text='Browse', command=self.browse_file)
        load_btn = ttk.Button(tab, text='Load', command=self.load_midi)

        # Place components in the frame
        lbl1.grid(row=0, column=0, padx=(10,5), pady=(5,5), sticky=tk.W)
        lbl2.grid(row=1, column=0, padx=(10,5), pady=(5,5), sticky=tk.W)
        lbl3.grid(row=2, column=0, padx=(10,5), pady=(5,5), sticky=tk.W)
        lbl4.grid(row=3, column=0, padx=(10,5), pady=(5,5), sticky=tk.W)

        midi_entry.grid(row=0, column=1, sticky="ew")
        read_threshold_entry.grid(row=3, column=1, sticky="ew")
        melody_track_combo.grid(row=1, column=1, sticky="ew")
        accomp_track_combo.grid(row=2, column=1, sticky="ew")

        browse_btn.grid(row=0, column=2, padx=(10,10), pady=(5,5))
        load_btn.grid(row=3, column=2, padx=(10,10), pady=(5,5))

        tab.columnconfigure(0, weight=0)
        tab.columnconfigure(1, weight=1)

    def init_io_tab(self, tab):
        # Create components
        input_lbl = ttk.Label(tab, text='Input')
        output_lbl = ttk.Label(tab, text='Output')
        self.input_listbox = tk.Listbox(tab, exportselection=False)
        self.output_listbox = tk.Listbox(tab, exportselection=False)
        self.input_listbox.config(activestyle='none')
        self.output_listbox.config(activestyle='none')
        self.input_listbox.insert(0, 'Input1', 'Input2')
        self.output_listbox.insert(0, 'Output1', 'Output2', 'Output3')

        # Place components in the frame
        input_lbl.grid(row=0, column=0)
        output_lbl.grid(row=0, column=1)
        self.input_listbox.grid(row=1, column=0, padx=(10,5), pady=(0,10), sticky="nsew")
        self.output_listbox.grid(row=1, column=1, padx=(5,10), pady=(0,10), sticky="nsew")
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=0)
        tab.rowconfigure(1, weight=1)

    def start(self): ...
    def stop(self): ...
    def undo(self): ...
    
    def load_midi(self): ...
    def change_threshold(self, old, new, entry):
        try:
            new = float(new)
            if new < 0: raise ValueError
            entry.config(
                highlightthickness=1,
                highlightbackground=self.CORRECT_COLOR, 
                highlightcolor=self.CORRECT_COLOR
            )
            old = new
        except ValueError:
            entry.config(
                highlightthickness=1, 
                highlightbackground=self.ERROR_COLOR, 
                highlightcolor=self.ERROR_COLOR
            )

    def browse_file(self):
        self.midi_file = filedialog.askopenfilename(initialdir = "/", 
                                          title = "Select a MIDI file", 
                                          filetypes = (("Midi files", 
                                                        "*.mid*"), 
                                                       ("all files", 
                                                        "*.*"))) 

if __name__=='__main__':
    app = FakePiano()
    app.mainloop()
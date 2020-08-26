import tkinter as tk
from tkinter import ttk, filedialog
from configparser import ConfigParser
import io
#from ttkthemes import ThemedTk
#class FakePiano(ThemedTk):

class FakePiano(tk.Tk):

    CORRECT_COLOR = 'green4'
    ERROR_COLOR = 'red'
    TTK_THEME = 'vista'
    WINDOW_TITLE = 'FakePiano'
    DEFAULT_SIZE = '500x300'
    CONFIG_FILE = 'config.ini'

    def __init__(self):
        super().__init__()
        self.title(self.WINDOW_TITLE)

        # On close protocol
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        # Read config file
        self.config = ConfigParser()
        self.config.read(self.CONFIG_FILE)

        # Size
        self.geometry(self.config.get('GENERAL', 'size'))

        # Attributes
        self.midi_file = tk.StringVar()
        self.melody_track = tk.StringVar()
        self.accomp_track = tk.StringVar()
        self.input_threshold = tk.StringVar()
        self.read_threshold = tk.StringVar()
        self.breakpoint_key = tk.StringVar()
        self.input = tk.StringVar()
        self.output = tk.StringVar()
        
        # Load attributes
        self.midi_file.set(self.config.get('FAKE-PIANO', 'midi_file'))
        self.melody_track.set(self.config.get('FAKE-PIANO', 'melody_track'))
        self.accomp_track.set(self.config.get('FAKE-PIANO', 'accomp_track'))
        self.input_threshold.set(self.config.get('FAKE-PIANO', 'input_threshold'))
        self.read_threshold.set(self.config.get('FAKE-PIANO', 'read_threshold'))
        self.breakpoint_key.set(self.config.get('FAKE-PIANO', 'breakpoint_key'))
        self.input.set(self.config.get('FAKE-PIANO', 'input'))
        self.output.set(self.config.get('FAKE-PIANO', 'output'))

        # Style
        style = ttk.Style()
        style.theme_use(self.config.get('GENERAL', 'theme'))
        style.layout('Tab',
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
        tab_control.pack(expand=True, fill='both')
        
        self.init_playback_tab(playback_tab)
        self.init_midi_tab(midi_tab)
        self.init_io_tab(io_tab)
    
    def init_playback_tab(self, tab):
        # Create components
        #   Buttons
        buttons_frame = ttk.Frame(tab)
        start_btn = ttk.Button(buttons_frame, text='Start', command=self.start)
        stop_btn = ttk.Button(buttons_frame, text='Stop', command=self.stop)
        undo_btn = ttk.Button(buttons_frame, text='Undo', command=self.undo)
        
        #   Input threshold
        input_threshold_lbl = ttk.Label(tab, text='Input threshold (ms)', anchor='w')
        input_threshold_entry = tk.Entry(tab, textvariable=self.input_threshold)
        self.input_threshold.trace('w', lambda name, index, mode: 
            self.change_threshold(self.input_threshold, self.input_threshold.get(), input_threshold_entry))

        #   Breakpoint key
        breakpoint_key_lbl = ttk.Label(tab, text='Breakpoint key', anchor='w')
        breakpoint_key_entry = tk.Entry(tab, textvariable=self.breakpoint_key)
        self.breakpoint_key.trace('w', lambda name, index, mode: 
            self.change_breakpoint_key(self.breakpoint_key.get(), breakpoint_key_entry))

        # Place components in the frame
        start_btn.grid(row=0, column=0)
        stop_btn.grid(row=0, column=1)
        undo_btn.grid(row=0, column=2)
        buttons_frame.grid(row=0, column=0, columnspan=3, pady=(15,10))
        input_threshold_lbl.grid(row=1, column=0, padx=(10,5), pady=(5,5), sticky='w')
        input_threshold_entry.grid(row=1, column=1, sticky='ew', padx=(0,15))
        breakpoint_key_lbl.grid(row=2, column=0, padx=(10,5), pady=(5,5), sticky='w')
        breakpoint_key_entry.grid(row=2, column=1, sticky='ew', padx=(0,15))

        tab.columnconfigure(1, weight=1)

    def init_midi_tab(self, tab):
        # Create components
        #   Labels
        lbl1 = ttk.Label(tab, text='MIDI file', anchor='w')
        lbl2 = ttk.Label(tab, text='Melody track', anchor='w')
        lbl3 = ttk.Label(tab, text='Accomp. track', anchor='w')
        lbl4 = ttk.Label(tab, text='Read threshold (ms)', anchor='w')

        #   Midi file entry
        midi_entry = tk.Entry(tab, textvariable=self.midi_file)

        #   Read threshold
        read_threshold_entry = tk.Entry(tab, textvariable=self.read_threshold)
        self.read_threshold.trace('w', lambda name, index, mode: 
            self.change_threshold(self.read_threshold, self.read_threshold.get(), read_threshold_entry))
            
        #   Tracks
        # TODO create values from available_midi_tracks from reader object
        midi_tracks = ['left_hand', 'right_hand']
        melody_track_combo = ttk.Combobox(tab, values=midi_tracks, textvariable=self.melody_track)
        accomp_track_combo = ttk.Combobox(tab, values=midi_tracks, textvariable=self.accomp_track)
        if melody_track_combo.current() == -1:
            melody_track_combo.current(0)
        if accomp_track_combo.current() == -1:
            accomp_track_combo.current(0)

        #   Buttons
        browse_btn = ttk.Button(tab, text='Browse', command=self.browse_file)
        load_btn = ttk.Button(tab, text='Load', command=self.load_midi)

        # Place components in the frame
        lbl1.grid(row=0, column=0, padx=(10,5), pady=(5,5), sticky='w')
        lbl2.grid(row=1, column=0, padx=(10,5), pady=(5,5), sticky='w')
        lbl3.grid(row=2, column=0, padx=(10,5), pady=(5,5), sticky='w')
        lbl4.grid(row=3, column=0, padx=(10,5), pady=(5,5), sticky='w')

        midi_entry.grid(row=0, column=1, sticky='ew')
        read_threshold_entry.grid(row=3, column=1, sticky='ew')
        melody_track_combo.grid(row=1, column=1, sticky='ew')
        accomp_track_combo.grid(row=2, column=1, sticky='ew')

        browse_btn.grid(row=0, column=2, padx=(10,10), pady=(5,5))
        load_btn.grid(row=3, column=2, padx=(10,10), pady=(5,5))

        tab.columnconfigure(0, weight=0)
        tab.columnconfigure(1, weight=1)

    def init_io_tab(self, tab):
        # Create components
        input_lbl = ttk.Label(tab, text='Input')
        output_lbl = ttk.Label(tab, text='Output')
        self.input_listbox = tk.Listbox(tab, exportselection=False, )
        self.output_listbox = tk.Listbox(tab, exportselection=False)
        self.input_listbox.config(activestyle='none')
        self.output_listbox.config(activestyle='none')
        self.input_listbox.insert(0, 'Input1', 'Input2')
        self.output_listbox.insert(0, 'Output1', 'Output2', 'Output3')
        # TODO set default selection
        apply_btn = ttk.Button(tab, text='Apply', command= lambda: self.set_input_output(
            self.input_listbox.get(self.input_listbox.curselection()),
            self.output_listbox.get(self.output_listbox.curselection()))
        )

        # Place components in the frame
        input_lbl.grid(row=0, column=0)
        output_lbl.grid(row=0, column=1)
        self.input_listbox.grid(row=1, column=0, padx=(10,5), pady=(0,5), sticky='nsew')
        self.output_listbox.grid(row=1, column=1, padx=(5,10), pady=(0,5), sticky='nsew')
        apply_btn.grid(row=2, column=1, padx=(0,10), pady=(0,5), sticky='se')

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=0)
        tab.rowconfigure(1, weight=1)

    # Playback functions
    def start(self): ...
    def stop(self): ...
    def undo(self): ...
    def change_breakpoint_key(self, key, entry):
        try:
            key = int(key)
            state = True
            self.breakpoint_key.set(key)
        except ValueError:
            state = False
        finally:
            self.change_entry_state(entry, state)
    
    # Midi functions
    def load_midi(self): ...
    def browse_file(self):
        self.midi_file.set(filedialog.askopenfilename(
            initialdir = '/', 
            title = 'Select a MIDI file', 
            filetypes = (('Midi files', '*.mid*'), 
                         ('all files', '*.*'))
        )) 

    # Input/Output functions
    def set_input_output(self, selected_input, selected_output): 
        self.input.set(selected_input)
        self.output.set(selected_output)

    # General functions
    def change_threshold(self, old, new, entry):
        try:
            new = float(new)
            if new < 0: raise ValueError
            state = True
            old = new
        except ValueError:
            state = False
        finally:
            self.change_entry_state(entry, state)
    
    def change_entry_state(self, entry, state: bool):
        if state:
            entry.config(
                highlightthickness=1,
                highlightbackground=self.CORRECT_COLOR, 
                highlightcolor=self.CORRECT_COLOR
            )
        else:
            entry.config(
                highlightthickness=1, 
                highlightbackground=self.ERROR_COLOR, 
                highlightcolor=self.ERROR_COLOR
            )
    
    def on_closing(self):
        self.config.set('GENERAL', 'size', self.winfo_geometry())
        self.config.set('FAKE-PIANO', 'midi_file', self.midi_file.get())
        self.config.set('FAKE-PIANO', 'melody_track', self.melody_track.get())
        self.config.set('FAKE-PIANO', 'accomp_track', self.accomp_track.get())
        self.config.set('FAKE-PIANO', 'input_threshold', self.input_threshold.get())
        self.config.set('FAKE-PIANO', 'read_threshold', self.read_threshold.get())
        self.config.set('FAKE-PIANO', 'breakpoint_key', self.breakpoint_key.get())
        self.config.set('FAKE-PIANO', 'input', self.input.get())
        self.config.set('FAKE-PIANO', 'output', self.output.get())

        with open(self.CONFIG_FILE, 'w') as f:
            self.config.write(f)
        self.destroy()

if __name__=='__main__':
    app = FakePiano()
    app.mainloop()
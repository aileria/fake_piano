import rtmidi_python as rtmidi
import fluidsynth
import mido
import time

class Player:
    def __init__(self, sf2_path, driver='alsa', channel=0, synth_gain=1, volume=127, input_threshold=0.02):
        # Synth
        self._synth = fluidsynth.Synth(gain=synth_gain)
        self._synth.start(driver)
        sfid = self._synth.sfload(sf2_path)
        self._synth.program_select(0, sfid, 0, 0)
        self._synth.cc(0, 7, volume)
        self.breakpoint_note = -1
        # Threshold
        self._threshold = input_threshold
        # Midi input port
        self.midi_in = None
        # Active keys list
        self._active_keys = []
    
    @property
    def synth(self):
        return self._synth

    @synth.setter
    def synth(self, s):
        if not s:
            raise ValueError("Invalid synth")
        self._synth = s

    @property
    def active_keys(self):
        return self._active_keys

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, t):
        self._threshold = t

    # MIDI input port
    def available_midi_in(self):
        """Returns all available midi input port names"""

        return tuple(rtmidi.MidiIn(b'in').ports)

    def set_midi_in(self, port_name):
        """It opens the available port which name matches (or contains) port_name"""

        self.midi_in = rtmidi.MidiIn(b'in')
        i = 0
        for port in self.midi_in.ports:
            if port_name in port:
                self.midi_in.open_port(i)
                break
            i += 1
        else:
            raise ValueError("Unable to find the specified port")

    # MIDI file and track
    def load_midi(self, path):
        """Loads the MIDI file of the specified path"""
        self.midi = mido.MidiFile(path)

    def available_midi_tracks(self):
        """Returns a list with the available tracks in the MIDI file"""

        return tuple([track.name for track in self.midi.tracks])

    def load_track(self, name, load_threshold=1):
        """Loads the MIDI track which name matches (or contains) the given name"""

        if not self.midi:
            raise ValueError("MIDI file not loaded")
        for track in self.midi.tracks:
            if name in track.name:
                play_track = track
                break
        else:
            raise ValueError("MIDI track not found")
        
        # Generate sequences from note_on and note_off messages. Every element
        # of each sequence will be a block of notes (to allow chords).
        threshold = load_threshold      # minimum time (tics) between blocks of notes
        tics_on = 0                     # tics from last note_on
        tics_off = 0                    # tics from last note_off
        aux_on = []                     # current block of note_on messages
        aux_off = []                    # current block of note_off messages
        noteon_seq = []                 # final note_on sequence
        noteoff_seq = []                # final note_off sequence

        for msg in play_track:     # Create sequences from right hand track

            if msg.type == 'note_on':
                tics_on += msg.time
                tics_off += msg.time
                if tics_on < threshold:             # Add note to current block
                    aux_on.append(msg.note)
                else:                               # Add note to new block
                    if aux_on:
                        noteon_seq.insert(0, aux_on.copy())
                    tics_on = 0
                    aux_on.clear()
                    aux_on.append(msg.note)

            elif msg.type == 'note_off':
                tics_on += msg.time
                tics_off += msg.time
                if tics_off < threshold:            # Add note to current block
                    aux_off.append(msg.note)
                    tics_off = tics_off + msg.time
                else:                               # Add note to new block
                    if aux_off:
                        noteoff_seq.insert(0, aux_off.copy())
                    tics_off = 0
                    aux_off.clear()
                    aux_off.append(msg.note)
        
        self.noteon_seq = noteon_seq
        self.noteoff_seq = noteoff_seq
    
    # Synth
    def change_volume(self, vol):
        self._synth.cc(0, 7, vol)

    def change_gain(self, gain):
        self._synth.gain=gain

    # Breakpoint note
    def set_breakpoint_note(self, note):
        self.breakpoint_note = note
    
    def read_breakpoint_note(self, time_limit=5):
        """Reads the breakpoint note from the connected MIDI input device"""

        breakpoint_note = -1
        print('Enter breakpoint note:')
        start_time = time.perf_counter()
        while breakpoint_note<=0:
            # Check time limit
            if time.perf_counter() - start_time >= time_limit:
                break
            # Read note
            message = self.midi_in.get_message()[0]
            if message:
                if message[0] == 144:
                    breakpoint_note = message[1]
                    print("Breakpoint note = "+str(breakpoint_note)+"\n")
        self.breakpoint_note = breakpoint_note

    # Threshold
    def set_threshold(self, threshold):
        self.threshold = threshold

    def start(self):
        """Starts reading and handling MIDI messages"""
        
        threshold = self._threshold     # Minimum time (seconds) between inputs
        time = 0.0                      # Elapsed time between inputs

        # Error checking
        if not self.noteon_seq:
            raise Exception("The selected track is empty")

        # Read and handle messages
        while True:
            #Receive message
            message, delta_time = self.midi_in.get_message()

            # Update time
            if delta_time is None:
                delta_time = 0
            time += delta_time

            # Process message
            if message:
                if len(message) >= 3 and message[0] == 144:     # noteon or noteoff

                    # Debug
                    print(message, delta_time)

                    # Invalid input
                    if message[1] < self.breakpoint_note or time < threshold:
                        continue
                    
                    # Valid input
                    time = 0
                    if message[2] == 0:     # noteoff
                        try:
                            for note in self.noteoff_seq.pop():
                                self._synth.noteoff(0, note)
                        except: break
                    else:                   # noteon
                        try:
                            self.active_keys.clear()
                            for note in self.noteon_seq.pop():
                                # TODO: check block notes velocity
                                self.active_keys.append(note)
                                self._synth.noteon(0, note, message[2])
                        except: pass

                elif message[0] == 176:     # sustain
                    self._synth.cc(0, message[1], message[2])

    def stop(self):
        pass

if __name__ == '__main__':
    ply = Player("soundfonts/FluidR3_GM.sf2", synth_gain=2)
    ply.load_midi("midi_files/a_comme_amour.mid")
    ply.load_track("right_hand", load_threshold=1)
    ply.set_threshold(0.002)
    while True:
        try:
            ply.set_midi_in(b'Piano')
            print("Connected")
            break
        except:
            pass
    ply.start()
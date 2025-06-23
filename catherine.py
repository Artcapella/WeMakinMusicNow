import pretty_midi
from mido import MidiFile, MidiTrack

class MidiEditor:
    def __init__(self, input_path):
        self.pm = pretty_midi.PrettyMIDI(input_path)
    
    def change_range_to_instrument(self, low_pitch, high_pitch, new_program):
        """Move all notes in pitch range [low, high] to a new instrument."""
        new_inst = pretty_midi.Instrument(program=new_program)
        for inst in self.pm.instruments:
            to_move = [n for n in inst.notes if low_pitch <= n.pitch <= high_pitch]
            for n in to_move: new_inst.notes.append(n)
            inst.notes = [n for n in inst.notes if not (low_pitch <= n.pitch <= high_pitch)]
        self.pm.instruments.append(new_inst)
    
    def swap_instrument(self, from_program, to_program):
        """Swap all instruments with program X to program Y."""
        for inst in self.pm.instruments:
            if inst.program == from_program and not inst.is_drum:
                inst.program = to_program

    def remove_notes_above(self, program, pitch_cutoff):
        """Remove notes above a pitch cutoff for a given instrument program."""
        for inst in self.pm.instruments:
            if inst.program == program and not inst.is_drum:
                inst.notes = [n for n in inst.notes if n.pitch <= pitch_cutoff]

    def save_pretty_midi(self, output_path):
        self.pm.write(output_path)

    def clean_control_changes(self, input_path, output_path, control=64):
        """Using Mido, remove given CC from the saved MIDI."""
        mid = MidiFile(input_path)
        out = MidiFile(ticks_per_beat=mid.ticks_per_beat)
        for track in mid.tracks:
            new = MidiTrack()
            for msg in track:
                if not (msg.type == 'control_change' and msg.control == control):
                    new.append(msg)
            out.tracks.append(new)
        out.save(output_path)

    def remove_notes_outside_pitch_and_instruments(self, valid_programs, min_pitch, max_pitch):
        """Keep only notes within pitch range and valid instruments."""
        for inst in self.pm.instruments:
            if inst.program not in valid_programs or inst.is_drum:
                inst.notes = []  # remove all notes if not valid instrument
            else:
                inst.notes = [n for n in inst.notes if min_pitch < n.pitch < max_pitch]
    
    def remove_notes_outside_pitch(self, min_pitch, max_pitch):
        """Remove notes outside the specified pitch range."""
        for inst in self.pm.instruments:
            inst.notes = [n for n in inst.notes if min_pitch <= n.pitch <= max_pitch]
    
    def remove_instrument(self, program):
        """Remove all notes from a specific instrument program."""
        self.pm.instruments = [inst for inst in self.pm.instruments if inst.program != program]

    def remove_outside_instrument(self, valid_programs):
        """Remove all instruments not in the valid programs list."""
        self.pm.instruments = [inst for inst in self.pm.instruments if inst.program in valid_programs]


if __name__ == "__main__":
    editor = MidiEditor('ShutDownDefault.mid')

    # 1. Range → new instrument (Acoustic Guitar program=24)
    #editor.change_range_to_instrument(60, 72, new_program=24)

    # 2. Swap program 0 → 40 (Violin)
    #editor.swap_instrument(0, 40)

    # 3. Remove notes from program 40 with pitch >80
    #editor.remove_notes_above(40, 80)

    # 4. Remove all notes that are:
    #    - F#6 (90) or higher
    #    - E4 (64) or lower
    #    - Not from Violin (40) or Cello (42)
    #editor.remove_notes_outside_pitch_and_instruments(valid_programs=[40, 42], min_pitch=64, max_pitch=90)

    #editor.remove_outside_instrument(valid_programs=[40, 42])  # Keep only Violin and Cello

    # remove non 909 drum notes
    editor.remove_outside_instrument(valid_programs=[0, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35])


    # Save before Mido edits
    editor.save_pretty_midi('staged.mid')

    # 4. Clean CC64 and save final
    editor.clean_control_changes('staged.mid', 'ShutDownDrums.mid', control=64)

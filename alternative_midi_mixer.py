# alternative_midi_mixer.py - Version without FluidSynth dependency

import mido
import tempfile
import os
import random
import numpy as np

class AlternativeMidiMixer:
    def __init__(self):
        """Initialize without FluidSynth dependency."""
        pass

    def humanize_midi(self, midi_in: str, midi_out: str,
                      timing_jitter_ms: float = 10,
                      velocity_jitter: int = 8,
                      swing: float = 0.1):
        """
        Add timing & velocity humanization and swing to a MIDI file.
        """
        mid = mido.MidiFile(midi_in)
        ticks_per_beat = mid.ticks_per_beat
        
        for track_idx, track in enumerate(mid.tracks):
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                if msg.type in ('note_on', 'note_off'):
                    # Calculate jitter
                    tempo_factor = 120  # Assume 120 BPM as default
                    jitter_ticks = int(timing_jitter_ms * ticks_per_beat / (60000 / tempo_factor))
                    
                    # Apply timing jitter
                    jitter = random.randint(-jitter_ticks, jitter_ticks)
                    msg.time = max(0, msg.time + jitter)  # Ensure time doesn't go negative
                    
                    # Apply velocity jitter for note_on messages
                    if msg.type == 'note_on' and hasattr(msg, 'velocity'):
                        velocity_change = random.randint(-velocity_jitter, velocity_jitter)
                        msg.velocity = max(1, min(127, msg.velocity + velocity_change))
                    
                    # Apply swing: delay every other 8th note
                    if swing > 0 and ticks_per_beat > 0:
                        eighth_note = ticks_per_beat // 2
                        if eighth_note > 0 and (abs_time // eighth_note) % 2:
                            msg.time += int(swing * ticks_per_beat)
        
        mid.save(midi_out)

    def process_midi(self, midi_in: str, midi_out: str,
                     timing_jitter_ms=10, velocity_jitter=8, swing=0.1):
        """
        Process MIDI file with humanization effects.
        This version only processes MIDI and doesn't convert to audio.
        """
        print(f"Processing MIDI file: {midi_in}")
        self.humanize_midi(midi_in, midi_out, timing_jitter_ms, velocity_jitter, swing)
        print(f"Humanized MIDI saved to: {midi_out}")
        print("Note: To convert to audio, you'll need to:")
        print("1. Install FluidSynth and a SoundFont, or")
        print("2. Use a DAW like Reaper, FL Studio, or Logic Pro")
        print("3. Or use online MIDI to WAV converters")

if __name__ == "__main__":
    mixer = AlternativeMidiMixer()
    midi_input = "CatherineStringCello.mid"
    midi_output = "CatherineStringCello_humanized.mid"
    
    # Check if MIDI file exists
    if not os.path.exists(midi_input):
        print(f"ERROR: MIDI file not found: {midi_input}")
        print("Please make sure the MIDI file exists in the current directory.")
        exit(1)
    
    mixer.process_midi(
        midi_in=midi_input,
        midi_out=midi_output,
        timing_jitter_ms=12,
        velocity_jitter=10,
        swing=0.08
    )
    print(f"Done: humanized MIDI exported to {midi_output}")

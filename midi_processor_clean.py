# midi_processor.py - MIDI-only version (no audio dependencies)

import mido
import tempfile
import os
import random

class MidiProcessor:
    """MIDI-only processor that focuses on humanization and MIDI effects."""
    
    def __init__(self):
        """Initialize without FluidSynth or audio dependencies."""
        print("MIDI Processor initialized (audio-free mode)")
    
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
    
    def apply_midi_effects(self, midi_in: str, midi_out: str,
                          transpose: int = 0,
                          velocity_scale: float = 1.0,
                          time_stretch: float = 1.0):
        """
        Apply various MIDI effects like transpose, velocity scaling, time stretching.
        """
        mid = mido.MidiFile(midi_in)
        
        for track in mid.tracks:
            for msg in track:
                # Apply time stretching
                if hasattr(msg, 'time'):
                    msg.time = int(msg.time * time_stretch)
                
                # Apply transpose and velocity scaling to note messages
                if msg.type in ('note_on', 'note_off'):
                    # Transpose
                    if hasattr(msg, 'note'):
                        new_note = msg.note + transpose
                        msg.note = max(0, min(127, new_note))
                    
                    # Velocity scaling
                    if msg.type == 'note_on' and hasattr(msg, 'velocity'):
                        new_velocity = int(msg.velocity * velocity_scale)
                        msg.velocity = max(1, min(127, new_velocity))
        
        mid.save(midi_out)
    
    def combine_midi_files(self, midi_files: list, output_file: str, 
                          channel_assignments: list = None):
        """
        Combine multiple MIDI files into one, optionally assigning different channels.
        """
        if not midi_files:
            print("No MIDI files provided")
            return False
        
        # Create new MIDI file
        combined = mido.MidiFile()
        
        # Process each input file
        for i, midi_file in enumerate(midi_files):
            if not os.path.exists(midi_file):
                print(f"Warning: {midi_file} not found, skipping...")
                continue
            
            try:
                mid = mido.MidiFile(midi_file)
                
                # Determine channel assignment
                if channel_assignments and i < len(channel_assignments):
                    target_channel = channel_assignments[i]
                else:
                    target_channel = i % 16  # Auto-assign channels 0-15
                
                # Add tracks from this file
                for track in mid.tracks:
                    new_track = mido.MidiTrack()
                    
                    for msg in track:
                        new_msg = msg.copy()
                        
                        # Reassign channel for note and control messages
                        if hasattr(new_msg, 'channel'):
                            new_msg.channel = target_channel
                        
                        new_track.append(new_msg)
                    
                    combined.tracks.append(new_track)
                
                print(f"Added {midi_file} on channel {target_channel}")
                
            except Exception as e:
                print(f"Error processing {midi_file}: {e}")
        
        # Save combined file
        combined.save(output_file)
        print(f"Combined MIDI saved to: {output_file}")
        return True
    
    def process_midi_complete(self, midi_in: str, midi_out: str,
                             timing_jitter_ms=10, velocity_jitter=8, swing=0.1,
                             transpose=0, velocity_scale=1.0, time_stretch=1.0):
        """
        Complete MIDI processing pipeline with humanization and effects.
        """
        print(f"Processing MIDI file: {midi_in}")
        
        # Step 1: Apply humanization
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as temp_midi:
            humanized_mid = temp_midi.name
        
        self.humanize_midi(midi_in, humanized_mid, timing_jitter_ms, velocity_jitter, swing)
        print("✓ Applied humanization effects")
        
        # Step 2: Apply additional MIDI effects
        self.apply_midi_effects(humanized_mid, midi_out, transpose, velocity_scale, time_stretch)
        print("✓ Applied MIDI effects")
        
        # Clean up temporary file
        if os.path.exists(humanized_mid):
            os.unlink(humanized_mid)
        
        print(f"✓ Complete! Processed MIDI saved to: {midi_out}")
        print("\nTo convert to audio:")
        print("1. Use a DAW like Reaper, FL Studio, or Logic Pro")
        print("2. Use online MIDI to WAV converters")
        print("3. Install FluidSynth + SoundFont for audio conversion")


def main():
    """Example usage of the MIDI processor."""
    processor = MidiProcessor()
    
    # Check for available MIDI files
    midi_files = [f for f in os.listdir('.') if f.endswith('.mid') or f.endswith('.midi')]
    
    if not midi_files:
        print("No MIDI files found in current directory.")
        return
    
    print(f"Found {len(midi_files)} MIDI file(s):")
    for i, file in enumerate(midi_files, 1):
        print(f"{i}. {file}")
    
    # Process first MIDI file as example
    input_file = midi_files[0]
    output_file = f"{os.path.splitext(input_file)[0]}_processed.mid"
    
    print(f"\nProcessing: {input_file}")
    
    processor.process_midi_complete(
        midi_in=input_file,
        midi_out=output_file,
        timing_jitter_ms=12,
        velocity_jitter=10,
        swing=0.08,
        transpose=0,          # No transpose
        velocity_scale=1.1,   # Slight velocity boost
        time_stretch=1.0      # No time change
    )


if __name__ == "__main__":
    main()

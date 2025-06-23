# plays MIDI files at specified BPM with actual audio output
import pretty_midi
from mido import MidiFile, MidiTrack
import time
import threading
import os
import pygame
import sys

class MIDIPlayer:
    def __init__(self):
        self.midi_data = None
        self.original_bpm = 120
        self.current_bpm = 120
        self.is_playing = False
        self.is_paused = False
        self.play_thread = None
        self.start_time = 0
        self.pause_time = 0
        self.current_position = 0
        self.current_file_path = None
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            self.audio_enabled = True
            print("Audio system initialized successfully.")
        except pygame.error as e:
            print(f"Warning: Could not initialize audio system: {e}")
            print("Will run in silent mode (console output only).")
            self.audio_enabled = False
        
    def load_midi_file(self, file_path):
        """Load a MIDI file and extract tempo information."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"MIDI file not found: {file_path}")
            
            # Store the file path for pygame playback
            self.current_file_path = file_path
            
            # Load with pretty_midi for better tempo handling
            self.midi_data = pretty_midi.PrettyMIDI(file_path)
            
            # Get original tempo (BPM)
            tempo_changes = self.midi_data.get_tempo_changes()
            if len(tempo_changes[1]) > 0:
                self.original_bpm = tempo_changes[1][0]
            else:
                self.original_bpm = 120  # Default BPM
            
            self.current_bpm = self.original_bpm
            print(f"Loaded MIDI file: {file_path}")
            print(f"Original BPM: {self.original_bpm}")
            print(f"Duration: {self.midi_data.get_end_time():.2f} seconds")
            return True
            
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            return False
    
    def set_bpm(self, bpm):
        """Set the playback BPM."""
        if bpm <= 0:
            raise ValueError("BPM must be positive")
        self.current_bpm = bpm
        print(f"BPM set to: {bpm}")
    
    def get_tempo_ratio(self):
        """Calculate the tempo ratio between original and current BPM."""
        return self.original_bpm / self.current_bpm
    
    def play_with_pygame(self, midi_file_path):
        """Play MIDI file using pygame (simpler approach)."""
        if not self.audio_enabled:
            print("Audio not available, playing in silent mode.")
            return
            
        try:
            # Load and play the MIDI file directly with pygame
            pygame.mixer.music.load(midi_file_path)
            pygame.mixer.music.play()
            print(f"♪ Now playing: {os.path.basename(midi_file_path)}")
        except pygame.error as e:
            print(f"Error playing with pygame: {e}")
            print("Falling back to silent mode.")
    
    def stop_pygame(self):
        """Stop pygame playback."""
        if self.audio_enabled:
            try:
                pygame.mixer.music.stop()
            except:
                pass
    
    def play(self, start_time=0):
        """Start playing the MIDI file."""
        if self.midi_data is None:
            print("No MIDI file loaded. Use load_midi_file() first.")
            return False
        
        if self.is_playing:
            print("Already playing. Use stop() first.")
            return False
        
        self.is_playing = True
        self.is_paused = False
        self.current_position = start_time
        self.start_time = time.time() - start_time
        
        # If we have the original file path, try pygame playback
        if hasattr(self, 'current_file_path') and self.current_file_path and self.audio_enabled:
            self.play_with_pygame(self.current_file_path)
        
        # Start timing thread for position tracking
        self.play_thread = threading.Thread(target=self._play_worker, daemon=True)
        self.play_thread.start()
        
        print(f"Playing MIDI at {self.current_bpm} BPM...")
        return True
    
    def _play_worker(self):
        """Worker thread for tracking playback position."""
        if self.midi_data is None:
            return
            
        tempo_ratio = self.get_tempo_ratio()
        total_duration = self.midi_data.get_end_time() * tempo_ratio
        
        while self.is_playing:
            if not self.is_paused:
                # Update current position
                current_time = time.time() - self.start_time
                self.current_position = current_time
                
                # Check if we've reached the end
                if self.current_position >= total_duration:
                    print("♪ Playback finished.")
                    self.is_playing = False
                    break
            
            time.sleep(0.1)  # Update every 100ms
    
    def pause(self):
        """Pause playback."""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            self.pause_time = time.time()
            if self.audio_enabled:
                pygame.mixer.music.pause()
            print("Playback paused.")
            return True
        return False
    
    def resume(self):
        """Resume playback."""
        if self.is_playing and self.is_paused:
            # Adjust start time to account for pause duration
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration
            self.is_paused = False
            if self.audio_enabled:
                pygame.mixer.music.unpause()
            print("Playback resumed.")
            return True
        return False
    
    def stop(self):
        """Stop playback."""
        if self.is_playing:
            self.is_playing = False
            self.is_paused = False
            self.current_position = 0
            
            # Stop pygame audio
            self.stop_pygame()
            
            if self.play_thread and self.play_thread.is_alive():
                self.play_thread.join(timeout=1)
            
            print("Playback stopped.")
            return True
        return False
    
    def get_status(self):
        """Get current playback status."""
        status = {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_position': self.current_position,
            'current_bpm': self.current_bpm,
            'original_bpm': self.original_bpm,
            'audio_enabled': self.audio_enabled
        }
        
        if self.midi_data:
            status['duration'] = self.midi_data.get_end_time() * self.get_tempo_ratio()
            status['file_loaded'] = True
            status['file_name'] = os.path.basename(self.current_file_path) if self.current_file_path else "Unknown"
        else:
            status['duration'] = 0
            status['file_loaded'] = False
            status['file_name'] = None
        
        return status
    
    def seek(self, position):
        """Seek to a specific position in seconds."""
        if self.midi_data is None:
            print("No MIDI file loaded.")
            return False
        
        max_duration = self.midi_data.get_end_time() * self.get_tempo_ratio()
        if position < 0 or position > max_duration:
            print(f"Position must be between 0 and {max_duration:.2f} seconds.")
            return False
        
        was_playing = self.is_playing
        if was_playing:
            self.stop()
        
        if was_playing:
            self.play(start_time=position)
        else:
            self.current_position = position
        
        print(f"Seeked to {position:.2f} seconds.")
        return True


def select_midi_file():
    """Allow user to select a MIDI file from available options."""
    # Look for MIDI files in the current directory
    midi_files = [f for f in os.listdir('.') if f.endswith('.mid') or f.endswith('.midi')]
    
    if not midi_files:
        print("No MIDI files found in current directory.")
        return None
    
    print("\nAvailable MIDI files:")
    for i, file in enumerate(midi_files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = input(f"\nSelect a file (1-{len(midi_files)}) or enter filename: ").strip()
            
            # Check if it's a number
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(midi_files):
                    return midi_files[index]
                else:
                    print(f"Please enter a number between 1 and {len(midi_files)}")
            
            # Check if it's a filename
            elif choice in midi_files:
                return choice
            
            # Check if it's a partial filename
            matches = [f for f in midi_files if choice.lower() in f.lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"Multiple matches found: {matches}")
                print("Please be more specific.")
            else:
                print("File not found. Please try again.")
                
        except KeyboardInterrupt:
            return None


def main():
    """Enhanced MIDI Player with file selection."""
    player = MIDIPlayer()
    
    print("🎵 Enhanced MIDI Player 🎵")
    print("=" * 30)
    
    # Let user select a MIDI file
    selected_file = select_midi_file()
    if not selected_file:
        print("No file selected. Exiting.")
        return
    
    # Load the selected MIDI file
    if player.load_midi_file(selected_file):
        print("\n🎵 Commands:")
        print("p - play/pause")
        print("s - stop")
        print("b <bpm> - set BPM (e.g., 'b 140')")
        print("t - show status")
        print("f - select different file")
        print("q - quit")
        
        while True:
            try:
                command = input("\n♪ Enter command: ").strip().lower()
                
                if command == 'q':
                    player.stop()
                    break
                elif command == 'p':
                    if player.is_playing:
                        if player.is_paused:
                            player.resume()
                        else:
                            player.pause()
                    else:
                        player.play()
                elif command == 's':
                    player.stop()
                elif command.startswith('b '):
                    try:
                        bpm = float(command.split()[1])
                        player.set_bpm(bpm)
                        if player.is_playing:
                            print("Note: BPM change will take effect on next play.")
                    except (IndexError, ValueError):
                        print("Usage: b <bpm> (e.g., b 140)")
                elif command == 't':
                    status = player.get_status()
                    print(f"\n📊 Status:")
                    print(f"File: {status['file_name']}")
                    print(f"State: {'Playing' if status['is_playing'] else 'Stopped'}")
                    if status['is_paused']:
                        print("(Paused)")
                    print(f"Position: {status['current_position']:.1f}s / {status['duration']:.1f}s")
                    print(f"BPM: {status['current_bpm']} (original: {status['original_bpm']})")
                    print(f"Audio: {'Enabled' if status['audio_enabled'] else 'Disabled'}")
                elif command == 'f':
                    player.stop()
                    new_file = select_midi_file()
                    if new_file:
                        player.load_midi_file(new_file)
                    else:
                        print("No file selected, keeping current file.")
                else:
                    print("Unknown command. Type 'q' to quit.")
                    
            except KeyboardInterrupt:
                player.stop()
                break
    
    print("\n🎵 Thanks for using MIDI Player! 🎵")


if __name__ == "__main__":
    main()

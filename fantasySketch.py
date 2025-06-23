from mido import MidiFile, MidiTrack, Message, MetaMessage
from music21 import stream, note, instrument, midi
import sys
print("python:", sys.executable)
import pygame
print("pygame:", pygame, "version:", pygame.__version__, "location:", pygame.__file__)

# Alternative MIDI playback using pygame directly
def play_midi_with_pygame(midi_file_path):
    """Play MIDI file using pygame mixer"""
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.music.load(midi_file_path)
        pygame.mixer.music.play()
        print(f"▶️ Playing {midi_file_path}...")
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        
        print("✅ Playback finished.")
        pygame.mixer.quit()
    except Exception as e:
        print(f"❌ Error playing MIDI: {e}")

# === CONFIGURATION ===
BPM = 60  # slow ambient pace
TICKS_PER_BEAT = 480  # MIDI resolution

# === FUNCTION TO CREATE A MELODY STREAM ===
def make_melody_stream(instr, notes, start_offset=0.0, duration=8.0):
    """
    instr: music21.instrument.* instance
    notes: list of pitch names, e.g. ['C5','D5','E5']
    start_offset: where in beats this melody enters
    duration: total length of this melody in beats
    """
    s = stream.Part()
    s.insert(start_offset, instr)  # set instrument at start
    beat_len = duration / len(notes)
    offset = start_offset
    for pitch in notes:
        n = note.Note(pitch)
        n.quarterLength = beat_len
        s.insert(offset, n)
        offset += beat_len
    return s

# === DEFINE MOTIFS ===
woodwind_motif = ['C5', 'D5', 'E5', 'D5']  # solo oboe/flute lead
string_motif = ['C4', 'E4', 'G4', 'E4']    # sparse quartet harmony

# === BUILD STREAMS ===
# Solo woodwind (oboe or flute)
wood_stream = make_melody_stream(instrument.Oboe(), woodwind_motif, start_offset=0.0, duration=8.0)

# Sparse strings: violin, viola, cello enter later
wood_stream = make_melody_stream(instrument.Oboe(), woodwind_motif, 0.0, 8.0)
string_stream1 = make_melody_stream(instrument.Violin(), string_motif, 4.0, 8.0)
string_stream2 = make_melody_stream(instrument.Viola(), string_motif, 4.0, 8.0)
string_stream3 = make_melody_stream(instrument.Violoncello(), string_motif, 4.0, 8.0)

# === SETUP TEMPO MARKING ===
from music21 import tempo
BPM_mark = tempo.MetronomeMark(number=BPM)

# === COMBINE INTO SCORE ===
score = stream.Score()
score.insert(0, tempo.MetronomeMark(number=BPM))
score.append(wood_stream)
score.append(string_stream1)
score.append(string_stream2)
score.append(string_stream3)

# === EXPORT TO MIDI FIRST ===
mf = midi.translate.streamToMidiFile(score)
mf.ticksPerQuarterNote = TICKS_PER_BEAT
mf.open('anime_ambient.mid', 'wb')
mf.write()
mf.close()

print("✅ Generated 'anime_ambient.mid' – ambient Frieren-inspired soundtrack.")

# === REALTIME PLAYBACK USING PYGAME ===
play_midi_with_pygame('anime_ambient.mid')
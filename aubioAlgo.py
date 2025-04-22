import sys
import aubio
from aubio import pitch
import queue
import music21
import pyaudio
import numpy as np
import threading

# PyAudio setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1, rate=44100, input=True,
                input_device_index=0, frames_per_buffer=512)

# Setup
q = queue.Queue()  
samplerate = 44100
win_s = 512 
hop_s = 512 
tolerance = 0.8
pitch_o = pitch("default", win_s, hop_s, samplerate)
pitch_o.set_tolerance(tolerance)

# Global flag for stopping the loop
stop_flag = threading.Event()

# Output file path
output_file = "detected_notes.txt"

def get_current_note():
    current_pitch = music21.pitch.Pitch()
    with open(output_file, 'w') as f:  # open file in write mode
        while not stop_flag.is_set():
            data = stream.read(hop_s, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=aubio.float_type)
            f0 = pitch_o(samples)[0]
            confidence = pitch_o.get_confidence()

            current = 'Nan'
            if f0 > 0:
                current_pitch.frequency = float(f0)
                current = current_pitch.nameWithOctave
                line = f"{f0:.2f} ---- {current} ---- {current_pitch.microtone.cents:.2f}"
                print(line)
                f.write(line + "\n")  # save to file

            q.put({'Note': current, 'Cents': current_pitch.microtone.cents, 'hz': f0})

def wait_for_enter():
    input("Press ENTER to stop...\n")
    stop_flag.set()

if __name__ == '__main__':
    thread = threading.Thread(target=get_current_note)
    thread.start()
    wait_for_enter()
    thread.join()
    stream.stop_stream()
    stream.close()
    p.terminate()
    print(f"✅ Program terminated. Output saved to '{output_file}'.")

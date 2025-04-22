import sys
import aubio
from aubio import pitch
import queue
import music21
import pyaudio
import numpy as np
import threading
import time

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

# Logging file
log_file = "note_output.txt"

def get_current_note():
    current_pitch = music21.pitch.Pitch()
    previous_time = time.time()

    with open(log_file, "w") as f:
        f.write("Time(s) | Δt(s) | Hz | Note | Cents | Amplitude\n")
        f.write("---------------------------------------------------\n")

    while not stop_flag.is_set():
        data = stream.read(hop_s, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=aubio.float_type)

        current_time = time.time()
        duration = current_time - previous_time
        previous_time = current_time

        f0 = pitch_o(samples)[0]
        confidence = pitch_o.get_confidence()
        amplitude = np.max(np.abs(samples))  # dynamics proxy

        current = 'Nan'
        cents = 0.0

        if f0 > 0:
            current_pitch.frequency = float(f0)
            current = current_pitch.nameWithOctave
            cents = current_pitch.microtone.cents

            output = f"[Time: {current_time:.2f}s | Δt: {duration:.2f}s] {f0:.2f} Hz ---- {current} ---- {cents:.2f} cents ---- amplitude: {amplitude:.2f}"
            print(output)

            # Save to file
            with open(log_file, "a") as f:
                f.write(f"{current_time:.2f} | {duration:.2f} | {f0:.2f} | {current} | {cents:.2f} | {amplitude:.2f}\n")

        q.put({'Note': current, 'Cents': cents, 'hz': f0, 'time': current_time, 'duration': duration, 'amplitude': amplitude})

def wait_for_enter():
    input("🎹 Press ENTER to stop recording...\n")
    stop_flag.set()

if __name__ == '__main__':
    thread = threading.Thread(target=get_current_note)
    thread.start()
    wait_for_enter()
    thread.join()
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("✅ Program terminated. Data saved to 'note_output.txt'")

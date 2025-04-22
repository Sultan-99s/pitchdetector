import music21
import re

# Function to convert amplitude to dynamic marking
def amplitude_to_dynamic(amplitude):
    if amplitude < 0.1:
        return 'pp'
    elif amplitude < 0.2:
        return 'p'
    elif amplitude < 0.5:
        return 'mf'
    elif amplitude < 0.8:
        return 'f'
    else:
        return 'ff'

# Function to convert the output from the text file into MusicXML format
def convert_to_musicxml_from_file(input_file, output_file):
    # Create a music21 Stream object to hold the music
    stream = music21.stream.Stream()

    # Open and read the input text file
    with open(input_file, 'r') as file:
        log_data = file.readlines()
    
    # Loop through the log data and extract necessary information
    for line in log_data:
        # Extract values using regular expressions
        match = re.match(r'\[Time: (\d+\.\d+)s \| Δt: (\d+\.\d+)s\] (\d+\.\d+) Hz ---- ([A-G#b]+[0-9]) ---- (-?\d+\.\d+) cents ---- amplitude: (\d+\.\d+)', line)
        
        if match:
            timestamp = float(match.group(1))  # Time
            delta_t = float(match.group(2))  # Δt (duration)
            frequency = float(match.group(3))  # Hz
            note_name = match.group(4)  # Note (e.g., 'C#6')
            cents = float(match.group(5))  # Cents deviation
            amplitude = float(match.group(6))  # Amplitude
            
            # Create a music21 note from the note name (e.g., 'C#6')
            note = music21.note.Note(note_name)
            note.quarterLength = delta_t  # Set the duration of the note (from Δt)
            
            # Map amplitude to dynamics (e.g., 'mf', 'f', etc.)
            dynamic = amplitude_to_dynamic(amplitude)
            note.dynamic = music21.dynamics.Dynamic(dynamic)
            
            # Add the note to the stream
            stream.append(note)

    # Save the stream as MusicXML
    stream.write('musicxml', fp=output_file)
    print(f"MusicXML saved to: {output_file}")

# Main function to run the conversion
if __name__ == "__main__":
    # Hard-coded input and output file paths
    input_file = 'note_output.txt'  # Path to your input text file
    output_file = 'converted_output.xml'  # Path where the MusicXML will be saved

    # Convert the text file to MusicXML
    convert_to_musicxml_from_file(input_file, output_file)

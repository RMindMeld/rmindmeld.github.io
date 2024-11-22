import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
import nltk
import os
import re
from tkinter.ttk import Progressbar
import keyring
from num2words import num2words


# Define available voices
AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Ensure NLTK data is downloaded for sentence and paragraph tokenizing
nltk.download('punkt')

# Load Script and Voices
SPEAKER_VOICE_MAP = {
    "John": "onyx",   
    "Jeane": "nova",
    "Mark": "echo",
    "Lucy": "shimmer",
    "David": "fable",
    "Sara": "alloy",
}

# Function to scan for voices in the script and populate SPEAKER_VOICE_MAP
def scan_for_voices(text):
    # Regular expression to find speaker names in the format "[voice]: "
    speaker_regex = re.compile(r'\[(\w+)\]:\s')
    speakers = speaker_regex.findall(text)
    
    # Get unique speakers
    unique_speakers = list(set(speakers))
    
    # Available voices
    available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    # Create a new SPEAKER_VOICE_MAP
    new_map = {}
    for i, speaker in enumerate(unique_speakers):
        # Assign a voice from the available list, cycling if necessary
        voice = available_voices[i % len(available_voices)]
        new_map[speaker] = voice
    
    return new_map


SPEAKER_VOICE_MAP = {}

# Function to update SPEAKER_VOICE_MAP
def update_speaker_voice_map(text):
    global SPEAKER_VOICE_MAP
    # Check if there are any speaker tags
    speaker_regex = re.compile(r'\[(\w+)\]:')
    speakers = speaker_regex.findall(text)
    
    if not speakers:
        # If no speakers found, don't modify the voice map
        return
    
    # Update voice map only if speakers are found
    unique_speakers = list(set(speakers))
    for i, speaker in enumerate(unique_speakers):
        if speaker not in SPEAKER_VOICE_MAP:
            SPEAKER_VOICE_MAP[speaker] = AVAILABLE_VOICES[i % len(AVAILABLE_VOICES)]
    
    print("Updated SPEAKER_VOICE_MAP:", SPEAKER_VOICE_MAP)

# Read the current script as a string (for example, from a file)
def load_script():
    # Assuming the script is in the same directory as this code
    script_path = Path(__file__)  # Get the current script's path
    with open(script_path, 'r') as script_file:
        return script_file.read()

# Initialize the SPEAKER_VOICE_MAP with voices found in the script
script_content = load_script()
SPEAKER_VOICE_MAP.update(scan_for_voices(script_content))

# Global variables

DEFAULT_VOICE = "alloy"
OUTPUT_FORMATS = ["mp3", "wav", "ogg"]

TTS_MODELS = ["tts-1", "tts-1-hd"]
CURRENT_TTS_MODEL = "tts-1"  # Default model


# API Key Management
def set_api_key():
    api_key = simpledialog.askstring("API Key", "Enter your OpenAI API key:", show='*')
    if api_key:
        keyring.set_password("openai_tts", "api_key", api_key)

def get_api_key():
    return keyring.get_password("openai_tts", "api_key")

# Initialize OpenAI client
api_key = get_api_key() 
# or add your API key here
client = OpenAI(api_key=api_key)

# Text Preprocessing
def preprocess_text(text):
    # Split the text into lines
    lines = text.split('\n')
    
    # Process each line separately
    processed_lines = []
    for line in lines:
        # Remove extra whitespace within each line
        line = re.sub(r'\s+', ' ', line).strip()
        
        # Convert numbers to words
        # line = re.sub(r'\b(\d+)\b', lambda m: num2words(int(m.group(0))), line)
        
        # Expand common abbreviations
        abbreviations = {
            "Mr.": "Mister",
            "Mrs.": "Misses",
            "Dr.": "Doctor",
            # Add more abbreviations here
        }
        for abbr, expansion in abbreviations.items():
            line = line.replace(abbr, expansion)
        
        processed_lines.append(line)
    
    # Join the processed lines back together
    return '\n'.join(processed_lines)

# Function to split text into manageable chunks while keeping track of speakers
def split_text_by_speaker(text, chunk_size=4000):
    # First, check if there are any speaker tags in the text
    speaker_pattern = r'\[(\w+)\]:'
    has_speaker_tags = bool(re.search(speaker_pattern, text))
    
    # If no speaker tags found, treat entire text as one voice
    if not has_speaker_tags:
        # Split the text into appropriate chunk sizes
        chunks = []
        while text:
            chunk = text[:chunk_size]
            if len(text) > chunk_size:
                # Find the last period to avoid cutting mid-sentence
                last_period = chunk.rfind('.')
                if last_period != -1:
                    chunk = text[:last_period + 1]
                    text = text[last_period + 1:].lstrip()
                else:
                    text = text[chunk_size:]
            else:
                text = ""
                
            if chunk.strip():
                chunks.append({
                    "speaker": None,
                    "voice": DEFAULT_VOICE,
                    "text": chunk.strip()
                })
        
        return chunks
    
    # If there are speaker tags, process them normally
    chunks = []
    pattern = r'\[(\w+)\]:\s*(.*?)(?=\n\[|$)'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    for match in matches:
        speaker = match.group(1)
        content = match.group(2).strip()
        voice = SPEAKER_VOICE_MAP.get(speaker, AVAILABLE_VOICES[0])
        
        if not content:
            continue
            
        if len(content) <= chunk_size:
            chunks.append({
                "speaker": speaker,
                "voice": voice,
                "text": content
            })
        else:
            # Split large content into smaller chunks
            while content:
                chunk = content[:chunk_size]
                if len(content) > chunk_size:
                    last_period = chunk.rfind('.')
                    if last_period != -1:
                        chunk = content[:last_period + 1]
                        content = content[last_period + 1:].lstrip()
                    else:
                        content = content[chunk_size:]
                else:
                    content = ""
                    
                if chunk.strip():
                    chunks.append({
                        "speaker": speaker,
                        "voice": voice,
                        "text": chunk.strip()
                    })
    
    print(f"Total chunks created: {len(chunks)}")
    return chunks
   
def split_large_chunk(text, speaker, voice, chunk_size):
    sentences = nltk.tokenize.sent_tokenize(text)
    current_chunk = ""
    chunks = []
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append({"speaker": speaker, "voice": voice, "text": current_chunk.strip()})
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append({"speaker": speaker, "voice": voice, "text": current_chunk.strip()})
    
    return chunks

# Function to create TTS audio files for each chunk

def lscreate_tts_audio(text_chunks, output_dir="output_audio", progress_bar=None):
    global CURRENT_TTS_MODEL
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    audio_files = []
    total_chunks = len(text_chunks)
    
    for idx, chunk in enumerate(text_chunks):
        speech_file_path = output_dir / f"speech_part_{idx + 1}.mp3"
        
        # Debug print
        print(f"Creating audio for chunk {idx + 1} using voice: {chunk['voice']}")
        
        # Create audio response using the selected model
        response = client.audio.speech.create(
            model=CURRENT_TTS_MODEL,
            voice=chunk["voice"],
            input=chunk["text"]
        )
        
        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)
        
        audio_files.append(speech_file_path)
        
        if progress_bar:
            progress_bar['value'] += (100 / total_chunks)
            root.update_idletasks()
    
    return audio_files

def oldcreate_tts_audio(text_chunks, output_dir="output_audio", progress_bar=None):
    global CURRENT_TTS_MODEL
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    audio_files = []
    total_chunks = len(text_chunks)
    
    for idx, chunk in enumerate(text_chunks):
        speech_file_path = output_dir / f"speech_part_{idx + 1}.mp3"
        
        # Debug print
        print(f"Creating audio for chunk {idx + 1} - Speaker: {chunk['speaker']}, Voice: {chunk['voice']}, Text: {chunk['text'][:50]}...")
        
        # Create audio response using the selected model and voice
        response = client.audio.speech.create(
            model=CURRENT_TTS_MODEL,
            voice=chunk["voice"],
            input=chunk["text"]
        )
        
        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)
        
        audio_files.append(speech_file_path)
        
        if progress_bar:
            progress_bar['value'] += (100 / total_chunks)
            root.update_idletasks()
    
    return audio_files

def create_tts_audio(text_chunks, output_dir="output_audio", progress_bar=None):
    global CURRENT_TTS_MODEL
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    audio_files = []
    total_chunks = len(text_chunks)
    
    for idx, chunk in enumerate(text_chunks):
        speech_file_path = output_dir / f"speech_part_{idx + 1}.mp3"
        
        # Debug print
        if chunk['speaker']:
            print(f"Creating audio for chunk {idx + 1} - Speaker: {chunk['speaker']}, Voice: {chunk['voice']}, Text: {chunk['text'][:50]}...")
        else:
            print(f"Creating audio for chunk {idx + 1} - Using default voice: {chunk['voice']}, Text: {chunk['text'][:50]}...")
        
        # Create audio response using the selected model and voice
        response = client.audio.speech.create(
            model=CURRENT_TTS_MODEL,
            voice=chunk["voice"],
            input=chunk["text"]
        )
        
        with open(speech_file_path, "wb") as audio_file:
            audio_file.write(response.content)
        
        audio_files.append(speech_file_path)
        
        if progress_bar:
            progress_bar['value'] += (100 / total_chunks)
            root.update_idletasks()
    
    return audio_files

# Function to merge audio files into one
def merge_audio_files(audio_files, output_path="final_output.mp3", format="mp3"):
    combined = AudioSegment.empty()
    for audio_file in audio_files:
        segment = AudioSegment.from_file(audio_file)
        combined += segment
    combined.export(output_path, format=format)

# Add a function to open model settings
def open_model_settings():
    global CURRENT_TTS_MODEL
    settings_window = tk.Toplevel(root)
    settings_window.title("TTS Model Settings")

    frame = ttk.Frame(settings_window, padding="10")
    frame.pack(fill=tk.X)

    ttk.Label(frame, text="Select TTS Model:").pack(side=tk.LEFT)

    model_var = tk.StringVar(value=CURRENT_TTS_MODEL)

    model_dropdown = ttk.Combobox(frame, textvariable=model_var, values=TTS_MODELS, state="readonly")
    model_dropdown.pack(side=tk.LEFT)

    def save_model_settings():
        global CURRENT_TTS_MODEL
        CURRENT_TTS_MODEL = model_var.get()
        messagebox.showinfo("Model Settings", f"TTS Model set to: {CURRENT_TTS_MODEL}")
        settings_window.destroy()

    save_button = ttk.Button(settings_window, text="Save Settings", command=save_model_settings)
    save_button.pack(pady=10)

# Main function to handle the entire process
def text_to_speech(text, chunk_size=4000, output_dir="output_audio", final_output="final_output.mp3", progress_bar=None):
    preprocessed_text = preprocess_text(text)
    print("poil:",preprocessed_text)
    update_speaker_voice_map(preprocessed_text)
    text_chunks = split_text_by_speaker(preprocessed_text, chunk_size)
    audio_files = create_tts_audio(text_chunks, output_dir=output_dir, progress_bar=progress_bar)
    merge_audio_files(audio_files, output_path=final_output, format=Path(final_output).suffix[1:])
    
    # Clean up temporary files
    for file in audio_files:
        os.remove(file)

    messagebox.showinfo("Success", f"Final audio saved as: {final_output}")



# GUI Functions
def load_text_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                text_input.delete(1.0, tk.END)
                text_input.insert(tk.END, text)
                update_speaker_voice_map(text)
        except UnicodeDecodeError:
            messagebox.showerror("Error", "Failed to decode the file. Please ensure it's a valid UTF-8 text file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the file: {e}")

def start_conversion():
    print("start_conversion")
    text = text_input.get(1.0, tk.END).strip()
    print("text:",text)
    if not text:
        messagebox.showwarning("Warning", "Please enter some text or load a text file.")
        return
    
    # Update SPEAKER_VOICE_MAP here
    update_speaker_voice_map(text)
    
    output_format = format_var.get()
    output_file = filedialog.asksaveasfilename(defaultextension=f".{output_format}", 
                                               filetypes=[(f"{output_format.upper()} files", f"*.{output_format}")])
    if not output_file:
        return
    
    progress_bar['value'] = 0
    
    print("text:",text)

    text_to_speech(text, final_output=output_file, progress_bar=progress_bar)

  
def open_voice_settings():
    # First, update the SPEAKER_VOICE_MAP with any new speakers from current text
    text = text_input.get(1.0, tk.END).strip()
    if text:
        update_speaker_voice_map(text)
    
    settings_window = tk.Toplevel(root)
    settings_window.title("Voice Settings")
    
    # Make window modal
    settings_window.transient(root)
    settings_window.grab_set()
    
    # Create a scrollable frame in case there are many speakers
    canvas = tk.Canvas(settings_window)
    scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    voice_vars = {}

    for speaker, voice in SPEAKER_VOICE_MAP.items():
        frame = ttk.Frame(scrollable_frame, padding="5")
        frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(frame, text=f"Voice for {speaker}:").pack(side=tk.LEFT, padx=(0, 10))

        voice_var = tk.StringVar(value=voice)
        voice_vars[speaker] = voice_var

        voice_dropdown = ttk.Combobox(frame, textvariable=voice_var, 
                                    values=AVAILABLE_VOICES, 
                                    state="readonly",
                                    width=15)
        voice_dropdown.pack(side=tk.LEFT)

    def save_voice_settings():
        global SPEAKER_VOICE_MAP
        for speaker, voice_var in voice_vars.items():
            SPEAKER_VOICE_MAP[speaker] = voice_var.get()
        messagebox.showinfo("Voice Settings", "Voice settings saved successfully!")
        settings_window.destroy()

    def refresh_voices():
        # Get current text and clear existing voice map
        current_text = text_input.get(1.0, tk.END).strip()
        if current_text:
            global SPEAKER_VOICE_MAP
            SPEAKER_VOICE_MAP = {}  # Clear the existing map
            update_speaker_voice_map(current_text)
        
        # Destroy current frames
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # Recreate voice settings for all speakers
        voice_vars.clear()
        for speaker, voice in SPEAKER_VOICE_MAP.items():
            frame = ttk.Frame(scrollable_frame, padding="5")
            frame.pack(fill=tk.X, padx=5, pady=2)

            ttk.Label(frame, text=f"Voice for {speaker}:").pack(side=tk.LEFT, padx=(0, 10))

            voice_var = tk.StringVar(value=voice)
            voice_vars[speaker] = voice_var

            voice_dropdown = ttk.Combobox(frame, textvariable=voice_var, 
                                        values=AVAILABLE_VOICES, 
                                        state="readonly",
                                        width=15)
            voice_dropdown.pack(side=tk.LEFT)
        
        settings_window.update_idletasks()

    
    # Button frame
    button_frame = ttk.Frame(settings_window, padding="10")
    button_frame.pack(fill=tk.X, side=tk.BOTTOM)

    refresh_button = ttk.Button(button_frame, text="Refresh Speakers", command=refresh_voices)
    refresh_button.pack(side=tk.LEFT, padx=5)

    save_button = ttk.Button(button_frame, text="Save Settings", command=save_voice_settings)
    save_button.pack(side=tk.RIGHT, padx=5)

    # Pack the canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Set a minimum size for the window
    settings_window.minsize(300, 200)

# Initialize the Tkinter window
global root, text_input, format_var, progress_bar

root = tk.Tk()
root.title("Text to Speech Converter with Enhanced Features")

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

text_input = tk.Text(main_frame, wrap=tk.WORD, height=10, width=50)
text_input.grid(row=0, column=0, columnspan=3, pady=10)

button_frame = ttk.Frame(main_frame)
button_frame.grid(row=1, column=0, columnspan=3, pady=5)

load_button = ttk.Button(button_frame, text="Load Text File", command=load_text_file)
load_button.grid(row=0, column=0, padx=5)

voice_settings_button = ttk.Button(button_frame, text="Voice Settings", command=open_voice_settings)
voice_settings_button.grid(row=0, column=1, padx=5)

model_settings_button = ttk.Button(button_frame, text="Model Settings", command=open_model_settings)
model_settings_button.grid(row=0, column=2, padx=5)

api_key_button = ttk.Button(button_frame, text="Set API Key", command=set_api_key)
api_key_button.grid(row=0, column=3, padx=5)

format_frame = ttk.Frame(main_frame)
format_frame.grid(row=2, column=0, columnspan=3, pady=5)

ttk.Label(format_frame, text="Output Format:").grid(row=0, column=0, padx=5)
format_var = tk.StringVar(value="mp3")
format_dropdown = ttk.Combobox(format_frame, textvariable=format_var, values=OUTPUT_FORMATS, state="readonly")
format_dropdown.grid(row=0, column=1, padx=5)

convert_button = ttk.Button(main_frame, text="Start Conversion", command=start_conversion)
convert_button.grid(row=3, column=0, columnspan=3, pady=10)

progress_bar = Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, pady=5)

# Start the Tkinter event loop
root.mainloop()
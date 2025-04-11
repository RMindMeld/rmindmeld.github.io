import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from pathlib import Path
from openai import OpenAI, APIError, AuthenticationError # Import specific errors
import nltk
import os
import re
import threading # Import threading
from tkinter.ttk import Progressbar
import keyring
from typing import List, Dict, Optional, Tuple # Import types for hinting

# --- Constants ---
AVAILABLE_VOICES: List[str] = ["alloy", "ash", "ballad","coral", "echo", "fable", "onyx", "nova", "sage", "shimmer", "verse"]
# Note: The actual available voices may vary based on OpenAI's API updates.
DEFAULT_VOICE: str = "alloy"
# Note: OpenAI TTS API currently primarily supports MP3 for direct streaming/concatenation.
# Supporting WAV/OGG directly would require a library like pydub to convert after generation.
# Sticking to MP3 for simplicity based on current OpenAI library capabilities.
OUTPUT_FORMATS: List[str] = ["mp3"]
TTS_MODELS: List[str] = ["tts-1", "tts-1-hd","gpt-4o-mini-tts"]
DEFAULT_TTS_MODEL: str = "gpt-4o-mini-tts"
KEYRING_SERVICE: str = "openai_tts_app" # More specific service name
KEYRING_USERNAME: str = "api_key"
MAX_CHUNK_SIZE: int = 4000 # OpenAI TTS limit

# --- Global Variables ---
# Using a class might be cleaner for managing state, but globals are okay for this scale
SPEAKER_VOICE_MAP: Dict[str, str] = {}
CURRENT_TTS_MODEL: str = DEFAULT_TTS_MODEL
client: Optional[OpenAI] = None # Initialize client later

# --- NLTK Setup ---
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    print("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt')
except LookupError: # Fallback for environments where find might raise LookupError
     print("NLTK 'punkt' tokenizer potentially missing. Attempting download...")
     nltk.download('punkt')

# --- API Key Management ---
def set_api_key() -> None:
    """Prompts the user for an API key and saves it securely using keyring."""
    api_key = simpledialog.askstring("API Key", "Enter your OpenAI API key:", show='*')
    if api_key:
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
            messagebox.showinfo("API Key", "API Key saved successfully.")
            initialize_openai_client() # Re-initialize client with the new key
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key:{e}")
    else:
         messagebox.showwarning("API Key", "No API Key entered.")

def get_api_key() -> Optional[str]:
    """Retrieves the API key from environment variables or keyring."""
    # Prefer environment variable if set
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        print("Using API key from environment variable.")
        return env_key
    # Otherwise, try keyring
    try:
        key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if key:
            print("Using API key from keyring.")
        return key
    except Exception as e:
        print(f"Could not retrieve key from keyring: {e}") # Non-critical error
        return None

def initialize_openai_client() -> None:
    """Initializes the OpenAI client using the retrieved API key."""
    global client
    api_key = get_api_key()
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            print("OpenAI client initialized successfully.")
        except Exception as e:
            client = None
            messagebox.showerror("OpenAI Client Error", f"Failed to initialize OpenAI client:{e}\nPlease check your API key or network connection.")
    else:
        client = None
        print("OpenAI client not initialized. API key missing.")
        # Optionally prompt user here, or rely on them clicking "Set API Key"
        # messagebox.showwarning("API Key Missing", "OpenAI API key not found. Please set it using the 'Set API Key' button.")


# --- Text Processing ---
def preprocess_text(text: str) -> str:
    """Cleans and preprocesses the input text."""
    processed_lines = []
    # Expanded abbreviations example
    abbreviations = {
        r"\bMr.\s": "Mister ", # Use regex for word boundaries and space
        r"\bMrs.\s": "Misses ",
        r"\bDr.\s": "Doctor ",
        # Add more robust abbreviations here if needed
    }
    # Process line by line to preserve structure important for splitting
    for line in text.splitlines(): # Use splitlines to handle different line endings
        line = line.strip()
        if not line: # Skip empty lines
            continue

        # Apply abbreviations
        for abbr, expansion in abbreviations.items():
             line = re.sub(abbr, expansion, line, flags=re.IGNORECASE) # Case-insensitive matching

        # Remove extra whitespace within the line *after* abbreviation expansion
        line = re.sub(r'\s+', ' ', line).strip()

        # Add other preprocessing steps here if needed (e.g., number to words)
        # Be cautious with number-to-words if numbers are part of speaker tags or context
        processed_lines.append(line)

    return '\n'.join(processed_lines)

def update_speaker_voice_map(text: str) -> None:
    """
    Scans text for [Speaker]: tags and updates the global SPEAKER_VOICE_MAP,
    assigning default voices only to newly found speakers.
    """
    global SPEAKER_VOICE_MAP
    speaker_regex = re.compile(r'\[(\w+)\]:')
    speakers_found = speaker_regex.findall(text)
    unique_speakers = sorted(list(set(speakers_found))) # Sort for consistent assignment order

    if not unique_speakers:
        return # No speaker tags found, do nothing

    newly_added = False
    available_voice_pool = AVAILABLE_VOICES[:] # Copy the list

    # Assign voices to speakers already in the map first to maintain consistency
    existing_speakers = [s for s in unique_speakers if s in SPEAKER_VOICE_MAP]
    for speaker in existing_speakers:
        assigned_voice = SPEAKER_VOICE_MAP[speaker]
        if assigned_voice in available_voice_pool:
            available_voice_pool.remove(assigned_voice) # Avoid reusing voices if possible

    # Assign voices to new speakers
    new_speakers = [s for s in unique_speakers if s not in SPEAKER_VOICE_MAP]
    for i, speaker in enumerate(new_speakers):
        if available_voice_pool:
            voice = available_voice_pool.pop(0) # Take next available
        else:
            # Cycle through voices if we run out of unique ones
            voice = AVAILABLE_VOICES[i % len(AVAILABLE_VOICES)]

        SPEAKER_VOICE_MAP[speaker] = voice
        newly_added = True

    if newly_added:
        print("Updated SPEAKER_VOICE_MAP:", SPEAKER_VOICE_MAP)

def split_text_by_speaker(text: str) -> List[Dict[str, Optional[str]]]:
    """
    Splits the text into chunks based on speaker tags `[Speaker]:`
    and instruction tags `<instruction>` within a speaker's block.
    Ensures proper handling of accumulated text and chunking.
    
    Returns:
        A list of dictionaries, each with "speaker", "voice", "text",
        and optionally "instructions".
    """
    global SPEAKER_VOICE_MAP, DEFAULT_VOICE, MAX_CHUNK_SIZE

    chunks = []
    
    # Split text by speaker blocks
    speaker_blocks = re.split(r'(\[\w+\]:)', text)
    
    current_speaker = None
    current_voice = DEFAULT_VOICE
    
    for block in speaker_blocks:
        block = block.strip()
        if not block:
            continue
        
        # Check if this is a speaker tag
        speaker_match = re.match(r'\[(\w+)\]:', block)
        if speaker_match:
            current_speaker = speaker_match.group(1)
            current_voice = SPEAKER_VOICE_MAP.get(current_speaker, DEFAULT_VOICE)
            continue
        
        # Skip if we haven't found a speaker yet
        if not current_speaker:
            continue
        
        # First, check if there's text before any instruction
        first_instruction_idx = block.find('<')
        if first_instruction_idx > 0:
            initial_text = block[:first_instruction_idx].strip()
            if initial_text:
                chunks.extend(split_large_chunk(initial_text, current_speaker, current_voice, None, MAX_CHUNK_SIZE))
        
        # Find all instructions and the text that follows each
        instruction_matches = re.finditer(r'<([^>]+)>([\s\S]*?)(?=<|$)', block)
        
        for match in instruction_matches:
            instruction = match.group(1).strip()
            following_text = match.group(2).strip()
            
            if following_text:
                chunks.extend(split_large_chunk(following_text, current_speaker, current_voice, instruction, MAX_CHUNK_SIZE))
    
    # Filter out empty chunks
    final_chunks = [chunk for chunk in chunks if chunk.get("text")]
    return final_chunks 
 
def split_large_chunk(text: str, speaker: Optional[str], voice: str, instructions: Optional[str], chunk_size: int) -> List[Dict[str, Optional[str]]]:
    """
    Splits text that exceeds the chunk_size, trying to break at sentence boundaries.
    Ensures that anything between <> is extracted into 'instructions', keeping text clean.
    """
    sub_chunks = []
    
    # Extract instructions from text
    extracted_instructions = " ".join(re.findall(r"<(.+?)>", text))
    text = re.sub(r"<.*?>", "", text).strip()  # Ensure all <> content is fully removed
    
    # Merge extracted instructions with given ones
    if extracted_instructions:
        instructions = (instructions + " " + extracted_instructions).strip() if instructions else extracted_instructions
    
    if len(text) <= chunk_size:
        sub_chunks.append({"speaker": speaker, "voice": voice, "text": text, "instructions": instructions})
    else:
        print(f"     Splitting large chunk for speaker '{speaker}' (length: {len(text)}, instructions: '{instructions}')...")        
        sentences = nltk.tokenize.sent_tokenize(text)
        current_sub_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_sub_chunk) + len(sentence) + 1 <= chunk_size:
                current_sub_chunk += sentence + " "
            else:
                if current_sub_chunk.strip():
                    sub_chunks.append({"speaker": speaker, "voice": voice, "text": current_sub_chunk.strip(), "instructions": instructions})
                    print(f"       Created sub-chunk (length: {len(current_sub_chunk.strip())})")

                if len(sentence) > chunk_size:
                    print(f"       Warning: Sentence is longer than chunk size ({len(sentence)} > {chunk_size}). Splitting mid-sentence.")
                    for i in range(0, len(sentence), chunk_size):
                        sub_chunks.append({"speaker": speaker, "voice": voice, "text": sentence[i:i+chunk_size].strip(), "instructions": instructions})
                    current_sub_chunk = ""
                else:
                    current_sub_chunk = sentence + " "

        if current_sub_chunk.strip():
            sub_chunks.append({"speaker": speaker, "voice": voice, "text": current_sub_chunk.strip(), "instructions": instructions})
            print(f"       Created final sub-chunk (length: {len(current_sub_chunk.strip())})")
    
    return sub_chunks

 
# Modify create_tts_audio to use instructions when available and model is gpt-4o-mini-tts
def create_tts_audio(text_chunks: List[Dict[str, Optional[str]]], progress_callback) -> Optional[bytes]:
    global CURRENT_TTS_MODEL, client

    if not client:
        messagebox.showerror("Error", "OpenAI client not initialized. Please set API key.")
        return None

    audio_bytes_list = []
    total_chunks = len(text_chunks)

    try:
        for idx, chunk in enumerate(text_chunks):
            voice = chunk["voice"]
            text_content = chunk["text"]
            xinstructions = chunk.get("instructions")  # Get instructions, defaults to None
            speaker = chunk["speaker"]

            if not text_content:  # Skip empty text chunks
                print(f"Skipping empty text chunk {idx + 1}")
                continue

            print(f"Generating audio for chunk {idx + 1}/{total_chunks} (Speaker: {speaker}, Voice: {voice}, Model: {CURRENT_TTS_MODEL}, Instructions: '{xinstructions or 'N/A'}')")
            print(f"content:{text_content}")
            response = None  # Initialize response variable

            # Check if the model supports instructions
            if CURRENT_TTS_MODEL != "gpt-4o-mini-tts":
                response = client.audio.speech.create(
                    model=CURRENT_TTS_MODEL,
                    voice=voice,  # Fixed unnecessary quotes
                    input=text_content
                )
            else:
                response = client.audio.speech.create(
                    model="gpt-4o-mini-tts",
                    voice=voice,  # Fixed unnecessary quotes
                    input=text_content,
                    instructions=xinstructions.strip() if xinstructions else "  "
                )

            # Validate response
            if response and hasattr(response, "content"):
                audio_bytes_list.append(response.content)
            else:
                print(f"Warning: No content received for chunk {idx + 1}")

            # Update progress bar
            progress_value = ((idx + 1) / total_chunks) * 100
            if "root" in globals():  # Ensure root exists
                root.after(0, progress_callback, progress_value)

        # Concatenate all audio bytes
        final_audio = b"".join(audio_bytes_list) if audio_bytes_list else None
        print("Audio generation complete.")
        return final_audio

    except Exception as e:
        print(f"Error generating audio: {e}")
        return None
    
# --- Core Conversion Process ---
def text_to_speech_task(text: str, final_output_path: str, progress_callback) -> None:
    """
    The main task function to be run in a separate thread.
    Handles preprocessing, chunking, API calls, and saving.
    """
    try:
        print("Preprocessing text...")
        preprocessed_text = preprocess_text(text)

        print("Updating speaker voice map...")
        update_speaker_voice_map(preprocessed_text) # Update map based on current text

        print("Splitting text by speaker...")
        text_chunks = split_text_by_speaker(preprocessed_text)

        if not text_chunks:
            messagebox.showwarning("Warning", "No text content found after processing.")
            root.after(0, conversion_finished, False, None) # Signal completion (failure)
            return

        print("Generating TTS audio...")
        # Pass the update_progress function directly
        final_audio_data = create_tts_audio(text_chunks, progress_callback)

        if final_audio_data:
            print(f"Saving concatenated audio to: {final_output_path}")
            try:
                with open(final_output_path, "wb") as final_audio_file:
                    final_audio_file.write(final_audio_data)
                print("File saved successfully.")
                # Schedule success message box from main thread
                root.after(0, conversion_finished, True, final_output_path)
            except IOError as e:
                messagebox.showerror("File Error", f"Failed to save audio file:\n{e}")
                root.after(0, conversion_finished, False, None) # Signal completion (failure)
            except Exception as e:
                 messagebox.showerror("Error", f"An unexpected error occurred while saving the file: {e}")
                 root.after(0, conversion_finished, False, None) # Signal completion (failure)
        else:
            # Error occurred during TTS generation, message already shown by create_tts_audio
            print("Audio generation failed.")
            root.after(0, conversion_finished, False, None) # Signal completion (failure)

    except Exception as e:
        # Catch any unexpected errors in the thread
        print(f"Error in TTS thread: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        messagebox.showerror("Thread Error", f"An unexpected error occurred: {e}")
        root.after(0, conversion_finished, False, None) # Signal completion (failure)


# --- GUI Functions ---

def load_text_file() -> None:
    """Loads text from a file into the text input widget."""
    file_path = filedialog.askopenfilename(
        title="Select Text File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            text_input.delete(1.0, tk.END)
            text_input.insert(tk.END, text)
            print(f"Loaded text from: {file_path}")
            # Update speaker map immediately after loading
            update_speaker_voice_map(text)
        except UnicodeDecodeError:
            messagebox.showerror("Encoding Error", "Failed to decode the file. Please ensure it's a valid UTF-8 text file.")
        except Exception as e:
            messagebox.showerror("File Error", f"An error occurred while reading the file:\n{e}")

def update_progress(value: float) -> None:
    """Updates the progress bar value."""
    progress_bar['value'] = value
    # root.update_idletasks() # Not strictly needed when using root.after

def conversion_finished(success: bool, output_path: Optional[str]) -> None:
    """Called when the TTS thread finishes, handles final GUI updates."""
    progress_bar['value'] = 0 # Reset progress bar
    convert_button['state'] = tk.NORMAL # Re-enable button
    if success and output_path:
        messagebox.showinfo("Success", f"Conversion complete!\nFinal audio saved as:\n{output_path}")
    elif not success:
         # Error message should have already been shown
         print("Conversion process failed.")
    # If success is True but output_path is None (shouldn't happen), do nothing extra.


def start_conversion() -> None:
    """Starts the TTS conversion process in a separate thread."""
    print("Start conversion button clicked.")
    global client
    if not client:
        messagebox.showerror("Error", "OpenAI Client not initialized.\nPlease set your API key using the 'Set API Key' button.")
        return

    text = text_input.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Input Required", "Please enter some text or load a text file.")
        return

    # Update speaker map *before* asking for filename, in case new speakers were typed
    print("Updating speaker map before proceeding...")
    update_speaker_voice_map(text)

    output_format = format_var.get()
    # Adjust file types based on supported formats
    file_types = [(f"{output_format.upper()} files", f"*.{output_format}")]

    output_file = filedialog.asksaveasfilename(
        title="Save Audio As",
        defaultextension=f".{output_format}",
        filetypes=file_types
    )
    if not output_file:
        print("File save canceled.")
        return # User canceled save dialog

    # Ensure the output path has the correct extension
    output_file_path = Path(output_file)
    if output_file_path.suffix.lower() != f".{output_format}":
       output_file_path = output_file_path.with_suffix(f".{output_format}")
       print(f"Adjusted filename to: {output_file_path}")


    # Disable button, reset progress bar
    convert_button['state'] = tk.DISABLED
    progress_bar['value'] = 0
    # root.update_idletasks() # Ensure GUI updates before starting thread

    # Start the background task
    print(f"Starting TTS thread for output: {output_file_path}")
    tts_thread = threading.Thread(
        target=text_to_speech_task,
        args=(text, str(output_file_path), update_progress), # Pass necessary args
        daemon=True # Allows closing app even if thread is running (use cautiously)
    )
    tts_thread.start()


def open_voice_settings() -> None:
    """Opens a window to configure voices for detected speakers."""
    global SPEAKER_VOICE_MAP

    # Update map based on current text before opening settings
    current_text = text_input.get(1.0, tk.END).strip()
    if current_text:
        update_speaker_voice_map(current_text)

    settings_window = tk.Toplevel(root)
    settings_window.title("Voice Settings")
    settings_window.transient(root) # Keep window on top of main
    settings_window.grab_set() # Make modal
    settings_window.minsize(350, 200)

    # Main Frame for content
    main_settings_frame = ttk.Frame(settings_window, padding="10")
    main_settings_frame.pack(fill=tk.BOTH, expand=True)

    # --- Top part for description ---
    desc_label = ttk.Label(main_settings_frame, text="Assign voices to speakers found in the text:")
    desc_label.pack(pady=(0, 10))

    # --- Scrollable area for speaker settings ---
    canvas_frame = ttk.Frame(main_settings_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(canvas_frame)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, padding=(10, 0)) # Add padding inside canvas

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Populate Speaker Settings ---
    voice_vars: Dict[str, tk.StringVar] = {}

    def populate_speaker_widgets():
        # Clear existing widgets first
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        voice_vars.clear()

        if not SPEAKER_VOICE_MAP:
             ttk.Label(scrollable_frame, text="No speakers detected yet.\nLoad text with [Speaker]: tags.").pack(pady=20)
             return # Don't add widgets if no speakers

        # Sort speakers alphabetically for consistent UI
        sorted_speakers = sorted(SPEAKER_VOICE_MAP.keys())

        for speaker in sorted_speakers:
            voice = SPEAKER_VOICE_MAP.get(speaker, DEFAULT_VOICE) # Default just in case
            frame = ttk.Frame(scrollable_frame) # No extra padding needed here
            frame.pack(fill=tk.X, pady=2)

            # Use speaker name in the label
            label = ttk.Label(frame, text=f"[{speaker}]:", width=15, anchor="w") # Fixed width for alignment
            label.pack(side=tk.LEFT, padx=(0, 5))

            voice_var = tk.StringVar(value=voice)
            voice_vars[speaker] = voice_var

            voice_dropdown = ttk.Combobox(frame, textvariable=voice_var,
                                            values=AVAILABLE_VOICES,
                                            state="readonly", width=15)
            voice_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)


    # --- Bottom Buttons ---
    button_frame = ttk.Frame(settings_window, padding="10")
    button_frame.pack(fill=tk.X, side=tk.BOTTOM)

    def save_voice_settings():
        global SPEAKER_VOICE_MAP
        changed = False
        for speaker, voice_var in voice_vars.items():
            new_voice = voice_var.get()
            if speaker in SPEAKER_VOICE_MAP and SPEAKER_VOICE_MAP[speaker] != new_voice:
                SPEAKER_VOICE_MAP[speaker] = new_voice
                changed = True
        if changed:
            messagebox.showinfo("Voice Settings", "Voice settings saved successfully!", parent=settings_window)
            print("Updated SPEAKER_VOICE_MAP from settings:", SPEAKER_VOICE_MAP)
        settings_window.destroy()

    def refresh_voices():
        print("Refreshing speaker list...")
        # Get current text and update the map
        current_text_refresh = text_input.get(1.0, tk.END).strip()
        if current_text_refresh:
             # Re-scan completely
             global SPEAKER_VOICE_MAP
             SPEAKER_VOICE_MAP = {} # Clear first
             update_speaker_voice_map(current_text_refresh)
        # Repopulate the GUI
        populate_speaker_widgets()
        # Force canvas update
        settings_window.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    refresh_button = ttk.Button(button_frame, text="Refresh Speakers", command=refresh_voices)
    refresh_button.pack(side=tk.LEFT, padx=5)

    save_button = ttk.Button(button_frame, text="Save & Close", command=save_voice_settings)
    save_button.pack(side=tk.RIGHT, padx=5)

    # Initial population
    populate_speaker_widgets()

    # Wait for the window to be closed
    root.wait_window(settings_window)


def open_model_settings() -> None:
    """Opens a window to select the TTS model."""
    global CURRENT_TTS_MODEL

    settings_window = tk.Toplevel(root)
    settings_window.title("TTS Model Settings")
    settings_window.transient(root)
    settings_window.grab_set()
    settings_window.resizable(False, False)

    frame = ttk.Frame(settings_window, padding="20")
    frame.pack(fill=tk.X)

    ttk.Label(frame, text="Select TTS Model:").pack(side=tk.LEFT, padx=(0, 10))

    model_var = tk.StringVar(value=CURRENT_TTS_MODEL)

    model_dropdown = ttk.Combobox(frame, textvariable=model_var, values=TTS_MODELS, state="readonly", width=15)
    model_dropdown.pack(side=tk.LEFT)

    def save_model_settings():
        global CURRENT_TTS_MODEL
        new_model = model_var.get()
        if new_model != CURRENT_TTS_MODEL:
             CURRENT_TTS_MODEL = new_model
             print(f"TTS Model set to: {CURRENT_TTS_MODEL}")
             messagebox.showinfo("Model Settings", f"TTS Model set to: {CURRENT_TTS_MODEL}", parent=settings_window)
        settings_window.destroy()

    save_button = ttk.Button(settings_window, text="Save & Close", command=save_model_settings)
    save_button.pack(pady=(0, 15))

    root.wait_window(settings_window)

# --- GUI Setup ---
def setup_gui(root_window: tk.Tk) -> Tuple[tk.Text, tk.StringVar, ttk.Progressbar, ttk.Button]:
    """Sets up the main GUI elements."""
    root_window.title("OpenAI TTS Converter")
    root_window.geometry("600x450") # Give it a default size

    # Configure grid layout
    root_window.columnconfigure(0, weight=1)
    root_window.rowconfigure(1, weight=1) # Allow text area to expand

    # --- Style ---
    style = ttk.Style()
    style.theme_use('clam') # Or 'alt', 'default', 'vista', etc. depending on OS

    # --- Main Frame ---
    main_frame = ttk.Frame(root_window, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1) # Text area row

    # --- Top Buttons Frame ---
    top_button_frame = ttk.Frame(main_frame)
    top_button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

    load_button = ttk.Button(top_button_frame, text="Load Text File", command=load_text_file)
    load_button.pack(side=tk.LEFT, padx=(0, 5))

    voice_settings_button = ttk.Button(top_button_frame, text="Voice Settings", command=open_voice_settings)
    voice_settings_button.pack(side=tk.LEFT, padx=5)

    model_settings_button = ttk.Button(top_button_frame, text="Model Settings", command=open_model_settings)
    model_settings_button.pack(side=tk.LEFT, padx=5)

    api_key_button = ttk.Button(top_button_frame, text="Set API Key", command=set_api_key)
    api_key_button.pack(side=tk.LEFT, padx=5)

    # --- Text Input Area with Scrollbar ---
    text_frame = ttk.Frame(main_frame)
    text_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
    text_frame.rowconfigure(0, weight=1)
    text_frame.columnconfigure(0, weight=1)

    text_input_widget = tk.Text(text_frame, wrap=tk.WORD, height=15, width=60, undo=True)
    text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_input_widget.yview)
    text_input_widget.configure(yscrollcommand=text_scrollbar.set)

    text_input_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    text_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    # --- Conversion Controls Frame ---
    controls_frame = ttk.Frame(main_frame)
    controls_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
    controls_frame.columnconfigure(1, weight=1) # Allow button to center/expand if needed

    format_label = ttk.Label(controls_frame, text="Output Format:")
    format_label.grid(row=0, column=0, padx=(0, 5), sticky=tk.W)

    # Note: Only MP3 is practically supported without extra libraries
    format_variable = tk.StringVar(value=OUTPUT_FORMATS[0])
    format_dropdown = ttk.Combobox(controls_frame, textvariable=format_variable,
                                   values=OUTPUT_FORMATS, state="readonly", width=7)
    format_dropdown.grid(row=0, column=1, padx=5, sticky=tk.W)

    convert_button_widget = ttk.Button(controls_frame, text="Start Conversion", command=start_conversion)
    # Place convert button towards the right
    convert_button_widget.grid(row=0, column=2, padx=(20, 0), sticky=tk.E)
    controls_frame.columnconfigure(2, weight=1) # Push button to the right

    # --- Progress Bar ---
    progress_bar_widget = Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
    progress_bar_widget.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))

    # Make main frame expandable within the root window
    root_window.rowconfigure(0, weight=1)
    root_window.columnconfigure(0, weight=1)

    return text_input_widget, format_variable, progress_bar_widget, convert_button_widget


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()

    # Call setup function
    text_input, format_var, progress_bar, convert_button = setup_gui(root)

    # Initialize OpenAI client *after* GUI is set up,
    # so potential error messages have a window to display in.
    initialize_openai_client()

    # Start the Tkinter event loop
    root.mainloop()
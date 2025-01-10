import os
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen import File
from mutagen.id3 import ID3NoHeaderError

def get_metadata_title(file_path):
    """
    Extracts title from MP3 metadata.
    Returns None if no title is found.
    """
    try:
        # Try to read ID3 tags
        audio = EasyID3(file_path)
        
        # Get title
        title = audio.get('title', [''])[0]
        
        # Return title if it exists
        if title:
            return title
            
    except (ID3NoHeaderError, Exception) as e:
        return None
    
    return None

def shorten_filename(file_path, episode_number, max_length=50):
    """
    Creates a shortened filename using title metadata when available,
    falls back to cleaned original filename if no title found.
    """
    original_name, ext = os.path.splitext(file_path.name)
    
    # Create episode number prefix
    ep_prefix = f"ep{episode_number:03d}_"
    
    # Try to get title from metadata
    title = get_metadata_title(file_path)
    
    if title:
        # Clean the metadata title
        base_name = ''.join(c for c in title if c.isalnum() or c.isspace())
    else:
        # Fall back to original filename if no metadata
        base_name = ''.join(c for c in original_name if c.isalnum() or c.isspace())
    
    # Convert spaces to underscores
    base_name = '_'.join(base_name.split())
    
    # Calculate available length
    available_length = max_length - len(ext) - len(ep_prefix)
    
    # Truncate if necessary
    if len(base_name) > available_length:
        base_name = base_name[:available_length-1] + '~'
    
    # Combine all parts
    return ep_prefix + base_name + ext

def rename_mp3_files(folder_path, start_episode=20, max_length=50):
    """
    Renames MP3 files using title metadata when available.
    """
    folder_path = Path(folder_path)
    
    # Get list of MP3 files and sort them
    mp3_files = sorted(folder_path.glob('*.mp3'))
    
    # Keep track of processed files
    processed_files = 0
    skipped_files = 0
    current_episode = start_episode
    
    print(f"Processing MP3 files in: {folder_path}")
    print(f"Starting with episode number: {start_episode}")
    
    # Process each MP3 file
    for file_path in mp3_files:
        try:
            # Generate new filename with episode number
            new_filename = shorten_filename(file_path, current_episode, max_length)
            new_path = file_path.parent / new_filename
            
            # Rename the file
            file_path.rename(new_path)
            print(f"Renamed: {file_path.name} -> {new_filename}")
            processed_files += 1
            current_episode += 1
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {str(e)}")
            skipped_files += 1
    
    # Print summary
    print("\nSummary:")
    print(f"Processed files: {processed_files}")
    print(f"Episode range: {start_episode} to {current_episode - 1}")
    print(f"Skipped files: {skipped_files}")

if __name__ == "__main__":
    # Get folder path from user
    folder_path = "C:\\Users\\Fernando\\Desktop\\New folder"
    #input("Enter the folder path containing MP3 files: ")
    start_ep = "21"
    #input("Enter starting episode number (press Enter for default 20): ")
    max_length = "100"
    #input("Enter maximum filename length (press Enter for default 50): ")

    # Use defaults if no input provided
    start_ep = int(start_ep) if start_ep.strip() else 21
    max_length = int(max_length) if max_length.strip() else 100
    
    # Confirm with user before proceeding
    print("\nWARNING: This will rename your original files. Make sure you have a backup if needed.")
    confirm = input("Do you want to continue? (y/n): ")
    
    if confirm.lower() == 'y':
        # Process the files
        rename_mp3_files(folder_path, start_ep, max_length)
    else:
        print("Operation cancelled.")
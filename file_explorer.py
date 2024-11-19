import os
from pathlib import Path

def explore_files(directory_path):
    # Convert the path to a Path object
    dir_path = Path(directory_path)
    
    try:
        # Check if directory exists
        if not dir_path.exists():
            print(f"Directory {directory_path} does not exist!")
            return
        
        # List to store files containing "prompt_"
        prompt_files = []
        
        # Walk through the directory
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / file
                try:
                    # Try to read the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'prompt_' in content:
                            prompt_files.append({
                                'path': str(file_path),
                                'name': file
                            })
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")
        
        # Print results
        if prompt_files:
            print("\nFiles containing 'prompt_':")
            for file in prompt_files:
                print(f"File: {file['name']}")
                print(f"Path: {file['path']}\n")
        else:
            print("\nNo files containing 'prompt_' were found.")
            
    except Exception as e:
        print(f"An error occurred while exploring the directory: {str(e)}")

if __name__ == "__main__":
    directory = r"H:\My Drive\blog_data\New folder"
    print(f"Exploring directory: {directory}")
    explore_files(directory)
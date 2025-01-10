import os
import json

# Define the directory containing the podcast files
directory = r"C:\Users\Fernando\Desktop\New folder"

# Initialize an empty list to hold track information
tracks = []

# Iterate through the files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".mp3"):
        # Extract metadata from the filename (assuming a naming convention)
        title = filename.replace("-", " ").replace(".mp3", "").title()
        description = f"A podcast episode titled {title}"
        url = f"https://rmindmeld.github.io/podcast_asset/{filename}"
        artwork = f"assets/podcasts/{filename.replace('.mp3', '.jpg')}"
        
        # Create a track dictionary
        track = {
            "title": title,
            "description": description,
            "url": url,
            "artwork": artwork
        }
        
        # Add the track dictionary to the list
        tracks.append(track)

# Create the final JSON structure
tracks_json = {
    "tracks": tracks
}

# Define the output JSON file path
output_file = os.path.join(directory, "tracks2.json")

# Write the JSON data to the file
with open(output_file, "w") as f:
    json.dump(tracks_json, f, indent=4)

print(f"tracks.json has been created at {output_file}")
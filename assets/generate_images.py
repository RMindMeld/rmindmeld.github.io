"""
MindMeld Image Generation Helper Script

This script helps organize and track image generation for the MindMeld website.
It reads the prompts.md file and helps manage the image generation process.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, NamedTuple

class ImagePrompt(NamedTuple):
    """Structure to hold image prompt information."""
    section: str
    title: str
    file_path: str
    prompt: str
    generated: bool = False

def parse_prompts_file(file_path: str) -> List[ImagePrompt]:
    """Parse the prompts.md file and extract image generation information."""
    prompts = []
    current_section = ""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split content into sections
    sections = re.split(r'^## ', content, flags=re.MULTILINE)[1:]
    
    for section in sections:
        lines = section.strip().split('\n')
        current_section = lines[0].strip()
        
        # Find all prompt blocks in the section
        prompt_blocks = re.finditer(r'### (.*?)\n\*\*File\*\*: (.*?)\n```\n(.*?)\n```', 
                                  section, re.DOTALL)
        
        for block in prompt_blocks:
            title = block.group(1).strip()
            file_path = block.group(2).strip()
            prompt = block.group(3).strip()
            
            # Check if image already exists
            full_path = os.path.join(os.path.dirname(file_path), file_path)
            generated = os.path.exists(full_path)
            
            prompts.append(ImagePrompt(
                section=current_section,
                title=title,
                file_path=file_path,
                prompt=prompt,
                generated=generated
            ))
    
    return prompts

def create_directory_structure(prompts: List[ImagePrompt]) -> None:
    """Create necessary directories for images."""
    for prompt in prompts:
        directory = os.path.dirname(prompt.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")

def generate_status_report(prompts: List[ImagePrompt]) -> str:
    """Generate a status report of image generation progress."""
    report = ["# Image Generation Status Report\n"]
    
    # Group by section
    sections: Dict[str, List[ImagePrompt]] = {}
    for prompt in prompts:
        if prompt.section not in sections:
            sections[prompt.section] = []
        sections[prompt.section].append(prompt)
    
    # Generate report
    total_images = len(prompts)
    generated_images = len([p for p in prompts if p.generated])
    
    report.append(f"## Overall Progress: {generated_images}/{total_images} images generated\n")
    
    for section, section_prompts in sections.items():
        report.append(f"### {section}")
        for prompt in section_prompts:
            status = "✅" if prompt.generated else "❌"
            report.append(f"- {status} {prompt.title}")
            report.append(f"  - File: {prompt.file_path}")
        report.append("")
    
    return "\n".join(report)

def main():
    """Main function to process prompts and generate reports."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_file = os.path.join(script_dir, 'prompts.md')
    
    if not os.path.exists(prompts_file):
        print(f"Error: prompts.md not found at {prompts_file}")
        return
    
    # Parse prompts
    prompts = parse_prompts_file(prompts_file)
    
    # Create directories
    create_directory_structure(prompts)
    
    # Generate and save status report
    report = generate_status_report(prompts)
    status_file = os.path.join(script_dir, 'generation_status.md')
    with open(status_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nStatus report generated: {status_file}")
    print("\nNext steps:")
    print("1. Review the status report")
    print("2. Generate missing images using DALL-E 3")
    print("3. Place generated images in their respective directories")
    print("4. Run this script again to update the status")

if __name__ == "__main__":
    main()
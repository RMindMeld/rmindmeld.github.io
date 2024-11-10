# MindMeld Image Assets

This directory contains all images used throughout the MindMeld website. The images are organized by section and are generated using DALL-E 3 based on carefully crafted prompts.

## Directory Structure

```
images/
├── blog/              # Blog post images
├── gallery/           # AI artwork gallery
├── podcasts/          # Podcast cover images
├── experiments/       # Technical diagrams
└── site/             # Site-wide assets
```

## Image Generation Process

1. **Find Prompts**
   - All image generation prompts are documented in `/assets/prompts.md`
   - Each prompt includes specific instructions for DALL-E 3
   - File paths and intended usage are clearly marked

2. **Generate Images**
   - Use the Python script `/assets/generate_images.py` to:
     - Create necessary directories
     - Track generation progress
     - Generate status reports

3. **Run the Helper Script**
```bash
python generate_images.py
```

4. **Check Status**
   - Review `generation_status.md` for:
     - Missing images
     - Generation progress
     - Section completion

## Image Specifications

### Dimensions
- Blog Headers: 1200x630px
- Gallery Images: 1024x1024px
- Podcast Covers: 1400x1400px
- Site Icons: Various sizes (see prompts.md)

### File Formats
- JPEG: Photos and complex images
- PNG: UI elements and transparency
- WebP: Performance-critical images
- SVG: Icons and simple graphics

### Optimization Guidelines
- Compress all images appropriately
- Keep file sizes under limits specified in prompts.md
- Maintain quality while optimizing for web

## Adding New Images

1. Add your prompt to `prompts.md` following the existing format
2. Run `generate_images.py` to update directories
3. Generate the image using DALL-E 3
4. Place the image in the correct directory
5. Run `generate_images.py` again to verify

## Quality Control

Before adding new images:
1. Verify dimensions match specifications
2. Ensure proper optimization
3. Check file naming follows conventions
4. Test in both light and dark modes
5. Verify accessibility (contrast, readability)

## Tools Used

- DALL-E 3: Primary image generation
- Python script: Organization and tracking
- Image optimization tools (as needed)

## Contact

For questions about image generation or to report issues:
- Check the main project README
- Use the contact form on the website
- File an issue in the repository

## Notes

- Always backup original DALL-E 3 generations
- Document any manual modifications
- Keep prompts.md updated with any changes
- Run generate_images.py regularly to track progress
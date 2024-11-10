# MindMeld Assets Directory

This directory contains all media assets used throughout the MindMeld website. The structure is organized by content type and section to maintain clarity and ease of use.

## Directory Structure

```
assets/
├── blog/              # Blog post images
│   └── thumbnails/    # Blog post thumbnail images
├── gallery/           # AI-generated artwork
│   ├── abstract/      # Abstract art pieces
│   └── landscapes/    # Landscape generations
├── experiments/       # Technical experiment visuals
│   ├── charts/        # Data visualization
│   └── screenshots/   # UI/output screenshots
└── site/             # Site-wide assets
    ├── favicon/       # Favicon files
    └── icons/        # UI icons and buttons
```

## Naming Conventions

1. All filenames should be lowercase and use hyphens for spaces
2. Include the date for blog and experiment assets: `YYYY-MM-DD-description.jpg`
3. Include the AI model for gallery items: `model-name-description.jpg`

Examples:
- Blog: `2024-01-15-first-experiment.jpg`
- Gallery: `dalle3-abstract-emotion.jpg`
- Experiment: `2024-01-17-prompt-comparison-chart.png`

## Image Guidelines

1. **Formats**
   - JPEG: Photos and complex images
   - PNG: UI elements, charts, and screenshots
   - SVG: Icons and simple graphics
   - WebP: When optimization is critical

2. **Sizes**
   - Blog thumbnails: 800x600px
   - Gallery images: 1024x1024px
   - Experiment screenshots: Native resolution
   - Icons: 24x24px or 48x48px

3. **Optimization**
   - Compress all images appropriately
   - Use WebP format for better performance
   - Keep file sizes under 500KB when possible

## Asset Management

1. **Version Control**
   - Keep original files in a separate backup
   - Document any significant modifications
   - Use clear commit messages when updating assets

2. **Metadata**
   - Include alt text in image references
   - Document AI model and prompts for gallery items
   - Note any licensing requirements

3. **Maintenance**
   - Regularly review and remove unused assets
   - Update image formats as new standards emerge
   - Monitor total asset directory size

## Usage Notes

1. **Blog Posts**
   - Place images in `/blog/YYYY/MM/` subdirectories
   - Include both full-size and thumbnail versions
   - Use descriptive filenames

2. **Gallery**
   - Include prompt text in a companion .txt file
   - Store high-resolution originals separately
   - Group related images in collections

3. **Experiments**
   - Include data sources for charts
   - Document tool versions used
   - Save raw data when applicable

## Contributing

When adding new assets:
1. Follow the established directory structure
2. Use consistent naming conventions
3. Optimize images before committing
4. Update this README if new categories are added

## Technical Details

- Maximum file sizes:
  - Blog images: 500KB
  - Gallery images: 1MB
  - Icons: 10KB
  - Screenshots: 2MB

- Recommended tools:
  - Image optimization: ImageOptim
  - Format conversion: FFmpeg
  - Metadata editing: ExifTool

## Contact

For questions about asset management or to report issues:
- Create an issue in the repository
- Contact: [your-email@example.com]
# ffmpeg ffmpeg-6.1.1 (Major v6)

VFX Platform 2025 compatible build package for ffmpeg.

## Package Information

- **Package Name**: ffmpeg
- **Version**: ffmpeg-6.1.1
- **Major Version**: 6
- **Repository**: vfxplatform-2025/ffmpeg-6
- **Description**: VFX Platform 2025 build package

## Build Instructions

```bash
rez-build -i
```

## Package Structure

```
ffmpeg/
├── ffmpeg-6.1.1/
│   ├── package.py      # Rez package configuration
│   ├── rezbuild.py     # Build script
│   ├── get_source.sh   # Source download script (if applicable)
│   └── README.md       # This file
```

## Installation

When built with `install` target, installs to: `/core/Linux/APPZ/packages/ffmpeg/ffmpeg-6.1.1`

## Version Strategy

This repository contains **Major Version 6** of ffmpeg. Different major versions are maintained in separate repositories:

- Major v6: `vfxplatform-2025/ffmpeg-6`

## VFX Platform 2025

This package is part of the VFX Platform 2025 initiative, ensuring compatibility across the VFX industry standard software stack.

# Haunted Terminal - Video Creation Guide

Complete guide to create demo videos from asciinema recordings.

## Prerequisites

Install required tools:

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install asciinema agg ffmpeg
```

## Step 1: Record Terminal Session

### Set Terminal Size (Optional but Recommended)

```bash
# Set to standard size (80 columns x 24 rows)
printf '\e[8;24;80t'

# Or larger for more content
printf '\e[8;30;100t'
```

### Record Your Session

```bash
# Start recording
asciinema rec demo.cast

# Do your demo...
# Press Ctrl+D or type 'exit' when done
```

## Step 2: Convert to Video

### Basic Conversion (Normal Speed)

```bash
# Convert .cast to GIF
agg demo.cast demo.gif

# Convert GIF to MP4 for iMovie
ffmpeg -i demo.gif -vf "scale=1280:720" -pix_fmt yuv420p demo.mp4
```

### Speed Up Video (Recommended for Demos)

```bash
# 2x speed (recommended)
agg --speed 2 demo.cast demo-2x.gif
ffmpeg -i demo-2x.gif -vf "scale=1280:720" -pix_fmt yuv420p demo-2x.mp4

# 3x speed (faster)
agg --speed 3 demo.cast demo-3x.gif
ffmpeg -i demo-3x.gif -vf "scale=1280:720" -pix_fmt yuv420p demo-3x.mp4

# 4x speed (very fast)
agg --speed 4 demo.cast demo-4x.gif
ffmpeg -i demo-4x.gif -vf "scale=1280:720" -pix_fmt yuv420p demo-4x.mp4
```

### Custom Dimensions

```bash
# 1080p (Full HD)
agg demo.cast demo.gif
ffmpeg -i demo.gif -vf "scale=1920:1080" -pix_fmt yuv420p demo-1080p.mp4

# 720p (HD)
agg demo.cast demo.gif
ffmpeg -i demo.gif -vf "scale=1280:720" -pix_fmt yuv420p demo-720p.mp4

# 4K
agg demo.cast demo.gif
ffmpeg -i demo.gif -vf "scale=3840:2160" -pix_fmt yuv420p demo-4k.mp4
```

### With Padding (if content is cut off)

```bash
# Add black padding to fit content
agg demo.cast demo.gif
ffmpeg -i demo.gif -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" -pix_fmt yuv420p demo-padded.mp4
```

## Step 3: Speed Up Existing MP4 (Alternative)

If you already have an MP4 and want to speed it up:

```bash
# 2x speed
ffmpeg -i demo.mp4 -filter:v "setpts=0.5*PTS" demo-2x.mp4

# 3x speed
ffmpeg -i demo.mp4 -filter:v "setpts=0.33*PTS" demo-3x.mp4

# 4x speed
ffmpeg -i demo.mp4 -filter:v "setpts=0.25*PTS" demo-4x.mp4
```

## Step 4: Import to iMovie

1. Open iMovie
2. Create New Project
3. Click "Import Media"
4. Select your `.mp4` file
5. Drag to timeline
6. Add voiceover, titles, transitions, etc.

### Speed Up in iMovie (Alternative)

1. Select the clip in timeline
2. Click speedometer icon (or press `Cmd+R`)
3. Choose "Fast"
4. Adjust slider (2x, 4x, 8x, 20x)

## Complete Workflow Example

```bash
# 1. Set terminal size
printf '\e[8;30;100t'

# 2. Record
asciinema rec haunted-demo.cast

# 3. Convert with 2x speed
agg --speed 2 haunted-demo.cast haunted-demo.gif

# 4. Convert to MP4
ffmpeg -i haunted-demo.gif -vf "scale=1280:720" -pix_fmt yuv420p haunted-demo.mp4

# 5. Clean up GIF
rm haunted-demo.gif

# 6. Move to Desktop
mv haunted-demo.mp4 ~/Desktop/

# Done! Import into iMovie
```

## One-Liner Commands

### Quick Convert (Normal Speed)

```bash
agg demo.cast demo.gif && ffmpeg -i demo.gif -vf "scale=1280:720" -pix_fmt yuv420p demo.mp4 && rm demo.gif
```

### Quick Convert (2x Speed)

```bash
agg --speed 2 demo.cast demo.gif && ffmpeg -i demo.gif -vf "scale=1280:720" -pix_fmt yuv420p demo-2x.mp4 && rm demo.gif
```

### Quick Convert (3x Speed)

```bash
agg --speed 3 demo.cast demo.gif && ffmpeg -i demo.gif -vf "scale=1280:720" -pix_fmt yuv420p demo-3x.mp4 && rm demo.gif
```

## Troubleshooting

### "width not divisible by 2" Error

Use scale filter to fix:

```bash
ffmpeg -i demo.gif -vf "scale=1280:720" -pix_fmt yuv420p demo.mp4
```

### Content Cut Off

Re-record with smaller terminal or add padding:

```bash
ffmpeg -i demo.gif -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" -pix_fmt yuv420p demo.mp4
```

### Video Too Slow

Speed up with agg:

```bash
agg --speed 2 demo.cast demo.gif
```

Or with ffmpeg:

```bash
ffmpeg -i demo.mp4 -filter:v "setpts=0.5*PTS" demo-2x.mp4
```

### Find Your Files

```bash
# Find all .cast files
find ~ -name "*.cast" -type f 2>/dev/null

# Find all .mp4 files
find ~ -name "*.mp4" -type f 2>/dev/null

# List files in current directory
ls -la *.cast *.gif *.mp4
```

## Tips for Best Results

1. **Terminal Size**: Use 80x24 or 100x30 for best compatibility
2. **Font Size**: Increase terminal font size for readability
3. **Speed**: 2-3x speed works best for demos
4. **Resolution**: 1280x720 (720p) is perfect for most demos
5. **Clean Up**: Delete .gif files after conversion to save space
6. **Test**: Watch the MP4 before importing to iMovie

## Voiceover with ElevenLabs

1. Go to elevenlabs.io
2. Paste your script from `DEMO_VOICEOVER_SCRIPT.txt`
3. Select German voice
4. Generate and download MP3
5. Import MP3 into iMovie
6. Sync with video using timestamps from `DEMO_VIDEO_TIMESTAMPS.md`

## Quick Reference

| Command | Purpose |
|---------|---------|
| `asciinema rec file.cast` | Record terminal |
| `agg file.cast file.gif` | Convert to GIF |
| `agg --speed 2 file.cast file.gif` | Convert with 2x speed |
| `ffmpeg -i file.gif -vf "scale=1280:720" -pix_fmt yuv420p file.mp4` | GIF to MP4 |
| `ffmpeg -i file.mp4 -filter:v "setpts=0.5*PTS" file-2x.mp4` | Speed up MP4 |

---

**Need help?** Check the troubleshooting section or re-record with adjusted settings.

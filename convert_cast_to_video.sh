#!/bin/bash
# Convert asciinema .cast file to MP4 for iMovie

if [ $# -eq 0 ]; then
    echo "Usage: ./convert_cast_to_video.sh input.cast [output.mp4]"
    exit 1
fi

INPUT=$1
OUTPUT=${2:-output.mp4}
TEMP_GIF="${INPUT%.cast}.gif"

echo "Converting $INPUT to video..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "Using Docker to convert to GIF..."
    docker run --rm -v $PWD:/data asciinema/asciicast2gif "$INPUT" "$TEMP_GIF"
elif command -v asciicast2gif &> /dev/null; then
    echo "Using asciicast2gif to convert to GIF..."
    asciicast2gif "$INPUT" "$TEMP_GIF"
else
    echo "Error: Neither Docker nor asciicast2gif found."
    echo "Install with: npm install -g asciicast2gif"
    echo "Or use Docker: docker pull asciinema/asciicast2gif"
    exit 1
fi

# Check if ffmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg not found. Install with: brew install ffmpeg"
    exit 1
fi

echo "Converting GIF to MP4..."
ffmpeg -i "$TEMP_GIF" -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$OUTPUT" -y

echo "Cleaning up temporary GIF..."
rm "$TEMP_GIF"

echo "Done! Video saved to: $OUTPUT"
echo "You can now import this into iMovie."

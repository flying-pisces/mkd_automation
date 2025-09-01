#!/bin/bash

# MKD Automation Linux Builder
# Builds standalone Linux executables using Docker

set -e  # Exit on any error

echo "🐧 MKD Automation Linux Builder"
echo "================================"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    echo "Please install Docker and try again."
    exit 1
fi

# Create output directory
OUTPUT_DIR="$(pwd)/release_linux"
mkdir -p "$OUTPUT_DIR"

echo "📦 Building Docker image for Ubuntu 22.04..."

# Build Docker image
docker build -f docker/Dockerfile.ubuntu22 -t mkd-automation-linux-builder .

echo "🔨 Running Linux build in container..."

# Run build in container
docker run --rm \
    -v "$OUTPUT_DIR:/output" \
    -v "$(pwd):/app" \
    -w /app \
    mkd-automation-linux-builder

echo "✅ Linux build complete!"
echo "📁 Linux executables available in: $OUTPUT_DIR"

# Show results
if [ -d "$OUTPUT_DIR" ] && [ "$(ls -A $OUTPUT_DIR)" ]; then
    echo ""
    echo "📦 Generated files:"
    ls -la "$OUTPUT_DIR"
    
    # Calculate total size
    TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | cut -f1)
    echo ""
    echo "📈 Total size: $TOTAL_SIZE"
    echo "🚀 Ready for Linux distribution!"
else
    echo "⚠️  No output files generated"
    exit 1
fi
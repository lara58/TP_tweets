#!/bin/bash

# Fix Debian Stretch repositories for archived versions
echo "Fixing Debian repositories for archived version..."

# Update sources.list to use archive.debian.org
cat > /etc/apt/sources.list <<EOF
deb http://archive.debian.org/debian stretch main
deb http://archive.debian.org/debian-security stretch/updates main
deb http://archive.debian.org/debian stretch-updates main
EOF

# Update package lists without checking for expiration
apt-get update -o Acquire::Check-Valid-Until=false

# Install Python 3 and pip
echo "Installing Python 3 and pip..."
apt-get install -y python3 python3-pip

# Install TextBlob for sentiment analysis
echo "Installing TextBlob..."
pip3 install textblob
python3 -m textblob.download_corpora lite

echo "Environment setup complete!"

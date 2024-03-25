#!/bin/bash
if ! command -v pip &> /dev/null
then
    echo "pip could not be found. Please ensure Python and pip are installed."
    exit 1
fi

# required packages.
PACKAGES=(
    requests
    urllib3
    ip2geotools
    sqlite3
    platform
    psutil
    win32crypt
    cryptography
    shlex
)

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install the Python packages
for pkg in "${PACKAGES[@]}"; do
    echo "Installing $pkg..."
    pip install $pkg
done

echo "All packages installed."

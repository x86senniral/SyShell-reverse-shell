#!/bin/bash

# Check if an IP address is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <IP-Address>"
    exit 1
fi

# The file to be modified
FILE="SyShell_executer.py"

cp "$FILE" "$FILE.bak"

# Replace the IP address at line 26
sed -i "26s/.*/host = '$1'  # HOST MACHINE IP/" "$FILE"

echo "IP address updated in $FILE."

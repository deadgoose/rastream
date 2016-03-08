#!/bin/bash

if hash pip 2>/dev/null; then
    echo "pip installed, upgrading..."
    pip install -U pip
    
else
    echo "please manually install pip"
    exit 1;
fi



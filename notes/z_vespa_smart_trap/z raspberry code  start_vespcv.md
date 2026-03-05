**One-line purpose:** raspberry pi script 
**Short summary:** use start_vespcv to start detection on raspberry pi4
**Agent:** archived

---

```sh
#!/bin/bash

# Check if credentials file exists
if [ ! -f ~/.vespcv_credentials ]; then
    echo "Warning: ~/.vespcv_credentials not found. Email functionality will be disabled."
fi

# Change to the vespCV directory
cd /home/vcv/vespcv

# Activate the virtual environment
source venv/bin/activate

# Set display for GUI
export DISPLAY=:0

# Add the project root to PYTHONPATH
export PYTHONPATH=/home/vcv/vespcv:$PYTHONPATH

# Start the application using the virtual environment's Python
/home/vcv/vespcv/venv/bin/python src/core/main.py
```

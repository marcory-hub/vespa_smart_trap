
**One-line purpose:** instruction how to make backup sd card for raspberry
**Short summary:** backup script
**Agent:** archived

---



# vespCV Backup Guide

## Overview
This guide explains how to backup your vespCV project using a USB SSD on your Raspberry Pi.

## Prerequisites
- USB SSD drive
- Raspberry Pi 4 with vespCV installed
- Basic terminal knowledge

## Backup Contents
The following items will be backed up:

### System Configurations
- Systemd service file (`/etc/systemd/system/vespcv.service`)
- Camera configuration (`/boot/config.txt`)
- System modules (`/etc/modules`)

### Project Files
- All source code in `/home/vcv/vespcv/`
- Configuration files in `config/`
- Documentation in `doc/`
- Model weights in `models/`
- Test files in `tests/`

### Excluded Items
- `data/` directory (detection images and logs)
- `venv/` directory (Python virtual environment)
- `__pycache__/` directories
- `.pyc` files
- `.DS_store` and `Thumbs.db` files

## Setup Instructions

### 1. Prepare USB SSD
```bash
# Create mount point
sudo mkdir -p /mnt/vespcv_backup

# Format SSD (if needed)
sudo mkfs.ext4 /dev/sda1  # Adjust device name as needed

# Mount SSD
sudo mount /dev/sda1 /mnt/vespcv_backup
```

### 2. Auto-mount Configuration
```bash
# Get SSD UUID
sudo blkid

# Add to /etc/fstab (replace UUID with your drive's UUID)
echo "UUID=your-uuid-here /mnt/vespcv_backup ext4 defaults,noatime 0 2" | sudo tee -a /etc/fstab
```

### 3. Create Backup Script
Create file `backup_to_usb.sh`:
```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/mnt/vespcv_backup"
PROJECT_DIR="/home/vcv/vespcv"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="vespcv_backup_$DATE"

# Create backup directory with timestamp
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup system configurations
sudo cp /etc/systemd/system/vespcv.service "$BACKUP_DIR/$BACKUP_NAME/"
sudo cp /boot/config.txt "$BACKUP_DIR/$BACKUP_NAME/"
sudo cp /etc/modules "$BACKUP_DIR/$BACKUP_NAME/"

# Backup project files (excluding data and venv)
rsync -av --exclude 'data/' \
          --exclude 'venv/' \
          --exclude '__pycache__/' \
          --exclude '*.pyc' \
          "$PROJECT_DIR/" "$BACKUP_DIR/$BACKUP_NAME/"

# Backup Python environment
source venv/bin/activate
pip freeze > "$BACKUP_DIR/$BACKUP_NAME/requirements.txt"

# Create restore script
cat > "$BACKUP_DIR/$BACKUP_NAME/restore.sh" << 'EOF'
#!/bin/bash

# Restore system configurations
sudo cp vespcv.service /etc/systemd/system/
sudo cp config.txt /boot/
sudo cp modules /etc/
sudo systemctl daemon-reload

# Restore project files
rsync -av --exclude 'data/' \
          --exclude 'venv/' \
          --exclude '__pycache__/' \
          --exclude '*.pyc' \
          ./ /home/vcv/vespcv/

# Restore Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Restore completed successfully!"
EOF

chmod +x "$BACKUP_DIR/$BACKUP_NAME/restore.sh"

echo "Backup completed successfully to $BACKUP_DIR/$BACKUP_NAME"
```

### 4. Make Script Executable
```bash
chmod +x backup_to_usb.sh
```

### 5. Optional: Set Up Automatic Backups
```bash
# Add to crontab to run daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/vcv/vespcv/backup_to_usb.sh") | crontab -
```

## Usage

### Manual Backup
```bash
./backup_to_usb.sh
```

### Restore from Backup
```bash
# Navigate to backup directory
cd /mnt/vespcv_backup/vespcv_backup_YYYYMMDD_HHMMSS

# Run restore script
./restore.sh
```

## Backup Structure
`
/mnt/vespcv_backup/
└── vespcv_backup_YYYYMMDD_HHMMSS/
├── vespcv.service
├── config.txt
├── modules
├── requirements.txt
├── restore.sh
└── [project files]


## Troubleshooting

### Common Issues
1. **USB SSD not mounting**
   - Check if drive is recognized: `lsblk`
   - Verify mount point exists: `ls /mnt/vespcv_backup`
   - Check fstab entry: `cat /etc/fstab`

2. **Permission denied**
   - Ensure script is executable: `chmod +x backup_to_usb.sh`
   - Check USB drive permissions: `ls -l /mnt/vespcv_backup`

3. **Backup fails**
   - Check available space: `df -h`
   - Verify USB drive is mounted: `mount | grep vespcv_backup`
   - Check backup script logs

## Maintenance

### Cleaning Old Backups
```bash
# List all backups
ls -l /mnt/vespcv_backup/

# Remove old backups (older than 30 days)
find /mnt/vespcv_backup/ -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

### Checking Backup Health
```bash
# Verify backup integrity
rsync -avn /home/vcv/vespcv/ /mnt/vespcv_backup/vespcv_backup_latest/

# Check backup size
du -sh /mnt/vespcv_backup/vespcv_backup_*
```

## Notes
- Always verify backups after creation
- Keep multiple backup copies for redundancy
- Test restore process periodically
- Monitor USB SSD health and space usage

## Support
For issues or questions, refer to:
- Project documentation in `doc/`
- GitHub repository: https://github.com/vespCV/vespcv


""" Python script to automate regular backups via external HDD and server upload"""
# TODO: bash instead? >.>
# TODO: Generate and add package list and basic system info to sync

import re                       # Regex for str parsing
import subprocess               # Executes OS functions
from datetime import datetime   # Handles dir_date creation
from pathlib import Path        # Handles paths nicer
from typing import List         # Handles lists nicer

# GLOBALS
BACKUP_DIRECTORIES: List[Path] = [Path("/etc/"), Path("/home/schark/"]
BACKUP_DESTINATION: Path = Path("/mnt/backup/")
BACKUP_UUID: Path = Path("e2408718-ac56-4d92-a4e3-4a775b60b347")
UPLOAD_SERVER: str = "root@schark.online"
UPLOAD_DIR: Path = Path("/samurai-backup")
UPLOAD_DESTINATION: Path = Path(f"{UPLOAD_SERVER}:{UPLOAD_DIR}")
LOGFILE: Path = Path(f"/home/schark/BACKUP_{datetime.today().strftime('%Y-%m-%d')}.log")

IGNORE_LIST: List[Path] = [Path("*cache*"), Path("*Cache*"), Path("*.config/discord*"), Path("*.dbus*"), Path("*.fontconfig*"), Path("*.java*"), Path("*.local*"), Path("*.mozilla*"), Path("*.steam*"), Path("*.thunderbird*"), Path("*.var*"), Path("*/videos/*")]

def _logger(msg: str):
    print(f"\n[Backup] {msg}")
    with open(LOGFILE, 'a+') as file:
        file.write(f"\n[Backup] {msg}")

_logger("Starting logging service...")

# ensure /mnt/backup is mounted
_logger(f"Checking that {BACKUP_DESTINATION} is mounted...")
try:
    subprocess.run(['findmnt', '-rn', '-S', BACKUP_UUID, BACKUP_DESTINATION], check=True)
except subprocess.CalledProcessError:
    _logger(f"{BACKUP_DESTINATION} is not mounted. Attempting to mount...")
    subprocess.run(['mount', f'UUID={BACKUP_UUID}', BACKUP_DESTINATION])

# check storage use of BACKUP_DESTINATION
_logger(f"Checking disk usage of {BACKUP_DESTINATION}...")
output = subprocess.run(['df', BACKUP_DESTINATION, '--output=pcent'], capture_output=True, text=True)
percent = int(re.findall(r'\d+', output.stdout.strip().split('\n')[1])[0])
if percent >= 90:
    _logger(f"Disk usage >90%! Cleaning oldest backup...")
    output = subprocess.run(['ls', BACKUP_DESTINATION], capture_output=True, text=True)
    oldest = Path(BACKUP_DESTINATION / output.stdout.strip().split('\n')[0])
    subprocess.run(['rm', '-rf', oldest])
    _logger(f"{output} has been deleted from the system.")
    
# rsync /etc/* and /home/schark/* to /mnt/backup/{date}
_logger(f"Syncing the following directories: {BACKUP_DIRECTORIES}")
date_dir = Path(BACKUP_DESTINATION / datetime.today().strftime('%Y-%m-%d'))
with open("/home/schark/ignore-list", "w+") as file:
    for path in IGNORE_LIST:
       file.write(f"{path}\n") 
try:
    _logger(f"Syncing with drive {date_dir}...")
    for path in BACKUP_DIRECTORIES:
        subprocess.run(['rsync', '-aH', '--progress', '--exclude-from=/home/schark/ignore-list', path, date_dir], text=True)
except subprocess.CalledProcessError:
    raise Exception(f"Error in syncing!")

# change ownership and umount
_logger(f'Changing ownership on drive...')
subprocess.run(['chown', 'schark', '-R', date_dir])
subprocess.run(['chgrp', 'schark', '-R', date_dir])
_logger(f'Unmounting drive...')
subprocess.run(['umount', BACKUP_DESTINATION])

# rsync /etc/* and /home/schark/* to root@schark.online:/samurai-backup/{$DATE}
date_dir = Path(UPLOAD_DESTINATION / datetime.today().strftime('%Y-%m-%d'))
try:
    _logger(f"Uploading to the server {date_dir}...")
    for path in BACKUP_DIRECTORIES:
        # NOTE: It is important we run this as root, as we have a special ssh key configured to complete
        # this command without need for an additional password entry
        subprocess.run(['rsync', '-aH', '--progress', '--exclude-from=/home/schark/ignore-list', path, date_dir], text=True)
except subprocess.CalledProcessError:
    raise Exception(f"Error in uploading!")

# delete old backup from root@schark.online:/samurai-backup
def _run_ssh_command(cmd):
    try:
        return subprocess.run(['ssh', UPLOAD_SERVER, cmd], capture_output=True, text=True, check=True)
    except:
        raise Exception(f"Failed ssh command [{cmd}]")

uploaded_backups = _run_ssh_command(f'ls {UPLOAD_DIR}')
parse_backups = uploaded_backups.stdout.strip().split('\n')
if len(parse_backups) > 1:
    old_backup = Path(UPLOAD_DIR / parse_backups[0])
    _logger(f'Deleting old backup {old_backup}')
    _run_ssh_command(f'rm -rf {old_backup}')

# clean up uneeded files
_logger(f'Cleaning up ignore-list...')
subprocess.run(['rm', '/home/schark/ignore-list'])

_logger('Backup successful!')
_logger('Awaiting manual termination...\n')
while True:
    continue


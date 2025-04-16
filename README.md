# Scripts for MaxPatrol VM

## sanitmpvmlogs.py

### About

When you export logs from MaxPatrol VM 27.2 using the diagnostic tool for troubleshooting, it leaks all passwords in clear text.

This script recursively iterates through the directory and removes those passwords.

The script might not be 100% accurate in detecting every password, as the vendor often changes internal components in MaxPatrol and new password strings might appear in future versions.
However, it's always a good idea to double-check using grep in the CLI — just in case.

Tested with MaxPatrol VM 27.2 logs on Astra Linux. Requires Python 3.x.

### Things to remember
- Do not run as root
- Check which directory you supply

### Usage
Be careful: this script makes permanent changes to all matching strings based on regex patterns, in all files within the specified directory recursively.

```bash
python3 sanitmpvmlogs.py --logs ./troubleshoot_dir
```

- - -
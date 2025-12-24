# Installation Guide

## Quick Install (Recommended)

Run the installer script to make the tools available from anywhere:

```bash
cd /Users/darshit.pipariya/Developer/json_diff_tool
./install.sh
```

This will create symlinks in `/usr/local/bin` so you can use the commands from any directory.

## Commands

After installation, you can use:

### `jcompare` - Compare JSON files

```bash
# JSON format (default)
jcompare file1.json file2.json -o report.json

# Text format (human-readable)
jcompare file1.json file2.json --format text -o report.txt

# From anywhere
cd ~/Documents
jcompare /path/to/file1.json /path/to/file2.json -o diff.json
```

### `jfetch` - Fetch JSON from curl commands

```bash
# Fetch from curl command file
jfetch -c curl_command.txt -o response.json

# Fetch from inline curl
jfetch --curl "curl 'https://api.example.com/data'" -o response.json
```

## Manual Installation

If you prefer not to use the installer, you can:

1. **Add to PATH** - Add this directory to your PATH in `~/.zshrc`:
   ```bash
   export PATH="$PATH:/Users/darshit.pipariya/Developer/json_diff_tool"
   ```

2. **Use directly** - Run with full path:
   ```bash
   /Users/darshit.pipariya/Developer/json_diff_tool/jcompare file1.json file2.json
   ```

## Uninstall

To remove the commands:

```bash
sudo rm /usr/local/bin/jcompare
sudo rm /usr/local/bin/jfetch
```

## Help

For detailed usage information:

```bash
jcompare --help
jfetch --help
```

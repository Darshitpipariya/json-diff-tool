# JSON Comparison Tools

A set of Python scripts to fetch JSON responses from APIs and compare them for differences.

## Tools

### 1. fetch_from_curl.py (RECOMMENDED)
**The easiest way!** Parse curl commands directly from your browser's network tab.

**Features:**
- Parse complete curl commands
- Automatically extracts URL, method, headers, and data
- Supports both inline curl commands and curl command files
- No manual parameter entry needed

**Usage:**
```bash
# From a curl command string
python3 fetch_from_curl.py --curl "curl 'https://api.example.com/data' -H 'Authorization: Bearer token'" --output response.json

# From a file containing the curl command (EASIEST)
python3 fetch_from_curl.py --curl-file curl_command.txt --output response.json
```

**Workflow:**
1. Open your browser's Network tab
2. Make the request you want to capture
3. Right-click on the request → Copy → Copy as cURL
4. Save it to a file (e.g., `curl_command.txt`)
5. Run: `python3 fetch_from_curl.py --curl-file curl_command.txt --output response1.json`

### 2. fetch_response.py
Fetch JSON responses from HTTP endpoints (manual parameter entry).

**Features:**
- GET and POST requests
- Custom headers support (authentication, etc.)
- JSON data for POST requests
- Error handling for network and JSON issues

**Usage:**
```bash
# GET request
python3 fetch_response.py --url "https://api.example.com/data" --output response1.json

# POST request with data
python3 fetch_response.py --url "https://api.example.com/data" \
  --method POST \
  --data '{"key": "value"}' \
  --output response2.json

# POST with authentication headers
python3 fetch_response.py --url "https://api.example.com/data" \
  --method POST \
  --data '{"key": "value"}' \
  --headers '{"Authorization": "Bearer YOUR_TOKEN"}' \
  --output response3.json
```

### 3. json_comparator.py
Compare two JSON files and report all differences.

**Features:**
- Deep nested comparison
- Identifies missing keys in either file
- Detects type mismatches
- Finds value differences
- Handles large files efficiently
- **Save results to file**

**Usage:**
```bash
# Print to console (text format)
python3 json_comparator.py file1.json file2.json

# Save to file (text format, RECOMMENDED for human reading)
python3 json_comparator.py file1.json file2.json --output report.txt

# Save as JSON (RECOMMENDED for programmatic processing)
python3 json_comparator.py file1.json file2.json --format json -o report.json

# Adjust ID search depth for very nested structures
python3 json_comparator.py file1.json file2.json -o report.txt --max-depth 10
```

**Output Categories:**
- **Missing in File 2**: Keys present in file1 but not in file2
- **Missing in File 1**: Keys present in file2 but not in file1
- **Type Mismatches**: Same key, different data types
- **Value Mismatches**: Same key and type, different values

## Example Workflow

### Quick Start (Using curl commands)

```bash
# Step 1: Copy your first request as curl from browser
# Save it to curl_command1.txt

# Step 2: Fetch first response
python3 fetch_from_curl.py --curl-file curl_command1.txt --output response1.json

# Step 3: Make changes to your request (modify parameters, etc.)
# Copy the new curl command and save to curl_command2.txt

# Step 4: Fetch second response
python3 fetch_from_curl.py --curl-file curl_command2.txt --output response2.json

# Step 5: Compare responses
python3 json_comparator.py response1.json response2.json -o comparison_report.txt
```

### Manual Method (Using fetch_response.py)

```bash
# Step 1: Fetch first response
python3 fetch_response.py \
  --url "https://api.example.com/endpoint" \
  --method POST \
  --data '{"param": "value1"}' \
  --headers '{"Authorization": "Bearer TOKEN"}' \
  --output response1.json

# Step 2: Fetch second response
python3 fetch_response.py \
  --url "https://api.example.com/endpoint" \
  --method POST \
  --data '{"param": "value2"}' \
  --headers '{"Authorization": "Bearer TOKEN"}' \
  --output response2.json

# Step 3: Compare responses
python3 json_comparator.py response1.json response2.json
```

## Sample Output

```
================================================================================
JSON COMPARISON REPORT
================================================================================
File 1: test1.json
File 2: test2.json
================================================================================

Total differences found: 10

────────────────────────────────────────────────────────────────────────────────
MISSING IN FILE 2 (2 items)
────────────────────────────────────────────────────────────────────────────────
  Path:  root['score']
  Value: 95.5

  Path:  root['metadata']['preferences']['language']
  Value: en

────────────────────────────────────────────────────────────────────────────────
TYPE MISMATCHES (1 items)
────────────────────────────────────────────────────────────────────────────────
  Path:   root['id']
  File 1: int = 1
  File 2: str = 1

────────────────────────────────────────────────────────────────────────────────
VALUE MISMATCHES (4 items)
────────────────────────────────────────────────────────────────────────────────
  Path:   root['tags'][1]
  File 1: python
  File 2: javascript
```

## Requirements

- Python 3.6+
- No external dependencies (uses standard library only)

## Notes

- **Smart Array Comparison**: Arrays of objects are automatically matched by ID fields found at **any depth** (searches for `id`, `_id`, `ID`, `identifier`, `key`, `uuid`)
- **Unlimited Depth by Default**: Searches through all nesting levels with circular reference protection
- **Configurable Depth**: Use `--max-depth N` to limit search depth if needed for performance
- **Structure-agnostic**: Works with any JSON structure - no need to know the schema in advance
- **Fallback to Index**: Arrays without ID fields are compared by index position
- Large values are truncated in the output for readability
- Both scripts include comprehensive error handling

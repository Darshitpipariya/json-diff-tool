# Quick Start Guide

## Comparing Two API Responses

### Step 1: Get Your First Response

1. Open your browser and go to your application
2. Open Developer Tools (F12) → Network tab
3. Make the API request you want to capture
4. Find the request in the Network tab
5. Right-click → Copy → **Copy as cURL**
6. Save it to a file:
   ```bash
   # Create a file called curl1.txt and paste the curl command
   ```

7. Fetch the response:
   ```bash
   python3 fetch_from_curl.py --curl-file curl1.txt --output response1.json
   ```

### Step 2: Get Your Second Response

1. Make changes to your request (change parameters, filters, etc.)
2. Repeat the same process:
   - Copy as cURL
   - Save to `curl2.txt`
   - Fetch:
     ```bash
     python3 fetch_from_curl.py --curl-file curl2.txt --output response2.json
     ```

### Step 3: Compare

```bash
# JSON format (default, easy to process programmatically)
python3 json_comparator.py response1.json response2.json -o comparison_report.json

# Or text format for human reading
python3 json_comparator.py response1.json response2.json --format text -o comparison_report.txt
```

The report will be saved in your chosen format for easy review or processing.

## What You'll See

The comparison will show:
- ✓ **Missing keys** - Fields present in one response but not the other
- ✓ **Type mismatches** - Same field, different data types (e.g., `"1"` vs `1`)
- ✓ **Value differences** - Same field, different values
- ✓ **Exact paths** - Shows you exactly where in the nested structure the difference is

## Example Output

```
================================================================================
JSON COMPARISON REPORT
================================================================================
Total differences found: 10

────────────────────────────────────────────────────────────────────────────────
MISSING IN FILE 2 (2 items)
────────────────────────────────────────────────────────────────────────────────
  Path:  root['Categories'][0]['Subcategories'][2]
  Value: {"id": "123", "name": "Product XYZ"}

────────────────────────────────────────────────────────────────────────────────
TYPE MISMATCHES (1 items)
────────────────────────────────────────────────────────────────────────────────
  Path:   root['id']
  File 1: int = 1
  File 2: str = 1
```

## Tips

- Keep your curl command files organized (e.g., `api_v1.txt`, `api_v2.txt`)
- The comparison works with any size JSON (tested with 44MB files!)
- Use descriptive output filenames (e.g., `response_before_fix.json`, `response_after_fix.json`)

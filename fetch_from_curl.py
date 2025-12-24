#!/usr/bin/env python3
"""
Fetch JSON from a curl command - Parse curl commands and fetch responses.

This script parses curl commands (from browser network tab) and fetches the response.
"""

import argparse
import json
import re
import shlex
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def parse_curl_command(curl_command):
    """
    Parse a curl command and extract URL, method, headers, and data.
    
    Args:
        curl_command: The curl command string
        
    Returns:
        dict with url, method, headers, and data
    """
    # Remove 'curl' from the beginning and any line continuations
    curl_command = curl_command.strip()
    curl_command = re.sub(r'\\\s*\n\s*', ' ', curl_command)  # Handle line continuations
    
    # Try to parse with shlex
    try:
        parts = shlex.split(curl_command)
    except ValueError:
        # If shlex fails, try a simpler approach
        parts = curl_command.split()
    
    # Remove 'curl' if it's the first part
    if parts and parts[0] == 'curl':
        parts = parts[1:]
    
    url = None
    method = 'GET'
    headers = {}
    data = None
    
    i = 0
    while i < len(parts):
        part = parts[i]
        
        # URL (first non-flag argument or after --location)
        if not part.startswith('-') and url is None:
            url = part
            i += 1
            continue
        
        # --location or -L
        if part in ['--location', '-L']:
            i += 1
            continue
        
        # --request or -X (method)
        if part in ['--request', '-X']:
            if i + 1 < len(parts):
                method = parts[i + 1].upper()
                i += 2
            else:
                i += 1
            continue
        
        # --header or -H
        if part in ['--header', '-H']:
            if i + 1 < len(parts):
                header_line = parts[i + 1]
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    headers[key.strip()] = value.strip()
                i += 2
            else:
                i += 1
            continue
        
        # --data, --data-raw, --data-binary, -d
        if part in ['--data', '--data-raw', '--data-binary', '-d']:
            if i + 1 < len(parts):
                data = parts[i + 1]
                if method == 'GET':
                    method = 'POST'
                i += 2
            else:
                i += 1
            continue
        
        i += 1
    
    if not url:
        raise ValueError("No URL found in curl command")
    
    return {
        'url': url,
        'method': method,
        'headers': headers,
        'data': data
    }


def fetch_and_save(url, method='GET', data=None, headers=None, output_file=None):
    """
    Fetch JSON from a URL and save it to a file.
    
    Args:
        url: The URL to fetch from
        method: HTTP method (GET or POST)
        data: JSON data for POST requests (dict or string)
        headers: Custom headers (dict)
        output_file: Path to save the response
    """
    try:
        # Prepare headers
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # Ensure Content-Type is set for POST with data
        if method.upper() == 'POST' and data and 'Content-Type' not in request_headers:
            request_headers['Content-Type'] = 'application/json'
        
        # Prepare data for POST requests
        request_data = None
        if method.upper() == 'POST' and data:
            if isinstance(data, str):
                request_data = data.encode('utf-8')
            else:
                request_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = Request(url, data=request_data, headers=request_headers, method=method.upper())
        
        # Make request
        print(f"Making {method.upper()} request to: {url}")
        if request_data:
            print(f"Request data size: {len(request_data)} bytes")
        
        with urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            
            # Parse JSON to validate
            json_data = json.loads(response_data)
            
            # Save to file
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Response saved to: {output_file}")
                print(f"✓ Response size: {len(response_data)} bytes")
            else:
                # Print to stdout if no output file specified
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
            
            return json_data
            
    except HTTPError as e:
        print(f"✗ HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        try:
            error_body = e.read().decode('utf-8', errors='ignore')
            print(f"  Response: {error_body}", file=sys.stderr)
        except:
            pass
        sys.exit(1)
    except URLError as e:
        print(f"✗ URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON response: {e}", file=sys.stderr)
        print(f"  Response preview: {response_data[:500]}...", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch JSON from a curl command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From curl command
  %(prog)s --curl "curl 'https://api.example.com/data' -H 'Authorization: Bearer token'" --output response.json
  
  # From file containing curl command
  %(prog)s --curl-file curl_command.txt --output response.json
        """
    )
    
    parser.add_argument('--curl', help='Curl command as a string')
    parser.add_argument('--curl-file','-c', help='File containing the curl command')
    parser.add_argument('--output', '-o', required=True, help='Output file path to save the JSON response')
    
    args = parser.parse_args()
    
    # Get curl command
    curl_command = None
    if args.curl:
        curl_command = args.curl
    elif args.curl_file:
        try:
            with open(args.curl_file, 'r') as f:
                curl_command = f.read()
        except Exception as e:
            print(f"✗ Error reading curl file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("✗ Please provide either --curl or --curl-file", file=sys.stderr)
        sys.exit(1)
    
    # Parse curl command
    try:
        parsed = parse_curl_command(curl_command)
        print(f"Parsed URL: {parsed['url']}")
        print(f"Method: {parsed['method']}")
        print(f"Headers: {len(parsed['headers'])} header(s)")
        if parsed['data']:
            print(f"Data: {len(parsed['data'])} bytes")
        print()
    except Exception as e:
        print(f"✗ Error parsing curl command: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Fetch and save
    fetch_and_save(
        parsed['url'],
        parsed['method'],
        parsed['data'],
        parsed['headers'],
        args.output
    )


if __name__ == '__main__':
    main()

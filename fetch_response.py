#!/usr/bin/env python3
"""
HTTP Request Fetcher - Fetch JSON responses from APIs and save to files.

This script supports GET and POST requests with custom headers and data.
"""

import argparse
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


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
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        
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
        print(f"  Response: {e.read().decode('utf-8', errors='ignore')}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"✗ URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON response: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch JSON responses from APIs and save to files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # GET request
  %(prog)s --url "https://api.example.com/data" --output response.json
  
  # POST request with inline JSON
  %(prog)s --url "https://api.example.com/data" --method POST --data '{"key": "value"}' --output response.json
  
  # POST with headers
  %(prog)s --url "https://api.example.com/data" --method POST --data '{"key": "value"}' --headers '{"Authorization": "Bearer token"}' --output response.json
        """
    )
    
    parser.add_argument('--url', required=True, help='URL to fetch from')
    parser.add_argument('--method', default='GET', choices=['GET', 'POST'], help='HTTP method (default: GET)')
    parser.add_argument('--data', help='JSON data for POST requests (as string)')
    parser.add_argument('--headers', help='Custom headers as JSON string (e.g., \'{"Authorization": "Bearer token"}\')')
    parser.add_argument('--output', '-o', help='Output file path to save the JSON response')
    
    args = parser.parse_args()
    
    # Parse headers if provided
    headers = None
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in headers: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Parse data if provided
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            # If it's not valid JSON, treat it as a raw string
            data = args.data
    
    # Fetch and save
    fetch_and_save(args.url, args.method, data, headers, args.output)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
JSON Comparator - Compare two JSON files and report differences.

This script identifies:
- Missing keys (present in one file but not the other)
- Type mismatches (same key, different data types)
- Value mismatches (same key and type, different values)
"""

import argparse
import json
import sys
from typing import Any, List, Tuple


class JSONComparator:
    """Compare two JSON structures and track differences."""
    
    def __init__(self, max_id_depth: int = None):
        self.missing_in_file2 = []
        self.missing_in_file1 = []
        self.type_mismatches = []
        self.value_mismatches = []
        self.max_id_depth = max_id_depth  # Maximum depth to search for ID fields (None = unlimited)
    
    def compare(self, obj1: Any, obj2: Any, path: str = "root") -> None:
        """
        Recursively compare two JSON objects.
        
        Args:
            obj1: First JSON object
            obj2: Second JSON object
            path: Current path in the JSON structure
        """
        # Check if types match
        if type(obj1) != type(obj2):
            self.type_mismatches.append({
                'path': path,
                'type1': type(obj1).__name__,
                'type2': type(obj2).__name__,
                'value1': self._format_value(obj1),
                'value2': self._format_value(obj2)
            })
            return
        
        # Compare based on type
        if isinstance(obj1, dict):
            self._compare_dicts(obj1, obj2, path)
        elif isinstance(obj1, list):
            self._compare_lists(obj1, obj2, path)
        else:
            # Primitive types (str, int, float, bool, None)
            if obj1 != obj2:
                self.value_mismatches.append({
                    'path': path,
                    'value1': obj1,
                    'value2': obj2
                })
    
    def _compare_dicts(self, dict1: dict, dict2: dict, path: str) -> None:
        """Compare two dictionaries."""
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        
        # Find missing keys
        for key in keys1 - keys2:
            self.missing_in_file2.append({
                'path': f"{path}['{key}']",
                'value': self._format_value(dict1[key])
            })
        
        for key in keys2 - keys1:
            self.missing_in_file1.append({
                'path': f"{path}['{key}']",
                'value': self._format_value(dict2[key])
            })
        
        # Compare common keys
        for key in keys1 & keys2:
            new_path = f"{path}['{key}']"
            self.compare(dict1[key], dict2[key], new_path)
    
    def _compare_lists(self, list1: list, list2: list, path: str) -> None:
        """Compare two lists, using ID-based matching for objects with 'id' field."""
        # Check if lists contain objects with 'id' field (top-level or nested)
        id_key1 = self._find_id_key(list1)
        id_key2 = self._find_id_key(list2)
        
        if id_key1 and id_key2 and id_key1 == id_key2:
            # ID-based comparison for arrays of objects
            self._compare_lists_by_id(list1, list2, path, id_key1)
        else:
            # Index-based comparison for primitive arrays or objects without IDs
            self._compare_lists_by_index(list1, list2, path)
    
    def _find_id_key(self, lst: list) -> str:
        """
        Find the key path to use for ID-based comparison.
        Recursively searches for common ID field names at any depth.
        """
        if not lst or not isinstance(lst[0], dict):
            return None
        
        obj = lst[0]
        
        # Common ID field names to search for (case-insensitive)
        id_field_names = ['id', '_id', 'ID', 'identifier', 'key', 'uuid']
        
        # Try to find an ID field recursively
        id_path = self._search_for_id_field(obj, id_field_names, max_depth=self.max_id_depth)
        return id_path
    
    def _search_for_id_field(self, obj: dict, id_names: list, current_path: str = "", max_depth: int = None, visited: set = None) -> str:
        """
        Recursively search for ID fields in an object.
        
        Args:
            obj: The object to search
            id_names: List of field names to look for
            current_path: Current path being built
            max_depth: Maximum depth to search (None = unlimited)
            visited: Set of visited object IDs to prevent circular references
            
        Returns:
            Path to the ID field (e.g., "Category.id" or "id") or None
        """
        # Initialize visited set on first call
        if visited is None:
            visited = set()
        
        # Check for circular references
        obj_id = id(obj)
        if obj_id in visited:
            return None
        visited.add(obj_id)
        
        # Check depth limit if specified
        if max_depth is not None and max_depth <= 0:
            return None
        
        if not isinstance(obj, dict):
            return None
        
        # Check direct keys first
        for key in obj.keys():
            if key.lower() in [name.lower() for name in id_names]:
                # Found an ID field
                if current_path:
                    return f"{current_path}.{key}"
                else:
                    return key
        
        # Calculate new depth
        new_max_depth = None if max_depth is None else max_depth - 1
        
        # Recursively search nested objects
        # Prioritize single-key wrapper objects (like {'Category': {...}})
        if len(obj) == 1:
            key = list(obj.keys())[0]
            value = obj[key]
            if isinstance(value, dict):
                new_path = key if not current_path else f"{current_path}.{key}"
                result = self._search_for_id_field(value, id_names, new_path, new_max_depth, visited)
                if result:
                    return result
        
        # Search all nested dictionaries
        for key, value in obj.items():
            if isinstance(value, dict):
                new_path = key if not current_path else f"{current_path}.{key}"
                result = self._search_for_id_field(value, id_names, new_path, new_max_depth, visited)
                if result:
                    return result
        
        return None
    
    def _get_nested_value(self, obj: dict, key_path: str):
        """Get value from nested key path like 'Skunit.id'."""
        if '.' not in key_path:
            return obj.get(key_path)
        
        keys = key_path.split('.')
        value = obj
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _compare_lists_by_id(self, list1: list, list2: list, path: str, id_key: str) -> None:
        """Compare two lists of objects by matching their ID fields."""
        # Create dictionaries mapping id -> object
        dict1 = {}
        dict2 = {}
        
        for obj in list1:
            if isinstance(obj, dict):
                obj_id = self._get_nested_value(obj, id_key)
                if obj_id is not None:
                    dict1[obj_id] = obj
        
        for obj in list2:
            if isinstance(obj, dict):
                obj_id = self._get_nested_value(obj, id_key)
                if obj_id is not None:
                    dict2[obj_id] = obj
        
        ids1 = set(dict1.keys())
        ids2 = set(dict2.keys())
        
        # Find missing IDs
        for obj_id in ids1 - ids2:
            self.missing_in_file2.append({
                'path': f"{path}[{id_key}={obj_id}]",
                'value': self._format_value(dict1[obj_id])
            })
        
        for obj_id in ids2 - ids1:
            self.missing_in_file1.append({
                'path': f"{path}[{id_key}={obj_id}]",
                'value': self._format_value(dict2[obj_id])
            })
        
        # Compare objects with matching IDs
        for obj_id in ids1 & ids2:
            new_path = f"{path}[{id_key}={obj_id}]"
            self.compare(dict1[obj_id], dict2[obj_id], new_path)
    
    def _compare_lists_by_index(self, list1: list, list2: list, path: str) -> None:
        """Compare two lists by index (fallback for non-object arrays)."""
        len1, len2 = len(list1), len(list2)
        
        # Compare common indices
        for i in range(min(len1, len2)):
            new_path = f"{path}[{i}]"
            self.compare(list1[i], list2[i], new_path)
        
        # Report extra items
        if len1 > len2:
            for i in range(len2, len1):
                self.missing_in_file2.append({
                    'path': f"{path}[{i}]",
                    'value': self._format_value(list1[i])
                })
        elif len2 > len1:
            for i in range(len1, len2):
                self.missing_in_file1.append({
                    'path': f"{path}[{i}]",
                    'value': self._format_value(list2[i])
                })
    
    def _format_value(self, value: Any, max_length: int = 100) -> str:
        """Format a value for display, truncating if too long."""
        if isinstance(value, (dict, list)):
            formatted = json.dumps(value, ensure_ascii=False)
            if len(formatted) > max_length:
                return formatted[:max_length] + "..."
            return formatted
        return str(value)
    
    
    def print_json_report(self, file1_name: str, file2_name: str, output_file: str = None) -> None:
        """Print comparison report in JSON format."""
        report = {
            "summary": {
                "file1": file1_name,
                "file2": file2_name,
                "total_differences": (
                    len(self.missing_in_file2) +
                    len(self.missing_in_file1) +
                    len(self.type_mismatches) +
                    len(self.value_mismatches)
                ),
                "missing_in_file2": len(self.missing_in_file2),
                "missing_in_file1": len(self.missing_in_file1),
                "type_mismatches": len(self.type_mismatches),
                "value_mismatches": len(self.value_mismatches)
            },
            "differences": {
                "missing_in_file2": self.missing_in_file2,
                "missing_in_file1": self.missing_in_file1,
                "type_mismatches": self.type_mismatches,
                "value_mismatches": self.value_mismatches
            }
        }
        
        output = open(output_file, 'w', encoding='utf-8') if output_file else sys.stdout
        
        try:
            json.dump(report, output, indent=2, ensure_ascii=False)
            if output_file:
                print(f"\n✓ JSON comparison report saved to: {output_file}")
        finally:
            if output_file and output != sys.stdout:
                output.close()
    
    def print_report(self, file1_name: str, file2_name: str, output_file: str = None) -> None:
        """Print a formatted comparison report."""
        # Determine output destination
        output = open(output_file, 'w', encoding='utf-8') if output_file else sys.stdout
        
        try:
            print("=" * 80, file=output)
            print(f"JSON COMPARISON REPORT", file=output)
            print("=" * 80, file=output)
            print(f"File 1: {file1_name}", file=output)
            print(f"File 2: {file2_name}", file=output)
            print("=" * 80, file=output)
            
            total_differences = (
                len(self.missing_in_file2) +
                len(self.missing_in_file1) +
                len(self.type_mismatches) +
                len(self.value_mismatches)
            )
            
            if total_differences == 0:
                print("\n✓ Files are identical!\n", file=output)
                return
            
            print(f"\nTotal differences found: {total_differences}\n", file=output)
            
            # Missing in File 2
            if self.missing_in_file2:
                print(f"\n{'─' * 80}", file=output)
                print(f"MISSING IN FILE 2 ({len(self.missing_in_file2)} items)", file=output)
                print(f"{'─' * 80}", file=output)
                for item in self.missing_in_file2:
                    print(f"  Path:  {item['path']}", file=output)
                    print(f"  Value: {item['value']}", file=output)
                    print(file=output)
            
            # Missing in File 1
            if self.missing_in_file1:
                print(f"\n{'─' * 80}", file=output)
                print(f"MISSING IN FILE 1 ({len(self.missing_in_file1)} items)", file=output)
                print(f"{'─' * 80}", file=output)
                for item in self.missing_in_file1:
                    print(f"  Path:  {item['path']}", file=output)
                    print(f"  Value: {item['value']}", file=output)
                    print(file=output)
            
            # Type mismatches
            if self.type_mismatches:
                print(f"\n{'─' * 80}", file=output)
                print(f"TYPE MISMATCHES ({len(self.type_mismatches)} items)", file=output)
                print(f"{'─' * 80}", file=output)
                for item in self.type_mismatches:
                    print(f"  Path:   {item['path']}", file=output)
                    print(f"  File 1: {item['type1']} = {item['value1']}", file=output)
                    print(f"  File 2: {item['type2']} = {item['value2']}", file=output)
                    print(file=output)
            
            # Value mismatches
            if self.value_mismatches:
                print(f"\n{'─' * 80}", file=output)
                print(f"VALUE MISMATCHES ({len(self.value_mismatches)} items)", file=output)
                print(f"{'─' * 80}", file=output)
                for item in self.value_mismatches:
                    print(f"  Path:   {item['path']}", file=output)
                    print(f"  File 1: {item['value1']}", file=output)
                    print(f"  File 2: {item['value2']}", file=output)
                    print(file=output)
            
            print("=" * 80, file=output)
            
            if output_file:
                print(f"\n✓ Comparison report saved to: {output_file}")
        finally:
            if output_file and output != sys.stdout:
                output.close()


def load_json_file(filepath: str) -> Any:
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Compare two JSON files and report differences',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.json file2.json
  %(prog)s file1.json file2.json --output diff_report.txt
  %(prog)s response1.json response2.json -o comparison.txt
        """
    )
    
    parser.add_argument('file1', help='First JSON file')
    parser.add_argument('file2', help='Second JSON file')
    parser.add_argument('--output', '-o', help='Output file to save the comparison report')
    parser.add_argument('--max-depth', type=int, default=None, 
                        help='Maximum depth to search for ID fields in nested objects (default: unlimited)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format: text (human-readable) or json (machine-readable, default: text)')
    
    args = parser.parse_args()
    
    # Load JSON files
    print(f"Loading {args.file1}...")
    json1 = load_json_file(args.file1)
    
    print(f"Loading {args.file2}...")
    json2 = load_json_file(args.file2)
    
    print("Comparing files...\n")
    
    # Compare
    comparator = JSONComparator(max_id_depth=args.max_depth)
    comparator.compare(json1, json2)
    
    # Print report in requested format
    if args.format == 'json':
        comparator.print_json_report(args.file1, args.file2, args.output)
    else:
        comparator.print_report(args.file1, args.file2, args.output)


if __name__ == '__main__':
    main()

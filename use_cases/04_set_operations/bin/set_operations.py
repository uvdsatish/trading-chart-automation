#!/usr/bin/env python3
"""
Set Operations Utility - Flexible list manipulation tool
Performs set operations on multiple input lists with various format support.

Usage Examples:
    # Interactive mode
    python set_operations.py

    # Direct command with comma-separated lists
    python set_operations.py -a "apple,banana,cherry" -b "banana" -c "date,elderberry"

    # From files
    python set_operations.py -a list_a.txt -b list_b.txt -c list_c.txt --output result.txt

    # Complex operations
    python set_operations.py -a file1.txt -b file2.txt -c file3.txt -d file4.txt --operation "A-B+C-D"

    # With custom delimiter
    python set_operations.py -a "apple|banana|cherry" -b "banana" --delimiter "|"

    # Format conversion (NEW)
    python set_operations.py --convert -a list.txt --to-format comma
    python set_operations.py --convert -a "A,B,C" --to-format columnar
"""

import argparse
import sys
import re
import os
from typing import Set, List, Union, Optional, Tuple
from pathlib import Path
import json
import csv
from collections import OrderedDict

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


class SetOperationsUtility:
    """Flexible set operations utility for list manipulation"""

    def __init__(self):
        self.sets = {}
        self.verbose = False
        self.case_sensitive = True
        self.preserve_order = False
        self.remove_duplicates = True

    def parse_input(self, input_data: str, delimiter: str = None) -> Set[str]:
        """
        Parse input data in various formats

        Supports:
        - Comma-separated values
        - Columnar format (one item per line)
        - Custom delimiters
        - File paths
        - JSON arrays
        - Mixed formats
        """
        items = set()

        # Check if input is a file path
        if os.path.isfile(input_data):
            return self.read_from_file(input_data, delimiter)

        # Try to parse as JSON array
        try:
            if input_data.strip().startswith('['):
                json_data = json.loads(input_data)
                if isinstance(json_data, list):
                    items = set(str(item).strip() for item in json_data if item)
                    if not self.case_sensitive:
                        items = set(item.lower() for item in items)
                    return items
        except (json.JSONDecodeError, ValueError):
            pass

        # Auto-detect format if no delimiter specified
        if delimiter is None:
            # Smart delimiter detection: count occurrences and use the most frequent
            # Special handling: if input is a single line with commas, prefer comma over newline
            delimiter_counts = {
                ',': input_data.count(','),
                '\n': input_data.count('\n'),
                ';': input_data.count(';'),
                '\t': input_data.count('\t'),
                '|': input_data.count('|')
            }

            # If we have commas and only 0-1 newlines (single line or line with trailing newline),
            # prefer comma delimiter
            if delimiter_counts[','] > 0 and delimiter_counts['\n'] <= 1:
                delimiter = ','
            # Otherwise, use the delimiter with the most occurrences
            elif max(delimiter_counts.values()) > 0:
                delimiter = max(delimiter_counts, key=delimiter_counts.get)
            else:
                delimiter = ','  # Default to comma

        # Split by delimiter
        raw_items = input_data.split(delimiter)

        # Clean and process items
        for item in raw_items:
            cleaned = item.strip()
            # Remove quotes if present
            if cleaned and cleaned[0] in '"\'`' and cleaned[-1] in '"\'`':
                cleaned = cleaned[1:-1]

            if cleaned:  # Only add non-empty items
                if not self.case_sensitive:
                    cleaned = cleaned.lower()
                items.add(cleaned)

        return items

    def read_from_file(self, filepath: str, delimiter: str = None) -> Set[str]:
        """Read items from a file"""
        items = set()
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to detect file format
        if path.suffix.lower() == '.json':
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    items = set(str(item).strip() for item in data if item)
                elif isinstance(data, dict):
                    # Extract values from dict
                    items = set(str(v).strip() for v in data.values() if v)
            except json.JSONDecodeError:
                pass
        elif path.suffix.lower() == '.csv':
            # Handle CSV file
            import io
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                items.update(item.strip() for item in row if item.strip())
        else:
            # Plain text file
            return self.parse_input(content, delimiter)

        if not self.case_sensitive:
            items = set(item.lower() for item in items)

        return items

    def perform_operation(self, operation: str, sets_dict: dict) -> Set[str]:
        """
        Perform complex set operations

        Supports: +, -, &, |, ^, ()
        Examples: "A-B+C", "(A|B)-C", "A&B|C", etc.
        """
        # Replace set names with actual sets in the operation
        expression = operation

        # Sort by length descending to avoid replacing substrings
        set_names = sorted(sets_dict.keys(), key=len, reverse=True)

        for name in set_names:
            if name in expression:
                expression = expression.replace(name, f"sets_dict['{name}']")

        # Replace operators with Python set operations
        expression = expression.replace('+', '|')  # Union
        expression = expression.replace('&', '&')  # Intersection (already correct)
        expression = expression.replace('^', '^')  # Symmetric difference
        expression = expression.replace('-', '-')  # Difference (already correct)

        try:
            result = eval(expression, {'sets_dict': sets_dict}, {})
            if not isinstance(result, set):
                result = set(result)
            return result
        except Exception as e:
            raise ValueError(f"Invalid operation '{operation}': {e}")

    def format_output(self, items: Union[Set[str], List[str]],
                     output_format: str = 'auto',
                     delimiter: str = ',',
                     sort: bool = False) -> str:
        """
        Format output in various styles

        Formats:
        - columnar: One item per line
        - comma: Comma-separated
        - json: JSON array
        - delimiter: Custom delimiter
        - auto: Auto-detect based on input
        """
        # Convert to list for ordering
        if isinstance(items, set):
            items_list = list(items)
        else:
            items_list = items

        if sort:
            items_list.sort()

        if output_format == 'columnar' or output_format == 'column':
            return '\n'.join(items_list)
        elif output_format == 'json':
            return json.dumps(items_list, indent=2)
        elif output_format == 'comma':
            return ', '.join(items_list)
        elif output_format == 'delimiter':
            return delimiter.join(items_list)
        else:  # auto or custom
            if delimiter == '\n':
                return '\n'.join(items_list)
            else:
                return delimiter.join(items_list)

    def interactive_mode(self):
        """Interactive mode for set operations"""
        print("=" * 60)
        print("SET OPERATIONS UTILITY - Interactive Mode")
        print("=" * 60)
        print("\nThis tool performs set operations on lists.")
        print("Default operation: A - B + C (items in A, minus items in B, plus items in C)")
        print("\nInput formats supported:")
        print("  - Comma-separated: apple,banana,cherry")
        print("  - Columnar (paste multiple lines)")
        print("  - File path: /path/to/list.txt")
        print("  - JSON array: [\"apple\", \"banana\", \"cherry\"]")
        print("\nType 'end' on a new line to finish multi-line input")
        print("-" * 60)

        sets_data = {}

        # Collect Set A
        print("\n[SET A] - Base set")
        print("Enter items for Set A (required):")
        set_a_input = self.get_multiline_input()
        if not set_a_input.strip():
            print("[ERROR] Set A cannot be empty!")
            return
        sets_data['A'] = self.parse_input(set_a_input)
        print(f"  [SUCCESS] Set A: {len(sets_data['A'])} unique items")

        # Collect Set B
        print("\n[SET B] - Items to subtract from A")
        print("Enter items for Set B (press Enter to skip):")
        set_b_input = self.get_multiline_input()
        sets_data['B'] = self.parse_input(set_b_input) if set_b_input.strip() else set()
        print(f"  [SUCCESS] Set B: {len(sets_data['B'])} unique items")

        # Collect Set C
        print("\n[SET C] - Items to add to result")
        print("Enter items for Set C (press Enter to skip):")
        set_c_input = self.get_multiline_input()
        sets_data['C'] = self.parse_input(set_c_input) if set_c_input.strip() else set()
        print(f"  [SUCCESS] Set C: {len(sets_data['C'])} unique items")

        # Ask for additional sets
        print("\nDo you want to add more sets? (y/n): ", end='')
        if input().lower().startswith('y'):
            set_letter = 'D'
            while ord(set_letter) <= ord('Z'):
                print(f"\n[SET {set_letter}] - Additional set")
                print(f"Enter items for Set {set_letter} (press Enter to finish adding sets):")
                set_input = self.get_multiline_input()
                if not set_input.strip():
                    break
                sets_data[set_letter] = self.parse_input(set_input)
                print(f"  [SUCCESS] Set {set_letter}: {len(sets_data[set_letter])} unique items")
                set_letter = chr(ord(set_letter) + 1)

        # Get operation
        print("\n" + "=" * 60)
        print("OPERATION")
        print("=" * 60)
        available_sets = list(sets_data.keys())
        print(f"Available sets: {', '.join(available_sets)}")
        print("Enter operation (default: A-B+C):")
        print("  Operators: + (union), - (difference), & (intersection), ^ (symmetric diff)")
        print("  Examples: A-B+C, (A|B)-C, A&B|C")
        operation = input("> ").strip()

        if not operation:
            # Default operation based on available sets
            if 'C' in sets_data and 'B' in sets_data:
                operation = 'A-B+C'
            elif 'B' in sets_data:
                operation = 'A-B'
            else:
                operation = 'A'

        # Perform operation
        try:
            result = self.perform_operation(operation, sets_data)
        except Exception as e:
            print(f"[ERROR] Failed to perform operation: {e}")
            return

        # Output format
        print("\n" + "=" * 60)
        print("OUTPUT FORMAT")
        print("=" * 60)
        print("Choose output format:")
        print("  1. Columnar (one per line)")
        print("  2. Comma-separated")
        print("  3. JSON array")
        print("  4. Custom delimiter")
        print("  5. Copy to clipboard (if available)")
        choice = input("Enter choice (1-5, default=1): ").strip()

        if choice == '2':
            output = self.format_output(result, 'comma', sort=True)
        elif choice == '3':
            output = self.format_output(result, 'json', sort=True)
        elif choice == '4':
            delimiter = input("Enter delimiter: ")
            output = self.format_output(result, 'delimiter', delimiter=delimiter, sort=True)
        elif choice == '5' and CLIPBOARD_AVAILABLE:
            output = self.format_output(result, 'columnar', sort=True)
            pyperclip.copy(output)
            print("[SUCCESS] Result copied to clipboard!")
        else:
            output = self.format_output(result, 'columnar', sort=True)

        # Display result
        print("\n" + "=" * 60)
        print(f"RESULT ({len(result)} items)")
        print("=" * 60)
        print(output)

        # Summary
        print("\n" + "-" * 60)
        print("SUMMARY:")
        print(f"  Operation: {operation}")
        print(f"  Set A: {len(sets_data.get('A', set()))} items")
        print(f"  Set B: {len(sets_data.get('B', set()))} items")
        print(f"  Set C: {len(sets_data.get('C', set()))} items")
        for letter in sorted(sets_data.keys()):
            if letter not in ['A', 'B', 'C']:
                print(f"  Set {letter}: {len(sets_data[letter])} items")
        print(f"  Result: {len(result)} items")

        # Save option
        print("\nSave result to file? (y/n): ", end='')
        if input().lower().startswith('y'):
            filename = input("Enter filename: ").strip()
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(output)
                    print(f"[SUCCESS] Result saved to {filename}")
                except Exception as e:
                    print(f"[ERROR] Failed to save: {e}")

    def get_multiline_input(self) -> str:
        """Get multi-line input from user"""
        lines = []
        while True:
            line = input()
            if line.lower() == 'end':
                break
            if not lines and not line:  # Empty input on first line
                break
            lines.append(line)
            if not lines[-1] and len(lines) > 1:  # Empty line after content
                lines.pop()  # Remove the empty line
                break
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Flexible Set Operations Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (easiest)
  python set_operations.py

  # Simple A - B + C with comma-separated lists
  python set_operations.py -a "apple,banana,cherry" -b "banana" -c "date"

  # From files
  python set_operations.py -a list_a.txt -b list_b.txt -c list_c.txt

  # Custom operation
  python set_operations.py -a file1.txt -b file2.txt -c file3.txt --operation "(A|B)-C"

  # With custom delimiter
  python set_operations.py -a "apple|banana|cherry" -b "banana" --delimiter "|"

  # Output to file
  python set_operations.py -a list1.txt -b list2.txt --output result.txt

  # Case-insensitive comparison
  python set_operations.py -a "Apple,BANANA,Cherry" -b "banana" --ignore-case

Operators:
  +  Union (A + B means all items in A or B)
  -  Difference (A - B means items in A but not in B)
  &  Intersection (A & B means items in both A and B)
  ^  Symmetric difference (A ^ B means items in either A or B but not both)
  |  Union (same as +)
  () Grouping for complex operations
        """
    )

    parser.add_argument('-a', '--set-a', help='Set A (base set) - file path or comma-separated values')
    parser.add_argument('-b', '--set-b', help='Set B - file path or comma-separated values')
    parser.add_argument('-c', '--set-c', help='Set C - file path or comma-separated values')
    parser.add_argument('-d', '--set-d', help='Set D - file path or comma-separated values')
    parser.add_argument('-e', '--set-e', help='Set E - file path or comma-separated values')

    parser.add_argument('--operation', default='A-B+C',
                       help='Set operation to perform (default: A-B+C)')

    parser.add_argument('--delimiter', help='Input delimiter (auto-detect if not specified)')
    parser.add_argument('--output-delimiter', default=',',
                       help='Output delimiter (default: comma)')

    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--output-format', choices=['columnar', 'comma', 'json', 'auto'],
                       default='auto', help='Output format')

    parser.add_argument('--ignore-case', action='store_true',
                       help='Case-insensitive comparison')
    parser.add_argument('--sort', action='store_true',
                       help='Sort output items')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    parser.add_argument('--clipboard', action='store_true',
                       help='Copy result to clipboard')

    # Format conversion mode arguments
    conversion_group = parser.add_argument_group('Format Conversion')
    conversion_group.add_argument('--convert', action='store_true',
                                 help='Convert format without set operations (requires only -a)')
    conversion_group.add_argument('--to-format',
                                 choices=['columnar', 'comma', 'json', 'column', 'csv'],
                                 help='Output format for conversion mode')

    args = parser.parse_args()

    utility = SetOperationsUtility()
    utility.verbose = args.verbose
    utility.case_sensitive = not args.ignore_case

    # CONVERSION MODE - Handle format conversion without set operations
    if args.convert:
        if not args.set_a:
            print("[ERROR] Conversion mode requires -a (input data)", file=sys.stderr)
            sys.exit(1)

        # Parse input (auto-detect format)
        try:
            items = utility.parse_input(args.set_a, args.delimiter)
        except Exception as e:
            print(f"[ERROR] Failed to parse input: {e}", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"[INFO] Converting {len(items)} unique items", file=sys.stderr)

        # Determine output format
        output_format = args.to_format or args.output_format

        # Map format aliases
        if output_format == 'column':
            output_format = 'columnar'
        elif output_format == 'csv':
            output_format = 'comma'

        # If no format specified, auto-detect opposite of input
        if not output_format or output_format == 'auto':
            # If input looks like columnar (has newlines or is a file), default to comma
            if '\n' in args.set_a or os.path.isfile(args.set_a):
                output_format = 'comma'
                if args.verbose:
                    print("[INFO] Auto-detected: Converting to comma-separated format", file=sys.stderr)
            else:
                output_format = 'columnar'
                if args.verbose:
                    print("[INFO] Auto-detected: Converting to columnar format", file=sys.stderr)

        # Format output
        if output_format == 'columnar':
            output = utility.format_output(items, 'columnar', sort=args.sort)
        elif output_format == 'comma':
            output = utility.format_output(items, 'comma', sort=args.sort)
        elif output_format == 'json':
            output = utility.format_output(items, 'json', sort=args.sort)
        else:
            output = utility.format_output(items, 'delimiter',
                                         delimiter=args.output_delimiter,
                                         sort=args.sort)

        # Output result
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"[SUCCESS] Converted {len(items)} items to {output_format} format")
                print(f"[SUCCESS] Result saved to {args.output}")
            except Exception as e:
                print(f"[ERROR] Failed to save output: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(output)

        # Copy to clipboard if requested
        if args.clipboard:
            if CLIPBOARD_AVAILABLE:
                pyperclip.copy(output)
                print("[SUCCESS] Result copied to clipboard")
            else:
                print("[WARNING] pyperclip not installed. Install with: pip install pyperclip",
                      file=sys.stderr)

        # Exit after conversion - don't continue to set operations
        sys.exit(0)

    # If no sets provided, run interactive mode
    if not args.set_a:
        utility.interactive_mode()
        return

    # Build sets dictionary
    sets_dict = {}

    # Process provided sets
    for set_name, set_value in [('A', args.set_a), ('B', args.set_b),
                                ('C', args.set_c), ('D', args.set_d),
                                ('E', args.set_e)]:
        if set_value:
            try:
                sets_dict[set_name] = utility.parse_input(set_value, args.delimiter)
                if args.verbose:
                    print(f"[INFO] Set {set_name}: {len(sets_dict[set_name])} items")
            except Exception as e:
                print(f"[ERROR] Failed to parse Set {set_name}: {e}", file=sys.stderr)
                sys.exit(1)

    # Validate operation
    operation = args.operation.upper()

    # Check if all referenced sets exist
    import re
    referenced_sets = re.findall(r'[A-Z]', operation)
    for set_name in referenced_sets:
        if set_name not in sets_dict:
            print(f"[ERROR] Set {set_name} referenced in operation but not provided", file=sys.stderr)
            sys.exit(1)

    # Perform operation
    try:
        result = utility.perform_operation(operation, sets_dict)
    except Exception as e:
        print(f"[ERROR] Failed to perform operation: {e}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.output_format == 'columnar':
        output = utility.format_output(result, 'columnar', sort=args.sort)
    elif args.output_format == 'comma':
        output = utility.format_output(result, 'comma', sort=args.sort)
    elif args.output_format == 'json':
        output = utility.format_output(result, 'json', sort=args.sort)
    else:
        # Auto or delimiter-based
        if args.output_delimiter == '\n':
            output = utility.format_output(result, 'columnar', sort=args.sort)
        else:
            output = utility.format_output(result, 'delimiter',
                                         delimiter=args.output_delimiter,
                                         sort=args.sort)

    # Output result
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            if args.verbose:
                print(f"[SUCCESS] Result saved to {args.output}")
        except Exception as e:
            print(f"[ERROR] Failed to save output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

    # Copy to clipboard if requested
    if args.clipboard:
        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(output)
            if args.verbose:
                print("[SUCCESS] Result copied to clipboard")
        else:
            print("[WARNING] pyperclip not installed. Install with: pip install pyperclip",
                  file=sys.stderr)

    # Summary if verbose
    if args.verbose:
        print("\n" + "=" * 60, file=sys.stderr)
        print("SUMMARY:", file=sys.stderr)
        print(f"  Operation: {operation}", file=sys.stderr)
        for set_name in sorted(sets_dict.keys()):
            print(f"  Set {set_name}: {len(sets_dict[set_name])} items", file=sys.stderr)
        print(f"  Result: {len(result)} items", file=sys.stderr)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Demo script for the Set Operations Utility
Shows various usage examples and capabilities
"""

import subprocess
import sys
import json

def run_command(cmd, description):
    """Run a command and display results"""
    print("\n" + "=" * 70)
    print(f"DEMO: {description}")
    print("-" * 70)
    print(f"Command: {' '.join(cmd)}")
    print("-" * 70)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("Output:")
        print(result.stdout)
    else:
        print("Error:")
        print(result.stderr)

    return result

def main():
    python_exe = sys.executable

    print("=" * 70)
    print("SET OPERATIONS UTILITY - DEMONSTRATION")
    print("=" * 70)

    # Demo 1: Basic A - B + C operation
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "apple,banana,cherry,date,elderberry",
         "-b", "banana,date",
         "-c", "fig,grape",
         "--sort"],
        "Basic A - B + C operation with comma-separated values"
    )

    # Demo 2: Using files
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "../../examples/basic/list_a.txt",
         "-b", "../../examples/basic/list_b.txt",
         "-c", "../../examples/basic/list_c.txt",
         "--output-format", "columnar",
         "--sort"],
        "Reading from files with columnar output"
    )

    # Demo 3: Complex operation
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "1,2,3,4,5",
         "-b", "3,4,5,6",
         "-c", "6,7,8",
         "--operation", "(A|B)-C",
         "--sort"],
        "Complex operation: (A union B) minus C"
    )

    # Demo 4: Intersection
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "red,blue,green,yellow",
         "-b", "blue,green,purple,orange",
         "--operation", "A&B",
         "--output-format", "json"],
        "Finding intersection of two sets with JSON output"
    )

    # Demo 5: Symmetric difference
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "cat,dog,fish,bird",
         "-b", "dog,bird,rabbit,hamster",
         "--operation", "A^B",
         "--sort",
         "--output-format", "columnar"],
        "Symmetric difference (items in either A or B but not both)"
    )

    # Demo 6: Case-insensitive comparison
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "Apple,BANANA,Cherry,date",
         "-b", "banana,CHERRY",
         "--operation", "A-B",
         "--ignore-case",
         "--sort"],
        "Case-insensitive subtraction"
    )

    # Demo 7: Custom delimiter input
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "item1|item2|item3|item4",
         "-b", "item2|item4",
         "-c", "item5|item6",
         "--delimiter", "|",
         "--output-delimiter", "; ",
         "--sort"],
        "Custom input delimiter (pipe) and output delimiter (semicolon)"
    )

    # Demo 8: Multiple sets with complex operation
    run_command(
        [python_exe, "../../bin/set_operations.py",
         "-a", "10,20,30,40,50",
         "-b", "20,40",
         "-c", "60,70",
         "-d", "70,80",
         "-e", "90,100",
         "--operation", "((A-B)+C)-D+E",
         "--sort",
         "--verbose"],
        "Using 5 sets (A through E) with complex operation"
    )

    print("\n" + "=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print("\nTo run the interactive mode, use:")
    print("  python set_operations.py")
    print("\nFor help and all options, use:")
    print("  python set_operations.py --help")

if __name__ == "__main__":
    main()
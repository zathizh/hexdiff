#! /usr/bin/python

import colorama
from colorama import Fore, Style
import argparse
import re
import sys

colorama.init(autoreset=True)

def read_file_bytes(file_path):
    """Read a file and return its contents as a list of bytes."""
    with open(file_path, 'rb') as file:
        return list(file.read())

def colorize_diff(a, b):
    """Colorize the differences between two byte strings."""
    if a == b:
        return (a, b)
    else:
        return (Fore.RED + a + Style.RESET_ALL, Fore.GREEN + b + Style.RESET_ALL)

def strip_color_codes(text):
    """Remove color codes from a string for accurate length calculation."""
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)

def wait_for_user():
    """Wait for the user to press Enter or Spacebar to continue or 'q' to quit."""
    while True:
        print("\nPress Enter or Spacebar to continue, 'q' to quit: ", end='', flush=True)
        user_input = input().strip().lower()
        if user_input == '' or user_input == ' ':  # Enter or Spacebar
            break
        elif user_input == 'q':
            print("Quitting...")
            sys.exit(0)  # Exit the program

def compare_files(file1_path, file2_path, bytes_per_line=8, lines_per_page=20):
    """Compare two files byte by byte and print differences side by side in chunks of given bytes."""
    file1_bytes = read_file_bytes(file1_path)
    file2_bytes = read_file_bytes(file2_path)

    # Get the maximum length between the two files
    max_len = max(len(file1_bytes), len(file2_bytes))

    # Pad the shorter file with empty bytes to match the length
    file1_bytes.extend([None] * (max_len - len(file1_bytes)))
    file2_bytes.extend([None] * (max_len - len(file2_bytes)))

#    header = f"{'Offset':<10} {'File 1':<{bytes_per_line * 3}} {'File 2'}"
#    print(header)
#    print("=" * (10 + bytes_per_line * 3 + bytes_per_line * 5))  # Adjust the separator line length

    line_count = 0
    space_between_files = 3  # Adjust this value as needed

    try:
        for i in range(0, max_len, bytes_per_line):
            line1 = []
            line2 = []

            for j in range(bytes_per_line):
                if i + j < max_len:
                    byte1 = file1_bytes[i + j]
                    byte2 = file2_bytes[i + j]

                    byte1_hex = f"{byte1:02X}" if byte1 is not None else "  "
                    byte2_hex = f"{byte2:02X}" if byte2 is not None else "  "

                    colored_byte1, colored_byte2 = colorize_diff(byte1_hex, byte2_hex)

                    line1.append(colored_byte1)
                    line2.append(colored_byte2)

            # Join the byte segments and align them
            line1_str = ' '.join(line1)
            line2_str = ' '.join(line2)

            # Calculate padding needed to align the colored text
            line1_length = len(strip_color_codes(line1_str))
            line1_padded = line1_str + ' ' * (bytes_per_line * space_between_files - line1_length)

            # Print the offset along with the byte comparisons
            print(f"{i:08X} {line1_padded} {line2_str}")

            line_count += 1

            # Check if we need to wait for the user input (after a full page)
            if line_count >= lines_per_page:
                wait_for_user()
                line_count = 0

    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting...")
        sys.exit(0)  # Cleanly exit the program

if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Compare two files byte by byte and display differences side by side.")
    parser.add_argument("file1", help="Path to the first file.")
    parser.add_argument("file2", help="Path to the second file.")
    parser.add_argument("-b", "--bytes", type=int, choices=[2, 4, 8, 16, 32, 64], default=16,
                        help="Number of bytes to display per line (2, 4, 8, 16, 32 or 64). Default is 16.")
    parser.add_argument("-l", "--lines", type=int, default=38,
                        help="Number of lines to display per page before waiting for input. Default is 38.")

    args = parser.parse_args()

    # Call the compare_files function with the provided arguments
    compare_files(args.file1, args.file2, args.bytes, args.lines)


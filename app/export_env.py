import sys
import os
from pathlib import Path

def generate_exports_from_env(env_file_path='.env'):
    """Read .env file and append export commands to ~/.zshrc"""
    zshrc_path = Path.home() / '.zshrc'
    exports = []

    try:
        # First read all valid environment variables
        with open(env_file_path, 'r') as file:
            for line in file:
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Split on first '=' only
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    exports.append(f"export {key}='{value}'")

        # If we found any variables, append them to .zshrc
        if exports:
            with open(zshrc_path, 'a') as zshrc:
                zshrc.write("\n# Environment variables from .env\n")
                for export in exports:
                    zshrc.write(f"{export}\n")
            print(f"Successfully added {len(exports)} environment variables to {zshrc_path}")
            print("Please run 'source ~/.zshrc' to apply the changes")

    except FileNotFoundError:
        print(f"Error: The file '{env_file_path}' does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if os.getcwd() != "/Users/oceanheart/Documents/code/meet-ben/app":
        print("You are not in the app directory. Please run this script from the app directory.")
        sys.exit(1)
    generate_exports_from_env()

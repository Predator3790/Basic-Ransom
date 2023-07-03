# Basic Ransom

Basic Python script capable of encrypting and decrypting files using the Fernet token algorithm. To install, run: `pip3 install cryptography`

## Usage

Encrypt a file: `python3 ransom.py encrypt <FILE>`

Decrypt a file: `python3 ransom.py decrypt <FILE>`

With a directory: `python3 ransom.py {encrypt,decrypt} <DIRECTORY>`

:warning: Do not use in important directories or it could lead to system malfunctioning. To do it with a directory and its subdirectories (recursively): `python3 ransom.py {encrypt,decrypt} -r <DIRECTORY>`

The script will always try to search for a key inside the **key.key** file or it will create it there unless the key is manually specified with `python3 ransom.py {encrypt,decrypt} <PATH> -k <KEY>`. When key is specified, there are NO CHANGES to **key.key** file. Remember that the key must be [32 url-safe base64-encoded.](https://www.pythoninformer.com/python-libraries/cryptography/fernet/)

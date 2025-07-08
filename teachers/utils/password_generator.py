# utils/password_generator.py
import random
import string

def generate_password(length=10):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for _ in range(length))

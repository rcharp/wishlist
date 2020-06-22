import os
from simplecrypt import encrypt, decrypt


def encrypt_string(plaintext):
    key = 'test'
    ciphertext = encrypt(key, plaintext)
    return ciphertext


def decrypt_string(cipher):
    key = 'test'
    plaintext = decrypt(key, cipher).decode('utf-8')
    return plaintext

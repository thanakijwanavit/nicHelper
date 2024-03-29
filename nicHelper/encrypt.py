# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/encrypt.ipynb (unless otherwise specified).

__all__ = ['hashSha256', 'encryptAes', 'encryptPasswordAes', 'decryptAes', 'decryptPasswordAes']

# Cell
from Crypto.Cipher import AES
from beartype import beartype
from typing import Tuple, Optional
from hashlib import sha256

# Cell
def hashSha256(data:bytes, salt:Optional[bytes] = b'')->bytes:
  m=sha256()
  m.update(data)
  m.update(salt)
  return m.digest()

# Cell
@beartype
def encryptAes(key:bytes, data:bytes)-> Tuple[bytes,bytes]:
  '''
    note that key has to be 16 bits long
    response:
      cipherText in bytes
  '''
  cipher = AES.new(key, AES.MODE_EAX)
  ciphertext, tag = cipher.encrypt_and_digest(data)
  return ciphertext, cipher.nonce


# Cell
@beartype
def encryptPasswordAes(password:bytes, data:bytes) ->Tuple[bytes,bytes]:
  key = hashSha256(password)[:16]
  return encryptAes(key=key,data=data)

# Cell
@beartype
def decryptAes(key:bytes, ciphertext:bytes, nonce:bytes)->bytes:
  cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
  plaintext = cipher.decrypt(ciphertext)
  return plaintext

# Cell
@beartype
def decryptPasswordAes(ciphertext:bytes, password:bytes, nonce:bytes)->bytes:
  key = hashSha256(password)[:16]
  return decryptAes(key, ciphertext, nonce)

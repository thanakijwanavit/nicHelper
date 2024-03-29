# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/colab.ipynb (unless otherwise specified).

__all__ = ['saveAwsPw', 'loadAwsPw', 'setUpAws', 'setUpAws2', 'shieldStrings', 'autoSetupAws']

# Cell
from .encrypt import encryptPasswordAes, decryptPasswordAes
from beartype import beartype
from getpass import getpass
from functools import partial
from typing import Tuple, Optional
from getpass import getpass
from pathlib import Path
import subprocess, pickle, os

# Cell
@beartype
def saveAwsPw(awskey:bytes, awssecret:bytes,
              path:str = '/content/drive/MyDrive/.awskey', password:bytes = b''):
  '''
    save your aws password in your
  '''

  # encrypt with aes
  encrypt = partial(encryptPasswordAes, password)
  cryptkey, keynonce = encrypt(awskey)
  cryptsecret, secretnonce = encrypt(awssecret)

  # save file as pickle
  print(f'saving the AES encrypted credentials to {path}')
  with open (path ,'wb') as f:
    pickle.dump((cryptkey, cryptsecret, keynonce, secretnonce),f)


# Cell
@beartype
def loadAwsPw(path = '/content/drive/MyDrive/.awskey',
              password:Optional[bytes] = b'' )->Optional[Tuple[bytes,bytes]]:
  '''
    load key and secret from path
  '''
  print( f'loading password from {path}')

  with open (path, 'rb') as f:
    cryptkey, cryptsecret, keynonce, secretnonce = pickle.load(f)
  decryptedKey = decryptPasswordAes(cryptkey,password,keynonce)
  decryptedSecret = decryptPasswordAes(cryptsecret, password, secretnonce)
  return decryptedKey, decryptedSecret


# Cell
@beartype
def setUpAws(awsKey:str, awsSecret:str,
             profile:Optional[str] = None, region:str = 'ap-southeast-1')->Tuple[str,str,str]:
  '''
    this code generate a string to be executed to the shell
    you can do this with, however, its not a bad idea to check before executing

    (exec(c) for c in setUpAws(...))

    response:
      (setupKey, setupSecret, setupRegion)

  '''
  if profile:  profileParameter = f'--profile {profile} '
  else: profileParameter = ''

  setupPrefix = f'aws configure {profileParameter}'
  setupKey = f'{setupPrefix}set aws_access_key_id {awsKey}'
  setupSecret = f'{setupPrefix}set aws_secret_access_key {awsSecret}'
  setupRegion = f'{setupPrefix}set default.region {region}'
  return (setupKey, setupSecret, setupRegion)



# Cell
@beartype
def setUpAws2(awsKey:str, awsSecret:str,
             profile:Optional[str] = None, region:str = 'ap-southeast-1')->Tuple[str,str]:

  configString = f'''[{profile or 'default'}]\nregion = {region}\noutput = json'''

  credentialString =  f'''[{profile or 'default'}]\naws_access_key_id = {awsKey}\naws_secret_access_key = {awsSecret}'''
  return configString, credentialString

# Cell
def shieldStrings(strings):
  r = ''
  for line in strings.split('\n'):
    words = line.split(' ')
    r += ' '.join(words[:2] + [f'{"*" * len(words[2])}' if len(line.split(' ')) == 3 else '']) + '\n'
  return r

# Cell
@beartype
def autoSetupAws(path:str, profile:Optional[str]=None, region:str='ap-southeast-1', mockup:bool = False, password:Optional[bytes] = None):
  key, secret = loadAwsPw(path, password=password) # key and secret in bytes
  try:
    key, secret = key.decode(), secret.decode()
  except:
    print('cant decode key and secret, maybe the password is wrong')
    return

  config, creds = setUpAws2(awsKey=key,
                          awsSecret=secret,
                          profile=profile,
                          region=region)
  print('config is :', shieldStrings(config), shieldStrings(creds), sep='\n')


  # check if reunning in colab
  isColab =  'google.colab' in str(get_ipython())
  if isColab:
    print('Running on CoLab')
  else:
    print('Not running on colab')

  awsPath = f'{Path.home()}/.aws'
  print(f'awspath is {awsPath}')

  if isColab:
    print('creating a folder')
    try:
      os.mkdir(awsPath)
    except:
      print('path exist')
    awsPath = f'{Path.home()}/.aws'
    print('writing creds files')
    with open (f'{awsPath}/credentials', 'w') as f:
      f.write(creds)
    with open (f'{awsPath}/config', 'w') as f:
      f.write(config)
  else:
    print('not colab')
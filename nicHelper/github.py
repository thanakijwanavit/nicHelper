# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/github.ipynb (unless otherwise specified).

__all__ = ['githubGet', 'githubGetYaml', 'githubImportModule']

# Cell
import requests
from requests import get, Response
from beartype import beartype
from typing import Any, Optional

# Cell
@beartype
def githubGet(url:str, token:Optional[str])->Response:
  '''
    get request to github using token
    parameters:
      url:str: github raw file url
      token:str: your personal access token
    response:
      response: requests.Response: response object
  '''
  r = requests.get(url, headers = {"Authorization": f"token {token}"})
  return r

# Cell
@beartype
def githubGetYaml(url:str, token:Optional[str])->dict:
  '''
    get yaml dictionary from github using token
    parameters:
      url:str: github raw file url
      token:str: your personal access token
    response:
      response: dict: yaml dictionary
  '''
  import yaml
  r = githubGet(url, token)
  return yaml.load(r.text,Loader=yaml.FullLoader)


# Cell
@beartype
def githubImportModule(url:str, token:Optional[str], path='/tmp/inputfile', sourceName='schema')->Any:
  import imp
  r = requests.get(url, headers={'Authorization': 'token '+token})
  with open(path, 'w') as f:
    f.write(r.text)
  return imp.load_source(sourceName, path)
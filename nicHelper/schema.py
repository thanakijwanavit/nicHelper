# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/schema.ipynb (unless otherwise specified).

__all__ = ['getSchemaPath', 'validateUrl', 'getTypes', 'typeMap', 'typeMapJsonSchema']

# Cell
import jsonschema, requests, yaml
from types import SimpleNamespace

# Cell
import dpath.util
def getSchemaPath(schemaUrl:str, path:str='/', isYaml = True):
  '''
  get a nested schema from path \n
  schemaUrl: str: url of the schema \n
  path: str: path of the schema, if root then path='/' \n
  isYaml: Bool: is the schema yaml (false indicates that the schema is json), default = True
  '''
  if isYaml:
    schema = yaml.load(requests.get(schemaUrl).text, Loader= yaml.Loader)
  else:
    schema = requests.get(schemaUrl).json()
  return dpath.util.get(schema, path)

# Cell
def validateUrl(url,input_, format_ = 'json', headers = {'Cache-Control': 'no-cache'}, path = '/'):
  '''
  verifies whether the input_ is valid under the schema located at path in the url \n
  url: str: url where the schema file is located \n
  input_: the input to be validated \n
  format_: str: the format of the schema; can be 'yaml' or 'json', default = 'json' \n
  headers: dict: dictionary of HTTP headers to send with the get request to retrieve the schema \n
  path: str: path of the schema within the file, if root then path='/'
  '''
  if format_ == 'yaml':
    schema = getSchemaPath(url, path = path, isYaml = True)
  elif format_ == 'json':
    schema = getSchemaPath(url, path = path, isYaml = False)
  else:
    print('invalid schema format, using json')
    schema = requests.get(url).json()
  res = jsonschema.validate(input_,schema)
  return SimpleNamespace(**input_)

# Cell
typeMap = {'string': str, 'number': float, 'integer': int, 'object': dict, 'array': list, 'boolean': bool, 'null': None}
def getTypes(schemaUrl:str, typeMap:dict=typeMap)->dict:
  '''
  get python types from json schema \n
  schemaUrl: str: url where the schema file is located \n
  typeMap: dict: the dictionary that matches the key to its corresponding data type
  '''
  r = requests.get(schemaUrl)
  s = yaml.load(r.text, Loader=yaml.FullLoader)
  properties = s['properties']
  dtypes = {k: typeMap.get(v['type']) for k,v in properties.items()}
  return dtypes

# Cell
def typeMapJsonSchema(url:str, input_:dict = {}, typeMap:dict = typeMap, defaultType=str):
  '''
  try to map the datatype into the one specified in url of json schema. \n
  if type is not found, the defaultType is used \n
  url: str where the schema file is located \n
  typeMap: dict: the dictionary that matches the key to its corresponding data type \n
  defaultType: set the default type if a type is not specified
  '''
  typesDict = getTypes(url, typeMap=typeMap) # get dtype from schema url
  print(f'typesDict is: {typesDict}')
  convertedInput = {k: (typesDict.get(k) or defaultType)(v) for k,v in input_.items()}
  return convertedInput
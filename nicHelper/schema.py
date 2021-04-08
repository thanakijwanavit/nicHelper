# AUTOGENERATED! DO NOT EDIT! File to edit: schema.ipynb (unless otherwise specified).

__all__ = ['getSchemaPath', 'validateUrl', 'getTypes', 'typeMapJsonSchema', 'typeMap']

# Cell
import jsonschema, requests, yaml
from types import SimpleNamespace

# Cell
import dpath.util
def getSchemaPath(schemaUrl:str, path:str='/', isYaml = True):
  '''
  get a nested schema from path
  schemaUrl: str: url of the schema
  path: str: path of the schema, if root then path='/'
  isYaml: Bool: is the schema yaml (false indicates that the schema is json)
  '''
  if isYaml:
    schema = yaml.load(requests.get(schemaUrl).text, Loader= yaml.Loader)
  else:
    schema = requests.get(schemaUrl).json()
  return dpath.util.get(schema, path)

# Cell
def validateUrl(url,input_, format_ = 'json', headers = {'Cache-Control': 'no-cache'}, path = '/'):
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
  '''get python types from json schema'''
  r = requests.get(schemaUrl)
  s = yaml.load(r.text, Loader=yaml.FullLoader)
  properties = s['properties']
  dtypes = {k: typeMap.get(v['type']) for k,v in properties.items()}
  return dtypes
def typeMapJsonSchema(url:str, input_:dict = {}, typeMap:dict = typeMap, defaultType=str):
  '''
  try to map the datatype into the one specified in url of json schema.
  if type is not found, the defaultType is used
  '''
  typesDict = getTypes(url, typeMap=typeMap) # get dtype from schema url
  print(f'typesDict is: {typesDict}')
  convertedInput = {k: (typesDict.get(k) or defaultType)(v) for k,v in input_.items()}
  return convertedInput

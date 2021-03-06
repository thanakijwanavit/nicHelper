# AUTOGENERATED! DO NOT EDIT! File to edit: pynamodbAttributes.ipynb (unless otherwise specified).

__all__ = ['SchemaAttribute', 'SuperModel', 'createData']

# Cell
from pynamodb.attributes import Attribute, UnicodeAttribute, NumberAttribute
from typing import Any, Optional, Type, TypeVar
from enum import Enum
import requests, dpath.util, yaml, jsonschema, json, os, pynamodb
from pynamodb.models import Model
from datetime import datetime

# Cell
class SchemaAttribute(Attribute):
  attr_type = pynamodb.constants.STRING
  def __init__(self, schemaUrl:str, path:str = '/', isYaml=True,
               headers={'Cache-Control': 'no-cache'},
               envName = 'SCHEMA_ATTRIBUTE', **kwargs: Any) -> None:
      """
      schemaUrl:str,
      path:str = '/',
      isYaml=True,  :yaml::Bool:: whether the schema is in yaml or json
      headers={'Cache-Control': 'no-cache'},
      :path::str:: the path of the object of interest in schema, if the schema is at root then '/'
      envName::str:: the name of schema to save to the environment
      """
      super().__init__(**kwargs)
      try:
        if isYaml: # yaml schema
          schema:dict = yaml.load(requests.get(schemaUrl, headers=headers).text, Loader = yaml.FullLoader)
        else: # probably json
          schema:dict = requests.get(schemaUrl, headers).json()
      except Exception as e:
        print(f'error parsing schema {e}')
        schema:dict = {}

      self.schema = dpath.util.get(schema, path) # get to the path in schema
      os.environ[envName] = json.dumps(self.schema)

  def deserialize(self, value: str) -> dict:
    return json.loads(value)

  def serialize(self, value:dict) -> str:
    res = jsonschema.validate(value,self.schema)
    return json.dumps(value)

# Cell
class SuperModel(Model):
  id_ = UnicodeAttribute(hash_key=True)
  data = SchemaAttribute(schemaUrl='https://gist.githubusercontent.com/thanakijwanavit/e2720d091ae0cef710a49b57c0c9cd4c/raw/ed2d322eac4900ee0f95b431d0f9067a40f3e0f0/squirrelOpenApiV0.0.3.yaml', null=True)
  lastEdited = NumberAttribute()
  creationTime = NumberAttribute()

  def __repr__(self):
    return json.dumps(vars(self)['attribute_values'])

  @classmethod
  def fromDict(cls, inputDict:dict):
    return cls(data = inputDict)

  #### saving ####
  def pullOutKeys(self):
    '''
    update the keys with data: please override this function by pulling out keys

    for example
    self.orderId = self.data['orderId']
    self.ownerId = self.data['ownerId']
    self.basketId = self.data['basketId']
    '''
    print('please dont foreget to override the pullOutKeys function if needed')
    self.id_ = self.data['id']

  def recordTime(self):
    '''record last edited and creation time'''
    self.lastEdited = datetime.now().timestamp() # record last edited
    if not self.creationTime: # record creation time
      self.creationTime = datetime.now().timestamp()

  def save(self):
    '''
    please override pullOutKeys function
    see docs
    '''
    self.recordTime()
    self.pullOutKeys()

    try:
      super().save()
      return next(self.query(self.id_))
    except ValidationError as e:
      raise ValidationError(f'failed validation \n {e}')

    except Exception as e:
      raise Exception(f'error saving id {self.id_} {e}')


# Cell
from awsSchema.apigateway import Event, Response
from jsonschema import ValidationError
from typing import Optional
from .schema import validateUrl

def createData(event:dict, hashKeyName: str,mainClass:Model, schemaUrl:Optional[str] = None ,schemaFormat:str ='yaml', *args):
  '''
    create a new basket
  '''
  # parse output
  query:dict = Event.parseBody(event)

  # check schema if provided
  if schemaUrl:
    try: validateUrl(schemaUrl,format_ = schemaFormat)
    except ValidationError as e: return Response.returnSuccess(f'{e}')

  # check for key
  if hashKeyName not in query:
    return Response.returnError(message=f'missing {hashKeyName}')

  # check if object exist
  if next(mainClass.query(query[hashKeyname]),None):
    return Response.returnError(message=f'item with the same hash key exists')

  # make pynamodb object
  item:mainClass = mainClass.fromDict(query)

  # try to save
  try:
    item.save()
    return Response.returnSuccess(body=item.to_dict())

  except ValidationError as e: # error validation handle
    return Response.returnError(f'validation error \n {e}')

  except Exception as e: # error handle
    return Response.returnError(f'unknown error \n {e} \n errorString())')
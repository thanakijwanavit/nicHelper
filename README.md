# Helpers
> various helpers from nic gist


full docs here
https://thanakijwanavit.github.io/nicHelper/

```python
from nicHelper.wrappers import add_method
```

## Install

`pip install nicHelper`

# How to use

## method module

### add method to a class

```python
class A:
  pass

@add_method(A)
def printHello(self):
  print('hello')
 
A().printHello()
```

    hello


This is equivalent to 
```
class A:
  def printHello(self):
    print('hello')
  
```

## Dict utilities

### Pretty print a dict
print only the first 10 characters of dict key, works with deep nested dict

```python
from nicHelper.dictUtil import printDict
printDict({'key':'sjfhdkljhafsdlkjhdfaslkjhkljfadshklhfa', 'nestedKey':{'nestedKey2':'938023840843', 'nested3':{'nested4':'hello'}}})
```

    key : sjfhdkljha
    nestedKey
     nestedKey2 : 9380238408
     nested3
      nested4 : hello


### change all nested datetime object into timestamp for json compatibility

```python
from nicHelper.dictUtil import filterDt
from datetime import datetime

filterDt({'time': {'time2':datetime.now()}, 'hello': 'world'})
```




    {'time': {'time2': 1615312774.297602}, 'hello': 'world'}



## Exception module

```python
from nicHelper.exception import errorString
try:
  error
except:
  print(f'error is \n{errorString()}')
```

    error is 
    Traceback (most recent call last):
      File "<ipython-input-6-86083feec525>", line 3, in <module>
        error
    NameError: name 'error' is not defined
    


## Image utils

```python
from nicHelper.images import imageFromUrl, imageToS3, showImgS3, resizeImage
from s3bz.s3bz import S3
```

```python
## test variables
key = 'testCat.png'
path = '/tmp/testCat.png'
bucket = 'villa-remove-bg-small-output'
url = 'https://sites.google.com/site/funnycatmeawww/_/rsrc/1422326075261/home/6997052-funny-cat.jpg?height=675&width=1200'
```

### Resize images

```python
resizeImage(url, 400)
```




![png](docs/images/output_20_0.png)



### load image from url

```python
img = imageFromUrl(url)
type(img)
```




    PIL.JpegImagePlugin.JpegImageFile



### save Image to S3

```python
imageToS3(img, bucket, key)
S3.exist(key,bucket)
```

    saving image to villa-remove-bg-small-output/testCat.png





    True



### display image from s3

```python
## full test
showImgS3(bucket, key)
```


![png](docs/images/output_26_0.png)


## Secrets

```python
from nicHelper.secrets import getSecret
secret = getSecret(name="removeBg", region='ap-southeast-1')
```

## Shorten link with tenxor.sh

```python
from nicHelper.shortenLink import shorten
```

```python
shorten('https://www.youtube.com/watch?v=fp85zRg2cwg')
```




    'https://tenxor.sh/d3Cp'



## Schema

```python
from nicHelper.schema import getSchemaPath, validateUrl, typeMapJsonSchema
```

### Get schema from path 

```python
testSchema = 'https://gist.githubusercontent.com/thanakijwanavit/e2720d091ae0cef710a49b57c0c9cd4c/raw/ed2d322eac4900ee0f95b431d0f9067a40f3e0f0/squirrelOpenApiV0.0.3.yaml'
path = 'components/schemas/Location'
getSchemaPath(testSchema, path)
```




    {'type': 'object',
     'required': ['id',
      'type',
      'street_address',
      'city',
      'state',
      'zip',
      'capacity',
      'status'],
     'properties': {'id': {'type': 'string', 'format': 'uuid'},
      'type': {'type': 'string', 'enum': ['pick up', 'drop off', 'overnight']},
      'street_address': {'type': 'string'},
      'city': {'type': 'string'},
      'state': {'type': 'string',
       'pattern': '^(?:(A[KLRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY]))$'},
      'zip': {'type': 'string', 'pattern': '(^\\d{5}$)|(^\\d{5}-\\d{4}$)'},
      'status': {'type': 'string', 'enum': ['open', 'in use']},
      'created': {'type': 'string', 'format': 'date-time'},
      'modified': {'type': 'string', 'format': 'date-time'}}}



### Validate Url

```python
url = 'https://raw.githubusercontent.com/thanakijwanavit/villaMasterSchema/master/Product.json'
input_ = {'iprcode': 4, 'cprcode': 123 , 'oprCode': '123'}
validateUrl(url, input_)
```




    namespace(cprcode=123, iprcode=4, oprCode='123')



### Convert type to comply with json schema 

```python
url = 'https://raw.githubusercontent.com/thanakijwanavit/villaMasterSchema/dev-manual/inventory/inventory.yaml'
inv = {
                  'iprcode': '0000009',
                  'brcode': '1000',
                  'ib_cf_qty': '50',
                  'new_ib_vs_stock_cv': '27',
                  'onlineflag': True
                }
typeMapJsonSchema(url, input_=inv)
```

    typesDict is: {'iprcode': <class 'int'>, 'brcode': <class 'int'>, 'ib_cf_qty': <class 'int'>, 'new_ib_vs_stock_cv': <class 'int'>, 'onlineflag': <class 'bool'>}





    {'iprcode': 9,
     'brcode': 1000,
     'ib_cf_qty': 50,
     'new_ib_vs_stock_cv': 27,
     'onlineflag': True}



## Pynamodb

```python
from nicHelper.pynamodb import SchemaAttribute, SuperModel, createData, getData, updateData
from pynamodb.attributes import Attribute, UnicodeAttribute, NumberAttribute
from beartype import beartype
from awsSchema.apigateway import Event, Response
```

### SchemaAttribute
a class which automatically parse and check data against json schema

```SchemaAttribute(*args, **kwargs) :: Attribute```

### Supermodel
a class which add some functionalities on top of the standard pynamodb model

```python
schemaUrl = 'https://raw.githubusercontent.com/thanakijwanavit/villaMasterSchema/master/Product.json'
from typing import Any
class TestModel(SuperModel):
  class Meta:
    table_name="colab-test-sensitive-column"
    region = 'ap-southeast-1'
  data = SchemaAttribute(schemaUrl = schemaUrl, null=True)
  phoneHash = UnicodeAttribute(hash_key=True)
  
    
  # Overrides
  def pullOutKeys(self)->None:
    self.phoneHash = str(self.data.get('phoneHash') or self.data.get('iprcode') or self.data.get('id') )

  @beartype
  def toDict(self)->dict:
    return self.data
    
  @classmethod
  @beartype
  def fromDict(cls, inputDict:dict)->Any:
    return cls(data=inputDict)
    
  @beartype  
  def update(self,inputDict:dict)->None:
    self.data.update(inputDict)
```

```python
from nicHelper.exception import errorString
try:
  test = TestModel.fromDict({'iprcode': 4, 'cprcode': 123 , 'oprCode': '123', 'orderId': 123})
  test.save()
except Exception as e:
  print(e)
  print(errorString())


next(TestModel.query('1'))
```




    {"data": {"type": "pick up", "street_address": "123", "id": "123", "city": "sth", "state": "CA", "zip": "23523", "capacity": 5, "status": "open"}}



### createData
create a new row of data

```python
## lambda create function
def create (event, *args):
  body = Event.parseBody(event)
  body['id'] = body['phoneHash']
  
  event2 = Event.getInput(body)
  r = createData(event2, hashKeyName='phoneHash', mainClass=TestModel)
  if r.get('statusCode') != 200: return r
  r2 = next(TestModel.query(body['phoneHash']), None)
  if not r2: return Response.returnError('st wrong with saving, saving but didnt go through')
  return Response.returnSuccess(r2)
```

```python
schemaUrl = 'https://raw.githubusercontent.com/thanakijwanavit/villaMasterSchema/master/Product.json'
data = {'phoneHash': '123','iprcode': 4, 'cprcode': 123 , 'oprCode': '123'}
event = Event.getInput(data)
item = next(TestModel.queryId('123'), None)
print('existing item is :',item)
# delete item if exist
if item:
  print(item.delete())
create(event)
```

    existing item is : {"creationTime": 1615893836.030621, "data": {"phoneHash": "123", "iprcode": 5, "cprcode": 123, "oprCode": "1234", "id": "123"}, "lastEdited": 1615894057.181481, "phoneHash": "123"}
    {'ConsumedCapacity': {'CapacityUnits': 1.0, 'TableName': 'colab-test-sensitive-column'}}





    {'body': '{"phoneHash":"123","iprcode":4,"cprcode":123,"oprCode":"123","id":"123"}',
     'statusCode': 200,
     'headers': {'Access-Control-Allow-Headers': '*',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': '*'}}



### getData

```python
def lambdaGet(event, *args):
  query = Event.parseBody(event)
  if 'key' not in query: return Response.returnError(f'missing key')
  return getData(query['key'], TestModel)
```

```python
data = {'phoneHash': '123','iprcode': 4, 'cprcode': 123 , 'oprCode': '123'}
event = Event.getInput(data)
create(event)

lambdaGet(Event.getInput({'key': '123'}))
```




    {'body': '{"phoneHash":"123","iprcode":4,"cprcode":123,"oprCode":"123","id":"123"}',
     'statusCode': 200,
     'headers': {'Access-Control-Allow-Headers': '*',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': '*'}}



### updateData

```python
def update(event, *args):
  body = Event.parseBody(event)
  body['id'] = body['phoneHash']
  
  event2 = Event.getInput(body)
  hashKeyname = 'id'
  return updateData(event2, hashKeyName=hashKeyname, mainClass=TestModel)
```

```python
r = create(Event.getInput({'phoneHash': '123','iprcode': 5, 'cprcode': 123 , 'oprCode': '123'}))
r = update(Event.getInput({'phoneHash': '123','iprcode': 5, 'cprcode': 123 , 'oprCode': '1234'}))
lambdaGet(Event.getInput({'key':'123'}))
```




    {'body': '{"phoneHash":"123","iprcode":5,"cprcode":123,"oprCode":"1234","id":"123"}',
     'statusCode': 200,
     'headers': {'Access-Control-Allow-Headers': '*',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': '*'}}



## Timer

```python
from nicHelper.timer import Timer
```

### setting start timer

```python
timer = Timer()
timer.t0
```




    datetime.datetime(2021, 4, 16, 6, 57, 1, 236974)



### print the time between starting time and current time

```python
timer.print_time()
```

    fuction took :3.422775 s





    3.422775



### print the time between starting time and current time and reset the timer

```python
timer.print_reset()
```

    function took :0.376299 s





    0.376299



## Pd Utils

```python
import pandas as pd
from nicHelper.pdUtils import getDfHash, saveLocalCache, saveLocalHash, loadLocalHash, loadLocalCache, saveRemoteHash, saveRemoteCache, loadRemoteCache, loadRemoteHash, forceType
from nicHelper.schema import getTypes
```

```python
df = pd.DataFrame({'hello':[1,2,3,4,5,5]})
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>hello</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



### Get a hash of a pandas dataframe

```python
getDfHash(df)
```




    'da39a3ee5e6b4b0d3255bfef95601890afd80709'



### Save and load local cache and hash

```python
saveLocalCache(df,force = True)
saveLocalHash(df)
print(loadLocalHash())
loadLocalCache()
```

    da39a3ee5e6b4b0d3255bfef95601890afd80709





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>hello</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



### Save and load remote cache and hash (from S3 bucket)

```python
testKey = 'testKey'
testBucket = 'villa-clipboard'
saveRemoteCache(df, key = testKey, bucket = testBucket)
print(loadRemoteHash(testKey, testBucket))
loadRemoteCache(key = testKey, bucket = testBucket)
```

    hashKey is testKey-hash
    saving hash to s3
    saved hash da39a3ee5e6b4b0d3255bfef95601890afd80709
    loading hashkey testKey-hash
    loaded hash is da39a3ee5e6b4b0d3255bfef95601890afd80709
    da39a3ee5e6b4b0d3255bfef95601890afd80709





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>hello</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



### PandasDataFrameAttribute
pynamodb attributes for pandas dataframe

```class PandasDataFrameAttribute(Attribute)```

### forceType

```python
url = 'https://raw.githubusercontent.com/thanakijwanavit/villaMasterSchema/dev-manual/inventory/inventory.yaml'
inv = {
                  'iprcode': '0000009',
                  'brcode': '1000',
                  'ib_cf_qty': '50',
                  'new_ib_vs_stock_cv': '27',
                  'onlineflag': True
                }
getTypes(url)
```




    {'iprcode': int,
     'brcode': int,
     'ib_cf_qty': int,
     'new_ib_vs_stock_cv': int,
     'onlineflag': bool}



```python
forceType(url, pd.DataFrame([inv]))
```

    {'iprcode': <class 'int'>, 'brcode': <class 'int'>, 'ib_cf_qty': <class 'int'>, 'new_ib_vs_stock_cv': <class 'int'>, 'onlineflag': <class 'bool'>}
    iprcode               int64
    brcode                int64
    ib_cf_qty             int64
    new_ib_vs_stock_cv    int64
    onlineflag             bool
    dtype: object


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
from nicHelper.pynamodbAttributes import SchemaAttribute, SuperModel
from pynamodb.attributes import Attribute, UnicodeAttribute, NumberAttribute
from beartype import beartype
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


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    <ipython-input-14-eaf92ec0ab48> in <module>
          1 schemaUrl = 'https://raw.githubusercontent.com/thanakijwanavit/villaMasterSchema/master/Product.json'
          2 from typing import Any
    ----> 3 class TestModel(SuperModel):
          4   class Meta:
          5     table_name="colab-test-sensitive-column"


    ~/anaconda3/envs/python38/lib/python3.8/site-packages/pynamodb/models.py in __init__(self, name, bases, namespace, discriminator)
        207             if attribute.is_hash_key:
        208                 if cls._hash_keyname and cls._hash_keyname != attr_name:
    --> 209                     raise ValueError(f"{cls.__name__} has more than one hash key: {cls._hash_keyname}, {attr_name}")
        210                 cls._hash_keyname = attr_name
        211             if attribute.is_range_key:


    ValueError: TestModel has more than one hash key: id_, phoneHash


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

    name 'TestModel' is not defined
    Traceback (most recent call last):
      File "<ipython-input-15-138906ed352c>", line 3, in <module>
        test = TestModel.fromDict({'iprcode': 4, 'cprcode': 123 , 'oprCode': '123', 'orderId': 123})
    NameError: name 'TestModel' is not defined
    



    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-15-138906ed352c> in <module>
          8 
          9 
    ---> 10 next(TestModel.query('1'))
    

    NameError: name 'TestModel' is not defined


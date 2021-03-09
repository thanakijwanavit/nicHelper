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


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-5-3c042eda53ab> in <module>
          2 from datetime import datetime
          3 
    ----> 4 filterDt({'time': {'time2':datetime.now()}, 'hello': 'world'})
    

    /mnt/efs/pip/nicHelper/nicHelper/dictUtil.py in filterDt(dtDict)
         28 def filterDt(dtDict:dict):
         29   '''convert unjsonable datetime object to timestamp in the dictionary'''
    ---> 30   return {k: (filterDt(v) if type(v) == dict else v) if type(v) != datetime else v.timestamp()
         31             for k,v in dtDict.items()}
         32 


    /mnt/efs/pip/nicHelper/nicHelper/dictUtil.py in <dictcomp>(.0)
         28 def filterDt(dtDict:dict):
         29   '''convert unjsonable datetime object to timestamp in the dictionary'''
    ---> 30   return {k: (filterDt(v) if type(v) == dict else v) if type(v) != datetime else v.timestamp()
         31             for k,v in dtDict.items()}
         32 


    NameError: name 'datetime' is not defined


## Exception module

```python
from nicHelper.exception import errorString
try:
  error
except:
  print(f'error is \n{errorString()}')
```

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

### load image from url

```python
img = imageFromUrl(url)
type(img)
```

### save Image to S3

```python
imageToS3(img, bucket, key)
S3.exist(key,bucket)
```

### display image from s3

```python
## full test
showImgS3(bucket, key)
```

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

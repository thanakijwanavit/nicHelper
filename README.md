# Helpers
> various helpers from nic gist


from nicHelper.

## Install

`pip install nicHelper`

## How to use

### add method to a class

```python
class A:
  pass
@add_method(A)
def printHello(self):
  print('hello')

A().printHello()
```


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-1-33c418d667e0> in <module>
          1 class A:
          2   pass
    ----> 3 @add_method(A)
          4 def printHello(self):
          5   print('hello')


    NameError: name 'add_method' is not defined


First, import the s3 module

## import package

```python
from importlib import reload
from s3bz.s3bz import S3
```

### set up dummy data

```python
bucket = 'pybz-test'
key = 'test.dict'
sampleDict = {'test': 'bool'}
USER = None
PW = None
```

## save object

```python
result = S3.save(key = key, 
       objectToSave = sampleDict,
       bucket = bucket,
       user=USER,
       pw = PW,
       accelerate = True)
print(('failed', 'success')[result])
```

    success


## check if an object exist

```python
result = S3.exist('', bucket, user=USER, pw=PW, accelerate = True)
print(('doesnt exist', 'exist')[result])
```

    exist


## load object

```python
result = S3.load(key = key,
       bucket = bucket,
       user = USER,
       pw = PW,
       accelerate = True)
print(result[0])
```

    {'ib_prcode': '10932', 'ib_brcode': '1003', 'ib_cf_qty': '473', 'new_ib_vs_stock_cv': '391'}


## presign download object

```python
url = S3.presign(key=key,
              bucket=bucket,
              expiry = 1000,
              user=USER,
              pw=PW)
print(url)
```

    https://pybz-test.s3-accelerate.amazonaws.com/test.dict?AWSAccessKeyId=AKIAVX4Z5TKDVNE5QZPQ&Signature=6PfnHRYWc9xyk4oshrSECL5Eeyw%3D&Expires=1604392828


### testing signed link

```python
from s3bz.s3bz import Requests
result = Requests.getContentFromUrl(url)
```

## File operations

### save

```python
inputPath = '/tmp/tmpFile.txt'
key = 'tmpFile'
downloadPath = '/tmp/downloadTmpFile.txt'
with open(inputPath , 'w')as f:
  f.write('hello world')
```

```python
S3.saveFile(key =key ,path = inputPath,bucket = bucket)
```

### load

```python
S3.loadFile(key= key , path = downloadPath, bucket = bucket)
```

```python
with open(downloadPath, 'r') as f:
  print(f.read())
```

    hello world


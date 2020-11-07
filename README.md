# Helpers
> various helpers from nic gist


```
from nicHelper.wrappers import add_method
```

## Install

`pip install nicHelper`

# How to use

### method module

### add method to a class

```
class A:
  pass
@add_method(A)
def printHello(self):
  print('hello')

A().printHello()
```

    hello


```
from nicHelper.exception import errorString
```

```
try:
  error
except:
  print(f'error is \n{errorString()}')
```

    error is 
    Traceback (most recent call last):
      File "<ipython-input-7-47ded3794279>", line 2, in <module>
        error
    NameError: name 'error' is not defined
    


## Dict utilities

```
from nicHelper.dictUtil import printDict
printDict({'key':'sjfhdkljhafsdlkjhdfaslkjhkljfadshklhfa', 'nestedKey':{'nestedKey2':'938023840843', 'nested3':{'nested4':'hello'}}})
```


    ---------------------------------------------------------------------------

    ImportError                               Traceback (most recent call last)

    <ipython-input-8-86df14b70186> in <module>
    ----> 1 from nicHelper.dictUtil import printDict
          2 printDict({'key':'sjfhdkljhafsdlkjhdfaslkjhkljfadshklhfa', 'nestedKey':{'nestedKey2':'938023840843', 'nested3':{'nested4':'hello'}}})


    ImportError: cannot import name 'printDict' from 'nicHelper.dictUtil' (/home/ec2-user/SageMaker/pip/nicHelper/nicHelper/dictUtil.py)


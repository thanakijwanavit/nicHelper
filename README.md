# Helpers
> various helpers from nic gist


```
from nicHelper.wrappers import add_method
```

## Install

`pip install nicHelper`

## How to use

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


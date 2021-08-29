# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/sentryUtil.ipynb (unless otherwise specified).

__all__ = ['logSentry']

# Cell
from sentry_sdk import add_breadcrumb, capture_exception, capture_message
from .exception import traceback
from typing import Any

# Cell
def logSentry(message:str, data:Any = (lambda :{})(), level:str = 'info', section:str='main'):
  '''
    just add docs for ease of logging to sentry
    Input:
      message ::str:: required :: message to send to sentry
      data ::dict:: optional :: and object to send to sentry (default is an empty dict)
      level ::str::optional:: log level (default:info)
      section ::str::optional:: section name or function name (default: main)
    Response:
      Bool:: true means logged properly, false for error, print error message to console
  '''
  try:
    add_breadcrumb(
      category=section,
      data={'data':data},
      level=level,
      message=message
    )
    return True
  except Exception as e:
    print(message, data, level, section)
    print(f'error is {e}, {traceback()}')
    return False
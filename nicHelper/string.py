# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/string.ipynb (unless otherwise specified).

__all__ = ['urlDecode', 'urlEncode']

# Cell
def urlDecode(s:str)->dict:
    """Decode a url-encoded string into a dictionary of key/value pairs"""
    return dict([x.split('=') for x in s.split('&')])

# Cell
def urlEncode(s:str)->str:
    """Encode a dictionary of key/value pairs into a url-encoded string"""
    return '&'.join([f'{k}={v}' for k,v in s.items()])
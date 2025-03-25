def urlDecode(s:str)->dict:
    """Decode a url-encoded string into a dictionary of key/value pairs"""
    return dict([x.split('=') for x in s.split('&')])

def urlEncode(s:str)->str:
    """Encode a dictionary of key/value pairs into a url-encoded string"""
    return '&'.join([f'{k}={v}' for k,v in s.items()])
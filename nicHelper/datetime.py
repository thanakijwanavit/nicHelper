# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/datetime.ipynb (unless otherwise specified).

__all__ = ['datestamp', 'stringToTimestamp']

# Cell
from beartype import beartype

# Cell
from datetime import datetime, timezone, timedelta
@beartype
def datestamp(dt:datetime = datetime.utcnow(), tz=timezone.utc)->int:
  adt:dt = dt.astimezone(tz)
  datestamp = datetime(day=adt.day,month=adt.month,year=adt.year, tzinfo=tz).timestamp()
  return int(datestamp)

# Cell
@beartype
def stringToTimestamp(stringTime:str, formatString:str, timeZone:timezone = timezone.utc)->float:
  return datetime.strptime(stringTime,formatString).replace(tzinfo=timeZone).timestamp()
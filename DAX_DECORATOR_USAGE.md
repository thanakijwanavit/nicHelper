# DAX Decorator Usage

The `@pynamodbdax` decorator adds DAX caching functionality to any PynamoDB model.

## Quick Start

```python
from nicHelper.pynamodb import pynamodbdax
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

@pynamodbdax
class MyModel(Model):
    class Meta:
        table_name = "my-table"
        region = "us-east-1"
        dax_endpoint = "my-dax-cluster.dax.us-east-1.cache.amazonaws.com:8111"

    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
```

## Required Configuration

The `Meta` class must include:

- `dax_endpoint`: Your DAX cluster endpoint (required)
- `region`: AWS region (defaults to "us-east-1" if not specified)

## Available Methods

After applying the decorator, your model gets these additional methods:

### Save with DAX

```python
# Automatically uses DAX when available, falls back to PynamoDB
item = MyModel(id="123", name="test")
item.save()
```

### Read with DAX

```python
# Get single item
item = MyModel.get_with_dax("123")

# Query items
items = MyModel.query_with_dax("123")

# Scan items
all_items = MyModel.scan_with_dax()
```

## Fallback Behavior

- If DAX is unavailable, all methods automatically fall back to PynamoDB
- No code changes needed - same API works with or without DAX
- Errors are logged but don't break your application

## Example with Real Endpoint

```python
@pynamodbdax
class UserModel(Model):
    class Meta:
        table_name = "users"
        region = "ap-southeast-1"
        dax_endpoint = "longtermcluster.vuu7lr.clustercfg.dax.apse1.cache.amazonaws.com:8111"

    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    name = UnicodeAttribute()

# Usage
user = UserModel(user_id="123", email="user@example.com", name="John")
user.save()  # Uses DAX

retrieved = UserModel.get_with_dax("123")  # Uses DAX
```

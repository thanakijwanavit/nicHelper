#!/usr/bin/env python3
"""
Example demonstrating the @pynamodbdax decorator pattern.

This example shows how to use the new decorator to add DAX functionality
to any PynamoDB model without subclassing.
"""

import os
import sys
from datetime import datetime
from typing import Optional

# Add the project root to the path so we can import nicHelper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from nicHelper.pynamodb import pynamodbdax


# Example 1: Basic usage with default DAX settings
@pynamodbdax
class UserModel(Model):
    """
    Basic user model with DAX functionality.
    Uses default DAX endpoint and region.
    """
    class Meta:
        table_name = "users-dax-example"
        region = "ap-southeast-1"
    
    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    name = UnicodeAttribute()
    age = NumberAttribute(null=True)
    created_at = NumberAttribute()
    
    def save(self, **kwargs):
        """Override save to set timestamp"""
        if not self.created_at:
            self.created_at = int(datetime.now().timestamp())
        return super().save(**kwargs)
    
    def __repr__(self):
        return f"UserModel(user_id='{self.user_id}', email='{self.email}', name='{self.name}')"


# Example 2: Custom DAX configuration
@pynamodbdax(
    dax_endpoint="my-custom-cluster.dax.us-west-2.cache.amazonaws.com:8111",
    dax_region="us-west-2"
)
class ProductModel(Model):
    """
    Product model with custom DAX configuration.
    """
    class Meta:
        table_name = "products-dax-example"
        region = "us-west-2"
    
    product_id = UnicodeAttribute(hash_key=True)
    category = UnicodeAttribute(range_key=True)  # Composite key
    name = UnicodeAttribute()
    price = NumberAttribute()
    description = UnicodeAttribute(null=True)
    stock = NumberAttribute(default=0)
    
    def save(self, **kwargs):
        """Override save to set default stock if not set"""
        if self.stock is None:
            self.stock = 0
        return super().save(**kwargs)
    
    def __repr__(self):
        return f"ProductModel(product_id='{self.product_id}', name='{self.name}', price={self.price})"


# Example 3: Model with complex attributes and DAX
@pynamodbdax
class OrderModel(Model):
    """
    Order model demonstrating complex DAX operations.
    """
    class Meta:
        table_name = "orders-dax-example"
        region = "ap-southeast-1"
    
    order_id = UnicodeAttribute(hash_key=True)
    user_id = UnicodeAttribute(range_key=True)  # Composite key
    status = UnicodeAttribute(default="pending")
    total_amount = NumberAttribute()
    items_count = NumberAttribute()
    created_at = NumberAttribute()
    updated_at = NumberAttribute()
    
    def save(self, **kwargs):
        """Override save to set timestamps"""
        now = int(datetime.now().timestamp())
        if not self.created_at:
            self.created_at = now
        self.updated_at = now
        return super().save(**kwargs)
    
    def __repr__(self):
        return f"OrderModel(order_id='{self.order_id}', user_id='{self.user_id}', status='{self.status}')"


def demonstrate_basic_usage():
    """Demonstrate basic DAX decorator usage."""
    print("=== Basic DAX Decorator Usage ===")
    
    # Create a user
    user = UserModel(
        user_id="user123",
        email="john@example.com",
        name="John Doe",
        age=30,
        created_at=int(datetime.now().timestamp())
    )
    
    print(f"Created user: {user}")
    
    # Save using regular PynamoDB (with DAX cache invalidation)
    try:
        user.save()
        print("✓ User saved successfully")
    except Exception as e:
        print(f"✗ Failed to save user: {e}")
        return
    
    # Retrieve using DAX with fallback
    try:
        retrieved_user = UserModel.get_with_dax("user123")
        if retrieved_user:
            print(f"✓ Retrieved user via DAX: {retrieved_user}")
        else:
            print("✗ User not found")
    except Exception as e:
        print(f"✗ Failed to retrieve user: {e}")
    
    # Query using DAX
    try:
        users = UserModel.query_with_dax("user123")
        print(f"✓ Queried users via DAX: {len(users)} found")
    except Exception as e:
        print(f"✗ Failed to query users: {e}")


def demonstrate_custom_dax_config():
    """Demonstrate custom DAX configuration."""
    print("\n=== Custom DAX Configuration ===")
    
    # Create a product
    product = ProductModel(
        product_id="prod456",
        category="electronics",
        name="Laptop",
        price=999.99,
        description="High-performance laptop",
        stock=10
    )
    
    print(f"Created product: {product}")
    print(f"Using DAX endpoint: {ProductModel.DAX_ENDPOINT}")
    print(f"Using DAX region: {ProductModel.DAX_REGION}")
    
    # Save the product
    try:
        product.save()
        print("✓ Product saved successfully")
    except Exception as e:
        print(f"✗ Failed to save product: {e}")
        return
    
    # Retrieve using DAX with composite key
    try:
        retrieved_product = ProductModel.get_with_dax("prod456", range_key="electronics")
        if retrieved_product:
            print(f"✓ Retrieved product via DAX: {retrieved_product}")
        else:
            print("✗ Product not found")
    except Exception as e:
        print(f"✗ Failed to retrieve product: {e}")
    
    # Query products in electronics category
    try:
        electronics_products = ProductModel.query_with_dax("prod456")
        print(f"✓ Queried electronics products via DAX: {len(electronics_products)} found")
    except Exception as e:
        print(f"✗ Failed to query products: {e}")


def demonstrate_complex_operations():
    """Demonstrate complex DAX operations."""
    print("\n=== Complex DAX Operations ===")
    
    # Create multiple orders
    orders = []
    for i in range(3):
        order = OrderModel(
            order_id=f"order{i+1}",
            user_id="user123",
            status="pending",
            total_amount=100.0 + i * 50,
            items_count=i + 1,
            created_at=int(datetime.now().timestamp()),
            updated_at=int(datetime.now().timestamp())
        )
        orders.append(order)
    
    print(f"Created {len(orders)} orders")
    
    # Save all orders
    for order in orders:
        try:
            order.save()
            print(f"✓ Saved order: {order.order_id}")
        except Exception as e:
            print(f"✗ Failed to save order {order.order_id}: {e}")
    
    # Query orders for user123
    try:
        user_orders = OrderModel.query_with_dax("order1", range_key_condition="user_id = :user_id")
        print(f"✓ Queried user orders via DAX: {len(user_orders)} found")
    except Exception as e:
        print(f"✗ Failed to query user orders: {e}")
    
    # Scan all orders
    try:
        all_orders = OrderModel.scan_with_dax(limit=10)
        print(f"✓ Scanned all orders via DAX: {len(all_orders)} found")
    except Exception as e:
        print(f"✗ Failed to scan orders: {e}")


def demonstrate_decorator_vs_subclass():
    """Demonstrate the difference between decorator and subclass approaches."""
    print("\n=== Decorator vs Subclass Comparison ===")
    
    # Decorator approach (new)
    @pynamodbdax
    class DecoratorModel(Model):
        class Meta:
            table_name = "decorator-example"
            region = "ap-southeast-1"
        
        id = UnicodeAttribute(hash_key=True)
        data = UnicodeAttribute()
    
    # Subclass approach (old)
    from nicHelper.pynamodb import DaxModelWrapper
    
    class SubclassModel(DaxModelWrapper):
        class Meta:
            table_name = "subclass-example"
            region = "ap-southeast-1"
        
        id = UnicodeAttribute(hash_key=True)
        data = UnicodeAttribute()
    
    print("Decorator approach benefits:")
    print("✓ Can be applied to any existing PynamoDB model")
    print("✓ No inheritance required")
    print("✓ Configurable DAX settings per model")
    print("✓ Cleaner, more explicit code")
    print("✓ Easier to test and maintain")
    
    print("\nSubclass approach limitations:")
    print("✗ Requires inheritance")
    print("✗ Can't be applied to existing models")
    print("✗ Harder to configure per model")
    print("✗ More complex inheritance chain")


def main():
    """Run all demonstrations."""
    print("DAX Decorator Pattern Examples")
    print("=" * 50)
    
    # Check if DAX is available
    try:
        from amazon.dax import AmazonDaxClient
        print("✓ DAX dependencies available")
    except ImportError:
        print("⚠ DAX dependencies not available - will fallback to PynamoDB")
    
    # Run demonstrations
    demonstrate_decorator_vs_subclass()
    demonstrate_basic_usage()
    demonstrate_custom_dax_config()
    demonstrate_complex_operations()
    
    print("\n" + "=" * 50)
    print("Example completed!")
    print("\nKey benefits of the @pynamodbdax decorator:")
    print("1. Simple to use: just add @pynamodbdax() to any model")
    print("2. Configurable: customize DAX endpoint and region per model")
    print("3. Safe: graceful fallback when DAX is unavailable")
    print("4. Compatible: works with any existing PynamoDB model")
    print("5. Clean: no inheritance required")


if __name__ == "__main__":
    main() 
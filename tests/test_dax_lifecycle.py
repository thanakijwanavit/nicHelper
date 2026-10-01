#!/usr/bin/env python3
"""
DAX Lifecycle Test Script
Demonstrates full lifecycle: create table, save item, delete item, delete table
Using the new @pynamodbdax decorator pattern
"""

import time
import json
from datetime import datetime, timezone
import sys

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from nicHelper.pynamodb import pynamodbdax

# Test configuration
TEST_TABLE_NAME = "test-dax-lifecycle-table"
DAX_ENDPOINT = "longtermcluster.vuu7lr.clustercfg.dax.apse1.cache.amazonaws.com:8111"
AWS_REGION = "ap-southeast-1"

@pynamodbdax
class TestDaxModel(Model):
    """Test model for DAX lifecycle testing using decorator pattern"""
    
    class Meta:
        table_name = TEST_TABLE_NAME
        region = AWS_REGION
        dax_endpoint = DAX_ENDPOINT
    
    id = UnicodeAttribute(hash_key=True)
    data = UnicodeAttribute(null=True)  # Use standard UnicodeAttribute instead of SchemaAttribute
    lastEdited = NumberAttribute()
    creationTime = NumberAttribute()
    
    def recordTime(self, tz=timezone.utc):
        self.lastEdited = datetime.now(tz=tz).timestamp()
        if not self.creationTime:
            self.creationTime = datetime.now(tz=tz).timestamp()
    
    def toDict(self):
        return json.loads(self.data) if self.data else {}
    
    def setData(self, data_dict):
        """Helper method to set data as JSON string"""
        self.data = json.dumps(data_dict)

def create_test_table():
    """Create table using pynamodb"""
    print(f"🔧 Creating table {TEST_TABLE_NAME} with PynamoDB...")
    if not TestDaxModel.exists():
        TestDaxModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        print(f"✅ Table {TEST_TABLE_NAME} created successfully")
    else:
        print(f"✅ Table {TEST_TABLE_NAME} already exists")

def delete_test_table():
    """Delete table using pynamodb"""
    print(f"🧹 Deleting table {TEST_TABLE_NAME} with PynamoDB...")
    if TestDaxModel.exists():
        TestDaxModel.delete_table()
        print(f"✅ Table {TEST_TABLE_NAME} deleted successfully")
    else:
        print(f"Table {TEST_TABLE_NAME} does not exist")

def test_dax_lifecycle():
    print("\n🚀 Starting DAX Lifecycle Test (Decorator Pattern)")
    print("=" * 60)
    print(f"📋 Using DAX endpoint: {TestDaxModel.DAX_ENDPOINT}")
    print(f"📋 Using DAX region: {TestDaxModel.DAX_REGION}")
    
    print("\n📋 Step 1: Creating DynamoDB table")
    create_test_table()
    
    print("\n📝 Step 2: Creating test data")
    test_data = {
        "name": "DAX Lifecycle Test Item",
        "description": "This is a test item for DAX lifecycle testing",
        "value": 100,
        "tags": ["test", "dax", "lifecycle"],
        "metadata": {
            "created_by": "test-script",
            "version": "1.0",
            "timestamp": datetime.now().isoformat()
        }
    }
    print(f"✅ Test data created")
    
    print("\n💾 Step 3: Saving item using PynamoDB (with DAX cache invalidation)")
    try:
        item = TestDaxModel(id="lifecycle-test-123")
        item.setData(test_data)  # Use the helper method to set data
        item.recordTime()  # Manually call recordTime before save
        item.save()
        print(f"✅ Item saved successfully: {item.id}")
        print(f"   Name: {item.toDict()['name']}")
        print(f"   Value: {item.toDict()['value']}")
        print(f"   Creation Time: {item.creationTime}")
        print(f"   Last Edited: {item.lastEdited}")
    except Exception as e:
        print(f"❌ Error saving item: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n📖 Step 4: Reading item using DAX")
    try:
        item_from_dax = TestDaxModel.get_with_dax("lifecycle-test-123")
        if item_from_dax:
            print(f"✅ Item read from DAX: {item_from_dax.id}")
            data_dict = item_from_dax.toDict()
            print(f"   Name: {data_dict['name']}")
            print(f"   Value: {data_dict['value']}")
            print(f"   Tags: {data_dict['tags']}")
        else:
            print("❌ Item not found via DAX")
    except Exception as e:
        print(f"❌ Error reading from DAX: {e}")
    
    print("\n📖 Step 5: Reading item using PynamoDB")
    try:
        item_from_pynamodb = TestDaxModel.get("lifecycle-test-123")
        print(f"✅ Item read from PynamoDB: {item_from_pynamodb.id}")
        data_dict = item_from_pynamodb.toDict()
        print(f"   Name: {data_dict['name']}")
        print(f"   Value: {data_dict['value']}")
    except Exception as e:
        print(f"❌ Error reading from PynamoDB: {e}")
    
    print("\n✏️  Step 6: Updating item")
    try:
        data_dict = item_from_pynamodb.toDict()
        data_dict["value"] = 200
        data_dict["description"] = "Updated description for DAX lifecycle test"
        data_dict["metadata"]["updated_at"] = datetime.now().isoformat()
        item_from_pynamodb.setData(data_dict)  # Use helper method to update data
        item_from_pynamodb.recordTime()  # Manually call recordTime before save
        updated_item = item_from_pynamodb.save()
        print(f"✅ Item updated successfully: {updated_item.id}")
        updated_data = updated_item.toDict()
        print(f"   New Value: {updated_data['value']}")
        print(f"   New Description: {updated_data['description']}")
    except Exception as e:
        print(f"❌ Error updating item: {e}")
    
    print("\n📖 Step 7: Reading updated item via DAX")
    try:
        final_item = TestDaxModel.get_with_dax("lifecycle-test-123")
        if final_item:
            print(f"✅ Updated item read from DAX: {final_item.id}")
            final_data = final_item.toDict()
            print(f"   Value: {final_data['value']}")
            print(f"   Description: {final_data['description']}")
            print(f"   Updated At: {final_data['metadata']['updated_at']}")
        else:
            print("❌ Updated item not found via DAX")
    except Exception as e:
        print(f"❌ Error reading updated item: {e}")
    
    print("\n🗑️  Step 8: Deleting item")
    try:
        item_to_delete = TestDaxModel.get("lifecycle-test-123")
        if item_to_delete:
            item_to_delete.delete()
            print(f"✅ Item deleted successfully: {item_to_delete.id}")
        else:
            print("❌ Item not found for deletion")
    except Exception as e:
        print(f"❌ Error deleting item: {e}")
    
    print("\n🔍 Step 9: Verifying item deletion")
    try:
        deleted_item = TestDaxModel.get("lifecycle-test-123")
        if deleted_item is None:
            print("✅ Item successfully deleted (not found)")
        else:
            print("❌ Item still exists after deletion")
    except Exception as e:
        print(f"✅ Item successfully deleted (exception: {e})")
    
    print("\n🧹 Step 10: Deleting DynamoDB table")
    delete_test_table()
    
    print("\n🎉 DAX Lifecycle Test Completed Successfully!")
    print("✅ Decorator pattern working correctly!")
    return True

def main():
    print("🚀 DAX Lifecycle Test Suite (Decorator Pattern)")
    print("=" * 60)
    try:
        if test_dax_lifecycle():
            print("\n✅ Lifecycle test completed successfully!")
        else:
            print("\n❌ Lifecycle test failed!")
            return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
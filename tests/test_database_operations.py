"""Test database operations for violation records."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from storage.database import (
    save_violation,
    search_violations,
    get_all_violations,
    count_by_type,
    get_total_count,
    delete_all_violations,
    delete_violation_by_id
)


def test_database_operations():
    """Test all database CRUD operations."""
    print("Testing Database Operations")
    print("=" * 50)
    
    # Test 1: Save violation record
    print("\n1. Testing save_violation()...")
    test_record = {
        "violation_type": "Test Violation",
        "confidence": 0.9,
        "license_plate": "TEST123",
        "plate_confidence": 0.85,
        "vehicle_class": "car",
        "bbox": [100, 100, 200, 200],
        "image_source": "test.jpg",
        "evidence_path": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": {"test": True}
    }
    
    record_id = save_violation(test_record)
    assert record_id > 0
    print(f"   ✓ Saved record with ID: {record_id}")
    
    # Test 2: Get total count
    print("\n2. Testing get_total_count()...")
    total = get_total_count()
    assert total > 0
    print(f"   ✓ Total records: {total}")
    
    # Test 3: Search violations
    print("\n3. Testing search_violations()...")
    results = search_violations(query="TEST123", limit=10)
    assert len(results) > 0
    print(f"   ✓ Found {len(results)} matching records")
    
    # Test 4: Get all violations
    print("\n4. Testing get_all_violations()...")
    all_records = get_all_violations(limit=100)
    assert len(all_records) > 0
    print(f"   ✓ Retrieved {len(all_records)} records")
    
    # Test 5: Count by type
    print("\n5. Testing count_by_type()...")
    # Add some more test records with different types
    test_types = ["Helmet Non-Compliance", "Stop-Line Violation", "Overspeed"]
    for i, vtype in enumerate(test_types):
        test_record = {
            "violation_type": vtype,
            "confidence": 0.8,
            "license_plate": f"TEST{i:03d}",
            "plate_confidence": 0.75,
            "vehicle_class": "car",
            "bbox": [100, 100, 200, 200],
            "image_source": "test.jpg",
            "evidence_path": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": {}
        }
        save_violation(test_record)
    
    type_counts = count_by_type()
    assert len(type_counts) > 0
    print(f"   ✓ Violation types found: {list(type_counts.keys())}")
    for vtype, count in type_counts.items():
        print(f"     - {vtype}: {count}")
    
    # Test 6: Delete specific record by ID
    print("\n6. Testing delete_violation_by_id()...")
    success = delete_violation_by_id(record_id)
    assert success
    print(f"   ✓ Deleted record with ID: {record_id}")
    
    # Test 7: Delete all violations
    print("\n7. Testing delete_all_violations()...")
    deleted_count = delete_all_violations()
    assert deleted_count > 0
    print(f"   ✓ Deleted {deleted_count} records")
    
    # Verify deletion
    final_count = get_total_count()
    assert final_count == 0
    print(f"   ✓ Verified deletion: {final_count} records remaining")
    
    # Test 8: Test speed data storage
    print("\n8. Testing speed data storage...")
    speed_record = {
        "violation_type": "Overspeed",
        "confidence": 0.85,
        "license_plate": "SPEED01",
        "plate_confidence": 0.8,
        "vehicle_class": "car",
        "bbox": [100, 100, 200, 200],
        "image_source": "test.jpg",
        "evidence_path": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": {},
        "speed": 65.5,
        "speed_limit": 50.0
    }
    
    speed_id = save_violation(speed_record)
    retrieved = search_violations(query="SPEED01", limit=1)
    assert len(retrieved) > 0
    assert retrieved[0]['speed'] == 65.5
    assert retrieved[0]['speed_limit'] == 50.0
    print(f"   ✓ Speed data stored and retrieved correctly")
    
    # Cleanup
    delete_all_violations()
    
    print("\n" + "=" * 50)
    print("Database Operations Test Complete")
    print("=" * 50)


if __name__ == "__main__":
    test_database_operations()
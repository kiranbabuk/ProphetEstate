import pytest
from datetime import datetime
from services.property_service import PropertyService
from database.mongodb import get_database

@pytest.fixture
def property_service():
    return PropertyService()

@pytest.fixture
def sample_property():
    db = get_database()
    property_data = {
        'address': '789 Test Rd',
        'city': 'toronto',
        'price': 850000,
        'property_type': 'house',
        'bedrooms': 3,
        'bathrooms': 2,
        'square_feet': 2000,
        'lot_size': 5000,
        'year_built': 1990,
        'listed_date': datetime.utcnow()
    }
    
    result = db.properties.insert_one(property_data)
    property_data['_id'] = result.inserted_id
    
    yield property_data
    
    # Cleanup
    db.properties.delete_one({'_id': result.inserted_id})

def test_search_properties(property_service, sample_property):
    properties = property_service.search_properties(
        city='toronto',
        property_type='house',
        price_range=(800000, 900000)
    )
    
    assert len(properties) > 0
    assert properties[0]['address'] == '789 Test Rd'
    assert properties[0]['price'] == 850000

def test_get_property_details(property_service, sample_property):
    property_id = str(sample_property['_id'])
    property_details = property_service.get_property_details(property_id)
    
    assert property_details['address'] == '789 Test Rd'
    assert property_details['city'] == 'toronto'
    assert property_details['price'] == 850000
    assert 'listed_date' in property_details

def test_add_property(property_service):
    new_property = {
        'address': '321 New St',
        'city': 'vancouver',
        'price': 1500000,
        'property_type': 'condo'
    }
    
    result = property_service.add_property(new_property)
    
    assert result['address'] == '321 New St'
    assert result['city'] == 'vancouver'
    assert 'id' in result
    
    # Cleanup
    db = get_database()
    db.properties.delete_one({'address': '321 New St'})

def test_add_property_missing_fields(property_service):
    invalid_property = {
        'address': '999 Invalid Rd',
        'city': 'toronto'
        # Missing required fields
    }
    
    with pytest.raises(ValueError) as exc_info:
        property_service.add_property(invalid_property)
    
    assert 'Missing required field' in str(exc_info.value)
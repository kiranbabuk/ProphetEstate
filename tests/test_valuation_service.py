import pytest
import numpy as np
from datetime import datetime, timedelta
from services.valuation_service import ValuationService
from database.mongodb import get_database

@pytest.fixture
def valuation_service():
    return ValuationService()

@pytest.fixture
def sample_properties():
    db = get_database()
    properties = [
        {
            'address': '111 Sold St',
            'city': 'toronto',
            'price': 1100000,
            'property_type': 'house',
            'square_feet': 2200,
            'bedrooms': 4,
            'bathrooms': 3,
            'lot_size': 5500,
            'year_built': 1995,
            'listed_date': datetime.utcnow() - timedelta(days=45),
            'sold_date': datetime.utcnow() - timedelta(days=15)
        },
        {
            'address': '222 Sold Ave',
            'city': 'toronto',
            'price': 950000,
            'property_type': 'house',
            'square_feet': 1800,
            'bedrooms': 3,
            'bathrooms': 2,
            'lot_size': 4500,
            'year_built': 1992,
            'listed_date': datetime.utcnow() - timedelta(days=60),
            'sold_date': datetime.utcnow() - timedelta(days=30)
        }
    ]
    
    db.properties.insert_many(properties)
    yield properties
    db.properties.delete_many({'address': {'$in': [p['address'] for p in properties]}})

def test_get_valuation(valuation_service, sample_properties):
    property_data = {
        'city': 'toronto',
        'property_type': 'house',
        'square_feet': 2000,
        'bedrooms': 3,
        'bathrooms': 2,
        'lot_size': 5000,
        'year_built': 1990
    }
    
    valuation = valuation_service.get_valuation(property_data)
    
    assert 'estimated_value' in valuation
    assert valuation['estimated_value'] > 0
    assert 'confidence_score' in valuation
    assert 70 <= valuation['confidence_score'] <= 95
    assert 'comparables' in valuation
    assert 'market_trends' in valuation

def test_prepare_features(valuation_service):
    property_data = {
        'square_feet': 2000,
        'bedrooms': 3,
        'bathrooms': 2,
        'lot_size': 5000,
        'year_built': 1990
    }
    
    features = valuation_service._prepare_features(property_data)
    
    assert len(features) == 5
    assert all(isinstance(f, float) for f in features)
    assert features[0] == 2000.0  # square_feet
    assert features[1] == 3.0     # bedrooms
    assert features[2] == 2.0     # bathrooms
    assert features[3] == 5000.0  # lot_size
    assert features[4] == 1990.0  # year_built

def test_find_comparable_properties(valuation_service, sample_properties):
    property_data = {
        'city': 'toronto',
        'property_type': 'house',
        'square_feet': 2000
    }
    
    comparables = valuation_service._find_comparable_properties(property_data)
    
    assert len(comparables) > 0
    for comp in comparables:
        assert 'address' in comp
        assert 'price' in comp
        assert 'sold_date' in comp
        assert 'similarity_score' in comp
        assert 0 <= comp['similarity_score'] <= 100

def test_calculate_similarity_score(valuation_service):
    property1 = {
        'square_feet': 2000,
        'bedrooms': 3,
        'bathrooms': 2,
        'lot_size': 5000,
        'year_built': 1990
    }
    
    property2 = {
        'square_feet': 2200,
        'bedrooms': 3,
        'bathrooms': 2,
        'lot_size': 5500,
        'year_built': 1995
    }
    
    score = valuation_service._calculate_similarity_score(property1, property2)
    
    assert 0 <= score <= 100
    
    # Test identical properties
    identical_score = valuation_service._calculate_similarity_score(property1, property1)
    assert identical_score == 100.0

def test_calculate_confidence_score(valuation_service):
    comparables = [
        {'price': 1000000, 'similarity_score': 90},
        {'price': 1050000, 'similarity_score': 85},
        {'price': 975000, 'similarity_score': 80}
    ]
    
    score = valuation_service._calculate_confidence_score(1000000, comparables)
    
    assert 70 <= score <= 95
    
    # Test with no comparables
    base_score = valuation_service._calculate_confidence_score(1000000, [])
    assert base_score == 70.0
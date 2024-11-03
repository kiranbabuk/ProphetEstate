import pytest
from datetime import datetime, timedelta
from services.market_analysis import MarketAnalysis
from database.mongodb import get_database

@pytest.fixture
def market_analysis():
    return MarketAnalysis()

@pytest.fixture
def sample_properties():
    db = get_database()
    properties = [
        {
            'address': '123 Test St',
            'city': 'toronto',
            'price': 1000000,
            'property_type': 'house',
            'listed_date': datetime.utcnow() - timedelta(days=30),
            'neighborhood': 'Downtown'
        },
        {
            'address': '456 Test Ave',
            'city': 'toronto',
            'price': 1200000,
            'property_type': 'condo',
            'listed_date': datetime.utcnow() - timedelta(days=15),
            'neighborhood': 'Downtown'
        }
    ]
    
    # Insert test data
    db.properties.insert_many(properties)
    
    yield properties
    
    # Cleanup
    db.properties.delete_many({'address': {'$in': [p['address'] for p in properties]}})

def test_get_market_overview(market_analysis, sample_properties):
    overview = market_analysis.get_market_overview()
    
    assert 'toronto' in overview
    toronto_stats = overview['toronto']
    
    assert 'avg_price' in toronto_stats
    assert toronto_stats['avg_price'] > 0
    assert 'price_trends' in toronto_stats
    assert 'hot_neighborhoods' in toronto_stats

def test_get_city_metrics(market_analysis, sample_properties):
    metrics = market_analysis._get_city_metrics('toronto')
    
    assert metrics['avg_price'] > 0
    assert metrics['total_listings'] == 2
    assert metrics['avg_days_on_market'] >= 0

def test_get_price_trends(market_analysis, sample_properties):
    trends = market_analysis._get_price_trends('toronto')
    
    assert 'monthly' in trends
    assert 'quarterly' in trends
    assert 'yearly' in trends
    assert all(isinstance(v, (int, float)) for v in trends.values())

def test_get_hot_neighborhoods(market_analysis, sample_properties):
    neighborhoods = market_analysis._get_hot_neighborhoods('toronto')
    
    assert len(neighborhoods) > 0
    assert 'name' in neighborhoods[0]
    assert 'avg_price' in neighborhoods[0]
    assert 'total_listings' in neighborhoods[0]
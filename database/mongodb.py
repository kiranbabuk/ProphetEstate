from pymongo import MongoClient
from typing import Any
import os

_db = None

def get_database() -> Any:
    """Get MongoDB database connection"""
    global _db
    
    if _db is None:
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/prophetestate'))
        _db = client.get_database()
        
        # Ensure indexes
        _ensure_indexes(_db)
    
    return _db

def _ensure_indexes(db: Any) -> None:
    """Create necessary database indexes"""
    # Properties collection indexes
    db.properties.create_index([('city', 1)])
    db.properties.create_index([('property_type', 1)])
    db.properties.create_index([('price', 1)])
    db.properties.create_index([('listed_date', -1)])
    db.properties.create_index([('sold_date', -1)])
    db.properties.create_index([
        ('location', '2dsphere')
    ], sparse=True)
    
    # Compound indexes for common queries
    db.properties.create_index([
        ('city', 1),
        ('property_type', 1),
        ('price', 1)
    ])
    db.properties.create_index([
        ('city', 1),
        ('neighborhood', 1),
        ('listed_date', -1)
    ])
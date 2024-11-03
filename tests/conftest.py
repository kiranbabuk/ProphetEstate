import pytest
import os
import mongomock
import pymongo
from database.mongodb import get_database

@pytest.fixture(autouse=True)
def mock_mongodb(monkeypatch):
    """Mock MongoDB for testing"""
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.db
    
    def mock_get_database():
        return mock_db
    
    monkeypatch.setattr('database.mongodb.get_database', mock_get_database)
    return mock_db

@pytest.fixture(autouse=True)
def clean_mongodb(mock_mongodb):
    """Clean up MongoDB after each test"""
    yield
    for collection in mock_mongodb.list_collection_names():
        mock_mongodb[collection].drop()
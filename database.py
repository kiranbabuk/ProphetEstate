from pymongo import MongoClient
from pymongo.collection import Collection
import os

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        self.db = self.client.prophetestate

    @property
    def properties(self) -> Collection:
        return self.db.properties
    
    @property
    def market_data(self) -> Collection:
        return self.db.market_data
    
    @property
    def valuations(self) -> Collection:
        return self.db.valuations

    def create_indexes(self):
        # Create geospatial index for property locations
        self.properties.create_index([("location", "2dsphere")])
        
        # Create indexes for common queries
        self.properties.create_index([("city", 1)])
        self.properties.create_index([("price", 1)])
        self.properties.create_index([("property_type", 1)])
        
        # Create indexes for market data
        self.market_data.create_index([("city", 1), ("date", -1)])

db = MongoDB()
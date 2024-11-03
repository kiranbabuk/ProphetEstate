from datetime import datetime
from typing import Dict, Any
from database import db

class Property:
    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        property_doc = {
            'address': data['address'],
            'city': data['city'].lower(),
            'price': float(data['price']),
            'property_type': data['property_type'],
            'bedrooms': int(data.get('bedrooms', 0)),
            'bathrooms': float(data.get('bathrooms', 0)),
            'square_feet': float(data.get('square_feet', 0)),
            'lot_size': float(data.get('lot_size', 0)),
            'year_built': int(data.get('year_built', 0)),
            'location': {
                'type': 'Point',
                'coordinates': [float(data['longitude']), float(data['latitude'])]
            },
            'listed_date': datetime.utcnow(),
            'features': data.get('features', []),
            'description': data.get('description', ''),
            'images': data.get('images', [])
        }
        
        result = db.properties.insert_one(property_doc)
        property_doc['_id'] = str(result.inserted_id)
        return property_doc

    @staticmethod
    def find_nearby(latitude: float, longitude: float, max_distance: int = 5000) -> list:
        """Find properties within max_distance meters of the coordinates"""
        return list(db.properties.find({
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [longitude, latitude]
                    },
                    '$maxDistance': max_distance
                }
            }
        }))
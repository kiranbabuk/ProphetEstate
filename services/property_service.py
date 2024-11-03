from typing import Dict, Any, List, Tuple
from database.mongodb import get_database
from datetime import datetime

class PropertyService:
    def __init__(self):
        self.db = get_database()
        self.properties_collection = self.db.properties

    def search_properties(
        self,
        city: str,
        property_type: str = 'all',
        price_range: Tuple[float, float] = (0, float('inf')),
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search properties based on criteria"""
        query = {
            'city': city.lower(),
            'price': {'$gte': price_range[0], '$lte': price_range[1]}
        }
        
        if property_type != 'all':
            query['property_type'] = property_type
            
        properties = list(self.properties_collection
            .find(query)
            .limit(limit))
            
        return [self._format_property(p) for p in properties]
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific property"""
        property_data = self.properties_collection.find_one({'_id': property_id})
        if not property_data:
            raise ValueError(f"Property not found: {property_id}")
            
        return self._format_property(property_data)
    
    def add_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new property listing"""
        property_data['listed_date'] = datetime.utcnow()
        property_data['city'] = property_data['city'].lower()
        
        # Ensure required fields
        required_fields = ['address', 'city', 'price', 'property_type']
        for field in required_fields:
            if field not in property_data:
                raise ValueError(f"Missing required field: {field}")
        
        result = self.properties_collection.insert_one(property_data)
        return self.get_property_details(result.inserted_id)
    
    def _format_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format property data for API response"""
        property_data['id'] = str(property_data.pop('_id'))
        
        # Format dates
        if 'listed_date' in property_data:
            property_data['listed_date'] = property_data['listed_date'].isoformat()
            
        return property_data
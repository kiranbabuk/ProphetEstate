from typing import Dict, Any, List
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from database.mongodb import get_database
from datetime import datetime, timedelta

class ValuationService:
    def __init__(self):
        self.db = get_database()
        self.properties_collection = self.db.properties
        self.model = self._train_model()

    def get_valuation(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered valuation for a property"""
        # Prepare features for prediction
        features = self._prepare_features(property_data)
        
        # Get estimated value
        estimated_value = self.model.predict([features])[0]
        
        # Get confidence score and comparable properties
        comparables = self._find_comparable_properties(property_data)
        confidence_score = self._calculate_confidence_score(estimated_value, comparables)
        
        return {
            'estimated_value': round(estimated_value, 2),
            'confidence_score': confidence_score,
            'comparables': comparables,
            'market_trends': self._get_market_trends(property_data['city'])
        }
    
    def _train_model(self) -> RandomForestRegressor:
        """Train the valuation model using historical data"""
        # Get training data from database
        properties = list(self.properties_collection.find({
            'sold_date': {'$exists': True}
        }))
        
        if not properties:
            # If no historical data, use basic model
            return self._create_basic_model()
        
        # Prepare features and target
        X = [self._prepare_features(p) for p in properties]
        y = [p['price'] for p in properties]
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        return model
    
    def _prepare_features(self, property_data: Dict[str, Any]) -> List[float]:
        """Extract and normalize features for model input"""
        features = [
            float(property_data.get('square_feet', 0)),
            float(property_data.get('bedrooms', 0)),
            float(property_data.get('bathrooms', 0)),
            float(property_data.get('lot_size', 0)),
            float(property_data.get('year_built', 2000))
        ]
        
        return features
    
    def _find_comparable_properties(
        self,
        property_data: Dict[str, Any],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Find similar properties in the same area"""
        query = {
            'city': property_data['city'],
            'property_type': property_data['property_type'],
            'sold_date': {
                '$gte': datetime.utcnow() - timedelta(days=180)
            },
            'square_feet': {
                '$gte': float(property_data['square_feet']) * 0.8,
                '$lte': float(property_data['square_feet']) * 1.2
            }
        }
        
        comparables = list(self.properties_collection
            .find(query)
            .limit(limit))
            
        return [
            {
                'address': p['address'],
                'price': p['price'],
                'sold_date': p['sold_date'].isoformat(),
                'square_feet': p['square_feet'],
                'similarity_score': self._calculate_similarity_score(
                    property_data,
                    p
                )
            }
            for p in comparables
        ]
    
    def _calculate_similarity_score(
        self,
        property1: Dict[str, Any],
        property2: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two properties"""
        features1 = self._prepare_features(property1)
        features2 = self._prepare_features(property2)
        
        # Calculate Euclidean distance and convert to similarity score
        distance = np.sqrt(sum((f1 - f2) ** 2 for f1, f2 in zip(features1, features2)))
        max_distance = np.sqrt(sum(max(f1, f2) ** 2 for f1, f2 in zip(features1, features2)))
        
        similarity = (1 - distance / max_distance) * 100
        return round(similarity, 2)
    
    def _calculate_confidence_score(
        self,
        estimated_value: float,
        comparables: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the valuation"""
        if not comparables:
            return 70.0  # Base confidence when no comparables
            
        # Calculate variance in comparable prices
        prices = [p['price'] for p in comparables]
        price_variance = np.std(prices) / np.mean(prices)
        
        # Calculate average similarity score
        similarity_scores = [p['similarity_score'] for p in comparables]
        avg_similarity = np.mean(similarity_scores)
        
        # Combine factors for final confidence score
        confidence = 95 - (price_variance * 100) + (avg_similarity / 10)
        return round(min(max(confidence, 70), 95), 2)
    
    def _get_market_trends(self, city: str) -> Dict[str, Any]:
        """Get market trends for the area"""
        now = datetime.utcnow()
        three_months_ago = now - timedelta(days=90)
        
        pipeline = [
            {
                '$match': {
                    'city': city,
                    'sold_date': {'$gte': three_months_ago}
                }
            },
            {
                '$group': {
                    '_id': None,
                    'avg_price': {'$avg': '$price'},
                    'avg_price_per_sqft': {
                        '$avg': {'$divide': ['$price', '$square_feet']}
                    },
                    'avg_days_on_market': {
                        '$avg': {
                            '$divide': [
                                {'$subtract': ['$sold_date', '$listed_date']},
                                24 * 60 * 60 * 1000
                            ]
                        }
                    }
                }
            }
        ]
        
        result = list(self.properties_collection.aggregate(pipeline))
        if not result:
            return {
                'price_trend': 0,
                'avg_days_on_market': 30,
                'price_per_sqft': 0
            }
            
        metrics = result[0]
        return {
            'price_trend': self._calculate_price_trend(city),
            'avg_days_on_market': round(metrics['avg_days_on_market'], 1),
            'price_per_sqft': round(metrics['avg_price_per_sqft'], 2)
        }
    
    def _calculate_price_trend(self, city: str) -> float:
        """Calculate price trend (percentage change) over last 3 months"""
        now = datetime.utcnow()
        three_months_ago = now - timedelta(days=90)
        
        pipeline = [
            {
                '$match': {
                    'city': city,
                    'sold_date': {'$gte': three_months_ago}
                }
            },
            {
                '$group': {
                    '_id': {
                        'month': {'$month': '$sold_date'}
                    },
                    'avg_price': {'$avg': '$price'}
                }
            },
            {'$sort': {'_id.month': 1}}
        ]
        
        results = list(self.properties_collection.aggregate(pipeline))
        if len(results) < 2:
            return 0.0
            
        first_month = results[0]['avg_price']
        last_month = results[-1]['avg_price']
        
        price_change = ((last_month - first_month) / first_month) * 100
        return round(price_change, 2)
    
    def _create_basic_model(self) -> RandomForestRegressor:
        """Create a basic model when no historical data is available"""
        # Generate synthetic data for initial model
        n_samples = 1000
        X = np.random.rand(n_samples, 5)  # 5 features
        y = (
            X[:, 0] * 1000 +  # square feet
            X[:, 1] * 200 +   # bedrooms
            X[:, 2] * 150 +   # bathrooms
            X[:, 3] * 500 +   # lot size
            X[:, 4] * 100     # year built
        ) * 1000  # Scale to realistic prices
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model
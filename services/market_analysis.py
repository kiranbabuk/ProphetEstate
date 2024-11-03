from datetime import datetime, timedelta
from database.mongodb import get_database
from typing import Dict, Any, List

class MarketAnalysis:
    def __init__(self):
        self.db = get_database()
        self.properties_collection = self.db.properties

    def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market overview for all cities"""
        stats = {}
        cities = ['toronto', 'vancouver', 'ottawa']
        
        for city in cities:
            stats[city] = {
                **self._get_city_metrics(city),
                'price_trends': self._get_price_trends(city),
                'hot_neighborhoods': self._get_hot_neighborhoods(city)
            }
        
        return stats
    
    def _get_city_metrics(self, city: str) -> Dict[str, Any]:
        """Calculate key metrics for a specific city"""
        pipeline = [
            {'$match': {'city': city}},
            {'$group': {
                '_id': None,
                'avg_price': {'$avg': '$price'},
                'total_listings': {'$sum': 1},
                'avg_days_on_market': {
                    '$avg': {
                        '$divide': [
                            {'$subtract': [datetime.utcnow(), '$listed_date']},
                            24 * 60 * 60 * 1000  # Convert to days
                        ]
                    }
                }
            }}
        ]
        
        result = list(self.properties_collection.aggregate(pipeline))
        if not result:
            return {
                'avg_price': 0,
                'total_listings': 0,
                'avg_days_on_market': 0
            }
            
        metrics = result[0]
        metrics.pop('_id', None)
        return metrics
    
    def _get_price_trends(self, city: str) -> Dict[str, float]:
        """Calculate price trends over different time periods"""
        now = datetime.utcnow()
        periods = {
            'monthly': now - timedelta(days=30),
            'quarterly': now - timedelta(days=90),
            'yearly': now - timedelta(days=365)
        }
        
        trends = {}
        for period_name, start_date in periods.items():
            pipeline = [
                {
                    '$match': {
                        'city': city,
                        'listed_date': {'$gte': start_date}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'avg_price': {'$avg': '$price'}
                    }
                }
            ]
            
            result = list(self.properties_collection.aggregate(pipeline))
            if result:
                trends[period_name] = result[0]['avg_price']
            else:
                trends[period_name] = 0
                
        return trends
    
    def _get_hot_neighborhoods(self, city: str) -> List[Dict[str, Any]]:
        """Identify hot neighborhoods based on price growth and sales velocity"""
        pipeline = [
            {
                '$match': {
                    'city': city,
                    'listed_date': {
                        '$gte': datetime.utcnow() - timedelta(days=90)
                    }
                }
            },
            {
                '$group': {
                    '_id': '$neighborhood',
                    'avg_price': {'$avg': '$price'},
                    'total_listings': {'$sum': 1},
                    'avg_days_on_market': {
                        '$avg': {
                            '$divide': [
                                {'$subtract': [datetime.utcnow(), '$listed_date']},
                                24 * 60 * 60 * 1000
                            ]
                        }
                    }
                }
            },
            {
                '$sort': {
                    'total_listings': -1,
                    'avg_days_on_market': 1
                }
            },
            {'$limit': 5}
        ]
        
        results = list(self.properties_collection.aggregate(pipeline))
        return [
            {
                'name': r['_id'],
                'avg_price': r['avg_price'],
                'total_listings': r['total_listings'],
                'avg_days_on_market': r['avg_days_on_market']
            }
            for r in results
        ]
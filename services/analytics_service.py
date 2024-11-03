from typing import Dict, Any, List
from datetime import datetime, timedelta
from database.mongodb import get_database
import numpy as np
from sklearn.linear_model import LinearRegression

class AnalyticsService:
    def __init__(self):
        self.db = get_database()
        self.properties = self.db.properties
    
    def get_market_trends(self, city: str, period: str = '1y') -> Dict[str, Any]:
        """Get detailed market trends analysis"""
        end_date = datetime.utcnow()
        start_date = self._get_start_date(end_date, period)
        
        pipeline = [
            {
                '$match': {
                    'city': city,
                    'sold_date': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$sold_date'},
                        'month': {'$month': '$sold_date'}
                    },
                    'avg_price': {'$avg': '$price'},
                    'total_sales': {'$sum': 1},
                    'avg_days_on_market': {
                        '$avg': {
                            '$divide': [
                                {'$subtract': ['$sold_date', '$listed_date']},
                                24 * 60 * 60 * 1000
                            ]
                        }
                    }
                }
            },
            {'$sort': {'_id.year': 1, '_id.month': 1}}
        ]
        
        results = list(self.properties.aggregate(pipeline))
        
        # Calculate price trends and predictions
        prices = [r['avg_price'] for r in results]
        dates = [datetime(r['_id']['year'], r['_id']['month'], 1) for r in results]
        
        predictions = self._predict_prices(dates, prices, 6)  # 6 months forecast
        
        return {
            'historical_data': [
                {
                    'date': f"{r['_id']['year']}-{r['_id']['month']:02d}",
                    'avg_price': r['avg_price'],
                    'total_sales': r['total_sales'],
                    'avg_days_on_market': r['avg_days_on_market']
                }
                for r in results
            ],
            'predictions': predictions,
            'summary': self._calculate_market_summary(results)
        }
    
    def get_neighborhood_analysis(
        self,
        city: str,
        neighborhood: str = None
    ) -> Dict[str, Any]:
        """Analyze neighborhood performance and trends"""
        match_query = {'city': city}
        if neighborhood:
            match_query['neighborhood'] = neighborhood
            
        pipeline = [
            {'$match': match_query},
            {
                '$group': {
                    '_id': '$neighborhood',
                    'avg_price': {'$avg': '$price'},
                    'price_per_sqft': {
                        '$avg': {'$divide': ['$price', '$square_feet']}
                    },
                    'total_listings': {'$sum': 1},
                    'avg_days_on_market': {
                        '$avg': {
                            '$divide': [
                                {'$subtract': ['$sold_date', '$listed_date']},
                                24 * 60 * 60 * 1000
                            ]
                        }
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'amenities',
                    'localField': '_id',
                    'foreignField': 'neighborhood',
                    'as': 'amenities'
                }
            }
        ]
        
        results = list(self.properties.aggregate(pipeline))
        
        return {
            'neighborhoods': [
                {
                    'name': r['_id'],
                    'metrics': {
                        'avg_price': r['avg_price'],
                        'price_per_sqft': r['price_per_sqft'],
                        'total_listings': r['total_listings'],
                        'avg_days_on_market': r['avg_days_on_market']
                    },
                    'amenities': self._summarize_amenities(r['amenities']),
                    'score': self._calculate_neighborhood_score(r)
                }
                for r in results
            ],
            'city_summary': self._calculate_city_summary(results)
        }
    
    def get_investment_opportunities(
        self,
        city: str,
        budget: float,
        property_type: str = 'all'
    ) -> List[Dict[str, Any]]:
        """Find investment opportunities based on criteria"""
        match_query = {
            'city': city,
            'price': {'$lte': budget},
            'listed_date': {'$gte': datetime.utcnow() - timedelta(days=30)}
        }
        
        if property_type != 'all':
            match_query['property_type'] = property_type
            
        pipeline = [
            {'$match': match_query},
            {
                '$lookup': {
                    'from': 'market_data',
                    'localField': 'neighborhood',
                    'foreignField': 'neighborhood',
                    'as': 'market_data'
                }
            }
        ]
        
        properties = list(self.properties.aggregate(pipeline))
        
        # Calculate investment metrics for each property
        opportunities = []
        for prop in properties:
            metrics = self._calculate_investment_metrics(prop)
            if metrics['roi_potential'] >= 5:  # Min 5% ROI potential
                opportunities.append({
                    'property': {
                        'id': str(prop['_id']),
                        'address': prop['address'],
                        'price': prop['price'],
                        'type': prop['property_type'],
                        'square_feet': prop['square_feet']
                    },
                    'metrics': metrics
                })
        
        # Sort by ROI potential
        opportunities.sort(key=lambda x: x['metrics']['roi_potential'], reverse=True)
        return opportunities[:10]  # Top 10 opportunities
    
    def _get_start_date(self, end_date: datetime, period: str) -> datetime:
        """Calculate start date based on period"""
        periods = {
            '1m': timedelta(days=30),
            '3m': timedelta(days=90),
            '6m': timedelta(days=180),
            '1y': timedelta(days=365),
            '2y': timedelta(days=730),
            '5y': timedelta(days=1825)
        }
        return end_date - periods.get(period, periods['1y'])
    
    def _predict_prices(
        self,
        dates: List[datetime],
        prices: List[float],
        months_ahead: int
    ) -> List[Dict[str, Any]]:
        """Predict future prices using linear regression"""
        if not dates or not prices:
            return []
            
        X = np.array([(d - dates[0]).days for d in dates]).reshape(-1, 1)
        y = np.array(prices)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future dates
        last_date = dates[-1]
        future_dates = [
            last_date + timedelta(days=30 * i)
            for i in range(1, months_ahead + 1)
        ]
        
        # Predict prices
        future_X = np.array([
            (d - dates[0]).days for d in future_dates
        ]).reshape(-1, 1)
        
        predictions = model.predict(future_X)
        
        return [
            {
                'date': d.strftime('%Y-%m'),
                'predicted_price': float(p)
            }
            for d, p in zip(future_dates, predictions)
        ]
    
    def _calculate_market_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate market summary metrics"""
        if not data:
            return {
                'price_trend': 0,
                'sales_trend': 0,
                'market_health': 'stable'
            }
            
        recent = data[-3:]  # Last 3 months
        
        # Calculate trends
        price_changes = [
            (r['avg_price'] - data[i-1]['avg_price']) / data[i-1]['avg_price']
            for i, r in enumerate(recent) if i > 0
        ]
        
        sales_changes = [
            (r['total_sales'] - data[i-1]['total_sales']) / data[i-1]['total_sales']
            for i, r in enumerate(recent) if i > 0
        ]
        
        avg_price_change = np.mean(price_changes) if price_changes else 0
        avg_sales_change = np.mean(sales_changes) if sales_changes else 0
        
        # Determine market health
        market_health = 'stable'
        if avg_price_change > 0.05 and avg_sales_change > 0:
            market_health = 'hot'
        elif avg_price_change < -0.05 and avg_sales_change < 0:
            market_health = 'cold'
        
        return {
            'price_trend': round(avg_price_change * 100, 2),
            'sales_trend': round(avg_sales_change * 100, 2),
            'market_health': market_health
        }
    
    def _summarize_amenities(self, amenities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize neighborhood amenities"""
        if not amenities:
            return {
                'schools': 0,
                'parks': 0,
                'transit': 0,
                'shopping': 0,
                'restaurants': 0
            }
            
        return {
            'schools': sum(1 for a in amenities if a['type'] == 'school'),
            'parks': sum(1 for a in amenities if a['type'] == 'park'),
            'transit': sum(1 for a in amenities if a['type'] == 'transit'),
            'shopping': sum(1 for a in amenities if a['type'] == 'shopping'),
            'restaurants': sum(1 for a in amenities if a['type'] == 'restaurant')
        }
    
    def _calculate_neighborhood_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall neighborhood score"""
        # Implement scoring logic based on various metrics
        scores = []
        
        # Price trend score (30%)
        price_trend = self._calculate_price_trend(data['_id'])
        scores.append(min(100, max(0, price_trend * 20)) * 0.3)
        
        # Market activity score (20%)
        days_on_market = data['avg_days_on_market']
        market_score = 100 * (1 - min(1, days_on_market / 90))
        scores.append(market_score * 0.2)
        
        # Amenities score (30%)
        if data.get('amenities'):
            amenity_count = sum(1 for a in data['amenities'])
            amenity_score = min(100, amenity_count * 5)
            scores.append(amenity_score * 0.3)
        
        # Investment potential score (20%)
        roi_potential = self._calculate_roi_potential(data)
        scores.append(min(100, roi_potential * 10) * 0.2)
        
        return round(sum(scores), 2)
    
    def _calculate_price_trend(self, neighborhood: str) -> float:
        """Calculate price trend for a neighborhood"""
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        
        pipeline = [
            {
                '$match': {
                    'neighborhood': neighborhood,
                    'sold_date': {'$gte': one_year_ago}
                }
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$sold_date'},
                        'month': {'$month': '$sold_date'}
                    },
                    'avg_price': {'$avg': '$price'}
                }
            },
            {'$sort': {'_id.year': 1, '_id.month': 1}}
        ]
        
        results = list(self.properties.aggregate(pipeline))
        if len(results) < 2:
            return 0
            
        first_price = results[0]['avg_price']
        last_price = results[-1]['avg_price']
        
        return (last_price - first_price) / first_price
    
    def _calculate_roi_potential(self, data: Dict[str, Any]) -> float:
        """Calculate ROI potential based on various factors"""
        # Implement ROI calculation logic
        price_trend = self._calculate_price_trend(data['_id'])
        rental_yield = self._estimate_rental_yield(data)
        
        # Weight factors
        roi = (price_trend * 0.6) + (rental_yield * 0.4)
        return max(0, roi * 100)
    
    def _estimate_rental_yield(self, data: Dict[str, Any]) -> float:
        """Estimate rental yield for a property"""
        # Implement rental yield estimation logic
        # This is a simplified example
        avg_price = data['avg_price']
        estimated_monthly_rent = avg_price * 0.004  # 0.4% rule
        annual_rent = estimated_monthly_rent * 12
        
        return annual_rent / avg_price
    
    def _calculate_city_summary(self, neighborhoods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate city-wide summary statistics"""
        if not neighborhoods:
            return {
                'avg_price': 0,
                'price_range': {'min': 0, 'max': 0},
                'total_listings': 0,
                'avg_days_on_market': 0
            }
            
        prices = [n['avg_price'] for n in neighborhoods]
        days_on_market = [n['avg_days_on_market'] for n in neighborhoods]
        total_listings = sum(n['total_listings'] for n in neighborhoods)
        
        return {
            'avg_price': np.mean(prices),
            'price_range': {
                'min': min(prices),
                'max': max(prices)
            },
            'total_listings': total_listings,
            'avg_days_on_market': np.mean(days_on_market)
        }
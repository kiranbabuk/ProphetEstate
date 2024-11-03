import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class ValuationModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        try:
            self.model = joblib.load('models/trained/valuation_model.joblib')
            self.scaler = joblib.load('models/trained/scaler.joblib')
        except:
            print("Training new model...")
            self.train_model()
    
    def train_model(self):
        # In production, you'd load real historical data
        # This is a simplified example
        data = pd.DataFrame({
            'price': np.random.normal(800000, 200000, 1000),
            'square_feet': np.random.normal(2000, 500, 1000),
            'bedrooms': np.random.randint(1, 6, 1000),
            'bathrooms': np.random.randint(1, 4, 1000),
            'year_built': np.random.randint(1950, 2024, 1000),
            'lot_size': np.random.normal(5000, 1000, 1000)
        })
        
        X = data.drop('price', axis=1)
        y = data['price']
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save model
        os.makedirs('models/trained', exist_ok=True)
        joblib.dump(self.model, 'models/trained/valuation_model.joblib')
        joblib.dump(self.scaler, 'models/trained/scaler.joblib')
    
    def predict(self, features):
        features_df = pd.DataFrame([features])
        features_scaled = self.scaler.transform(features_df)
        prediction = self.model.predict(features_scaled)[0]
        
        # Calculate confidence score (simplified)
        confidence = 95 - np.random.randint(0, 10)
        
        return {
            'estimated_value': round(prediction, 2),
            'confidence': confidence,
            'comparable_properties': self.get_comparables(features),
            'market_trends': self.get_market_trends(features['city'])
        }
    
    def get_comparables(self, features):
        # In production, query database for similar properties
        return [
            {
                'address': '123 Nearby St',
                'price': 850000,
                'sold_date': '2024-01-15',
                'similarity': 92
            },
            {
                'address': '456 Similar Ave',
                'price': 875000,
                'sold_date': '2024-02-01',
                'similarity': 88
            }
        ]
    
    def get_market_trends(self, city):
        # In production, calculate from historical data
        return {
            'yearly_appreciation': 5.2,
            'average_days_on_market': 15,
            'price_per_sqft': 625
        }
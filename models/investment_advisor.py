import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta

class InvestmentAdvisor:
    def __init__(self):
        self.risk_profiles = {
            'conservative': {
                'max_price': 800000,
                'min_roi': 0.05,
                'max_leverage': 0.65,
                'preferred_types': ['condo', 'townhouse']
            },
            'moderate': {
                'max_price': 1200000,
                'min_roi': 0.07,
                'max_leverage': 0.75,
                'preferred_types': ['townhouse', 'semi-detached']
            },
            'aggressive': {
                'max_price': 2000000,
                'min_roi': 0.09,
                'max_leverage': 0.80,
                'preferred_types': ['detached', 'multi-family']
            }
        }
    
    def get_investment_recommendations(
        self,
        budget: float,
        risk_profile: str,
        location: str,
        investment_horizon: int
    ) -> Dict[str, Any]:
        """Generate personalized investment recommendations"""
        profile = self.risk_profiles[risk_profile]
        
        # Calculate investment metrics
        max_property_price = min(budget / (1 - profile['max_leverage']), profile['max_price'])
        monthly_payment = self._calculate_mortgage_payment(
            max_property_price * profile['max_leverage'],
            0.05,  # Interest rate
            25     # Amortization period
        )
        
        # Calculate potential returns
        rental_income = self._estimate_rental_income(max_property_price, location)
        appreciation = self._estimate_appreciation(location, investment_horizon)
        cash_flow = rental_income - monthly_payment - self._estimate_expenses(max_property_price)
        
        # Generate property recommendations
        recommendations = self._find_matching_properties(
            max_property_price,
            profile['preferred_types'],
            location
        )
        
        return {
            'summary': {
                'max_purchase_price': round(max_property_price, 2),
                'recommended_down_payment': round(max_property_price * (1 - profile['max_leverage']), 2),
                'monthly_payment': round(monthly_payment, 2),
                'estimated_cash_flow': round(cash_flow, 2),
                'projected_appreciation': round(appreciation * 100, 2),
                'estimated_roi': round(self._calculate_roi(
                    max_property_price,
                    cash_flow,
                    appreciation,
                    investment_horizon
                ) * 100, 2)
            },
            'recommendations': recommendations,
            'risk_analysis': self._analyze_risks(
                max_property_price,
                monthly_payment,
                cash_flow,
                location
            )
        }
    
    def _calculate_mortgage_payment(self, principal: float, rate: float, years: int) -> float:
        """Calculate monthly mortgage payment"""
        monthly_rate = rate / 12
        num_payments = years * 12
        return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
               ((1 + monthly_rate)**num_payments - 1)
    
    def _estimate_rental_income(self, property_price: float, location: str) -> float:
        """Estimate monthly rental income"""
        # In production, use real market data
        rental_yield = {
            'toronto': 0.04,
            'vancouver': 0.035,
            'ottawa': 0.045
        }.get(location.lower(), 0.04)
        
        return (property_price * rental_yield) / 12
    
    def _estimate_expenses(self, property_price: float) -> float:
        """Estimate monthly expenses"""
        # Property tax, insurance, maintenance, etc.
        return property_price * 0.02 / 12
    
    def _estimate_appreciation(self, location: str, years: int) -> float:
        """Estimate annual appreciation rate"""
        # In production, use historical data and ML models
        base_rates = {
            'toronto': 0.06,
            'vancouver': 0.055,
            'ottawa': 0.05
        }
        return base_rates.get(location.lower(), 0.05)
    
    def _calculate_roi(
        self,
        purchase_price: float,
        monthly_cash_flow: float,
        appreciation_rate: float,
        years: int
    ) -> float:
        """Calculate return on investment"""
        total_appreciation = purchase_price * ((1 + appreciation_rate)**years - 1)
        total_cash_flow = monthly_cash_flow * 12 * years
        down_payment = purchase_price * 0.2  # Assuming 20% down payment
        
        return (total_appreciation + total_cash_flow) / down_payment
    
    def _find_matching_properties(
        self,
        max_price: float,
        property_types: List[str],
        location: str
    ) -> List[Dict[str, Any]]:
        """Find properties matching investment criteria"""
        # In production, query database for actual properties
        return [
            {
                'address': '123 Investment Ave',
                'price': max_price * 0.95,
                'type': property_types[0],
                'roi': 0.08,
                'cash_flow': 500,
                'appreciation_potential': 'high'
            },
            {
                'address': '456 Opportunity St',
                'price': max_price * 0.85,
                'type': property_types[1],
                'roi': 0.075,
                'cash_flow': 600,
                'appreciation_potential': 'medium'
            }
        ]
    
    def _analyze_risks(
        self,
        price: float,
        monthly_payment: float,
        cash_flow: float,
        location: str
    ) -> Dict[str, Any]:
        """Analyze investment risks"""
        return {
            'market_risk': {
                'level': 'medium',
                'factors': [
                    'Historical price volatility',
                    'Market cycle position',
                    'Local economic indicators'
                ]
            },
            'cash_flow_risk': {
                'level': 'low' if cash_flow > monthly_payment * 0.2 else 'medium',
                'factors': [
                    'Rental demand',
                    'Vacancy rates',
                    'Operating expenses'
                ]
            },
            'location_risk': {
                'level': 'low',
                'factors': [
                    'Population growth',
                    'Employment trends',
                    'Infrastructure development'
                ]
            }
        }</content>
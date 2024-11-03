from flask import Blueprint, jsonify, request
from services.market_analysis import MarketAnalysis
from services.property_service import PropertyService
from services.valuation_service import ValuationService
from services.analytics_service import AnalyticsService

api_bp = Blueprint('api', __name__)
market_analysis = MarketAnalysis()
property_service = PropertyService()
valuation_service = ValuationService()
analytics_service = AnalyticsService()

@api_bp.route('/market-stats')
def get_market_stats():
    try:
        stats = market_analysis.get_market_overview()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/market-trends')
def get_market_trends():
    try:
        city = request.args.get('city', 'toronto')
        period = request.args.get('period', '1y')
        trends = analytics_service.get_market_trends(city, period)
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/neighborhood-analysis')
def get_neighborhood_analysis():
    try:
        city = request.args.get('city', 'toronto')
        neighborhood = request.args.get('neighborhood')
        analysis = analytics_service.get_neighborhood_analysis(city, neighborhood)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/investment-opportunities')
def get_investment_opportunities():
    try:
        city = request.args.get('city', 'toronto')
        budget = float(request.args.get('budget', 1000000))
        property_type = request.args.get('type', 'all')
        
        opportunities = analytics_service.get_investment_opportunities(
            city=city,
            budget=budget,
            property_type=property_type
        )
        return jsonify(opportunities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
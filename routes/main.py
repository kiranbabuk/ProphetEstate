from flask import Blueprint, render_template
from services.market_analysis import MarketAnalysis

main_bp = Blueprint('main', __name__)
market_analysis = MarketAnalysis()

@main_bp.route('/')
def home():
    market_stats = market_analysis.get_market_overview()
    return render_template('index.html', stats=market_stats)

@main_bp.route('/map')
def map_view():
    return render_template('map.html')

@main_bp.route('/valuation')
def valuation():
    return render_template('valuation.html')
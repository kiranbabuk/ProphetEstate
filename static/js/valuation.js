// AI Valuation functionality
async function submitValuation(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Analyzing...';
    submitButton.disabled = true;
    
    try {
        const response = await fetch('/api/valuation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(formData))
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showValuationResult(result);
        } else {
            throw new Error(result.error || 'Valuation failed');
        }
    } catch (error) {
        console.error('Valuation error:', error);
        showError('Failed to get valuation. Please try again.');
    } finally {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

function showValuationResult(result) {
    const resultSection = document.getElementById('valuationResult');
    resultSection.innerHTML = `
        <div class="result-card">
            <div class="result-header">
                <h2>Estimated Value</h2>
                <div class="confidence-score">
                    <div class="score-circle" style="--score: ${result.confidence_score}%">
                        <span>${result.confidence_score}%</span>
                    </div>
                    <p>Confidence Score</p>
                </div>
            </div>
            
            <div class="estimated-value">
                $${result.estimated_value.toLocaleString()}
            </div>
            
            <div class="market-trends">
                <h3>Market Trends</h3>
                <div class="trends-grid">
                    <div class="trend-item">
                        <span class="trend-label">Price Trend</span>
                        <span class="trend-value ${result.market_trends.price_trend >= 0 ? 'positive' : 'negative'}">
                            ${result.market_trends.price_trend >= 0 ? '↑' : '↓'}
                            ${Math.abs(result.market_trends.price_trend)}%
                        </span>
                    </div>
                    <div class="trend-item">
                        <span class="trend-label">Days on Market</span>
                        <span class="trend-value">
                            ${result.market_trends.avg_days_on_market} days
                        </span>
                    </div>
                    <div class="trend-item">
                        <span class="trend-label">Price per Sq Ft</span>
                        <span class="trend-value">
                            $${result.market_trends.price_per_sqft.toLocaleString()}
                        </span>
                    </div>
                </div>
            </div>
            
            <div class="comparables">
                <h3>Comparable Properties</h3>
                <div class="comparables-list">
                    ${result.comparables.map(comp => `
                        <div class="comparable-item">
                            <div class="comparable-header">
                                <h4>${comp.address}</h4>
                                <span class="similarity-score">
                                    ${comp.similarity_score}% Match
                                </span>
                            </div>
                            <div class="comparable-details">
                                <span class="price">$${comp.price.toLocaleString()}</span>
                                <span class="sold-date">Sold: ${formatDate(comp.sold_date)}</span>
                                <span class="square-feet">${comp.square_feet.toLocaleString()} sq ft</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    resultSection.classList.remove('hidden');
    resultSection.scrollIntoView({ behavior: 'smooth' });
    
    // Initialize charts
    initValuationCharts(result);
}

function initValuationCharts(result) {
    // Price Distribution Chart
    const ctx = document.getElementById('priceDistributionChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: generatePriceRanges(result.estimated_value),
            datasets: [{
                label: 'Price Distribution',
                data: generatePriceDistribution(result.estimated_value, result.comparables),
                backgroundColor: 'rgba(37, 99, 235, 0.5)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y} properties`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function generatePriceRanges(estimatedValue) {
    const range = estimatedValue * 0.2; // 20% range
    const step = range / 4;
    const ranges = [];
    
    for (let i = -2; i <= 2; i++) {
        const value = estimatedValue + (i * step);
        ranges.push(`$${(value / 1000000).toFixed(1)}M`);
    }
    
    return ranges;
}

function generatePriceDistribution(estimatedValue, comparables) {
    const range = estimatedValue * 0.2;
    const step = range / 4;
    const distribution = new Array(5).fill(0);
    
    comparables.forEach(comp => {
        const diff = comp.price - estimatedValue;
        const index = Math.floor((diff + range) / step);
        if (index >= 0 && index < distribution.length) {
            distribution[index]++;
        }
    });
    
    return distribution;
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function showError(message) {
    const errorDiv = document.getElementById('valuationError');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

// Initialize form validation and event listeners
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('valuationForm');
    form.addEventListener('submit', submitValuation);
    
    // Initialize number input validations
    const numberInputs = form.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', () => {
            const value = parseFloat(input.value);
            const min = parseFloat(input.min);
            const max = parseFloat(input.max);
            
            if (value < min) input.value = min;
            if (value > max) input.value = max;
        });
    });
});
"""
FinGuard IntelliAgent - Insights Tool
=====================================

This tool analyzes transaction data to generate financial insights,
identify patterns, and provide actionable recommendations for Kenyan SMEs.

Milestone 4 Implementation:
    - Cash flow analysis with income/expense tracking
    - Spending pattern detection with category breakdown
    - Trend analysis with forecasting
    - Personalized recommendation engine
    - Financial health scoring system
    
Author: Alfred Munga
License: MIT
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
from collections import defaultdict
import logging
import statistics

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================

class TransactionCategory(Enum):
    """Transaction categories for Kenyan SMEs."""
    UTILITIES = "utilities"
    FUEL = "fuel"
    GROCERIES = "groceries"
    RESTAURANT = "restaurant"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    AIRTIME = "airtime"
    CASH_WITHDRAWAL = "cash_withdrawal"
    BUSINESS_EXPENSE = "business_expense"
    PERSONAL_TRANSFER = "personal_transfer"
    INCOME = "income"
    OTHER = "other"


class InsightType(Enum):
    """Types of financial insights."""
    CASH_FLOW = "cash_flow"
    SPENDING_PATTERN = "spending_pattern"
    TREND = "trend"
    RECOMMENDATION = "recommendation"
    FINANCIAL_HEALTH = "financial_health"


class TimePeriod(Enum):
    """Time periods for analysis."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendDirection(Enum):
    """Direction of trends."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


# Merchant to category mapping for Kenyan market
MERCHANT_CATEGORIES = {
    # Utilities
    "KPLC": TransactionCategory.UTILITIES,
    "KENYA POWER": TransactionCategory.UTILITIES,
    "NAIROBI WATER": TransactionCategory.UTILITIES,
    "SAFARICOM": TransactionCategory.AIRTIME,
    "AIRTEL": TransactionCategory.AIRTIME,
    
    # Fuel
    "SHELL": TransactionCategory.FUEL,
    "TOTAL": TransactionCategory.FUEL,
    "KENOL": TransactionCategory.FUEL,
    "RUBIS": TransactionCategory.FUEL,
    
    # Groceries
    "NAIVAS": TransactionCategory.GROCERIES,
    "CARREFOUR": TransactionCategory.GROCERIES,
    "CHANDARANA": TransactionCategory.GROCERIES,
    "QUICKMART": TransactionCategory.GROCERIES,
    
    # Restaurants
    "KFC": TransactionCategory.RESTAURANT,
    "JAVA": TransactionCategory.RESTAURANT,
    "ARTCAFFE": TransactionCategory.RESTAURANT,
    "PIZZA INN": TransactionCategory.RESTAURANT,
    
    # Transport
    "UBER": TransactionCategory.TRANSPORT,
    "BOLT": TransactionCategory.TRANSPORT,
    "LITTLE CAB": TransactionCategory.TRANSPORT,
    
    # Entertainment
    "IMAX": TransactionCategory.ENTERTAINMENT,
    "CENTURY CINEMAX": TransactionCategory.ENTERTAINMENT,
}


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class CashFlowAnalysis:
    """
    Cash flow analysis results.
    
    Attributes:
        total_income: Total incoming funds
        total_expenses: Total outgoing funds
        net_cash_flow: Income minus expenses
        daily_breakdown: Daily cash flow data
        income_sources: Breakdown by income source
        expense_categories: Breakdown by expense category
        average_daily_income: Average income per day
        average_daily_expense: Average expense per day
        cash_flow_trend: Overall trend direction
        savings_rate: Percentage of income saved
    """
    total_income: Decimal
    total_expenses: Decimal
    net_cash_flow: Decimal
    daily_breakdown: List[Dict[str, Any]]
    income_sources: Dict[str, Decimal]
    expense_categories: Dict[str, Decimal]
    average_daily_income: Decimal
    average_daily_expense: Decimal
    cash_flow_trend: TrendDirection
    savings_rate: Decimal


@dataclass
class SpendingPattern:
    """
    Spending pattern analysis results.
    
    Attributes:
        category_breakdown: Spending by category
        top_merchants: Most frequent merchants
        daily_spending_pattern: Spending by day of week
        average_transaction: Average transaction amount
        largest_transaction: Largest single transaction
        transaction_frequency: Transactions per day
        budget_status: Budget compliance status
    """
    category_breakdown: Dict[str, Dict[str, Any]]
    top_merchants: List[Dict[str, Any]]
    daily_spending_pattern: Dict[str, Decimal]
    average_transaction: Decimal
    largest_transaction: Dict[str, Any]
    transaction_frequency: Decimal
    budget_status: Dict[str, Any]


@dataclass
class TrendAnalysis:
    """
    Trend analysis results.
    
    Attributes:
        trend_direction: Overall trend direction
        weekly_trend: Week-over-week changes
        percentage_change: Percentage change over period
        forecast: Forecasted values for next period
        seasonality: Detected seasonal patterns
    """
    trend_direction: TrendDirection
    weekly_trend: List[Dict[str, Any]]
    percentage_change: Decimal
    forecast: Dict[str, Decimal]
    seasonality: Optional[Dict[str, Any]] = None


@dataclass
class Recommendation:
    """
    Financial recommendation.
    
    Attributes:
        title: Recommendation title
        description: Detailed description
        category: Recommendation category
        priority: Priority level (high/medium/low)
        potential_savings: Estimated savings amount
        action_items: Specific actions to take
    """
    title: str
    description: str
    category: str
    priority: str
    potential_savings: Optional[Decimal] = None
    action_items: List[str] = field(default_factory=list)


@dataclass
class FinancialHealthScore:
    """
    Financial health scoring.
    
    Attributes:
        overall_score: Overall health score (0-100)
        cash_flow_score: Cash flow component score
        savings_score: Savings rate component score
        spending_score: Spending pattern component score
        trend_score: Trend stability component score
        grade: Letter grade (A/B/C/D/F)
        insights: Key insights about financial health
    """
    overall_score: int
    cash_flow_score: int
    savings_score: int
    spending_score: int
    trend_score: int
    grade: str
    insights: List[str]


# ============================================================================
# Insights Tool Class
# ============================================================================

class InsightsTool:
    """
    Tool for generating financial insights from transaction data.
    
    This tool provides:
    - Cash flow analysis with income/expense tracking
    - Spending pattern identification with categorization
    - Trend detection and forecasting
    - Personalized recommendations
    - Financial health scoring
    """
    
    def __init__(self):
        """Initialize the insights tool."""
        logger.info("Insights Tool initialized (Milestone 4)")
    
    def categorize_transaction(self, transaction: Dict[str, Any]) -> TransactionCategory:
        """
        Categorize a transaction based on merchant and type.
        
        Args:
            transaction: Transaction dictionary with 'recipient' and 'transaction_type'
            
        Returns:
            TransactionCategory enum value
        """
        recipient = transaction.get('recipient', '').upper()
        tx_type = transaction.get('transaction_type', '').lower()
        
        # Check for income
        if tx_type in ['received', 'deposit', 'reversal']:
            return TransactionCategory.INCOME
        
        # Check merchant mappings
        for merchant, category in MERCHANT_CATEGORIES.items():
            if merchant in recipient:
                return category
        
        # Check transaction type
        if 'airtime' in tx_type:
            return TransactionCategory.AIRTIME
        elif 'withdraw' in tx_type:
            return TransactionCategory.CASH_WITHDRAWAL
        elif 'paybill' in tx_type or 'till' in tx_type:
            return TransactionCategory.BUSINESS_EXPENSE
        elif 'send' in tx_type or 'transfer' in tx_type:
            return TransactionCategory.PERSONAL_TRANSFER
        
        return TransactionCategory.OTHER
    
    def analyze_cash_flow(
        self,
        transactions: List[Dict[str, Any]],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CashFlowAnalysis:
        """
        Analyze cash flow patterns.
        
        Args:
            transactions: List of parsed transactions
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            CashFlowAnalysis object with comprehensive cash flow data
        """
        logger.info(f"Analyzing cash flow for {len(transactions)} transactions")
        
        # Filter by date range if specified
        filtered_txs = self._filter_by_date(transactions, start_date, end_date)
        
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        income_sources = defaultdict(Decimal)
        expense_categories = defaultdict(Decimal)
        daily_data = defaultdict(lambda: {'income': Decimal('0'), 'expenses': Decimal('0')})
        
        for tx in filtered_txs:
            amount = Decimal(str(tx.get('amount', 0)))
            date = tx.get('timestamp', datetime.now()).date()
            category = self.categorize_transaction(tx)
            recipient = tx.get('recipient', 'Unknown')
            
            if category == TransactionCategory.INCOME:
                total_income += amount
                income_sources[recipient] += amount
                daily_data[date]['income'] += amount
            else:
                total_expenses += amount
                expense_categories[category.value] += amount
                daily_data[date]['expenses'] += amount
        
        # Calculate daily breakdown
        daily_breakdown = [
            {
                'date': str(date),
                'income': float(data['income']),
                'expenses': float(data['expenses']),
                'net': float(data['income'] - data['expenses'])
            }
            for date, data in sorted(daily_data.items())
        ]
        
        # Calculate averages
        num_days = len(daily_data) or 1
        avg_daily_income = total_income / num_days
        avg_daily_expense = total_expenses / num_days
        
        # Determine trend
        if len(daily_breakdown) >= 2:
            recent = sum(Decimal(str(d['net'])) for d in daily_breakdown[-7:])
            older = sum(Decimal(str(d['net'])) for d in daily_breakdown[:7])
            if recent > older * Decimal('1.1'):
                trend = TrendDirection.INCREASING
            elif recent < older * Decimal('0.9'):
                trend = TrendDirection.DECREASING
            else:
                trend = TrendDirection.STABLE
        else:
            trend = TrendDirection.STABLE
        
        # Calculate savings rate
        net_cash_flow = total_income - total_expenses
        savings_rate = (net_cash_flow / total_income * 100) if total_income > 0 else Decimal('0')
        
        return CashFlowAnalysis(
            total_income=total_income,
            total_expenses=total_expenses,
            net_cash_flow=net_cash_flow,
            daily_breakdown=daily_breakdown,
            income_sources=dict(income_sources),
            expense_categories=dict(expense_categories),
            average_daily_income=avg_daily_income,
            average_daily_expense=avg_daily_expense,
            cash_flow_trend=trend,
            savings_rate=savings_rate.quantize(Decimal('0.01'))
        )
    
    def analyze_spending_patterns(
        self,
        transactions: List[Dict[str, Any]],
        budget: Optional[Dict[str, Decimal]] = None
    ) -> SpendingPattern:
        """
        Analyze spending patterns and categorize expenses.
        
        Args:
            transactions: List of parsed transactions
            budget: Optional budget limits by category
            
        Returns:
            SpendingPattern object with spending analysis
        """
        logger.info(f"Analyzing spending patterns for {len(transactions)} transactions")
        
        category_data = defaultdict(lambda: {'amount': Decimal('0'), 'count': 0, 'transactions': []})
        merchant_data = defaultdict(lambda: {'amount': Decimal('0'), 'count': 0})
        daily_spending = defaultdict(Decimal)
        
        all_amounts = []
        largest = {'amount': Decimal('0'), 'transaction': {}}
        
        for tx in transactions:
            category = self.categorize_transaction(tx)
            
            # Skip income transactions
            if category == TransactionCategory.INCOME:
                continue
            
            amount = Decimal(str(tx.get('amount', 0)))
            recipient = tx.get('recipient', 'Unknown')
            timestamp = tx.get('timestamp', datetime.now())
            day_of_week = timestamp.strftime('%A')
            
            # Category breakdown
            category_data[category.value]['amount'] += amount
            category_data[category.value]['count'] += 1
            category_data[category.value]['transactions'].append(tx)
            
            # Merchant tracking
            merchant_data[recipient]['amount'] += amount
            merchant_data[recipient]['count'] += 1
            
            # Daily pattern
            daily_spending[day_of_week] += amount
            
            # Track amounts and largest
            all_amounts.append(amount)
            if amount > largest['amount']:
                largest = {'amount': amount, 'transaction': tx}
        
        # Build category breakdown
        total_expenses = sum(data['amount'] for data in category_data.values())
        category_breakdown = {}
        
        for category, data in category_data.items():
            percentage = (data['amount'] / total_expenses * 100) if total_expenses > 0 else Decimal('0')
            budget_limit = budget.get(category) if budget else None
            budget_used = (data['amount'] / budget_limit * 100) if budget_limit else None
            
            category_breakdown[category] = {
                'amount': float(data['amount']),
                'percentage': float(percentage.quantize(Decimal('0.01'))),
                'transaction_count': data['count'],
                'budget_limit': float(budget_limit) if budget_limit else None,
                'budget_used_percent': float(budget_used.quantize(Decimal('0.01'))) if budget_used else None,
                'over_budget': budget_used > 100 if budget_used else False
            }
        
        # Top merchants
        top_merchants = sorted(
            [{'merchant': m, 'amount': float(d['amount']), 'count': d['count']}
             for m, d in merchant_data.items()],
            key=lambda x: x['amount'],
            reverse=True
        )[:10]
        
        # Calculate averages
        avg_transaction = sum(all_amounts) / len(all_amounts) if all_amounts else Decimal('0')
        
        # Calculate transaction frequency
        if transactions:
            date_range = (max(tx.get('timestamp', datetime.now()) for tx in transactions) -
                         min(tx.get('timestamp', datetime.now()) for tx in transactions)).days + 1
            frequency = Decimal(len(transactions)) / Decimal(date_range)
        else:
            frequency = Decimal('0')
        
        # Budget status
        budget_status = {
            'has_budget': budget is not None,
            'categories_over_budget': sum(1 for c in category_breakdown.values() if c.get('over_budget', False)),
            'total_budget': float(sum(budget.values())) if budget else None,
            'total_spent': float(total_expenses),
            'budget_remaining': float(sum(budget.values()) - total_expenses) if budget else None
        }
        
        return SpendingPattern(
            category_breakdown=category_breakdown,
            top_merchants=top_merchants,
            daily_spending_pattern={day: float(amount) for day, amount in daily_spending.items()},
            average_transaction=avg_transaction,
            largest_transaction={'amount': float(largest['amount']), **largest['transaction']},
            transaction_frequency=frequency.quantize(Decimal('0.01')),
            budget_status=budget_status
        )
    
    def detect_trends(
        self,
        transactions: List[Dict[str, Any]],
        period: TimePeriod = TimePeriod.WEEKLY
    ) -> TrendAnalysis:
        """
        Detect spending and income trends.
        
        Args:
            transactions: List of parsed transactions
            period: Time period for trend analysis
            
        Returns:
            TrendAnalysis object with trend data
        """
        logger.info(f"Detecting {period.value} trends")
        
        # Group transactions by week
        weekly_data = defaultdict(lambda: {'income': Decimal('0'), 'expenses': Decimal('0')})
        
        for tx in transactions:
            timestamp = tx.get('timestamp', datetime.now())
            week_start = timestamp - timedelta(days=timestamp.weekday())
            week_key = week_start.strftime('%Y-W%U')
            
            amount = Decimal(str(tx.get('amount', 0)))
            category = self.categorize_transaction(tx)
            
            if category == TransactionCategory.INCOME:
                weekly_data[week_key]['income'] += amount
            else:
                weekly_data[week_key]['expenses'] += amount
        
        # Build weekly trend
        weekly_trend = []
        sorted_weeks = sorted(weekly_data.items())
        
        for week, data in sorted_weeks:
            net = data['income'] - data['expenses']
            weekly_trend.append({
                'week': week,
                'income': float(data['income']),
                'expenses': float(data['expenses']),
                'net': float(net)
            })
        
        # Determine trend direction
        if len(weekly_trend) >= 2:
            recent_net = Decimal(str(weekly_trend[-1]['net']))
            previous_net = Decimal(str(weekly_trend[-2]['net']))
            
            if recent_net > previous_net * Decimal('1.1'):
                direction = TrendDirection.INCREASING
            elif recent_net < previous_net * Decimal('0.9'):
                direction = TrendDirection.DECREASING
            else:
                direction = TrendDirection.STABLE
            
            # Calculate percentage change
            pct_change = ((recent_net - previous_net) / abs(previous_net) * 100) if previous_net != 0 else Decimal('0')
        else:
            direction = TrendDirection.STABLE
            pct_change = Decimal('0')
        
        # Simple forecast (moving average)
        if len(weekly_trend) >= 3:
            recent_values = [Decimal(str(w['net'])) for w in weekly_trend[-3:]]
            forecast_net = sum(recent_values) / len(recent_values)
        else:
            forecast_net = Decimal(str(weekly_trend[-1]['net'])) if weekly_trend else Decimal('0')
        
        forecast = {
            'next_period': float(forecast_net),
            'confidence': 'medium',
            'method': 'moving_average'
        }
        
        return TrendAnalysis(
            trend_direction=direction,
            weekly_trend=weekly_trend,
            percentage_change=pct_change.quantize(Decimal('0.01')),
            forecast=forecast
        )
    
    def generate_recommendations(
        self,
        cash_flow: CashFlowAnalysis,
        spending: SpendingPattern,
        trends: TrendAnalysis
    ) -> List[Recommendation]:
        """
        Generate personalized financial recommendations.
        
        Args:
            cash_flow: Cash flow analysis results
            spending: Spending pattern analysis results
            trends: Trend analysis results
            
        Returns:
            List of Recommendation objects
        """
        logger.info("Generating recommendations")
        
        recommendations = []
        
        # Cash flow recommendations
        if cash_flow.net_cash_flow < 0:
            recommendations.append(Recommendation(
                title="Negative Cash Flow Alert",
                description=f"Your expenses (KES {cash_flow.total_expenses:,.2f}) exceed your income "
                           f"(KES {cash_flow.total_income:,.2f}) by KES {abs(cash_flow.net_cash_flow):,.2f}.",
                category="cash_flow",
                priority="high",
                potential_savings=abs(cash_flow.net_cash_flow),
                action_items=[
                    "Review and reduce non-essential expenses",
                    "Identify opportunities to increase income",
                    "Create a strict budget to control spending"
                ]
            ))
        
        # Savings rate recommendations
        if cash_flow.savings_rate < 10:
            recommendations.append(Recommendation(
                title="Low Savings Rate",
                description=f"You're saving only {cash_flow.savings_rate:.1f}% of your income. "
                           "Aim for at least 20% for financial stability.",
                category="savings",
                priority="high",
                action_items=[
                    "Set up automatic savings transfers",
                    "Reduce discretionary spending by 10-15%",
                    "Look for additional income streams"
                ]
            ))
        
        # Budget recommendations
        if spending.budget_status.get('categories_over_budget', 0) > 0:
            over_budget_cats = [cat for cat, data in spending.category_breakdown.items() 
                              if data.get('over_budget', False)]
            recommendations.append(Recommendation(
                title="Budget Exceeded in Multiple Categories",
                description=f"You've exceeded your budget in {len(over_budget_cats)} categories: "
                           f"{', '.join(over_budget_cats)}.",
                category="budget",
                priority="high",
                action_items=[
                    f"Reduce spending in {', '.join(over_budget_cats[:3])}",
                    "Review budget allocations - they may be unrealistic",
                    "Track expenses daily to stay on target"
                ]
            ))
        
        # Spending pattern recommendations
        top_category = max(spending.category_breakdown.items(), 
                          key=lambda x: x[1]['amount'])[0] if spending.category_breakdown else None
        
        if top_category and spending.category_breakdown[top_category]['percentage'] > 40:
            amount = spending.category_breakdown[top_category]['amount']
            pct = spending.category_breakdown[top_category]['percentage']
            potential = Decimal(str(amount)) * Decimal('0.15')  # 15% reduction
            
            recommendations.append(Recommendation(
                title=f"High Spending in {top_category.replace('_', ' ').title()}",
                description=f"You're spending {pct:.1f}% of your budget on {top_category}. "
                           f"This is significantly higher than recommended.",
                category="spending",
                priority="medium",
                potential_savings=potential,
                action_items=[
                    f"Look for cheaper alternatives in {top_category}",
                    "Consider bulk buying or loyalty programs",
                    f"Set a monthly limit for {top_category} expenses"
                ]
            ))
        
        # Trend recommendations
        if trends.trend_direction == TrendDirection.DECREASING:
            recommendations.append(Recommendation(
                title="Negative Financial Trend Detected",
                description=f"Your net cash flow is declining (down {abs(trends.percentage_change):.1f}% "
                           "from previous period).",
                category="trend",
                priority="high",
                action_items=[
                    "Identify the cause of declining income or rising expenses",
                    "Take immediate action to reverse the trend",
                    "Review your business model or income sources"
                ]
            ))
        
        return recommendations
    
    def calculate_financial_health_score(
        self,
        cash_flow: CashFlowAnalysis,
        spending: SpendingPattern,
        trends: TrendAnalysis
    ) -> FinancialHealthScore:
        """
        Calculate overall financial health score (0-100).
        
        Args:
            cash_flow: Cash flow analysis results
            spending: Spending pattern analysis results
            trends: Trend analysis results
            
        Returns:
            FinancialHealthScore object
        """
        logger.info("Calculating financial health score")
        
        # Cash flow score (0-25 points)
        if cash_flow.net_cash_flow > 0:
            cf_score = min(25, int(cash_flow.savings_rate / 4))
        else:
            cf_score = 0
        
        # Savings score (0-25 points)
        if cash_flow.savings_rate >= 20:
            savings_score = 25
        elif cash_flow.savings_rate >= 10:
            savings_score = 15
        elif cash_flow.savings_rate >= 5:
            savings_score = 10
        else:
            savings_score = max(0, int(cash_flow.savings_rate * 2))
        
        # Spending score (0-25 points)
        budget_compliance = 25
        if spending.budget_status.get('has_budget'):
            over_budget = spending.budget_status.get('categories_over_budget', 0)
            budget_compliance = max(0, 25 - (over_budget * 5))
        
        spending_score = budget_compliance
        
        # Trend score (0-25 points)
        if trends.trend_direction == TrendDirection.INCREASING:
            trend_score = 25
        elif trends.trend_direction == TrendDirection.STABLE:
            trend_score = 15
        else:  # DECREASING
            trend_score = 5
        
        # Calculate overall score
        overall = cf_score + savings_score + spending_score + trend_score
        
        # Assign grade
        if overall >= 90:
            grade = 'A'
        elif overall >= 80:
            grade = 'B'
        elif overall >= 70:
            grade = 'C'
        elif overall >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        # Generate insights
        insights = []
        
        if cf_score < 15:
            insights.append("Cash flow needs improvement - focus on increasing income or reducing expenses")
        if savings_score < 15:
            insights.append("Savings rate is below recommended levels - aim for 20% of income")
        if spending_score < 20:
            insights.append("Budget management needs attention - multiple categories over budget")
        if trend_score < 15:
            insights.append("Financial trend is concerning - take action to reverse negative patterns")
        
        if overall >= 80:
            insights.append("Strong financial health - maintain current practices")
        
        return FinancialHealthScore(
            overall_score=overall,
            cash_flow_score=cf_score,
            savings_score=savings_score,
            spending_score=spending_score,
            trend_score=trend_score,
            grade=grade,
            insights=insights
        )
    
    def _filter_by_date(
        self,
        transactions: List[Dict[str, Any]],
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Filter transactions by date range."""
        if not start_date and not end_date:
            return transactions
        
        filtered = []
        for tx in transactions:
            tx_date = tx.get('timestamp', datetime.now())
            if start_date and tx_date < start_date:
                continue
            if end_date and tx_date > end_date:
                continue
            filtered.append(tx)
        
        return filtered


# ============================================================================
# Convenience Functions
# ============================================================================

def generate_comprehensive_insights(
    transactions: List[Dict[str, Any]],
    budget: Optional[Dict[str, Decimal]] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive financial insights from transactions.
    
    Args:
        transactions: List of parsed transactions
        budget: Optional budget limits by category
        
    Returns:
        Dict containing all insights and analyses
    """
    tool = InsightsTool()
    
    try:
        # Perform all analyses
        cash_flow = tool.analyze_cash_flow(transactions)
        spending = tool.analyze_spending_patterns(transactions, budget)
        trends = tool.detect_trends(transactions)
        recommendations = tool.generate_recommendations(cash_flow, spending, trends)
        health_score = tool.calculate_financial_health_score(cash_flow, spending, trends)
        
        return {
            "success": True,
            "cash_flow": {
                "total_income": float(cash_flow.total_income),
                "total_expenses": float(cash_flow.total_expenses),
                "net_cash_flow": float(cash_flow.net_cash_flow),
                "savings_rate": float(cash_flow.savings_rate),
                "trend": cash_flow.cash_flow_trend.value,
                "daily_breakdown": cash_flow.daily_breakdown
            },
            "spending": {
                "category_breakdown": spending.category_breakdown,
                "top_merchants": spending.top_merchants,
                "daily_pattern": spending.daily_spending_pattern,
                "budget_status": spending.budget_status
            },
            "trends": {
                "direction": trends.trend_direction.value,
                "weekly_trend": trends.weekly_trend,
                "percentage_change": float(trends.percentage_change),
                "forecast": trends.forecast
            },
            "recommendations": [
                {
                    "title": r.title,
                    "description": r.description,
                    "category": r.category,
                    "priority": r.priority,
                    "potential_savings": float(r.potential_savings) if r.potential_savings else None,
                    "action_items": r.action_items
                }
                for r in recommendations
            ],
            "health_score": {
                "overall_score": health_score.overall_score,
                "grade": health_score.grade,
                "components": {
                    "cash_flow": health_score.cash_flow_score,
                    "savings": health_score.savings_score,
                    "spending": health_score.spending_score,
                    "trends": health_score.trend_score
                },
                "insights": health_score.insights
            },
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Insights generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    """Test the insights tool with sample data."""
    
    # Sample transaction data
    sample_transactions = [
        {
            "amount": 5000,
            "recipient": "CUSTOMER A",
            "transaction_type": "received",
            "timestamp": datetime.now() - timedelta(days=5)
        },
        {
            "amount": 1500,
            "recipient": "KPLC",
            "transaction_type": "paybill",
            "timestamp": datetime.now() - timedelta(days=3)
        },
        {
            "amount": 3000,
            "recipient": "SHELL PETROL",
            "transaction_type": "paybill",
            "timestamp": datetime.now() - timedelta(days=2)
        },
        {
            "amount": 2500,
            "recipient": "NAIVAS",
            "transaction_type": "till",
            "timestamp": datetime.now() - timedelta(days=1)
        }
    ]
    
    print("=" * 60)
    print("FinGuard IntelliAgent - Financial Insights Tool")
    print("=" * 60)
    
    # Generate insights
    insights = generate_comprehensive_insights(sample_transactions)
    
    if insights["success"]:
        print("\n✅ Insights Generated Successfully\n")
        
        print("Cash Flow Analysis:")
        print(f"  Income: KES {insights['cash_flow']['total_income']:,.2f}")
        print(f"  Expenses: KES {insights['cash_flow']['total_expenses']:,.2f}")
        print(f"  Net: KES {insights['cash_flow']['net_cash_flow']:,.2f}")
        print(f"  Savings Rate: {insights['cash_flow']['savings_rate']:.1f}%")
        
        print("\nFinancial Health Score:")
        print(f"  Grade: {insights['health_score']['grade']}")
        print(f"  Score: {insights['health_score']['overall_score']}/100")
        
        print("\nTop Recommendations:")
        for i, rec in enumerate(insights['recommendations'][:3], 1):
            print(f"  {i}. {rec['title']} ({rec['priority']} priority)")
    else:
        print(f"\n❌ Error: {insights['error']}")
    
    print("\n" + "=" * 60)

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ..models import Transaction, BudgetGoal, db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/spending', methods=['GET'])
@jwt_required()
def get_spending_analytics():
    user_id = get_jwt_identity()
    results = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter_by(
        user_id=user_id,
        transaction_type='expense'
    ).group_by(Transaction.category).all()
    
    return jsonify({
        'categories': [{
            'category': r.category,
            'total': float(r.total)
        } for r in results]
    })

@analytics_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_spending_trends():
    user_id = get_jwt_identity()
    results = db.session.query(
        func.strftime('%Y-%m', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter_by(
        user_id=user_id
    ).group_by('month').order_by('month').all()
    
    return jsonify({
        'trends': [{
            'month': r.month,
            'total': float(r.total)
        } for r in results]
    })

@analytics_bp.route('/budget-status', methods=['GET'])
@jwt_required()
def get_budget_status():
    user_id = get_jwt_identity()
    
    # Get current month's spending by category
    current_month = datetime.now().replace(day=1)
    next_month = current_month + relativedelta(months=1)
    
    spending = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('spent')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.date >= current_month,
        Transaction.date < next_month,
        Transaction.transaction_type == 'expense'
    ).group_by(Transaction.category).all()
    
    # Get budget goals
    budget_goals = BudgetGoal.query.filter_by(user_id=user_id).all()
    
    status = {}
    for goal in budget_goals:
        spent = next((s.spent for s in spending if s.category == goal.category), 0)
        status[goal.category] = {
            'budget': goal.amount,
            'spent': float(spent),
            'remaining': goal.amount - float(spent),
            'status': goal.check_alert(float(spent))
        }
    
    return jsonify(status)
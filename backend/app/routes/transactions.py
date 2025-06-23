# /api/transactions
GET /transactions  # Get all user transactions with filtering
POST /transactions  # Create new transaction
GET /transactions/<id>  # Get single transaction
PUT /transactions/<id>  # Update transaction
DELETE /transactions/<id>  # Delete transaction
GET /transactions/summary  # Get monthly summary using Transaction.get_monthly_summary()
GET /transactions/category-summary  # Get summary by category
GET /transactions/search  # Search transactions by description or category

# /api/budget-goals
GET /budget-goals  # Get all user budget goals
POST /budget-goals  # Create new budget goal
GET /budget-goals/<id>  # Get single budget goal
PUT /budget-goals/<id>  # Update budget goal
GET /budget-goals/alerts  # Get alerts using BudgetGoal.check_alert()

# /api/exports
POST /exports/csv  # Export transactions to CSV
POST /exports/pdf  # Export transactions to PDF
GET /exports  # Get export history from ExportLog

# /api/analytics
GET /analytics/spending  # Get spending by category
GET /analytics/trends  # Get spending trends over time
GET /analytics/budget-status  # Get current budget status vs goals

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models import Transaction, db
from marshmallow import Schema, fields, validate
from dateutil.relativedelta import relativedelta

logging.basicConfig(level=INFO)
logger = logging.getLogger(__name__)

transaction_bp = Blueprint('transactions', __name__)

class TransactionSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(required=True)
    category = fields.Str(required=True)
    transaction_type = fields.Str(validate=validate.OneOf(['income', 'expense']))
    is_recurring = fields.Boolean()
    recurring_interval = fields.Str(validate=validate.OneOf(['daily', 'weekly', 'monthly', 'yearly']))

transaction_schema = TransactionSchema()

def calculate_next_recurring_date(current_date, interval):
    """Calculate next date based on recurring interval"""
    if interval == 'daily':
        return current_date + relativedelta(days=1)
    elif interval == 'weekly':
        return current_date + relativedelta(weeks=1)
    elif interval == 'monthly':
        return current_date + relativedelta(months=1)
    elif interval == 'yearly':
        return current_date + relativedelta(years=1)
    return None

def handle_recurring_transaction(transaction):
    """Helper function to handle recurring transactions"""
    if transaction.is_recurring:
        next_transaction = Transaction(
            user_id=transaction.user_id,
            amount=transaction.amount,
            description=transaction.description,
            category=transaction.category,
            transaction_type=transaction.transaction_type,
            is_recurring=True,
            recurring_interval=transaction.recurring_interval,
            date=calculate_next_recurring_date(transaction.date, transaction.recurring_interval)
        )
        db.session.add(next_transaction)

@transaction_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get query parameters for filtering
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')
    
    # Base query
    query = Transaction.query.filter_by(user_id=user_id)
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    # Add pagination
    paginated_transactions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'amount': t.amount,
            'description': t.description,
            'category': t.category,
            'transaction_type': t.transaction_type,
            'date': t.date.isoformat(),
            'is_recurring': t.is_recurring,
            'recurring_interval': t.recurring_interval
        } for t in paginated_transactions.items],
        'total': paginated_transactions.total,
        'pages': paginated_transactions.pages,
        'current_page': page
    })

@transaction_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input data
    errors = transaction_schema.validate(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    transaction = Transaction(
        user_id=user_id,
        amount=data['amount'],
        description=data.get('description'),
        category=data.get('category'),
        transaction_type=data['transaction_type'],
        is_recurring=data.get('is_recurring', False),
        recurring_interval=data.get('recurring_interval')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    handle_recurring_transaction(transaction)
    
    return jsonify({
        'id': transaction.id,
        'message': 'Transaction created successfully'
    }), 201

@transaction_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_transaction(id):
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    return jsonify({
        'id': transaction.id,
        'amount': transaction.amount,
        'description': transaction.description,
        'category': transaction.category,
        'transaction_type': transaction.transaction_type,
        'date': transaction.date.isoformat(),
        'is_recurring': transaction.is_recurring,
        'recurring_interval': transaction.recurring_interval
    })

@transaction_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input data
    errors = transaction_schema.validate(data, partial=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    for key, value in data.items():
        if hasattr(transaction, key):
            setattr(transaction, key, value)
    
    db.session.commit()
    return jsonify({'message': 'Transaction updated successfully'})

@transaction_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'})

@transaction_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = get_jwt_identity()
    month = int(request.args.get('month', datetime.now().month))
    year = int(request.args.get('year', datetime.now().year))
    
    transactions = Transaction.get_monthly_summary(user_id, month, year)
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    
    return jsonify({
        'month': month,
        'year': year,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net': total_income - total_expenses
    })

@transaction_bp.route('/category-summary', methods=['GET'])
@jwt_required()
def get_category_summary():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    
    category_totals = {}
    for t in transactions:
        if t.category not in category_totals:
            category_totals[t.category] = 0
        category_totals[t.category] += t.amount
    
    return jsonify(category_totals)

@transaction_bp.route('/search', methods=['GET'])
@jwt_required()
def search_transactions():
    user_id = get_jwt_identity()
    search_term = request.args.get('q', '')
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if search_term:
        query = query.filter(
            db.or_(
                Transaction.description.ilike(f'%{search_term}%'),
                Transaction.category.ilike(f'%{search_term}%')
            )
        )
    
    transactions = query.all()
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'description': t.description,
        'category': t.category,
        'transaction_type': t.transaction_type,
        'date': t.date.isoformat()
    } for t in transactions])

@transaction_bp.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
    return jsonify({
        'error': str(error),
        'message': 'An error occurred while processing your request'
    }), 500
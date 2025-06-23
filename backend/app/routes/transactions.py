
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

VALID_CATEGORIES = [
    'food', 'transport', 'utilities', 'entertainment', 
    'healthcare', 'shopping', 'housing', 'other'
]

class TransactionSchema(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(required=True)
    category = fields.Str(required=True, validate=validate.OneOf(VALID_CATEGORIES))
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

def validate_date_range(start_date, end_date):
    """Validate date range for transaction queries"""
    try:
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start_date and start > end:
                return False, "Start date cannot be after end date"
        return True, None
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

def paginate_query(query, page=1, per_page=10):
    """Helper function to handle pagination"""
    try:
        page = max(1, int(page))
        per_page = min(100, max(1, int(per_page)))
    except (TypeError, ValueError):
        page = 1
        per_page = 10
    
    return query.paginate(page=page, per_page=per_page, error_out=False)

def format_transaction_response(transaction):
    """Helper function to format transaction response"""
    return {
        'id': transaction.id,
        'amount': float(transaction.amount),
        'description': transaction.description,
        'category': transaction.category,
        'transaction_type': transaction.transaction_type,
        'date': transaction.date.isoformat(),
        'is_recurring': transaction.is_recurring,
        'recurring_interval': transaction.recurring_interval
    }

@transaction_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    query = Transaction.query.filter_by(user_id=user_id)
    
    # Apply filters and pagination
    paginated = paginate_query(query, 
                             request.args.get('page'), 
                             request.args.get('per_page'))
    
    return jsonify({
        'transactions': [format_transaction_response(t) for t in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page
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
    
    return jsonify(format_transaction_response(transaction))

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
    return jsonify([format_transaction_response(t) for t in transactions])

@transaction_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_transaction_statistics():
    user_id = get_jwt_identity()
    
    # Get time period from query params
    period = request.args.get('period', 'month')  # 'week', 'month', 'year'
    
    # Calculate date range
    end_date = datetime.now()
    if period == 'week':
        start_date = end_date - relativedelta(weeks=1)
    elif period == 'month':
        start_date = end_date - relativedelta(months=1)
    else:
        start_date = end_date - relativedelta(years=1)
    
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.date.between(start_date, end_date)
    ).all()
    
    return jsonify({
        'total_transactions': len(transactions),
        'average_amount': sum(t.amount for t in transactions) / len(transactions) if transactions else 0,
        'most_common_category': max(set(t.category for t in transactions), key=lambda x: sum(1 for t in transactions if t.category == x)) if transactions else None,
        'period': period
    })

@transaction_bp.route('/bulk', methods=['POST'])
@jwt_required()
def bulk_create_transactions():
    user_id = get_jwt_identity()
    transactions_data = request.get_json()
    
    if not isinstance(transactions_data, list):
        return jsonify({'error': 'Expected a list of transactions'}), 400
    
    created_transactions = []
    for data in transactions_data:
        errors = transaction_schema.validate(data)
        if errors:
            return jsonify({'errors': errors, 'at_index': len(created_transactions)}), 400
            
        transaction = Transaction(
            user_id=user_id,
            amount=data['amount'],
            description=data.get('description'),
            category=data.get('category'),
            transaction_type=data['transaction_type']
        )
        created_transactions.append(transaction)
    
    db.session.bulk_save_objects(created_transactions)
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully created {len(created_transactions)} transactions',
        'count': len(created_transactions)
    }), 201

@transaction_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()
    
    # Get unique categories for user
    categories = db.session.query(Transaction.category)\
        .filter_by(user_id=user_id)\
        .distinct()\
        .all()
    
    return jsonify({
        'categories': [category[0] for category in categories]
    })

@transaction_bp.route('/report', methods=['GET'])
@jwt_required()
def generate_report():
    user_id = get_jwt_identity()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Validate date range
    is_valid, error = validate_date_range(start_date, end_date)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    transactions = query.all()
    
    report = {
        'period': {
            'start': start_date,
            'end': end_date
        },
        'summary': {
            'total_income': sum(t.amount for t in transactions if t.transaction_type == 'income'),
            'total_expenses': sum(t.amount for t in transactions if t.transaction_type == 'expense'),
            'transaction_count': len(transactions)
        },
        'category_breakdown': {},
        'monthly_totals': {}
    }
    
    # Add category breakdown
    for t in transactions:
        if t.category not in report['category_breakdown']:
            report['category_breakdown'][t.category] = 0
        report['category_breakdown'][t.category] += t.amount
    
    # Add monthly totals
    for t in transactions:
        month_key = t.date.strftime('%Y-%m')
        if month_key not in report['monthly_totals']:
            report['monthly_totals'][month_key] = 0
        report['monthly_totals'][month_key] += t.amount
    
    return jsonify(report)

@transaction_bp.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
    return jsonify({
        'error': str(error),
        'message': 'An error occurred while processing your request'
    }), 500
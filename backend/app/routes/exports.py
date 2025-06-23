import csv
import io
from flask import Blueprint, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Transaction, ExportLog, db

export_bp = Blueprint('exports', __name__)

@export_bp.route('/csv', methods=['POST'])
@jwt_required()
def export_csv():
    user_id = get_jwt_identity()
    
    # Get transactions
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Amount', 'Description', 'Category', 'Type'])
    
    for transaction in transactions:
        writer.writerow([
            transaction.date.isoformat(),
            transaction.amount,
            transaction.description,
            transaction.category,
            transaction.transaction_type
        ])
    
    # Log export
    export_log = ExportLog(
        user_id=user_id,
        export_type='csv',
        status='completed'
    )
    db.session.add(export_log)
    db.session.commit()
    
    # Return file
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'transactions_{datetime.now().strftime("%Y%m%d")}.csv'
    )
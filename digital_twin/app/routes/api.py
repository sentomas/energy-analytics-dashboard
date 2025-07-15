from flask import Blueprint, jsonify, request
from app.models.cnc_data import CNCDataModel
from app.services.digital_twin_service import DigitalTwinService
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

# Initialize services
mongo_uri = "mongodb://petrus:petrusConnect@10.20.30.130:27017/?authMechanism=DEFAULT"
cnc_model = CNCDataModel(mongo_uri)
twin_service = DigitalTwinService(cnc_model)

@api_bp.route('/twin/<machine_id>')
def get_twin_state(machine_id):
    """Get digital twin state for a specific machine"""
    try:
        twin_state = twin_service.get_twin_state(machine_id)
        return jsonify(twin_state)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/machines')
def get_machines():
    """Get list of all machines"""
    try:
        # Get unique machine IDs from the database
        machines = cnc_model.collection.distinct('machine_id')
        machine_list = []
        
        for machine_id in machines:
            status = cnc_model.get_machine_status(machine_id)
            machine_list.append({
                'id': machine_id,
                'name': f'CNC Machine {machine_id}',
                'status': status['status'],
                'last_seen': status['last_seen'].isoformat() if status['last_seen'] else None
            })
        
        return jsonify(machine_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/data/<machine_id>')
def get_machine_data(machine_id):
    """Get historical data for a machine"""
    try:
        hours = request.args.get('hours', 24, type=int)
        start_time = datetime.now() - timedelta(hours=hours)
        
        data = cnc_model.get_cutting_time_data(machine_id, start_time)
        
        # Convert datetime objects to ISO format for JSON serialization
        for item in data:
            if 'timestamp' in item:
                item['timestamp'] = item['timestamp'].isoformat()
            if '_id' in item:
                item['_id'] = str(item['_id'])
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/data', methods=['POST'])
def add_cutting_data():
    """Add new cutting data"""
    try:
        data = request.json
        result_id = cnc_model.insert_cutting_data(data)
        return jsonify({'success': True, 'id': result_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
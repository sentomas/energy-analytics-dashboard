from flask import Blueprint, render_template, request, jsonify
from app.models.cnc_data import CNCDataModel
from app.services.digital_twin_service import DigitalTwinService
import os

main_bp = Blueprint('main', __name__)

# Initialize services
mongo_uri = "mongodb://petrus:petrusConnect@10.20.30.130:27017/?authMechanism=DEFAULT"
cnc_model = CNCDataModel(mongo_uri)
twin_service = DigitalTwinService(cnc_model)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard/<machine_id>')
def dashboard(machine_id):
    return render_template('dashboard.html', machine_id=machine_id)

@main_bp.route('/machines')
def machines():
    return render_template('machines.html')
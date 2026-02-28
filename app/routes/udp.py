"""UDP (Unified Data Pipeline) configuration API routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.udp_configuration import UDPConfiguration
from datetime import datetime

udp_bp = Blueprint('udp', __name__)


def validate_udp_data(data):
    """Validate required UDP configuration fields. Returns error message or None."""
    if not data:
        return 'Request body is required'
    required = ['name', 'kind', 'author', 'spec']
    for field in required:
        if not data.get(field):
            return f'{field} is required'
    spec = data.get('spec', {})
    if not isinstance(spec, dict):
        return 'spec must be an object'
    input_spec = spec.get('input', {})
    if not input_spec or not input_spec.get('input_directory') or not input_spec.get('format'):
        return 'spec.input.input_directory and spec.input.format are required'
    output_spec = spec.get('output', {})
    if not output_spec or not output_spec.get('catalog_name') or not output_spec.get('schema_name') or not output_spec.get('table_name'):
        return 'spec.output.catalog_name, schema_name, and table_name are required'
    return None


@udp_bp.route('', methods=['GET'])
@jwt_required()
@limiter.limit("100 per minute")
def get_udp_configurations():
    """Get all UDP configurations"""
    try:
        configs = UDPConfiguration.query.all()
        return jsonify([c.to_dict() for c in configs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@udp_bp.route('/<name>', methods=['GET'])
@jwt_required()
@limiter.limit("100 per minute")
def get_udp_configuration(name):
    """Get a specific UDP configuration by name"""
    try:
        config = UDPConfiguration.query.get(name)
        if not config:
            return jsonify({'error': 'UDP configuration not found'}), 404
        return jsonify({'configuration': config.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@udp_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_udp_configuration():
    """Create a new UDP configuration"""
    try:
        data = request.get_json()
        err = validate_udp_data(data)
        if err:
            return jsonify({'error': err}), 400

        if UDPConfiguration.query.get(data['name']):
            return jsonify({'error': f"UDP configuration '{data['name']}' already exists"}), 400

        config = UDPConfiguration(
            name=data['name'],
            kind=data['kind'],
            author=data['author'],
            description=data.get('description', ''),
            options=data.get('options', []),
            spec=data['spec'],
            spark_config=data.get('spark_config', [])
        )
        db.session.add(config)
        db.session.commit()

        return jsonify({
            'message': 'UDP configuration created successfully',
            'configuration': config.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@udp_bp.route('/<name>', methods=['PUT'])
@jwt_required()
@limiter.limit("20 per minute")
def update_udp_configuration(name):
    """Update an existing UDP configuration"""
    try:
        config = UDPConfiguration.query.get(name)
        if not config:
            return jsonify({'error': 'UDP configuration not found'}), 404

        data = request.get_json()
        err = validate_udp_data(data)
        if err:
            return jsonify({'error': err}), 400

        # Name cannot be changed
        if data.get('name') and data['name'] != name:
            return jsonify({'error': 'Cannot change configuration name'}), 400

        config.kind = data['kind']
        config.author = data['author']
        config.description = data.get('description', '')
        config.options = data.get('options', [])
        config.spec = data['spec']
        config.spark_config = data.get('spark_config', [])
        config.updated_ts = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'UDP configuration updated successfully',
            'configuration': config.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@udp_bp.route('/<name>', methods=['DELETE'])
@jwt_required()
@limiter.limit("20 per minute")
def delete_udp_configuration(name):
    """Delete a UDP configuration"""
    try:
        config = UDPConfiguration.query.get(name)
        if not config:
            return jsonify({'error': 'UDP configuration not found'}), 404

        db.session.delete(config)
        db.session.commit()

        return jsonify({'message': 'UDP configuration deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, limiter
from app.models.dataset import Dataset
from datetime import datetime
from sqlalchemy.exc import IntegrityError

datasets_bp = Blueprint('datasets', __name__)

@datasets_bp.route('', methods=['GET'])
@jwt_required()
@limiter.limit("100 per minute")
def get_datasets():
    """Get all datasets with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        dataset_type = request.args.get('dataset_type')
        layer = request.args.get('layer')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Dataset.query
        
        if status:
            query = query.filter(Dataset.status == status)
        if dataset_type:
            query = query.filter(Dataset.dataset_type == dataset_type)
        if layer:
            query = query.filter(Dataset.layer == layer)
        
        # Pagination
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        datasets = [dataset.to_dict() for dataset in pagination.items]
        
        return jsonify({
            'datasets': datasets,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@datasets_bp.route('/<dataset_id>', methods=['GET'])
@jwt_required()
@limiter.limit("100 per minute")
def get_dataset(dataset_id):
    """Get a specific dataset by ID"""
    try:
        dataset = Dataset.query.get(dataset_id)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        return jsonify({
            'dataset': dataset.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@datasets_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_dataset():
    """Create a new dataset"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['dataset_id', 'dataset_name', 'dataset_type', 'layer']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if dataset_id already exists
        if Dataset.query.get(data['dataset_id']):
            return jsonify({'error': 'Dataset ID already exists'}), 400
        
        # Validate upstream_dependencies - ensure all referenced datasets exist
        upstream_deps = data.get('upstream_dependencies', [])
        if upstream_deps:
            existing_datasets = Dataset.query.filter(
                Dataset.dataset_id.in_(upstream_deps)
            ).all()
            existing_ids = {ds.dataset_id for ds in existing_datasets}
            missing_ids = set(upstream_deps) - existing_ids
            if missing_ids:
                return jsonify({
                    'error': f'Upstream dependencies not found: {", ".join(missing_ids)}'
                }), 400
        
        # Create new dataset
        dataset = Dataset(
            dataset_id=data['dataset_id'],
            dataset_name=data['dataset_name'],
            dataset_type=data['dataset_type'],
            layer=data['layer'],
            upstream_dependencies=upstream_deps,
            status=data.get('status', 'active')
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return jsonify({
            'message': 'Dataset created successfully',
            'dataset': dataset.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Dataset ID already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@datasets_bp.route('/<dataset_id>', methods=['PUT'])
@jwt_required()
@limiter.limit("20 per minute")
def update_dataset(dataset_id):
    """Update an existing dataset"""
    try:
        dataset = Dataset.query.get(dataset_id)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields (dataset_id cannot be changed)
        if 'dataset_name' in data:
            dataset.dataset_name = data['dataset_name']
        if 'dataset_type' in data:
            dataset.dataset_type = data['dataset_type']
        if 'layer' in data:
            dataset.layer = data['layer']
        if 'upstream_dependencies' in data:
            # Validate upstream_dependencies - ensure all referenced datasets exist
            upstream_deps = data['upstream_dependencies']
            if upstream_deps:
                # Exclude self from validation
                existing_datasets = Dataset.query.filter(
                    Dataset.dataset_id.in_(upstream_deps),
                    Dataset.dataset_id != dataset_id
                ).all()
                existing_ids = {ds.dataset_id for ds in existing_datasets}
                missing_ids = set(upstream_deps) - existing_ids
                if missing_ids:
                    return jsonify({
                        'error': f'Upstream dependencies not found: {", ".join(missing_ids)}'
                    }), 400
            dataset.upstream_dependencies = upstream_deps
        if 'status' in data:
            dataset.status = data['status']
        
        dataset.updated_ts = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Dataset updated successfully',
            'dataset': dataset.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@datasets_bp.route('/<dataset_id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("20 per minute")
def delete_dataset(dataset_id):
    """Delete a dataset"""
    try:
        dataset = Dataset.query.get(dataset_id)
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        db.session.delete(dataset)
        db.session.commit()
        
        return jsonify({
            'message': 'Dataset deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



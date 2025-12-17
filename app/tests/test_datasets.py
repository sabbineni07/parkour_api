import pytest
from app import db
from app.models.dataset import Dataset

def test_create_dataset(client, auth_headers):
    """Test creating a new dataset"""
    response = client.post('/api/datasets', 
                          headers=auth_headers,
                          json={
                              'dataset_id': 'ds_001',
                              'dataset_name': 'Test Dataset',
                              'dataset_type': 'table',
                              'layer': 'bronze',
                              'upstream_dependencies': ['ds_000'],
                              'status': 'active'
                          })
    
    assert response.status_code == 201
    assert response.json['dataset']['dataset_id'] == 'ds_001'
    assert response.json['dataset']['dataset_name'] == 'Test Dataset'
    assert response.json['dataset']['upstream_dependencies'] == ['ds_000']

def test_create_dataset_missing_fields(client, auth_headers):
    """Test creating dataset with missing required fields"""
    response = client.post('/api/datasets',
                          headers=auth_headers,
                          json={
                              'dataset_id': 'ds_002',
                              'dataset_name': 'Test Dataset 2'
                              # Missing dataset_type and layer
                          })
    
    assert response.status_code == 400
    assert 'required' in response.json['error'].lower()

def test_create_duplicate_dataset_id(client, auth_headers):
    """Test creating dataset with duplicate ID"""
    # Create first dataset
    client.post('/api/datasets',
                headers=auth_headers,
                json={
                    'dataset_id': 'ds_003',
                    'dataset_name': 'First Dataset',
                    'dataset_type': 'table',
                    'layer': 'bronze'
                })
    
    # Try to create duplicate
    response = client.post('/api/datasets',
                          headers=auth_headers,
                          json={
                              'dataset_id': 'ds_003',
                              'dataset_name': 'Second Dataset',
                              'dataset_type': 'table',
                              'layer': 'bronze'
                          })
    
    assert response.status_code == 400
    assert 'already exists' in response.json['error'].lower()

def test_get_dataset(client, auth_headers):
    """Test getting a specific dataset"""
    # Create dataset first
    dataset = Dataset(
        dataset_id='ds_004',
        dataset_name='Get Test Dataset',
        dataset_type='view',
        layer='silver',
        upstream_dependencies=['ds_001', 'ds_002'],
        status='active'
    )
    db.session.add(dataset)
    db.session.commit()
    
    # Get the dataset
    response = client.get('/api/datasets/ds_004', headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['dataset']['dataset_id'] == 'ds_004'
    assert response.json['dataset']['dataset_name'] == 'Get Test Dataset'
    assert len(response.json['dataset']['upstream_dependencies']) == 2

def test_get_nonexistent_dataset(client, auth_headers):
    """Test getting a dataset that doesn't exist"""
    response = client.get('/api/datasets/nonexistent', headers=auth_headers)
    
    assert response.status_code == 404
    assert 'not found' in response.json['error'].lower()

def test_get_all_datasets(client, auth_headers):
    """Test getting all datasets"""
    # Create multiple datasets
    datasets = [
        Dataset(
            dataset_id=f'ds_{i:03d}',
            dataset_name=f'Dataset {i}',
            dataset_type='table',
            layer='bronze',
            status='active'
        )
        for i in range(5, 8)
    ]
    db.session.add_all(datasets)
    db.session.commit()
    
    # Get all datasets
    response = client.get('/api/datasets', headers=auth_headers)
    
    assert response.status_code == 200
    assert len(response.json['datasets']) >= 3
    assert 'total' in response.json
    assert 'page' in response.json

def test_get_datasets_with_filters(client, auth_headers):
    """Test getting datasets with filters"""
    # Create datasets with different statuses
    active_dataset = Dataset(
        dataset_id='ds_active',
        dataset_name='Active Dataset',
        dataset_type='table',
        layer='bronze',
        status='active'
    )
    inactive_dataset = Dataset(
        dataset_id='ds_inactive',
        dataset_name='Inactive Dataset',
        dataset_type='table',
        layer='bronze',
        status='inactive'
    )
    db.session.add_all([active_dataset, inactive_dataset])
    db.session.commit()
    
    # Filter by status
    response = client.get('/api/datasets?status=active', headers=auth_headers)
    
    assert response.status_code == 200
    assert all(d['status'] == 'active' for d in response.json['datasets'])

def test_update_dataset(client, auth_headers):
    """Test updating a dataset"""
    # Create dataset
    dataset = Dataset(
        dataset_id='ds_update',
        dataset_name='Original Name',
        dataset_type='table',
        layer='bronze',
        status='active'
    )
    db.session.add(dataset)
    db.session.commit()
    
    # Update dataset
    response = client.put('/api/datasets/ds_update',
                        headers=auth_headers,
                        json={
                            'dataset_name': 'Updated Name',
                            'status': 'inactive',
                            'upstream_dependencies': ['ds_001']
                        })
    
    assert response.status_code == 200
    assert response.json['dataset']['dataset_name'] == 'Updated Name'
    assert response.json['dataset']['status'] == 'inactive'
    assert response.json['dataset']['upstream_dependencies'] == ['ds_001']

def test_update_nonexistent_dataset(client, auth_headers):
    """Test updating a dataset that doesn't exist"""
    response = client.put('/api/datasets/nonexistent',
                         headers=auth_headers,
                         json={'dataset_name': 'New Name'})
    
    assert response.status_code == 404
    assert 'not found' in response.json['error'].lower()

def test_delete_dataset(client, auth_headers):
    """Test deleting a dataset"""
    # Create dataset
    dataset = Dataset(
        dataset_id='ds_delete',
        dataset_name='To Be Deleted',
        dataset_type='table',
        layer='bronze',
        status='active'
    )
    db.session.add(dataset)
    db.session.commit()
    
    # Delete dataset
    response = client.delete('/api/datasets/ds_delete', headers=auth_headers)
    
    assert response.status_code == 200
    assert 'deleted successfully' in response.json['message'].lower()
    
    # Verify it's deleted
    get_response = client.get('/api/datasets/ds_delete', headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_nonexistent_dataset(client, auth_headers):
    """Test deleting a dataset that doesn't exist"""
    response = client.delete('/api/datasets/nonexistent', headers=auth_headers)
    
    assert response.status_code == 404
    assert 'not found' in response.json['error'].lower()

def test_datasets_require_authentication(client):
    """Test that dataset endpoints require authentication"""
    # Try to access without auth
    response = client.get('/api/datasets')
    assert response.status_code == 401
    
    response = client.post('/api/datasets', json={})
    assert response.status_code == 401
    
    response = client.get('/api/datasets/ds_001')
    assert response.status_code == 401




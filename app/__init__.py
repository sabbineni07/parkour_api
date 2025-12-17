from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Custom key function to exclude OPTIONS requests from rate limiting
def rate_limit_key_func():
    """Custom key function that excludes OPTIONS requests from rate limiting"""
    if request.method == 'OPTIONS':
        # Return None to skip rate limiting for OPTIONS requests
        return None
    return get_remote_address()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

# Get rate limits from environment or use defaults
# Development: More permissive limits
# Production: Stricter limits
flask_env = os.getenv('FLASK_ENV', 'development')
if flask_env == 'production':
    default_limits = os.getenv('RATE_LIMIT', "1000 per day, 200 per hour, 60 per minute")
else:
    # Development: Much more permissive
    default_limits = os.getenv('RATE_LIMIT', "10000 per day, 1000 per hour, 200 per minute")

limiter = Limiter(
    key_func=rate_limit_key_func,
    default_limits=[default_limits],
    storage_uri="memory://"  # Use Redis in production: "redis://localhost:6379"
)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/parkour_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if os.getenv('FLASK_ENV') == 'production' else logging.DEBUG,
        format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    
    # Configure CORS
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:4200,http://localhost:3000,http://127.0.0.1:4200,http://127.0.0.1:3000').split(',')
    # Clean up origins (remove whitespace)
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
    
    # Log CORS configuration in development
    if os.getenv('FLASK_ENV') != 'production':
        logging.info(f'CORS Origins: {cors_origins}')
    
    CORS(app, 
         origins=cors_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         expose_headers=['Content-Type', 'Authorization'],
         supports_credentials=True,
         max_age=3600)  # Cache preflight requests for 1 hour
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.datasets import datasets_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(datasets_bp, url_prefix='/api/datasets')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'parkour-api'}, 200
    
    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database with sample data"""
        from app.models.user import User
        
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@parkour.com',
                first_name='Admin',
                last_name='User'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")
        
        print("Database initialized successfully!")
    
    @app.cli.command()
    def seed_datasets():
        """Seed sample datasets following medallion architecture"""
        import uuid
        from app.models.dataset import Dataset
        
        # Clear existing datasets
        Dataset.query.delete()
        db.session.commit()
        print("Cleared existing datasets...")
        
        # Generate UUIDs for all datasets
        # Bronze Layer: Raw data from Azure ADLS
        bronze_customer_uuid = str(uuid.uuid4())
        bronze_transaction_uuid = str(uuid.uuid4())
        bronze_product_uuid = str(uuid.uuid4())
        
        bronze_datasets = [
            {
                'dataset_id': bronze_customer_uuid,
                'dataset_name': 'adls://bronze/customer/raw_customer_data',
                'dataset_type': 'adls',
                'layer': 'bronze',
                'upstream_dependencies': [],  # No dependencies - source data
                'status': 'active'
            },
            {
                'dataset_id': bronze_transaction_uuid,
                'dataset_name': 'adls://bronze/transactions/raw_transaction_data',
                'dataset_type': 'adls',
                'layer': 'bronze',
                'upstream_dependencies': [],
                'status': 'active'
            },
            {
                'dataset_id': bronze_product_uuid,
                'dataset_name': 'adls://bronze/products/raw_product_catalog',
                'dataset_type': 'adls',
                'layer': 'bronze',
                'upstream_dependencies': [],
                'status': 'active'
            }
        ]
        
        # Silver Layer: Cleaned and validated data (depends on Bronze)
        silver_customer_cleaned_uuid = str(uuid.uuid4())
        silver_transaction_cleaned_uuid = str(uuid.uuid4())
        silver_product_cleaned_uuid = str(uuid.uuid4())
        silver_customer_enriched_uuid = str(uuid.uuid4())
        
        silver_datasets = [
            {
                'dataset_id': silver_customer_cleaned_uuid,
                'dataset_name': 'uc.bronze.customer_cleaned',
                'dataset_type': 'delta',
                'layer': 'silver',
                'upstream_dependencies': [bronze_customer_uuid],
                'status': 'active'
            },
            {
                'dataset_id': silver_transaction_cleaned_uuid,
                'dataset_name': 'uc.bronze.transaction_cleaned',
                'dataset_type': 'delta',
                'layer': 'silver',
                'upstream_dependencies': [bronze_transaction_uuid],
                'status': 'active'
            },
            {
                'dataset_id': silver_product_cleaned_uuid,
                'dataset_name': 'uc.bronze.product_catalog_cleaned',
                'dataset_type': 'delta',
                'layer': 'silver',
                'upstream_dependencies': [bronze_product_uuid],
                'status': 'active'
            },
            {
                'dataset_id': silver_customer_enriched_uuid,
                'dataset_name': 'uc.silver.customer_enriched',
                'dataset_type': 'delta',
                'layer': 'silver',
                'upstream_dependencies': [
                    silver_customer_cleaned_uuid,
                    silver_transaction_cleaned_uuid
                ],
                'status': 'active'
            }
        ]
        
        # Gold Layer: Business-ready aggregated data (depends on Silver)
        gold_customer_analytics_uuid = str(uuid.uuid4())
        gold_transaction_summary_uuid = str(uuid.uuid4())
        gold_customer_ltv_uuid = str(uuid.uuid4())
        gold_product_performance_uuid = str(uuid.uuid4())
        
        gold_datasets = [
            {
                'dataset_id': gold_customer_analytics_uuid,
                'dataset_name': 'uc.gold.customer_analytics',
                'dataset_type': 'delta',
                'layer': 'gold',
                'upstream_dependencies': [silver_customer_enriched_uuid],
                'status': 'active'
            },
            {
                'dataset_id': gold_transaction_summary_uuid,
                'dataset_name': 'uc.gold.transaction_summary',
                'dataset_type': 'delta',
                'layer': 'gold',
                'upstream_dependencies': [
                    silver_transaction_cleaned_uuid,
                    silver_product_cleaned_uuid
                ],
                'status': 'active'
            },
            {
                'dataset_id': gold_customer_ltv_uuid,
                'dataset_name': 'uc.gold.customer_lifetime_value',
                'dataset_type': 'delta',
                'layer': 'gold',
                'upstream_dependencies': [
                    gold_customer_analytics_uuid,
                    gold_transaction_summary_uuid
                ],
                'status': 'active'
            },
            {
                'dataset_id': gold_product_performance_uuid,
                'dataset_name': 'adls://gold/reporting/product_performance',
                'dataset_type': 'adls',
                'layer': 'gold',
                'upstream_dependencies': [
                    silver_product_cleaned_uuid,
                    silver_transaction_cleaned_uuid
                ],
                'status': 'active'
            }
        ]
        
        # Create datasets in order: Bronze -> Silver -> Gold
        all_datasets = bronze_datasets + silver_datasets + gold_datasets
        
        for dataset_data in all_datasets:
            dataset = Dataset(
                dataset_id=dataset_data['dataset_id'],
                dataset_name=dataset_data['dataset_name'],
                dataset_type=dataset_data['dataset_type'],
                layer=dataset_data['layer'],
                upstream_dependencies=dataset_data['upstream_dependencies'],
                status=dataset_data['status']
            )
            db.session.add(dataset)
        
        db.session.commit()
        print(f"Successfully seeded {len(all_datasets)} datasets:")
        print(f"  - Bronze layer: {len(bronze_datasets)} datasets")
        print(f"  - Silver layer: {len(silver_datasets)} datasets")
        print(f"  - Gold layer: {len(gold_datasets)} datasets")
        print("\nDataset IDs are UUIDs. Dataset names use:")
        print("  - ADLS paths (e.g., adls://bronze/customer/raw_customer_data)")
        print("  - Unity Catalog format (e.g., uc.schema.table_name)")
    
    return app

# Create the app instance for Gunicorn
app = create_app()


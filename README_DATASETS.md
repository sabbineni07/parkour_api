# Datasets Management

## Overview

The datasets follow a **Medallion Architecture** pattern, commonly used in Azure Databricks and ADLS (Azure Data Lake Storage) environments. This architecture organizes data into three layers:

1. **Bronze Layer**: Raw, unprocessed data ingested from source systems
2. **Silver Layer**: Cleaned, validated, and enriched data
3. **Gold Layer**: Business-ready, aggregated data for analytics and reporting

## Dataset Structure

### Fields

- `dataset_id` (Primary Key): Unique UUID string identifier for the dataset (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- `dataset_name`: Table name or source path. Can be:
  - Unity Catalog format: `uc.schema.table_name` (e.g., `uc.bronze.customer_cleaned`)
  - Azure ADLS path: `adls://layer/category/table_name` (e.g., `adls://bronze/customer/raw_customer_data`)
- `dataset_type`: Type of dataset (e.g., `delta`, `adls`, `parquet`, `csv`)
- `layer`: Medallion layer (`bronze`, `silver`, `gold`)
- `upstream_dependencies`: Array of `dataset_id` (UUID) values that this dataset depends on
- `status`: Dataset status (`active`, `inactive`, `deprecated`)
- `created_ts`: Creation timestamp
- `updated_ts`: Last update timestamp

### Key Rules

1. **Unique `dataset_id`**: Each dataset must have a unique identifier (enforced by primary key)
2. **Upstream Dependencies**: 
   - Bronze datasets typically have no dependencies (source data)
   - Silver datasets depend on Bronze datasets
   - Gold datasets depend on Silver datasets (or other Gold datasets)
3. **Referential Integrity**: All `upstream_dependencies` must reference existing `dataset_id` values

## Sample Datasets

The seed command creates 11 sample datasets:

### Bronze Layer (3 datasets)
- Raw Customer Data
- Raw Transaction Data
- Raw Product Catalog

### Silver Layer (4 datasets)
- Cleaned Customer Data (depends on: Raw Customer Data)
- Cleaned Transaction Data (depends on: Raw Transaction Data)
- Cleaned Product Catalog (depends on: Raw Product Catalog)
- Customer Enriched Data (depends on: Cleaned Customer Data, Cleaned Transaction Data)

### Gold Layer (4 datasets)
- Customer Analytics (depends on: Customer Enriched Data)
- Transaction Summary Report (depends on: Cleaned Transaction Data, Cleaned Product Catalog)
- Customer Lifetime Value (depends on: Customer Analytics, Transaction Summary Report)
- Product Performance Metrics (depends on: Cleaned Product Catalog, Cleaned Transaction Data)

## Commands

### Seed Datasets

**With Docker:**
```bash
make seed-datasets
```

**Without Docker (local):**
```bash
flask seed-datasets
```

This command will:
1. Clear all existing datasets
2. Create sample datasets following medallion architecture
3. Establish proper parent-child relationships through `upstream_dependencies`

### Create Dataset via API

```bash
POST /api/datasets
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
  "dataset_name": "uc.bronze.new_raw_data",
  "dataset_type": "delta",
  "layer": "bronze",
  "upstream_dependencies": [],
  "status": "active"
}
```

**Note:** `dataset_id` must be a valid UUID string. You can generate one using:
- Python: `import uuid; str(uuid.uuid4())`
- Online: Any UUID generator tool

### Validation

The API automatically validates:
- All required fields are present
- `dataset_id` is unique
- All `upstream_dependencies` reference existing datasets
- No circular dependencies (dataset cannot depend on itself)

## Example Dependency Graph

```
Bronze Layer (No dependencies)
├── Raw Customer Data
├── Raw Transaction Data
└── Raw Product Catalog

Silver Layer (Depends on Bronze)
├── Cleaned Customer Data → Raw Customer Data
├── Cleaned Transaction Data → Raw Transaction Data
├── Cleaned Product Catalog → Raw Product Catalog
└── Customer Enriched → Cleaned Customer Data, Cleaned Transaction Data

Gold Layer (Depends on Silver/Gold)
├── Customer Analytics → Customer Enriched
├── Transaction Summary → Cleaned Transaction Data, Cleaned Product Catalog
├── Customer Lifetime Value → Customer Analytics, Transaction Summary
└── Product Performance → Cleaned Product Catalog, Cleaned Transaction Data
```


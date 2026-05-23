from pymilvus import Collection, FieldSchema, CollectionSchema, DataType, connections, utility

# Connect first
try:
    connections.connect(alias='default', host='127.0.0.1', port='19530')
    print("Connected to Milvus")
except Exception as e:
    print(f"Connection error: {e}")

# Test 1: Check if collection can be created with schema
try:
    fields = [
        FieldSchema(name='pk', dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=768)
    ]
    schema = CollectionSchema(fields, description='test')
    
    # This should create the collection
    col = Collection(name='test_create_method', schema=schema)
    print("✓ Successfully created collection with schema parameter")
except Exception as e:
    print(f"✗ Error creating collection: {type(e).__name__}: {e}")

# Test 2: Try using drop and recreate
try:
    if utility.has_collection('test_drop_recreate'):
        utility.drop_collection('test_drop_recreate')
        print("✓ Dropped existing test collection")
    
    fields = [
        FieldSchema(name='pk', dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=768)
    ]
    schema = CollectionSchema(fields, description='test')
    col = Collection(name='test_drop_recreate', schema=schema)
    print("✓ Successfully created collection after checking/dropping")
except Exception as e:
    print(f"✗ Error in drop/recreate test: {type(e).__name__}: {e}")

# Test 3: List all collections
try:
    collections = utility.list_collections()
    print(f"✓ Available collections: {collections}")
except Exception as e:
    print(f"✗ Error listing collections: {type(e).__name__}: {e}")

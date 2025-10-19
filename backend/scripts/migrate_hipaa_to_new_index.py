"""
Migrate HIPAA vectors from dentaflow-hipaa index to dentaflow-knowledge/hipaa namespace
"""

import os
from pinecone import Pinecone

# Get API key
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if not pinecone_api_key:
    print("❌ PINECONE_API_KEY not set")
    exit(1)

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)

# Get both indexes
old_index = pc.Index("dentaflow-hipaa")
new_index = pc.Index("dentaflow-knowledge")

print("="*60)
print("Migrating HIPAA vectors to new index")
print("="*60)

# Fetch all vectors from old index
print("\nFetching vectors from dentaflow-hipaa...")
stats = old_index.describe_index_stats()
total_vectors = stats.total_vector_count
print(f"Total vectors to migrate: {total_vectors}")

# Fetch vectors in batches
batch_size = 100
migrated = 0
failed = 0

# Get all vector IDs
# Note: Pinecone doesn't have a direct "list all IDs" method
# We'll use the query method with a dummy vector to get IDs

# First, let's try to fetch some vectors to understand the structure
try:
    # Query to get some vector IDs
    results = old_index.query(
        vector=[0.0] * 1536,  # Dummy vector
        top_k=10000,  # Get as many as possible
        include_values=True,
        include_metadata=True
    )
    
    print(f"\nFound {len(results.matches)} vectors")
    
    # Migrate each vector
    for match in results.matches:
        try:
            # Upsert to new index in 'hipaa' namespace
            new_index.upsert(
                vectors=[{
                    'id': match.id,
                    'values': match.values,
                    'metadata': match.metadata
                }],
                namespace='hipaa'
            )
            migrated += 1
            if migrated % 10 == 0:
                print(f"  Migrated {migrated}/{len(results.matches)} vectors...")
        except Exception as e:
            print(f"  ❌ Failed to migrate {match.id}: {e}")
            failed += 1
    
    print(f"\n✅ Migration complete!")
    print(f"  Migrated: {migrated}")
    print(f"  Failed: {failed}")
    
    # Verify
    print("\nVerifying migration...")
    new_stats = new_index.describe_index_stats()
    hipaa_vectors = new_stats.namespaces.get('hipaa', {}).get('vector_count', 0)
    print(f"  HIPAA namespace now has: {hipaa_vectors} vectors")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    exit(1)

print("="*60)


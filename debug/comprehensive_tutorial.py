# -*- coding: utf-8 -*-

import boto3
from s3vectorm.api import (
    Bucket,
    Index,
    Vector,
    BaseMetadata,
    MetaKey,
)

# Configure your AWS credentials and region
bucket_name = "s3vectorm-tutorial-bucket"
index_name = "document-embeddings"

# Create AWS S3 Vectors client
boto_ses = boto3.Session()
s3_vectors_client = boto_ses.client("s3vectors")

# Create a bucket instance
bucket = Bucket(name=bucket_name)


def Creating_a_Vector_Bucket():
    # Create the bucket in AWS (returns None if already exists)
    create_result = bucket.create(s3_vectors_client)
    if create_result:
        print("✅ Bucket created successfully")
    else:
        print("ℹ️ Bucket already exists")


def Listing_Indexes_in_a_Bucket():
    # List all indexes in the bucket
    print("📋 Indexes in bucket:")
    for page in bucket.list_index(
        s3_vectors_client,
        prefix="document-",  # Optional: filter by prefix
        page_size=50,
    ):
        indexes = page.indexes or []
        for index_summary in indexes:
            print(f"  - {index_summary.indexName} (dim: {index_summary.dimension})")


# Create an index with specific configuration
index = Index(
    bucket_name=bucket_name,
    index_name=index_name,
    data_type="float32",
    dimension=768,  # Common dimension for many LLM embeddings
    distance_metric="cosine",
)


def Creating_a_Vector_Index():
    # Create the index in AWS
    create_result = index.create(s3_vectors_client)
    if create_result:
        print("✅ Index created successfully")
    else:
        print("ℹ️ Index already exists")


def Retrieving_an_Existing_Index():
    # Retrieve an existing index by name
    existing_index = Index.get(
        s3_vectors_client, vector_bucket_name=bucket_name, index_name=index_name
    )

    if existing_index:
        print(f"📊 Retrieved index: {existing_index.index_name}")
        print(f"   Dimension: {existing_index.dimension}")
        print(f"   Distance metric: {existing_index.distance_metric}")
    else:
        print("❌ Index not found")


def Creating_Index_Objects_for_Deletion():
    # Create index object specifically for deletion operations
    deletion_index = Index.new_for_delete(
        bucket_name=bucket_name, index_name=index_name
    )


from pydantic import Field


class DocumentChunk(Vector):
    """Custom vector class for document chunks with metadata"""

    document_id: str = Field(description="ID of the source document")
    chunk_seq: int = Field(description="Sequence number of the chunk")
    title: str = Field(description="Document title")
    category: str = Field(description="Document category")
    owner_id: str = Field(description="ID of the document owner")
    created_at: str = Field(description="Creation timestamp")


def Understanding_Vector_Conversion():
    # Create a sample vector
    sample_vector = DocumentChunk(
        key="doc-1#chunk-1",
        data=[0.1, 0.2, 0.3] * 256,  # 768-dimensional vector
        document_id="doc-1",
        chunk_seq=1,
        title="Introduction to AI",
        category="technology",
        owner_id="user-123",
        created_at="2025-01-01T10:00:00Z",
    )
    # Extract just the metadata
    metadata = sample_vector.to_metadata_dict()
    print("📋 Metadata only:", metadata)


def Inserting_Vectors():
    # Create a collection of document vectors
    vectors = [
        DocumentChunk(
            key="doc-1#chunk-1",
            data=[0.1] * 768,
            document_id="doc-1",
            chunk_seq=1,
            title="Introduction to Machine Learning",
            category="technology",
            owner_id="user-alice",
            created_at="2025-01-01T10:00:00Z",
        ),
        DocumentChunk(
            key="doc-1#chunk-2",
            data=[0.2] * 768,
            document_id="doc-1",
            chunk_seq=2,
            title="Introduction to Machine Learning",
            category="technology",
            owner_id="user-alice",
            created_at="2025-01-01T10:05:00Z",
        ),
        DocumentChunk(
            key="doc-2#chunk-1",
            data=[0.3] * 768,
            document_id="doc-2",
            chunk_seq=1,
            title="Business Strategy Guide",
            category="business",
            owner_id="user-bob",
            created_at="2025-01-01T11:00:00Z",
        ),
        DocumentChunk(
            key="doc-2#chunk-2",
            data=[0.4] * 768,
            document_id="doc-2",
            chunk_seq=2,
            title="Business Strategy Guide",
            category="business",
            owner_id="user-bob",
            created_at="2025-01-01T11:05:00Z",
        ),
    ]

    # Store all vectors in the index
    index.put_vectors(s3_vectors_client, vectors)
    print(f"✅ Successfully stored {len(vectors)} vectors")


# Base metadata class with common fields
class BaseDocumentMeta(BaseMetadata):
    document_id = MetaKey()
    chunk_seq = MetaKey()


# Extended metadata class with additional fields
class DocumentMeta(BaseDocumentMeta):
    title = MetaKey()
    category = MetaKey()
    owner_id = MetaKey()
    created_at = MetaKey()


def Understanding_Query_Operators():
    # Demonstrate all available operators
    meta = DocumentMeta()

    # Equality operators
    equality_filter = meta.category.eq("technology")
    not_equal_filter = meta.owner_id.ne("user-deleted")

    # Comparison operators
    sequence_filter = meta.chunk_seq.gt(1)  # Greater than
    recent_filter = meta.chunk_seq.gte(2)  # Greater than or equal
    early_filter = meta.chunk_seq.lt(5)  # Less than
    boundary_filter = meta.chunk_seq.lte(3)  # Less than or equal

    # List operators
    multi_user_filter = meta.owner_id.in_(["user-alice", "user-bob"])
    not_category_filter = meta.category.nin(["draft", "archived"])

    # Existence operators
    has_title_filter = meta.title.exists(True)
    no_title_filter = meta.title.exists(False)

    print("🔍 All operators available for metadata filtering")


# Query vector (representing a search query embedding)
query_data = [0.15] * 768


def Basic_Similarity_Search():
    # Basic similarity search
    results = index.query_vectors(
        s3_vectors_client,
        data=query_data,
        top_k=5,
        return_metadata=True,
        return_distance=True,
    )

    # Process results
    print("🔍 Basic similarity search results:")
    for i, vector in enumerate(results.as_vector_objects(DocumentChunk), 1):
        print(f"  {i}. {vector.title} (distance: {vector.distance:.6f})")
        print(f"     Key: {vector.key}, Owner: {vector.owner_id}")


def Filtered_Similarity_Search():
    # Search within specific category
    category_filter = DocumentMeta.category.eq("technology")
    tech_results = index.query_vectors(
        s3_vectors_client,
        data=query_data,
        top_k=3,
        filter=category_filter,
        return_metadata=True,
        return_distance=True,
    )

    print("🎯 Technology documents:")
    for vector in tech_results.as_vector_objects(DocumentChunk):
        print(f"  - {vector.title} (chunk {vector.chunk_seq})")


def Complex_Query_Combinations():
    # Complex query: Technology documents owned by Alice, chunk sequence > 1
    complex_filter = (
        DocumentMeta.category.eq("technology")
        & DocumentMeta.owner_id.eq("user-alice")
        & DocumentMeta.chunk_seq.gt(1)
    )

    complex_results = index.query_vectors(
        s3_vectors_client,
        data=query_data,
        filter=complex_filter,
        return_metadata=True,
        return_distance=True,
    )

    print("🧠 Complex filtered results:")
    for vector in complex_results.as_vector_objects(DocumentChunk):
        print(
            f"  - {vector.title} (chunk {vector.chunk_seq}, owner: {vector.owner_id})"
        )


def Multi_User_Query_Example():
    # Find documents from specific users
    multi_user_filter = DocumentMeta.owner_id.in_(["user-alice", "user-bob"])
    multi_user_results = index.query_vectors(
        s3_vectors_client,
        data=query_data,
        filter=multi_user_filter,
        return_metadata=True,
    )

    print("👥 Multi-user search results:")
    for vector in multi_user_results.as_vector_objects(DocumentChunk):
        print(f"  - {vector.title} by {vector.owner_id}")


def Listing_All_Vectors():
    # List all vectors with metadata
    print("📃 All vectors in index:")
    all_keys = []

    for page in index.list_vectors(
        s3_vectors_client,
        return_metadata=True,
        return_data=False,  # Don't return vector data for performance
        page_size=100,
    ):
        for vector in page.as_vector_objects(DocumentChunk):
            all_keys.append(vector.key)
            print(f"  - {vector.key}: {vector.title} ({vector.category})")

    print(f"📊 Total vectors found: {len(all_keys)}")


def Listing_Vectors_with_Data():
    # List vectors with their embedding data
    print("🔢 Vectors with embedding data:")
    for page in index.list_vectors(
        s3_vectors_client,
        return_data=True,
        return_metadata=True,
        page_size=2,  # Small page size for demo
    ):
        for vector in page.as_vector_objects(DocumentChunk):
            data_preview = vector.data[:3] if vector.data else None
            print(f"  - {vector.key}: data preview {data_preview}...")


def Segmented_Vector_Listing():
    # Process vectors in segments (useful for parallel processing)
    segment_count = 2
    for segment_index in range(segment_count):
        print(f"📦 Processing segment {segment_index + 1}/{segment_count}:")

        for page in index.list_vectors(
            s3_vectors_client,
            segment_count=segment_count,
            segment_index=segment_index,
            return_metadata=True,
            page_size=50,
        ):
            vectors_in_segment = list(page.as_vector_objects(DocumentChunk))
            print(f"   Found {len(vectors_in_segment)} vectors in this segment")


def Deleting_Specific_Vectors():
    # Delete specific vectors by key
    keys_to_delete = ["doc-1#chunk-1", "doc-2#chunk-1"]
    index.delete_vectors(s3_vectors_client, keys=keys_to_delete)
    print(f"🗑️ Deleted {len(keys_to_delete)} specific vectors")

    # Verify deletion
    remaining_count = 0
    for page in index.list_vectors(s3_vectors_client, return_metadata=True):
        for vector in page.as_vector_objects(DocumentChunk):
            remaining_count += 1

    print(f"📊 Remaining vectors: {remaining_count}")


def Deleting_an_Index():
    # Delete the index (this also deletes all vectors)
    index.delete(s3_vectors_client)
    print("🗑️ Index deleted successfully")


def Bulk_Index_Management():
    # List and delete all indexes in a bucket
    print("🔍 Finding all indexes in bucket:")
    for page in bucket.list_index(s3_vectors_client):
        # Create index objects for deletion
        index_list = Index.new_for_delete_from_list_index_response(page)

        for idx in index_list:
            print(f"  Deleting index: {idx.index_name}")
            idx.delete(s3_vectors_client)

    print("✅ All indexes deleted")


def Deleting_the_Bucket():
    # Delete the bucket (must be empty of indexes)
    try:
        delete_result = bucket.delete(s3_vectors_client)
        print("🗑️ Bucket deleted successfully")
        print(f"Response: {delete_result}")
    except Exception as e:
        print(f"❌ Failed to delete bucket: {e}")
        print("💡 Make sure all indexes are deleted first")


Creating_a_Vector_Bucket()
Listing_Indexes_in_a_Bucket()
Creating_a_Vector_Index()
Retrieving_an_Existing_Index()
Understanding_Vector_Conversion()
Basic_Similarity_Search()
Filtered_Similarity_Search()
Complex_Query_Combinations()
Multi_User_Query_Example()
Listing_All_Vectors()
Listing_Vectors_with_Data()
Deleting_Specific_Vectors()
Deleting_an_Index()
Bulk_Index_Management()
Deleting_the_Bucket()

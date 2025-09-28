.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.1 (2025-09-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**First Release**

**Features and Improvements**

- **S3 Vector Bucket Management**: Create, delete, and list vector buckets with automatic conflict handling
- **Vector Index Operations**: Full CRUD operations for vector indexes including creation, retrieval, and deletion
- **Type-Safe Vector Models**: Pydantic-based vector classes with automatic data validation and metadata support
- **ORM-Style Query Builder**: SQLAlchemy-inspired metadata filtering with support for all comparison operators (eq, ne, gt, gte, lt, lte, in_, nin, exists)
- **Complex Query Combinations**: Logical operators (AND, OR) for building sophisticated metadata filters
- **Vector Similarity Search**: High-performance similarity search with configurable distance metrics and top-K results
- **Pagination Support**: Built-in pagination for listing vectors and indexes with configurable page sizes
- **Segmented Processing**: Parallel processing support through vector segmentation for large datasets
- **Bulk Operations**: Efficient batch vector insertion and deletion operations
- **Type Preservation**: Generic type system that preserves Vector subclass types throughout query operations

**Vector Management**

- **put_vectors()**: Store multiple vectors with metadata in batch operations
- **query_vectors()**: Similarity search with optional metadata filtering and distance calculation
- **list_vectors()**: Paginated vector listing with optional data and metadata return
- **delete_vectors()**: Selective vector deletion by keys
- **delete_all_vectors()**: Convenient method to clear all vectors from an index
- **as_vector_objects()**: Convert AWS responses back to strongly-typed Vector instances

**Metadata System**

- **BaseMetadata**: Declarative metadata models with inheritance support
- **MetaKey**: Fluent query builder for all AWS S3 Vectors filtering operators
- **Automatic Field Registration**: Metaclass-driven field discovery and registration
- **Query Expression Building**: Natural Python syntax for complex filter construction

**Developer Experience**

- **Comprehensive Documentation**: Full tutorial with real-world examples
- **Type Safety**: Full type hints with IDE auto-completion support
- **Error Handling**: Meaningful error messages with actionable guidance
- **AWS Integration**: Seamless integration with boto3 and AWS S3 Vectors service

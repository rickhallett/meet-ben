# Vector Store

## Understanding Vectors in AI Systems

Vector embeddings are numerical representations of data (text, images, etc.) that capture semantic meaning in a high-dimensional space. These embeddings enable:

- Semantic search capabilities
- Similarity comparisons
- Efficient information retrieval
- Context-aware AI operations

## Why PostgreSQL?

Using PostgreSQL with pgvectorscale as your vector database offers several key advantages over dedicated vector databases:

- PostgreSQL is a robust, open-source database with a rich ecosystem of tools, drivers, and connectors. This ensures transparency, community support, and continuous improvements.

- By using PostgreSQL, you can manage both your relational and vector data within a single database. This reduces operational complexity, as there's no need to maintain and synchronize multiple databases.

- Pgvectorscale enhances pgvector with faster search capabilities, higher recall, and efficient time-based filtering. It leverages advanced indexing techniques, such as the DiskANN-inspired index, to significantly speed up Approximate Nearest Neighbor (ANN) searches.

Pgvectorscale Vector builds on top of [pgvector](https://github.com/pgvector/pgvector), offering improved performance and additional features, making PostgreSQL a powerful and versatile choice for AI applications.



## Current Implementation

Our PostgreSQL vector implementation uses TimescaleDB's vector extension:

```python
class VectorStore:
    def __init__(self, session: Session):
        self.session = session
        self.config = get_settings().database.vector_store

    async def create_embedding(self, text: str, metadata: Dict = None) -> UUID:
        # Create embedding using configured provider
        embedding = await self.create_embedding_vector(text)
        
        # Store in PostgreSQL with TimescaleDB vector
        vector_id = await self.store_vector(
            embedding=embedding,
            metadata=metadata
        )
        return vector_id
```

### Schema Setup

```sql
-- Enable vector extension
CREATE EXTENSION vector;

-- Create hypertable with vector support
CREATE TABLE embeddings (
    id uuid PRIMARY KEY,
    embedding vector(1536),
    metadata jsonb,
    created_at TIMESTAMPTZ NOT NULL
);

-- Create vector index
CREATE INDEX ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## Extending or Replacing the Vector Store

The vector store implementation is designed to be replaceable. You can implement your own vector store by:

1. Creating a new vector store class:
```python
class CustomVectorStore:
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        # Initialize your vector store

    def create_embedding(
        self,
        text: str,
        metadata: Dict = None
    ) -> str:
        # Implement embedding creation and storage
        pass

    def search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Dict]:
        # Implement similarity search
        pass
```

2. Updating the configuration:
```python
# config/database_config.py
class VectorStoreConfig(BaseSettings):
    provider: str = "custom"  # or "postgres", "pinecone", etc.
    # Additional provider-specific settings
```

### Popular Alternatives

You might consider these alternatives based on your needs:

1. **Pinecone**
   - Specialized vector database
   - Managed service
   - High performance
   - Built-in scaling

2. **Weaviate**
   - Multi-modal vectors
   - Rich query capabilities
   - GraphQL interface
   - Self-hosted option

3. **Qdrant**
   - Rust-based performance
   - Rich filtering
   - Easy deployment
   - Active development

## Performance Considerations

When using PostgreSQL for vectors:

1. **Indexing**
   - Use appropriate index types (IVFFlat, HNSW)
   - Configure index parameters based on data size
   - Regular index maintenance

2. **Partitioning**
   - TimescaleDB hypertables for time-based partitioning
   - Partition by metadata attributes if needed
   - Balance partition sizes


## Implementation Tutorial

For a detailed walkthrough of implementing vector search in PostgreSQL, check out our [YouTube tutorial](https://www.youtube.com/watch?v=hAdEuDBN57g) which covers:

- Setting up PostgreSQL with vector extensions
- Creating and configuring indexes
- Implementing similarity search
- Performance optimization tips
- Real-world usage patterns


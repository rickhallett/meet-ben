# Database and Migrations

The GenAI Launchpad uses PostgreSQL as its primary data store, with Alembic handling database migrations. This setup provides a robust foundation for event storage and processing while maintaining schema flexibility through JSON columns.

## Database Architecture

### Event Storage Model

The core of our database design is the Event model, which implements a flexible schema for storing both incoming events and their processing results:

```python
class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid1)
    data = Column(JSON)              # Raw event data
    task_context = Column(JSON)      # Processing results
    created_at = Column(DateTime)    # Event creation timestamp
    updated_at = Column(DateTime)    # Last update timestamp
```

This design allows for:

- Unique identification of each event through UUIDs
- Flexible storage of any event type through JSON columns
- Automatic timestamp tracking
- Easy querying of both raw data and processing results

## Repository Pattern

We implement the repository pattern to abstract database operations and provide a clean interface for data access:

```python
class GenericRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        return obj
```

This pattern provides:

- Type-safe database operations
- Consistent error handling
- Transaction management
- Reusable CRUD operations

## Session Management

Database sessions are managed through a dependency injection pattern:

```python
def db_session() -> Generator:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

This ensures:

- Proper connection handling
- Automatic transaction management
- Resource cleanup
- Connection pooling

## Database Migrations with Alembic

Alembic is a lightweight database migration tool for Python, designed to work with SQLAlchemy, the popular SQL toolkit
and Object-Relational Mapping (ORM) library.

- Version Control Database Schemas: Alembic keeps track of different versions of your database schema, enabling you to upgrade or downgrade to any version as needed.
- Generate Migration Scripts: It can automatically generate migration scripts by comparing your current database schema with your SQLAlchemy models. These scripts describe the changes to be applied, such as adding a new table or modifying a column.
- Apply Migrations Consistently: Using Alembic ensures that all developers on a project apply database changes in the same order and manner, reducing discrepancies between development environments.
- Integrate with CI/CD Pipelines: Alembic can be incorporated into continuous integration and deployment workflows to automate database migrations during deployment.

### Key Components

- Migration Scripts: Python files that detail specific changes to the database schema.
- Command-Line Interface: Tools to create new migrations, apply existing ones, and manage the migration history.
- Configuration File: Defines connection strings and Alembic settings, typically named alembic.ini.

### Migration Architecture

Alembic manages database schema evolution through version-controlled migration scripts. Our setup uses autogeneration to maintain migrations based on SQLAlchemy models.

### Migration Configuration

The Alembic environment is configured in `env.py`:

```python
from database.session import Base
from database.event import *  # Required for autogeneration

target_metadata = Base.metadata

config.set_main_option(
    "sqlalchemy.url", 
    DatabaseUtils.get_connection_string()
)
```

### Migration Workflow

1. **Creating Migrations**
   ```bash
   ./makemigration.sh
   ```
   This script:
   - Detects model changes
   - Generates a new migration file
   - Adds it to version control

2. **Applying Migrations**
   ```bash
   ./migrate.sh
   ```
   This script:
   - Checks current database version
   - Applies pending migrations
   - Updates version tracking

### Migration Best Practices

1. **Version Control**
   - All migrations are version controlled
   - Migration files are treated as code
   - Never modify existing migrations

2. **Testing**
   - Test migrations on a copy of production data
   - Include both upgrade and downgrade paths
   - Verify data integrity after migration

3. **Deployment**
   - Run migrations before deploying new code
   - Back up database before migration
   - Use transaction wrapping for safety

## Database Utilities

The DatabaseUtils class provides centralized database configuration:

```python
class DatabaseUtils:
    @staticmethod
    def get_connection_string():
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
```

This ensures:

- Consistent connection string formatting
- Environment-based configuration
- Single source of truth for database settings

## Security Considerations

1. **Connection Security**
   - SSL/TLS encryption for connections
   - Strong password policies
   - Connection pooling limits

2. **Data Security**
   - JSON validation before storage
   - Input sanitization
   - Access control through repository layer

3. **Operational Security**
   - Regular backups
   - Migration rollback capabilities
   - Transaction isolation

## Performance Optimization

1. **Indexing Strategy**
   - UUID primary key optimization
   - JSON column indexing for common queries
   - Timestamp indexing for time-based queries

2. **Query Optimization**
   - Efficient JSON operators
   - Prepared statements
   - Connection pooling

## Extending the Database

To add new models:

1. Create a new model class:

```python
class CustomModel(Base):
    __tablename__ = "custom_models"
    id = Column(UUID(as_uuid=True), primary_key=True)
    # Add custom fields
```

2. Generate migration:

```bash

./makemigration.sh "add_custom_model"
```

3. Apply migration:

```bash
./migrate.sh
```

The modular design makes it straightforward to extend the database while maintaining data integrity and migration history.
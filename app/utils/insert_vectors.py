import sys
from pathlib import Path

app_root = Path(__file__).parent.parent
sys.path.append(str(app_root))

import json  # noqa: E402
from datetime import datetime  # noqa: E402

import pandas as pd  # noqa: E402
from services.vector_store import VectorStore  # noqa: E402
from timescale_vector.client import uuid_from_time  # noqa: E402

# Initialize VectorStore
vec = VectorStore(local=True)


def load_data():
    try:
        data_file = app_root.parent / "data" / "dataset.json"
        if not data_file.exists():
            raise FileNotFoundError(f"Dataset file not found at: {data_file}")

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)


# Prepare data for insertion
def prepare_record(row):
    """Prepare a record for insertion into the vector store.

    This function creates a record with a UUID version 1 as the ID, which captures
    the current time or a specified time.

    Note:
        - By default, this function uses the current time for the UUID.
        - To use a specific time:
          1. Import the datetime module.
          2. Create a datetime object for your desired time.
          3. Use uuid_from_time(your_datetime) instead of uuid_from_time(datetime.now()).

        Example:
            from datetime import datetime
            specific_time = datetime(2023, 1, 1, 12, 0, 0)
            id = str(uuid_from_time(specific_time))

        This is useful when your content already has an associated datetime.
    """
    content = f"Question: {row['question']}\nAnswer: {row['answer']}"
    embedding = vec.get_embedding(content)
    return pd.Series(
        {
            "id": str(uuid_from_time(datetime.now())),
            "metadata": {
                "category": row["category"],
                "created_at": datetime.now().isoformat(),
            },
            "contents": content,
            "embedding": embedding,
        }
    )


# Load data from JSON file
data = load_data()
df = pd.DataFrame(data)
records_df = df.apply(prepare_record, axis=1)

# Create tables and insert data
vec.create_tables()
vec.create_index()  # DiskAnnIndex
vec.upsert(records_df)

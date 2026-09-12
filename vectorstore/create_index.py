import os
from dotenv import load_dotenv
import chromadb

load_dotenv()


def create_index(
    persist_directory: str | None = None,
    collection_name: str | None = None
) -> None:
    """
    Create / initialize local ChromaDB vector store collection.

    Args:
        persist_directory: Path to persistent directory.
        collection_name: Name of the vector collection.
    """
    path = persist_directory or os.getenv("VECTOR_STORE_PATH", "./data/vectorstore")
    name = collection_name or os.getenv("VECTOR_STORE_COLLECTION", "investor-intelligence")

    os.makedirs(path, exist_ok=True)
    client = chromadb.PersistentClient(path=path)
    client.get_or_create_collection(name=name)

    print(f"ChromaDB collection '{name}' initialized successfully at '{path}'.")


if __name__ == "__main__":
    create_index()
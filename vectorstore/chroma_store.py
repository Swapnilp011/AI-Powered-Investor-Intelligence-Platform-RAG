import os
import uuid
from types import SimpleNamespace
import chromadb
from dotenv import load_dotenv

load_dotenv()


class ChromaVectorStore:
    """ChromaDB local persistent vector store."""

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None
    ) -> None:
        self.persist_directory = (
            persist_directory
            or os.getenv("VECTOR_STORE_PATH", "./data/vectorstore")
        )
        self.collection_name = (
            collection_name
            or os.getenv("VECTOR_STORE_COLLECTION", "investor-intelligence")
        )
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def upload_chunks(
        self,
        chunks: list,
        embeddings,
        company: str,
        year: str | int,
        source_file: str
    ) -> None:
        """
        Embed and upload document chunks to ChromaDB.
        """
        if not chunks:
            print("No chunks provided for upload.")
            return

        documents = [chunk.page_content for chunk in chunks]
        metadatas = [
            {
                "company": str(company),
                "year": str(year),
                "source_file": source_file
            }
            for _ in chunks
        ]
        ids = [str(uuid.uuid4()) for _ in chunks]

        # Generate vector embeddings
        if hasattr(embeddings, "embed_documents"):
            vectors = embeddings.embed_documents(documents)
        else:
            vectors = [embeddings.embed_query(doc) for doc in documents]

        self.collection.add(
            ids=ids,
            embeddings=vectors,
            documents=documents,
            metadatas=metadatas
        )

        print(f"Successfully uploaded {len(chunks)} chunks to ChromaDB collection '{self.collection_name}'.")


class Retriever:
    """
    Retriever for retrieving document chunks from ChromaDB with metadata filtering.
    Matches the interface expected by RAG extractor and Chat routes.
    """

    def __init__(
        self,
        embeddings=None,
        persist_directory: str | None = None,
        collection_name: str | None = None
    ) -> None:
        self.persist_directory = (
            persist_directory
            or os.getenv("VECTOR_STORE_PATH", "./data/vectorstore")
        )
        self.collection_name = (
            collection_name
            or os.getenv("VECTOR_STORE_COLLECTION", "investor-intelligence")
        )
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

        if embeddings is None:
            from llm.llm_client import get_embedding_client
            self.embeddings = get_embedding_client()
        else:
            self.embeddings = embeddings

    def invoke(
        self,
        query: str,
        company: str | None = None,
        year: int | str | None = None,
        top_k: int = 20
    ) -> list:
        """
        Retrieve relevant chunks from ChromaDB.
        Returns a list of SimpleNamespace objects with page_content attribute.
        """
        query_vector = self.embeddings.embed_query(query)

        # Build metadata filter
        where_filter = None
        if company and year:
            where_filter = {
                "$and": [
                    {"company": {"$eq": str(company)}},
                    {"year": {"$eq": str(year)}}
                ]
            }
        elif company:
            where_filter = {"company": {"$eq": str(company)}}
        elif year:
            where_filter = {"year": {"$eq": str(year)}}

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_filter
        )

        documents = []
        if results and "documents" in results and results["documents"]:
            doc_list = results["documents"][0]
            for doc in doc_list:
                documents.append(SimpleNamespace(page_content=doc))

        return documents

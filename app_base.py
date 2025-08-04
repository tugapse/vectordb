import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

# Define a default database name. This can be overridden when initializing ChromaAppBase
# or by the CHROMA_DB_PATH environment variable.
DEFAULT_DB_NAME = "my_app_db"

class ChromaAppBase:
    """
    A base class for interacting with ChromaDB.

    This class provides core functionalities for managing ChromaDB clients,
    collections, and documents. It supports persistent storage by resolving
    the database path from explicit arguments, environment variables, or a
    default location in the user's home directory.
    """

    def __init__(self, db_path: str = None, db_name: str = DEFAULT_DB_NAME):
        """
        Initializes the ChromaDB client.

        The database path is resolved in the following order of precedence:
        1. Explicit `db_path` argument.
        2. `CHROMA_DB_PATH` environment variable.
        3. Default path: `~/.chromadb/{db_name}/`.

        If no persistent path is resolved, an in-memory client is used.

        Args:
            db_path (str, optional): Explicit path to the ChromaDB directory.
                                     Defaults to None.
            db_name (str, optional): A name for the database, used in the
                                     default path. Defaults to DEFAULT_DB_NAME.
        """
        self.db_name = db_name
        self.client = None
        self.db_directory = None

        # 1. Check for explicit db_path argument
        if db_path:
            self.db_directory = Path(db_path).expanduser().resolve()
        else:
            # 2. Check for CHROMA_DB_PATH environment variable
            env_db_path = os.getenv("CHROMA_DB_PATH")
            if env_db_path:
                self.db_directory = Path(env_db_path).expanduser().resolve()
            else:
                # 3. Default to ~/.chromadb/{db_name}/
                self.db_directory = Path.home() / ".chromadb" / self.db_name

        # Initialize ChromaDB client
        if self.db_directory:
            # Ensure the directory exists for persistent storage
            self.db_directory.mkdir(parents=True, exist_ok=True)
            print(f"Initializing persistent ChromaDB at: {self.db_directory}")
            self.client = chromadb.PersistentClient(path=str(self.db_directory))
        else:
            print("Initializing in-memory ChromaDB.")
            self.client = chromadb.Client() # In-memory client

        # Initialize the default embedding function
        # Requires 'sentence-transformers' to be installed (e.g., pip install sentence-transformers)
        try:
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        except Exception as e:
            print(f"Warning: Could not load DefaultEmbeddingFunction. Please ensure 'sentence-transformers' is installed. Error: {e}")
            print("Using a dummy embedding function. Document additions/queries might not work as expected.")
            # Fallback to a dummy embedding function if sentence-transformers is not available
            # The dimension (384) is typical for 'all-MiniLM-L6-v2' used by DefaultEmbeddingFunction
            self.embedding_function = lambda texts: [[0.0] * 384 for _ in texts]

    def _get_collection(self, collection_name: str, create_if_not_exists: bool = False):
        """
        Internal helper method to get a ChromaDB collection.

        Args:
            collection_name (str): The name of the collection.
            create_if_not_exists (bool): If True, creates the collection if it does not exist.

        Returns:
            chromadb.api.models.Collection.Collection: The ChromaDB collection object.

        Raises:
            ValueError: If the collection does not exist and create_if_not_exists is False.
        """
        try:
            # Use get_or_create_collection to simplify logic, it handles both cases
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            return collection
        except Exception as e:
            # If get_or_create_collection fails, it indicates a deeper issue or a misconfiguration
            # rather than just non-existence if create_if_not_exists is True.
            # For non-existence when create_if_not_exists is False, ChromaDB's get_collection
            # would raise a specific exception, which get_or_create_collection wraps.
            raise ValueError(f"Could not get or create collection '{collection_name}': {e}")


    def create_collection(self, collection_name: str):
        """
        Creates a new ChromaDB collection.

        Args:
            collection_name (str): The name of the collection to create.

        Returns:
            chromadb.api.models.Collection.Collection: The created collection object.
        """
        try:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"Collection '{collection_name}' created successfully.")
            return collection
        except Exception as e:
            print(f"Error creating collection '{collection_name}': {e}")
            return None

    def delete_collection(self, collection_name: str):
        """
        Deletes a ChromaDB collection.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        try:
            self.client.delete_collection(name=collection_name)
            print(f"Collection '{collection_name}' deleted successfully.")
        except Exception as e:
            print(f"Error deleting collection '{collection_name}': {e}")

    def list_collections(self):
        """
        Lists all existing ChromaDB collections.

        Returns:
            list: A list of ChromaDB collection objects.
        """
        try:
            collections = self.client.list_collections()
            if collections:
                print("Available Collections:")
                for col in collections:
                    print(f"- {col.name}")
            else:
                print("No collections found.")
            return collections
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []

    def add_documents(self, collection_name: str, documents: list[str], metadatas: list[dict] = None, ids: list[str] = None):
        """
        Adds documents to a specified ChromaDB collection.

        Args:
            collection_name (str): The name of the collection.
            documents (list[str]): A list of text documents to add.
            metadatas (list[dict], optional): A list of dictionaries, where each dict
                                               contains metadata for the corresponding document.
                                               Must be the same length as `documents`.
                                               Defaults to None.
            ids (list[str], optional): A list of unique IDs for the documents. If None,
                                       ChromaDB will generate them. Must be the same length
                                       as `documents`. Defaults to None.
        """
        if not documents:
            print("No documents provided to add.")
            return

        if metadatas and len(metadatas) != len(documents):
            print("Error: Length of metadatas must match length of documents.")
            return

        if ids and len(ids) != len(documents):
            print("Error: Length of ids must match length of documents.")
            return

        try:
            # Ensure the collection exists, create if not
            collection = self._get_collection(collection_name, create_if_not_exists=True)
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(documents)} document(s) to collection '{collection_name}'.")
        except ValueError as ve:
            print(f"Error adding documents: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred while adding documents: {e}")

    def query_documents(self, collection_name: str, query_texts: list[str], n_results: int = 5, where: dict = None, where_document: dict = None):
        """
        Queries a collection for documents similar to the query texts.

        Args:
            collection_name (str): The name of the collection to query.
            query_texts (list[str]): A list of texts to query with.
            n_results (int, optional): The number of top results to return. Defaults to 5.
            where (dict, optional): A dictionary for metadata filtering. Defaults to None.
            where_document (dict, optional): A dictionary for document content filtering.
                                            Defaults to None.

        Returns:
            dict: The query results from ChromaDB.
        """
        if not query_texts:
            print("No query texts provided.")
            return {}

        try:
            collection = self._get_collection(collection_name)
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=['documents', 'distances', 'metadatas'] # Include relevant information
            )
            print(f"Query results from collection '{collection_name}':")
            if results and results.get('documents'):
                for i, doc_list in enumerate(results['documents']):
                    print(f"\n--- Query: '{query_texts[i]}' ---")
                    if not doc_list:
                        print("  No matching documents found.")
                        continue
                    for j, doc in enumerate(doc_list):
                        doc_id = results['ids'][i][j]
                        distance = results['distances'][i][j]
                        metadata = results['metadatas'][i][j]
                        print(f"  Result {j+1} (ID: {doc_id}):")
                        print(f"    Document: {doc}")
                        print(f"    Distance: {distance:.4f}")
                        if metadata:
                            print(f"    Metadata: {metadata}")
            else:
                print("No results found for the query.")
            return results
        except ValueError as ve:
            print(f"Error querying documents: {ve}")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while querying documents: {e}")
            return {}

    def delete_documents(self, collection_name: str, ids: list[str] = None, where: dict = None, where_document: dict = None):
        """
        Deletes documents from a specified ChromaDB collection based on IDs or filters.

        Args:
            collection_name (str): The name of the collection.
            ids (list[str], optional): A list of document IDs to delete. Defaults to None.
            where (dict, optional): A dictionary for metadata filtering. Defaults to None.
            where_document (dict, optional): A dictionary for document content filtering.
                                            Defaults to None.
        """
        if not ids and not where and not where_document:
            print("No IDs or filters provided for deletion. Specify at least one criterion.")
            return

        try:
            collection = self._get_collection(collection_name)
            # ChromaDB's delete method returns the IDs of the deleted documents
            deleted_ids = collection.delete(
                ids=ids,
                where=where,
                where_document=where_document
            )
            if deleted_ids:
                print(f"Deleted {len(deleted_ids)} document(s) from collection '{collection_name}'.")
                print(f"Deleted IDs: {deleted_ids}")
            else:
                print(f"No documents matched the criteria for deletion in collection '{collection_name}'.")
        except ValueError as ve:
            print(f"Error deleting documents: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred while deleting documents: {e}")

    def get_all_documents(self, collection_name: str):
        """
        Retrieves all documents, their IDs, and metadata from a specified collection.

        Args:
            collection_name (str): The name of the collection to retrieve documents from.

        Returns:
            dict: A dictionary containing 'ids', 'documents', and 'metadatas' for all
                  documents in the collection. Returns an empty dict if no documents
                  or collection not found.
        """
        try:
            collection = self._get_collection(collection_name)
            # Use collection.get() with no filters to retrieve all documents
            all_data = collection.get(
                ids=None, # No specific IDs, so get all
                where=None,
                where_document=None,
                limit=None, # No limit, get all
                offset=None,
                include=['documents', 'metadatas'] # Include content and metadata
            )

            if all_data and all_data.get('ids'):
                print(f"Retrieved {len(all_data['ids'])} documents from collection '{collection_name}':")
                for i in range(len(all_data['ids'])):
                    doc_id = all_data['ids'][i]
                    document = all_data['documents'][i]
                    metadata = all_data['metadatas'][i]
                    print(f"\n--- Document ID: {doc_id} ---")
                    print(f"  Document: {document}")
                    if metadata:
                        print(f"  Metadata: {metadata}")
            else:
                print(f"No documents found in collection '{collection_name}'.")
            return all_data
        except ValueError as ve:
            print(f"Error retrieving all documents: {ve}")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while retrieving all documents: {e}")
            return {}

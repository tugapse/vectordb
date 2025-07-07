import argparse
import json

def parse_metadata_arg(metadata_list):
    """
    Parses a list of 'key=value' strings into a dictionary.
    """
    if not metadata_list:
        return None
    metadata_dict = {}
    for item in metadata_list:
        if '=' in item:
            key, value = item.split('=', 1)
            metadata_dict[key] = value
        else:
            print(f"Warning: Metadata item '{item}' is not in 'key=value' format and will be ignored.")
    return metadata_dict

def build_parser():
    """
    Builds and returns the ArgumentParser for the ChromaDB CLI.
    This function defines all the commands and arguments.
    """
    parser = argparse.ArgumentParser(
        description="ChromaDB CLI Application",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--db-path",
        type=str,
        help="Explicit path to the ChromaDB directory. Overrides CHROMA_DB_PATH env var and default."
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default="my_chroma_app_db", # Use a default here, as DEFAULT_DB_NAME is in chroma_app_base
        help=f"Name for the database, used in the default path (~/.chromadb/{{db_name}}/). "
             f"Defaults to 'my_chroma_app_db'. Ignored if --db-path is provided."
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Collection Commands ---
    collection_parser = subparsers.add_parser(
        "collection", help="Manage ChromaDB collections."
    )
    collection_subparsers = collection_parser.add_subparsers(
        dest="collection_command", help="Collection commands"
    )

    # Collection Create
    create_collection_parser = collection_subparsers.add_parser(
        "create", help="Create a new collection."
    )
    create_collection_parser.add_argument(
        "name", type=str, help="Name of the collection to create."
    )

    # Collection Delete
    delete_collection_parser = collection_subparsers.add_parser(
        "delete", help="Delete a collection."
    )
    delete_collection_parser.add_argument(
        "name", type=str, help="Name of the collection to delete."
    )

    # Collection List
    list_collection_parser = collection_subparsers.add_parser(
        "list", help="List all collections."
    )

    # --- Document Commands ---
    document_parser = subparsers.add_parser(
        "document", help="Manage documents within a collection."
    )
    document_subparsers = document_parser.add_subparsers(
        dest="document_command", help="Document commands"
    )

    # Document Add
    add_document_parser = document_subparsers.add_parser(
        "add", help="Add documents to a collection."
    )
    add_document_parser.add_argument(
        "collection_name", type=str, help="Name of the collection to add documents to."
    )
    add_document_parser.add_argument(
        "--text",
        action="append", # Allows multiple --text arguments
        required=True,
        help="Text content of the document. Use multiple --text for multiple documents."
    )
    add_document_parser.add_argument(
        "--metadata",
        action="append", # Allows multiple --metadata arguments
        help="Metadata for the document in 'key=value' format. "
             "If adding multiple documents, provide metadata for each in order. "
             "Example: --metadata 'author=John Doe' --metadata 'year=2023'"
    )
    add_document_parser.add_argument(
        "--id",
        action="append", # Allows multiple --id arguments
        help="Unique ID for the document. If adding multiple documents, provide IDs for each in order."
    )

    # Document Query
    query_document_parser = document_subparsers.add_parser(
        "query", help="Query documents in a collection."
    )
    query_document_parser.add_argument(
        "collection_name", type=str, help="Name of the collection to query."
    )
    query_document_parser.add_argument(
        "--query-text",
        action="append", # Allows multiple --query-text arguments
        required=True,
        help="Text to query for similarity. Use multiple --query-text for multiple queries."
    )
    query_document_parser.add_argument(
        "--n-results",
        type=int,
        default=5,
        help="Number of top results to return. Defaults to 5."
    )
    query_document_parser.add_argument(
        "--where",
        type=str,
        help="JSON string for metadata filtering (e.g., '{\"author\": \"John\"}')."
    )
    query_document_parser.add_argument(
        "--where-document",
        type=str,
        help="JSON string for document content filtering (e.g., '{\"$contains\": \"keyword\"}')."
    )

    # Document Delete
    delete_document_parser = document_subparsers.add_parser(
        "delete", help="Delete documents from a collection."
    )
    delete_document_parser.add_argument(
        "collection_name", type=str, help="Name of the collection to delete documents from."
    )
    delete_document_parser.add_argument(
        "--id",
        action="append", # Allows multiple --id arguments
        help="ID(s) of the document(s) to delete."
    )
    delete_document_parser.add_argument(
        "--where",
        type=str,
        help="JSON string for metadata filtering (e.g., '{\"author\": \"John\"}')."
    )
    delete_document_parser.add_argument(
        "--where-document",
        type=str,
        help="JSON string for document content filtering (e.g., '{\"$contains\": \"keyword\"}')."
    )

    # Document Get All
    get_all_document_parser = document_subparsers.add_parser(
        "get-all", help="Retrieve all documents from a collection."
    )
    get_all_document_parser.add_argument(
        "collection_name", type=str, help="Name of the collection to retrieve documents from."
    )

    return parser


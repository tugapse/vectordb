import cli
import json
from app_base import ChromaAppBase, DEFAULT_DB_NAME 

def main():
    """
    Main entry point for the ChromaDB CLI application.
    Parses command-line arguments and dispatches to ChromaAppBase methods.
    """
    parser = cli.build_parser()
    args = parser.parse_args()

    if not hasattr(args, 'command') or args.command is None:
        parser.print_help()
        return # Exit after printing help

    app = ChromaAppBase(db_path=args.db_path, db_name=args.db_name)

    try:
        if args.command == "collection":
            if args.collection_command == "create":
                app.create_collection(args.name)
            elif args.collection_command == "delete":
                app.delete_collection(args.name)
            elif args.collection_command == "list":
                app.list_collections()
            else:
                # This case should ideally not be reached if argparse is configured correctly
                # to require a sub-command.
                print("Invalid collection command.")
        elif args.command == "document":
            if args.document_command == "add":
                # Parse metadata if provided
                metadatas = None
                if args.metadata:
                    # If multiple documents, try to parse metadata for each
                    if len(args.metadata) == len(args.text):
                        # Each metadata string is treated as a single metadata dict for a document
                        metadatas = [cli.parse_metadata_arg([m]) for m in args.metadata]
                    elif len(args.metadata) == 1 and len(args.text) > 1:
                        # Apply same metadata to all if only one metadata string is given for multiple texts
                        single_metadata = cli.parse_metadata_arg(args.metadata)
                        metadatas = [single_metadata] * len(args.text)
                    else:
                        print("Warning: Number of --metadata arguments does not match number of --text arguments. Metadata will be ignored.")
                        metadatas = None
                app.add_documents(
                    collection_name=args.collection_name,
                    documents=args.text,
                    metadatas=metadatas,
                    ids=args.id
                )
            elif args.document_command == "query":
                where_clause = json.loads(args.where) if args.where else None
                where_document_clause = json.loads(args.where_document) if args.where_document else None
                app.query_documents(
                    collection_name=args.collection_name,
                    query_texts=args.query_text,
                    n_results=args.n_results,
                    where=where_clause,
                    where_document=where_document_clause
                )
            elif args.document_command == "delete":
                where_clause = json.loads(args.where) if args.where else None
                where_document_clause = json.loads(args.where_document) if args.where_document else None
                app.delete_documents(
                    collection_name=args.collection_name,
                    ids=args.id,
                    where=where_clause,
                    where_document=where_document_clause
                )
            elif args.document_command == "get_all":
                app.get_all_documents(collection_name=args.collection_name)
            else:
                # This case should ideally not be reached if argparse is configured correctly
                # to require a sub-command.
                print("Invalid document command.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format for --where or --where-document. Please ensure it's valid JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

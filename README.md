**# ChromaDB CLI Application**
=====================================

## **Introduction**
---------------

The ChromaDB CLI application is a command-line interface for interacting with the ChromaDB database. It provides core functionalities for managing collections and documents within the database.

## **Installation**
-----------------

Ensure you have Python 3.8 or higher installed on your system.

```bash
pip install -r "requirements.txt"
```

**Usage**

To use the ChromaDB CLI, follow these steps:


### **Run the CLI**

Run the ChromaDB CLI by executing the following command in your terminal:

```bash
python main.py
```

### **List Available Commands**

Use `--help` to list available commands and their usage.

```bash
python main.py --help
```
### **Create a Database**

To create a new database, use the following command with the `--db-path` option to specify a custom path or use an environment variable like `CHROMA_DB_PATH`. If no path is provided, it will default to `~/.chromadb/{DB_NAME}`.

```bash
python main.py --db-path ~/my_db_directory
```

### **Manage Collections**

Use the `collection` command to manage collections in your database.

   * Create a new collection with the following command:
```bash
python main.py collection create my_collection_name
```
   * List all available collections using:
```bash
python main.py collection list
```
   * Delete a collection using:
```bash
python main.py collection delete my_collection_name
```

### **Manage Documents**

Use the `document` command to manage documents within a collection.

   * Add multiple documents to an existing collection with their metadata and IDs (optional):
```bash
python main.py document add --collection-name my_collection_name --text "doc1 content" "doc2 content" \
--metadata 'author=John Doe' 'year=2023' \
--id doc1_id doc2_id
```
   * Query for documents within a collection that are similar to your query texts, optionally filtering by metadata or document text:

```bash
python main.py document query --collection-name my_collection_name --query-text "Query 1" "Query 2"
```

   * Delete multiple documents from an existing collection based on their IDs or optional filters:

```bash
python main.py document delete --collection-name my_collection_name --id doc1_id doc2_id \
--where 'author=John Doe' \
--where-document '{"$contains": "specific keyword"}'
```

### **Retrieve All Documents from a Collection**

   To retrieve all documents and their metadata for an entire collection, use the following command:
   ```bash
python main.py document get-all --collection-name my_collection_name
```
### **View Help**

At any point during usage, view the help for a specific command by adding `--help` at the end of it.

This CLI provides basic functions to interact with ChromaDB collections and documents. For more advanced features or complex operations, refer to the [ChromaDB documentation](https://chroma.db/docs).
~
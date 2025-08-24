# OpenAI Conversation Importer for Graphiti

This project provides a set of Python scripts to parse your OpenAI conversation history and import it into a [Graphiti](https://github.com/Graphiti-AI/graphiti-python) knowledge graph. This allows you to analyze and query your past conversations using the power of a graph database.

## How it Works

The process is broken down into two main steps:

1.  **Parsing:** The `parse.py` script reads the `conversations.json` file exported from your OpenAI account. It extracts each conversation, cleans it up, and saves it as a separate text file. It also creates a `conversation_summary.json` file that contains metadata about each conversation.

2.  **Importing:** The `add_memory_graphiti.py` script takes the `conversation_summary.json` and imports each conversation as an "episode" into your Graphiti knowledge graph. It connects to a Neo4j database and uses the Graphiti library to handle the import process.

The `main.py` script orchestrates this entire process, reading a `config.yaml` file for configuration.

## Prerequisites

*   Python 3.7+
*   An OpenAI account and your `conversations.json` export.
*   A running Neo4j instance.
*   The required Python packages listed in `pyproject.toml`.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Fisher2107/Memory-Test-with-OpenAI-conversations
    cd openai-graphiti-importer
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Configure the application:**
    Create a `config.yaml` file in the root of the project 

## Exporting OpenAI Data

To get your conversation history, you need to export it from your OpenAI account. Follow the instructions in this link: [How to export your ChatGPT history and data](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data).

You will receive an email with a link to download a zip file. Unpack this file and place the `conversations.json` file in the directory specified by `data_folder` in your `config.yaml`.

## Usage

Once you have completed the setup, you can run the importer:

```bash
uv run python main.py
```

The script will first parse your OpenAI conversations and then import them into your Graphiti knowledge graph.

## Scripts

*   `main.py`: The main entry point for the application.
*   `parse.py`: Handles the parsing of the `conversations.json` file.
*   `add_memory_graphiti.py`: Imports the parsed conversations into Graphiti.
*   `test_memory.py`: (Optional) A script for testing the Graphiti integration.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
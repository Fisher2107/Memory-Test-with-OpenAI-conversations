import json
from test_memory import test_graphiti
from add_memory_graphiti import add_episodes_graphiti
from parse import parse
import yaml
import os
import asyncio


async def main():
    # Load config.yaml
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Access OpenAI data folders
    data_folder = config["openai_data"]["data_folder"]
    output_folder = config["openai_data"]["output_folder"]
    assert os.path.isdir(data_folder), "Cannot find provided openai_data -> data_folder"
    assert os.path.isdir(
        output_folder
    ), "Cannot find provided openai_data -> output_folder"


    # Step 1: parse provided OpenAI data folder
    input_file = data_folder + "/conversations.json"
    print(input_file)
    assert os.path.isfile(
        input_file
    ), "Ensure that conversations.json exists within provided openai_data -> data_folder"

    parse(input_file, output_folder)

    conversation_summary_path = output_folder + "/conversation_summary.json"
    assert os.path.isfile(
        conversation_summary_path
    ), "Parsing failed: Was unable to produce conversation summary"

    with open(conversation_summary_path, "r") as f:
        conversation_summary = json.load(f)


    # Step 2: insert parsed openai data into graphiti
    await add_episodes_graphiti(config["NEO-4j"], config["model_config"], conversation_summary)

    # Step 3 (Optional): Run your test data TODO
    # if config.get('test'):
    #     #Load test questions
    #     test_questions = []
    #     await test_graphiti(config["NEO-4j"], config["llmconfig"],test_questions)


if __name__ == "__main__":
    asyncio.run(main())

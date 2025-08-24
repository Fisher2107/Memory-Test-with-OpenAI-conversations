from graphiti_core import Graphiti
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.nodes import EpisodeType 
from tqdm import tqdm
from datetime import datetime


async def add_episodes_graphiti(
    neo4j_config: dict, model_config: dict, conversation_summary: dict
):
    #################################################
    # INITIALIZATION
    #################################################
    # Connect to Neo4j and set up Graphiti indices
    # This is required before using other Graphiti
    # functionality
    #################################################

    # Access Neo4j settings
    neo4j_user = neo4j_config["user"]
    neo4j_pass = neo4j_config["pass"]
    neo4j_uri = neo4j_config["uri"]

    # Access llm configuration settings
    provider = model_config["provider"]
    assert provider in [
        "OpenAI",
        "Ollama",
    ], "Ensure llmconfig -> provider is either OpenAI or Ollama"

    if provider == "OpenAI":
        graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_pass)

    elif provider == "Ollama":
        required_keys = ["api_key", "llm_model", "embed_model", "embed_dim", "url"]
        assert all(
            key in model_config for key in required_keys
        ), f"Missing required keys for Ollama config: {[k for k in required_keys if k not in model_config]}"

        llm_config = LLMConfig(
            api_key=model_config["api_key"],
            model=model_config["llm_model"],
            small_model=model_config["llm_model"],
            base_url=model_config["url"],
        )

        llm_client = OpenAIClient(config=llm_config)

        embedder = OpenAIEmbedder(
                config=OpenAIEmbedderConfig(
                    api_key=model_config["api_key"],
                    embedding_model=model_config["embed_model"],
                    embedding_dim=model_config["embed_dim"],
                    base_url=model_config["url"],
                )
            ) 
        
        cross_encoder = OpenAIRerankerClient(client=llm_client, config=llm_config)

        graphiti = Graphiti(
            neo4j_uri,
            neo4j_user,
            neo4j_pass,
            llm_client=llm_client,
            embedder=embedder,
            cross_encoder=cross_encoder,
        )

    try:
        # Initialize the graph database with graphiti's indices. This only needs to be done once.
        await graphiti.build_indices_and_constraints()

        #################################################
        # ADDING EPISODES
        #################################################
        # Episodes are the primary units of information
        # in Graphiti. They can be text or structured JSON
        # and are automatically processed to extract entities
        # and relationships.
        #################################################

        # Load episodes
        episodes = []

        for month, conversations in conversation_summary.items():   # month = "2025_08"
            for conversation in conversations:
                # print(conversation)
                # Build episode body from messages
                episode_body = ""
                for msg in conversation.get("messages", []):
                    episode_body += f"{msg['author']}: {msg['text']}\n"

                # Convert update_time (or create_time) to datetime
                ref_time_str = conversation.get("update_time") or conversation.get("create_time")
                try:
                    reference_time = datetime.strptime(ref_time_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    reference_time = datetime.now()

                # Construct episode object (dict) to pass later
                episode = dict(
                    name=conversation["title"].replace(" ", "_"),   # safe name
                    episode_body=episode_body.strip(),
                    source=EpisodeType.message,
                    source_description=f"Conversation between user and agent",
                    reference_time=reference_time,
                )

                episodes.append(episode)

        # Add episodes to the graph
        for episode in tqdm(episodes, total=len(episodes)):
            await graphiti.add_episode(**episode)
    
    finally:
        #################################################
        # CLEANUP
        #################################################
        # Always close the connection to Neo4j when
        # finished to properly release resources
        #################################################

        # Close the connection
        await graphiti.close()
        print("\nConnection closed")

import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.cosmos import CosmosClient
from openai import AzureOpenAI


def get_query_vector(prompt: str):
    """
    Generate an embedding vector for the user's natural-language prompt.
    Must use the SAME embedding model you used when creating the stored embeddings.
    """
    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )

    ai = AzureOpenAI(
        azure_endpoint=os.environ["FOUNDRY_ENDPOINT"],
        azure_ad_token_provider=token_provider,
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-01-preview"),
    )

    model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    resp = ai.embeddings.create(model=model, input=prompt)
    return resp.data[0].embedding


def vector_search_cosmos(query_vector, top_k: int = 7):
    """
    Query Cosmos DB in Fabric for top_k closest vectors.
    Lower VectorDistance = more similar.
    """
    credential = DefaultAzureCredential()

    client = CosmosClient(
        os.environ["COSMOS_ENDPOINT"],
        credential=credential
    )

    container = (
        client.get_database_client(os.environ.get("COSMOS_DB", "movielens-db"))
              .get_container_client(os.environ.get("COSMOS_CONTAINER", "animated-movies"))
    )

    query = f"""
    SELECT TOP {top_k}
        c.id,
        c.title,
        c.genres,
        c.description,
        VectorDistance(c.embedding, @qv) AS score
    FROM c
    ORDER BY VectorDistance(c.embedding, @qv)
    """

    results = list(container.query_items(
        query=query,
        parameters=[{"name": "@qv", "value": query_vector}],
        enable_cross_partition_query=True
    ))

    return results


def main():
    load_dotenv()

    print("=== MovieLens Animated Movies: Simple Semantic Search ===\n")
    while True:
        prompt = input("Ask for an animated movie (or 'q' to quit): ").strip()
        if prompt.lower() in ("q", "quit", "exit"):
            break
        if not prompt:
            continue

        qv = get_query_vector(prompt)
        hits = vector_search_cosmos(qv, top_k=7)

        print("\nTop matches:\n")
        for i, h in enumerate(hits, start=1):
            title = h.get("title", "<no title>")
            score = h.get("score", None)
            genres = h.get("genres", "")
            desc = h.get("description", "")

            print(f"{i}. {title}  | score={score:.4f}" if isinstance(score, (int, float)) else f"{i}. {title}")
            if genres:
                print(f"   genres: {genres}")
            if desc:
                print(f"   desc/tags: {desc}")
            print()

        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()
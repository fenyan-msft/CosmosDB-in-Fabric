# Movies Semantic Search Demo using Cosmos DB in Fabric

A demo application that showcases semantic search capabilities in Cosmos DB in Microsoft Fabric, using movie data.

## Prerequisites

Before setting up this demo, ensure you have:

- **Azure Subscription**: Required for Azure Key Vault and Microsoft Foundry
- **Microsoft Fabric Workspace**: Access to Microsoft Fabric for lakehouse and Cosmos DB
- **Python 3.8+**: For running the search application
- **Visual Studio Code**: Recommended for working with notebooks and code

## Setup Instructions

### Step 1: Download MovieLens 25M Dataset

Download the MovieLens 25M dataset from [GroupLens](https://grouplens.org/datasets/movielens/25m/). Extract the CSV files. You'll need:
- `movies.csv`
- `ratings.csv`
- `links.csv`

### Step 2: Register with TMDB and Get an API Key

1. Create an account at [The Movie Database (TMDB)](https://www.themoviedb.org/)
2. Navigate to your account settings → API section
3. Request an API key (choose the free tier for personal/educational use)
4. Save your API key securely - you'll need it for fetching movie descriptions

### Step 3: Create Microsoft Foundry Resources

1. Create a Microsoft Foundry resource in Azure Portal
2. Navigate to the Foundry portal
3. Create a new project
4. Deploy an embedding model (recommended: `text-embedding-3-small`)
5. Note your Foundry endpoint URL and key for later configuration

### Step 4: Create an Azure Key Vault

Create an Azure Key Vault to securely store your API keys as secrets. You can do this in the Azure Portal or using the code below:

```
az keyvault create --name <your-keyvault-name> --resource-group <your-rg> --location <region>
```

Store your secrets:
```
az keyvault secret set --vault-name <your-keyvault-name> --name "TMDB-API-KEY" --value "<your-tmdb-key>"
az keyvault secret set --vault-name <your-keyvault-name> --name "FOUNDRY-ENDPOINT-KEY" --value "<your-foundry-key>"
```

### Step 5: Create Fabric Workspace and Lakehouse

1. Open [Microsoft Fabric](https://app.fabric.microsoft.com/)
2. Create a new workspace
3. In the workspace, create a new **Lakehouse**
4. Navigate to the lakehouse's **Files** section
5. Upload the MovieLens movies, ratings and links CSV files you downloaded in Step 1

### Step 6: Import and Run the Data Transformation Notebook

1. Import the notebooks from the `notebooks/` folder into your Fabric workspace:
   - `Load and Transform Movie Data.ipynb`
   - `Write from Lakehouse to Cosmos DB.ipynb`
2. For each imported notebook, add the lakehouse you created in Step 5:
   - Open the notebook
   - Click **Add lakehouse** (or the lakehouse icon)
   - Select **Existing lakehouse** and choose the lakehouse you created
3. Open **Load and Transform Movie Data.ipynb**
4. Update the notebook with your key vault references
5. Run the cells one at a time to:
   - Load MovieLens data
   - Fetch movie descriptions from TMDB
   - Generate embeddings using your Foundry embedding model
   - Save the enriched data back to the lakehouse

### Step 7: Create Cosmos DB Database in Fabric

1. In your Fabric workspace, create a new **Cosmos DB** database
2. Create a container with the following configuration:
   - **Partition key**: `/id`
   - **Vector policy**: Enable vector indexing for the `embedding` field, 
   
Example vector policy configuration:
```json
{
  "vectorEmbeddings": [
    {
      "path": "/embedding",
      "dataType": "float32",
      "dimensions": 1536,
      "distanceFunction": "cosine"
    }
  ]
}
```

### Step 8: Write Data to Cosmos DB

1. Open **Write from Lakehouse to Cosmos DB.ipynb**
2. Configure the notebook with your Cosmos DB connection details
3. Run the cells one at a time to write the movie data with embeddings from the lakehouse to your Cosmos DB container

### Step 9: Configure Local Environment

1. Copy the `.env_example` file to `.env`:

2. Fill in the required values in `.env`:
   ```env
   COSMOS_ENDPOINT=https://<your-cosmos-account>.documents.azure.com:443/
   COSMOS_DB=<database name>
   COSMOS_CONTAINER=<container name>
   
   FOUNDRY_ENDPOINT=https://<your-foundry-endpoint>
   EMBEDDING_MODEL=<model deployed>
   AZURE_OPENAI_API_VERSION=<API version from the model description>
   ```

### Step 10: Run the Search Application

1. In a terminal window, create and activate a virtual environment:
   
   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   
   **macOS/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install Python dependencies:
   ```
   pip install azure-cosmos azure-identity openai python-dotenv
   ```

3. Authenticate with Azure:
   ```
   az login
   ```

4. Run the search application:
   ```
   python simple_search.py
   ```

5. Enter natural language queries to search for animated movies!


## Usage

Once the application is running, you can enter natural language queries:

```
=== MovieLens Animated Movies: Simple Semantic Search ===

Ask for an animated movie (or 'q' to quit): a movie about friendship and adventure

Top matches:

1. Toy Story  | score=0.8234
   genres: Animation|Children|Comedy
   desc/tags: A cowboy doll is profoundly threatened when a new spaceman figure...

2. Finding Nemo  | score=0.8156
   genres: Animation|Children|Adventure
   desc/tags: A clownfish travels across the ocean to find his missing son...

...
```

### Example Queries

- "a magical princess story"
- "robots and technology"
- "friendship and adventure in space"
- "classic Disney animation"
- "superhero family"

Type `q`, `quit`, or `exit` to close the application.

## Project Structure

```
CosmosDB-in-Fabric/
├── simple_search.py              # Main search application
├── .env_example                  # Environment variable template
├── .env                          # Your configuration (git-ignored)
├── notebooks/
│   ├── Load and Transform Movie Data.ipynb
│   └── Write from Lakehouse to Cosmos DB.ipynb
└── README.md                     # This file
```

### Key Files

- **simple_search.py**: Interactive command-line application for semantic search. Generates embeddings for user queries and searches Cosmos DB using vector similarity.
- **Load and Transform Movie Data.ipynb**: Notebook for loading MovieLens data, fetching TMDB descriptions, and generating embeddings.
- **Write from Lakehouse to Cosmos DB.ipynb**: Notebook for transferring enriched movie data from Fabric lakehouse to Cosmos DB.
- **.env_example**: Template showing required environment variables.

## Authentication

This demo uses **DefaultAzureCredential** from Azure Identity library, which supports multiple authentication methods:
- Azure CLI (`az login`)
- Managed Identity (when running in Azure)
- Environment variables
- Visual Studio Code
- Azure PowerShell

Ensure you're authenticated via one of these methods before running the application.

## License

This demo uses publicly available datasets. Please review the licenses for:
- [MovieLens Dataset](https://grouplens.org/datasets/movielens/) - provided by GroupLens Research
- [TMDB API](https://www.themoviedb.org/documentation/api/terms-of-use) - review terms of use

## Troubleshooting

**Authentication Errors**: Run `az login` to authenticate with Azure CLI.

**Module Not Found Errors**: Ensure all dependencies are installed: `pip install azure-cosmos azure-identity openai python-dotenv`

**Cosmos DB Connection Issues**: Verify your `COSMOS_ENDPOINT` is correct and your Azure account has appropriate RBAC permissions (Cosmos DB Data Contributor role).

**Vector Search Returns No Results**: Ensure your Cosmos DB container has the vector policy configured correctly and contains data with embeddings.

**Embedding Generation Fails**: Verify your `FOUNDRY_ENDPOINT` and ensure the embedding model deployment is active in your Foundry project.

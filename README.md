# Hooper AI Agent

**Hooper AI Agent** is a powerful sports science assistant designed to guide athletes in improving their **mental, psychological, physical, and nutritional wellbeing**. By leveraging multiple specialized AI agents, Hooper AI provides personalized advice and actionable insights to enhance performance.

---

## Agent Details

Hooper AI is a **multimodal agent** composed of several sub-agents, each specialized to address different aspects of athletic development:

1. **Faith & Mental Agent**  
   Provides mental guidance to help athletes manage stress, maintain focus, and stay motivated in a high-performance lifestyle.

2. **Drills Agent**  
   Recommends basketball drills through YouTube videos, tailored to the user's weaknesses using the `search_youtube` tool.

3. **Fitness Agent**  
   Delivers comprehensive advice including:
   - Nutrition, recovery, and hydration tips  
   - Workout planning and scheduling  
   - Personalized Kenyan recipes (via RAG tool)  
   - Weather-aware recovery guidance (uses coordinates or typed location)  
   - Integration with Google Calendar to create, list, delete, and update workout and meal prep events.

4. **Play Analysis Agent**  
   Helps athletes improve basketball IQ by analyzing plays from its RAG corpus.  
   - Textual explanations of strategies and plays  
   - Visual drill recommendations in conjunction with Drills Agent  

5. **AlloyDB / Analytics Agent**  
   Contains career data from **Kobe Bryant** to guide smart decision-making on shot selection and positioning.  
   **Database Interaction (NL2SQL):** Converts natural language queries into SQL for **BigQuery** and **AlloyDB**.

---

## Key Features

- **Vertex AI Memory Bank**:  
  Stores contextual information about the user to provide **personalized, continuous advice** across sessions.  
  It allows the agent to remember user preferences, previous workouts, performance metrics, and more.

- **Multimodal Advice System**: Integrates mental, physical, and tactical guidance in one agent.

- **RAG-powered Knowledge Retrieval**: Provides data-backed recommendations from curated sources and your own datasets.

- **Weather & Location Awareness**: Adjusts fitness and recovery recommendations based on local weather conditions.

- **Google Calendar Integration**: Schedules workouts and meal prep efficiently.

- **Natural Language Database Querying**: Ask questions about historical player data in natural language, and the agent translates them into SQL.

- **YouTube Drill Recommendations**: Personalized video links for skills improvement.

---

## Setup & Installation

### Prerequisites

- Python 3.13 or higher
- Google Cloud project with **Vertex AI** enabled
- Google Calendar API key
- YouTube Data API v3 key

---

### 1. Clone the Repository

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/podcast_transcript_agent

```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

This project uses `uv` to manage dependencies. `uv` is an extremely fast Python package installer and resolver. It provides a more efficient and reliable way to manage your project's dependencies.

To install the dependencies, run the following command:

```bash
uv sync
```

### 4. Configure Environment Variables

Create a `.env` file in the root of the project and add the following configuration for Vertex AI Authentication:

```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="your-gcp-region"
```

If you are using Vertex AI, make sure you are authenticated with `gcloud`:

```bash
gcloud auth application-default login
```

## Running the Agent

You can run the agent in two ways: through the interactive web interface or as a standalone API server.

### Using the ADK Web Interface

The web interface provides a user-friendly way to interact with the agent.

To start the web interface, run the following command from the root of the project:

```bash
adk web --8090
```

### FastAPI server
To start the fastAPI server for the location tool you are to run
```bash
uvicorn main:app --reload
```
This will enable you to access the location/weather forecast tool
 

### CalendarAPI
To set up Google Calendar integration:
        1. Go to https://console.cloud.google.com/"
        2. Create a new project or select an existing one
        3. Enable the Google Calendar API
        4. Create OAuth 2.0 credentials (Desktop application)
        5. Download the credentials and save them as 'credentials.json' in the project directory.

After setting up the required credentials, you are to run 
```python
python setup_calendar_auth.py
```


#### MCP Toolkit for Databases: Local Setup

To use this dataset, you also need to set up the [MCP Toolbox for Databases][mcp-toolbox].
For initial setup, you can run the toolbox locally by following these steps:

1. Download the latest version of Toolbox as a binary:

    ```bash
    export OS="linux/amd64" # one of linux/amd64, darwin/arm64, darwin/amd64, or windows/amd64
    curl -O https://storage.googleapis.com/genai-toolbox/v0.12.0/$OS/toolbox
    ```

1. Make the binary executable:

    ```bash
    chmod +x toolbox
    ```

1. Copy the `toolbox_env-example.sh` file to a file called `toolbox_env.sh` and
populate it with the appropriate values for your project. Then source the `toolbox_env.sh` file:

    ```bash
    . ./toolbox_env.sh
    ```

1. Run the Toolbox server, pointing to the `toolbox-alloydb-local.yaml` configuration file:

    ```bash
    ./toolbox --tools-file "toolbox-alloydb-local.yaml"
    ```




#### AlloyDB Cluster Configuration

For this demo, we will setup your AlloyDB cluster in the same project as you will be using for the Vertex AI API calls. 
allow your ADK Agent to access the AlloyDB cluster.

1. Enable APIs:

    ```bash
    gcloud services enable alloydb.googleapis.com \
                           compute.googleapis.com \
                           cloudresourcemanager.googleapis.com \
                           servicenetworking.googleapis.com \
                           vpcaccess.googleapis.com \
                           aiplatform.googleapis.com
    ```

1. Download and install [postgres-client cli (`psql`)][install-psql].

1. Install the [AlloyDB Auth Proxy][install-alloydb-auth-proxy].

1. Set environment variables. For security reasons, use a different password for
   `$DB_PASS` and note it for future use:

    ```bash
    export CLUSTER=my-alloydb-cluster
    export INSTANCE=my-alloydb-instance
    export REGION=us-central1
    export DB_USER=postgres
    export DB_PASS=my-alloydb-pass
    ```

1. Create an AlloyDB cluster:

    ```bash
    gcloud alloydb clusters create $CLUSTER \
        --password=$DB_PASS\
        --network=default \
        --region=$REGION \
        --project=$PROJECT_ID
    ```

1. Create a primary instance:

    ```bash
    gcloud alloydb instances create $INSTANCE \
        --instance-type=PRIMARY \
        --cpu-count=8 \
        --region=$REGION \
        --cluster=$CLUSTER \
        --project=$PROJECT_ID \
        --ssl-mode=ALLOW_UNENCRYPTED_AND_ENCRYPTED \
        --database-flags=password.enforce_complexity=on
    ```

1. Enable public IP on instance:

    ```bash
    gcloud alloydb instances update $INSTANCE \
        --cluster=$CLUSTER  \
        --region=$REGION  \
        --assign-inbound-public-ip=ASSIGN_IPV4
    ```

1. Connect to instance using AlloyDB auth proxy:

    ```bash
    ./alloydb-auth-proxy --public-ip \
        "projects/$PROJECT_ID/locations/$REGION/clusters/$CLUSTER/instances/$INSTANCE"
    ```

1. Verify you can connect to your instance with the `psql` tool. Enter
   password for AlloyDB (`$DB_PASS` environment variable set above) when prompted:

    ```bash
    psql -h 127.0.0.1 -p 5432 -U $DB_USER
    ```

[install-psql]: https://www.timescale.com/blog/how-to-install-psql-on-mac-ubuntu-debian-windows/
[install-alloydb-auth-proxy]: https://cloud.google.com/alloydb/docs/auth-proxy/connect#install


### Manual Data insertion
Go to alloydb studio and navigate to the created database and key in this sql command
```SQL
CREATE TABLE public.players_stats (
    action_type TEXT,
    combined_shot_type TEXT,
    game_event_id INT,
    game_id INT,
    lat FLOAT,
    loc_x INT,
    loc_y INT,
    lon FLOAT,
    minutes_remaining INT,
    period INT,
    playoffs INT,
    season TEXT,
    seconds_remaining INT,
    shot_distance INT,
    shot_made_flag FLOAT,
    shot_type TEXT,
    shot_zone_area TEXT,
    shot_zone_basic TEXT,
    shot_zone_range TEXT,
    team_id INT,
    team_name TEXT,
    game_date TEXT,
    matchup TEXT,
    opponent TEXT,
    shot_id INT PRIMARY KEY
);

```



Go to your created instance on AlloyDB for Postgress on Google console.
Click on the import button on th dashboard.
Click import as csv from local computer. Click the csv.
You will be prompted also to upload the file into a google storage bucket. Then click import and wait for 10 secs for the db to be populated. 

# How to Create and Retrieve Your Agent Engine ID (Vertex AI)
## ✅ 1. Install the Vertex AI SDK

```bash
pip install google-cloud-aiplatform
```
How to Create an API Key
Go to Google Cloud Console → https://console.cloud.google.com
Make sure your project is selected.
Navigate to:
APIs & Services → Credentials

Click “Create Credentials” → “API key”

Copy the generated key.

(Optional but recommended) Restrict the API key to:
 .Vertex AI API
 .Your allowed domains or IPs

This is the key you will use in the code snippet below

```python
import vertexai
from vertexai import agent_engines # <-- Import the correct module
# Note: ReasoningEngine class is NOT needed for this specific use case.

# --- CONFIGURATION (UPDATE THESE VALUES) ---
# Your project ID is now set correctly:
PROJECT_ID = "YOUR_GOOGLE_CLOUD_PROJECT_ID"  # <-- Replace with your GCP project ID
LOCATION = "YOUR_GOOGLE_CLOUD_LOCATION"  # <-- Replace with your GCP location, e.g., "us-central1"
ENGINE_DISPLAY_NAME = "My Memory Bank Engine"
ENGINE_DESCRIPTION = "Engine used solely for Vertex AI Memory Bank access."
# ---------------------------------------------

# --- 1. INITIALIZE VERTEX AI SDK AND CLIENT ---
# This uses the credentials set by 'gcloud auth application-default login'
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)

# Initialize the client AFTER vertexai.init()
client = vertexai.Client(
    project=PROJECT_ID,  
    location=LOCATION
)

# --- 2. CREATE THE AGENT ENGINE FOR MEMORY BANK ---
print(f"Creating Agent Engine (Memory Bank) '{ENGINE_DISPLAY_NAME}'...")

try:
    # Use client.agent_engines.create() with the required memory_bank_config.
    # The absence of the 'agent' argument means no agent code is deployed.
    memory_engine = client.agent_engines.create(
        config={
            "display_name": ENGINE_DISPLAY_NAME,
            "description": ENGINE_DESCRIPTION,
            "context_spec": {
                "memory_bank_config": {
                    # Example config: specify the model for memory generation
                    "generation_config": {
                        "model": f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/gemini-2.5-flash"
                    }
                }
            }
        }
    )

    AGENT_ENGINE_ID = memory_engine.api_resource.name.split("/")[-1]

    print("\n✅ Agent Engine (Memory Bank) Created Successfully!")
    print("Full Resource Name:", memory_engine.api_resource.name)
    print("Agent Engine ID:", AGENT_ENGINE_ID)
    
    # --- NEXT STEP: ACCESSING MEMORY ---
    print("\nNext Step: You can now use this engine ID to initialize your Memory object:")
    print(f'from vertexai.agents import Memory')
    print(f'memory = Memory(reasoning_engine_id="{AGENT_ENGINE_ID}", session_id="my-first-session")')
    
except Exception as e:
    print(f"\n❌ An error occurred during creation: {e}")

```

# How to Get a YouTube Data API v3 Key (Step-by-Step)
Follow the steps below to create and retrieve a **YouTube Data API v3 key** from Google Cloud Console.
---

## ✅ 1. Open Google Cloud Console

Go to:  
https://console.cloud.google.com

Make sure you are signed in with your Google account.

---

## ✅ 2. Select or Create a Project

1. Click the **Project Selector** at the top.
2. Choose an existing project **or** click **“New Project”** to create one.
3. Enter a name and click **Create**.

---

## ✅ 3. Enable the YouTube Data API v3

1. In the left sidebar, navigate to:  
   **APIs & Services → Library**
2. Search for:  
   **YouTube Data API v3**
3. Click on it.
4. Click **Enable**.

---

## ✅ 4. Create an API Key

1. Go to:  
   **APIs & Services → Credentials**
2. Click **“Create Credentials”**
3. Select **API key**
4. A new API key will appear in a popup.  
   This is your **YouTube API Key**.

---

## ✅ 5. (Recommended) Restrict Your API Key

You should restrict your key to prevent unauthorized use.

### To restrict it:

1. In the **Credentials** list, click on your API key.
2. Under **API restrictions**, choose:
   - **Restrict key**
   - Select **YouTube Data API v3**
3. Under **Application restrictions**, choose one of:
   - **HTTP referrers (Websites)** → for web apps  
   - **IP addresses** → for servers  
   - **Android apps**  
   - **iOS apps**
4. Click **Save**.

---

## 🎉 Done!

### WeatherAPI
Create or Select a Google Cloud Project
Go to the Google Cloud Console and create a new project (or select an existing one).

Enable the Weather API
From “APIs & Services → Library”, search for “Weather API” and enable it for your project. 

Ensure billing is enabled (as required by Google Cloud when using some APIs) so that the API can function. 


Generate Credentials (API Key or OAuth)

Go to “APIs & Services → Credentials” → “Create credentials” → choose “API key” (or other credential types as appropriate). 
Store this key securely — you’ll need it to authenticate your requests.


### VertexAIRAG engine
### How to Create a RAG Corpus in Vertex AI

Follow these steps to  create your RAG corpus in Vertex AI. This corpus will act as the knowledge base that your agent retrieves information from.

1. **Open Vertex AI RAG Studio**
Go to Google Cloud Console
In the left menu, navigate to:
--Vertex AI → RAG
--Select RAG Studio.

2. **Create a New Corpus**
Click Create Corpus.
Enter a name and an optional description.
Choose the location (e.g., us-east1, us-central1).
Click Create.
This will generate a resource ID in this format:

```bash
projects/PROJECT_ID/locations/REGION/ragCorpora/CORPUS_ID
```

You will use this value inside your agent code.

3. **Add Documents to the Corpus**
You can populate your corpus with files or text:
Option A — Upload Files:
Inside your newly created corpus, click Upload Documents.
Upload:
--PDFs
--HTML files
--Text files
--Markdown
--Word documents

Save and process.

4. **(Optional) Configure Metadata Filters**

If you want the agent to retrieve specific subsets of knowledge:
Select a document.
Add metadata key-value pairs (e.g., "type": "fitness_guide").
You can later filter queries using these fields.

5. **(Optional) Adjust Embedding/Chunking Settings**
Inside your corpus settings:
Choose chunk size (default ~300 tokens)
Enable semantic metadata splitting
Configure default embedding model

These settings influence retrieval accuracy.

6. **Get the Corpus Resource Name**
Once the corpus is created:
  Open the corpus details page
  Look for the Resource name
  It will look like:

```bash
projects/your-project-id/locations/us-east1/ragCorpora/1234567890123456789
```

Copy this and paste it into the environment variable as either fitness or play analysis agent.

You can test using this article for fitness agent:
https://www.researchgate.net/publication/344503648_Post-Exercise_Recovery_Strategies_in_Basketball_Practical_Applications_Based_on_Scientific_Evidence



### WeatherAPI
Create or Select a Google Cloud Project
Go to the Google Cloud Console and create a new project (or select an existing one).

Enable the Weather API
From “APIs & Services → Library”, search for “Weather API” and enable it for your project. 

Ensure billing is enabled (as required by Google Cloud when using some APIs) so that the API can function. 


Generate Credentials (API Key or OAuth)

Go to “APIs & Services → Credentials” → “Create credentials” → choose “API key” (or other credential types as appropriate). 
Store this key securely — you’ll need it to authenticate your requests.


### Vertex AI service account

Generating a Service Account JSON Key:
1. Create a Service Account: Navigate to "IAM & Admin" > "Service Accounts" in the Google Cloud Console and create a new service account.
2. Assign Roles: Grant the necessary IAM roles to the service account, such as "Vertex AI User," "Vertex AI Administrator," or more specific roles depending on the required access.
3. Create Key: In the service account details, go to the "Keys" tab, select "Add Key," and choose "Create new key." Select "JSON" as the key type.
4. Download Key: Create the key, and a JSON file containing the service account's private key and other credentials will be downloaded to your local machine.
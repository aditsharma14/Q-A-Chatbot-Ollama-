# Q&A Chatbot with Ollama

A simple question-answering chatbot built with **Streamlit** and **LangChain**. It runs open-source LLMs such as **Llama 3** locally with **Ollama**. Your questions never leave your machine, and there are no API costs.

## Features

- Chat with any model you have pulled in Ollama. The app defaults to `llama3`.
- The model list comes from your local Ollama install, so you can only pick models that are downloaded.
- Answers stream in word by word as they are generated.
- Sidebar controls for **Temperature** and **Max Tokens**.
- Optional [LangSmith](https://smith.langchain.com/) tracing.
- Clear error messages when Ollama is not running, no models are installed, or generation fails.

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | Tested with Python 3.13 |
| [Ollama](https://ollama.com/download) | Must be installed and running (default: `http://localhost:11434`) |
| At least one Ollama model | e.g. `llama3` (~4.7 GB download, ~8 GB RAM recommended) |

## Setup

1. **Clone the repository and enter the folder**

   ```bash
   git clone <your-repo-url>
   cd "Q&A-Chatbot(Ollama)"
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Pull a model with Ollama**

   ```bash
   ollama pull llama3
   ollama list        # verify the model shows up
   ```

5. **(Optional) Enable LangSmith tracing.** Create a `.env` file in the project root:

   ```env
   LANGCHAIN_API_KEY=your_langsmith_api_key
   ```

   Without this key, the app still runs and tracing stays off.

## Run the app

Make sure Ollama is running first. It usually starts automatically after install; if not, run `ollama serve`. Then start the app:

```bash
streamlit run code.py
```

Streamlit opens the app at <http://localhost:8501>.

## Usage

1. Pick a model in the sidebar (default: `llama3:latest`).
2. Adjust **Temperature**. Lower values give more focused answers, higher values more creative ones.
3. Adjust **Max Tokens** to set the maximum answer length.
4. Type your question in the **You:** box and press Enter.

## Deploying to Streamlit Community Cloud

Streamlit Cloud runs the app on its own servers, which have no Ollama. The deployed app has to connect to an Ollama server that is reachable over the internet. Set that server in the app's **Settings → Secrets**:

```toml
OLLAMA_HOST = "https://your-ollama-server"
OLLAMA_API_KEY = "..."        # only if the server needs one
LANGCHAIN_API_KEY = "..."     # optional, for LangSmith tracing
```

Choose one of these servers:

**Option A: Ollama Cloud (no laptop needed)**
1. Sign in at [ollama.com](https://ollama.com) and create an API key.
2. Set `OLLAMA_HOST = "https://ollama.com"` and `OLLAMA_API_KEY = "<your key>"`.
3. The model dropdown shows the models your Ollama Cloud account can use. These are cloud models, which may not include `llama3`.

**Option B: Expose your own Ollama with ngrok (laptop must stay on)**
1. Install [ngrok](https://ngrok.com/) and run:
   ```bash
   ngrok http 11434 --host-header="localhost:11434"
   ```
2. Set `OLLAMA_HOST` to the `https://….ngrok-free.app` URL that ngrok prints.
3. The app works only while your laptop, Ollama and ngrok are running. Anyone with the URL can use your Ollama, so stop ngrok when you're done.

Locally, you don't need any of this. The app defaults to `http://localhost:11434`.

## Troubleshooting

| Problem | Fix |
|---|---|
| "Could not connect to Ollama" | **Locally:** start Ollama (`ollama serve` or open the Ollama app), then refresh the page. **On Streamlit Cloud:** set `OLLAMA_HOST` in the app's secrets (see [Deploying](#deploying-to-streamlit-community-cloud)). |
| "No Ollama models are installed" | Run `ollama pull llama3`, then refresh the page. |
| `404` / "model not found" | The model is not on the Ollama server the app connects to. Check with `ollama list` and pull it again. |
| Responses are slow | On a CPU-only machine, `llama3` (8B) generates only a few tokens per second. Lower **Max Tokens**, or use a smaller model such as `llama3.2:3b` or `gemma:2b`. Run `ollama ps` to check whether the model is on CPU or GPU. |
| High memory usage | Unload models you are not using with `ollama stop <model>`. |

## Project structure

```
.
├── code.py            # Streamlit app
├── requirements.txt   # Python dependencies
├── .env               # (optional, not committed) LangSmith API key
└── readme.md
```

## Tech stack

- [Streamlit](https://streamlit.io/): UI
- [LangChain](https://python.langchain.com/) + [langchain-ollama](https://pypi.org/project/langchain-ollama/): prompt and model chain
- [Ollama](https://ollama.com/): local LLM runtime
- [LangSmith](https://smith.langchain.com/): optional tracing

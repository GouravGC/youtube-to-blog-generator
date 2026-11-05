# 🎬 YouTube to Blog Generator

An AI-powered application that transforms YouTube videos into concise, structured technical blog posts using **CrewAI, OpenRouter, and Streamlit**.

Paste a YouTube video URL, extract its available transcript, and let two AI agents collaborate to research the content and write a technical blog.

## 🚀 Live Application

**Try it here:** https://youtube-to-blog-generator-latest.onrender.com/

## ✨ Features

- **YouTube Transcript Extraction:** Retrieves available captions directly using `youtube-transcript-api`, without requiring a YouTube API key or local transcription model.
- **Multi-Agent AI Workflow:** Two specialized CrewAI agents collaborate to generate the blog.
- **Researcher Agent:** Analyzes the transcript, extracts important concepts, and prepares factual research notes.
- **Writer Agent:** Converts the research notes into a concise, structured Markdown blog.
- **OpenRouter Integration:** Uses the OpenRouter model routing endpoint for LLM inference.
- **Markdown Preview:** Displays the generated blog inside the Streamlit application.
- **TXT Export:** Download the generated blog as a text file.
- **Execution Tracing:** Supports LangSmith tracing for observing workflow execution.
- **Dockerized Deployment:** Runs the Streamlit application as a single container.
- **CI/CD Automation:** GitHub Actions builds and pushes the Docker image to GitHub Container Registry (GHCR), then triggers deployment on Render.

## 🏗️ Architecture

```text
                 User
                  |
                  v
          Streamlit Frontend
                  |
                  v
          YouTube URL Validation
                  |
                  v
         Transcript Extraction
          (YouTube Captions)
                  |
                  v
            CrewAI Workflow
                  |
          +-------+-------+
          |               |
          v               |
     Researcher Agent     |
          |               |
          v               |
     Research Notes       |
          |               |
          v               |
       Writer Agent       |
          |               |
          v               |
      Generated Blog <----+
          |
          v
    Markdown Preview
          |
          v
      TXT Download
```

## 🤖 AI Agents

| Agent | Responsibility |
|---|---|
| YouTube Video Researcher | Extracts key concepts, explanations, examples, and technical details from the transcript. |
| Professional Technical Blog Writer | Converts research findings into a concise, structured technical blog. |

The agents operate sequentially: the researcher prepares notes first, and the writer uses those notes as its factual source.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Language | Python 3.11 |
| Agent Framework | CrewAI |
| LLM Gateway | OpenRouter |
| Frontend | Streamlit |
| Transcript Extraction | youtube-transcript-api |
| Observability | LangSmith |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Container Registry | GitHub Container Registry |
| Deployment | Render |

## 📁 Project Structure

```text
youtube-to-blog-generator/
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── agents.py
├── app.py
├── crew.py
├── tasks.py
├── tools.py
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/GouravGC/youtube-to-blog-generator.git
cd youtube-to-blog-generator
```

### 2. Create and activate a Conda environment

```bash
conda create -n agentic_ai python=3.11.10 -y
conda activate agentic_ai
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional: LangSmith observability
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=youtube-blog-agentops

LANGSMITH_TRACING=true
LANGSMITH_PROJECT=youtube-blog-agentops

# CrewAI native tracing
CREWAI_TRACING_ENABLED=true
```

Never commit your `.env` file or expose API keys in source code.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed by Streamlit, usually:

```text
http://localhost:8501
```

## 🐳 Docker

Build the image:

```bash
docker build -t youtube-to-blog-generator .
```

Run the container:

```bash
docker run --env-file .env -p 8501:8501 youtube-to-blog-generator
```

Open:

```text
http://localhost:8501
```

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for automated container builds and deployment.

The pipeline:

1. Triggers on pushes to the `main` branch or manual workflow execution.
2. Checks out the repository.
3. Builds the Docker image.
4. Authenticates with GitHub Container Registry.
5. Pushes the image to GHCR.
6. Triggers the Render deployment hook.

Required GitHub repository secret:

```text
RENDER_DEPLOY_HOOK_URL
```

The Render service must be configured to use the published GHCR image.

## 🔍 Observability

LangSmith tracing is integrated into the workflow to help inspect:

- YouTube transcript extraction.
- Researcher execution.
- Writer execution.
- Final workflow output.

LangSmith tracing requires valid LangSmith credentials and enabled tracing configuration.

CrewAI native tracing is independently configurable through:

```env
CREWAI_TRACING_ENABLED=true
```

## ⚠️ Current Limitations

- Transcript extraction depends on captions being available and accessible from the execution environment.
- Some cloud hosting IP addresses may be restricted by YouTube.
- Very long transcripts are currently limited to the first 60,000 characters supplied to the AI workflow.
- OpenRouter model availability and rate limits depend on the selected model and provider routing.

## 🔮 Future Improvements

- Process long transcripts in multiple chunks.
- Aggregate research findings across transcript sections.
- Add model selection.
- Improve token-count validation and blog refinement.
- Add additional export formats.
- Expand workflow observability and error handling.

## 👨‍💻 Author

**Gourav Chhatwani**

GitHub: https://github.com/GouravGC

---

Built with Python, CrewAI, OpenRouter, and Streamlit.
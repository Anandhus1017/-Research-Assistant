# Research Assistant

A powerful AI-powered research assistant that helps you conduct research and analyze academic papers using the Gemma model through Ollama.

## Quick Start

1. Install Ollama and pull the Gemma model:
   ```bash
   ollama pull gemma
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the server:
   ```bash
   .\run_server.bat  # Windows
   # OR
   python -m uvicorn main:app --host 127.0.0.1 --port 9000  # Unix/MacOS
   ```

4. Access the API at `http://localhost:9000/docs`

## Features

- **Research Query**: Conduct research on any topic using AI-powered analysis
- **Paper Analysis**: Upload and analyze research papers in PDF format
- **Smart Summarization**: Get concise summaries of research papers
- **Local Processing**: All processing is done locally using Ollama and Gemma model

## System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space (5GB for Gemma model)
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+**
   - Download and install from [python.org](https://www.python.org/downloads/)

2. **Ollama**
   - Download from [ollama.ai](https://ollama.ai/)
   - Install and ensure it's running
   - Pull the Gemma model: `ollama pull gemma`

3. **Git** (optional)
   - Download from [git-scm.com](https://git-scm.com/downloads)

## Installation

1. **Clone the repository** (or download the source code):
   ```bash
   git clone <repository-url>
   cd research_assistant
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update the following variables in `.env`:
     ```
     PROJECT_NAME=Research Assistant
     VERSION=1.0.0
     OLLAMA_HOST=http://localhost:11434
     OLLAMA_MODEL=gemma
     ```

## Running the Application

1. **Ensure Ollama is running**:
   - Start Ollama if it's not already running
   - Verify the Gemma model is available:
     ```bash
     ollama list
     ```

2. **Start the server**:
   - On Windows:
     ```bash
     .\run_server.bat
     ```
   - On Unix/MacOS:
     ```bash
     python -m uvicorn main:app --host 127.0.0.1 --port 9000
     ```

3. **Access the API**:
   - Open your web browser and go to: `http://localhost:9000/docs`
   - You'll see the Swagger UI documentation

## Example Usage

### 1. Research Query Example
```bash
curl -X POST "http://localhost:9000/api/v1/research" \
     -H "Content-Type: application/json" \
     -d '{"query": "quantum computing applications", "max_papers": 3}'
```

Expected Response:
```json
{
  "status": "success",
  "results": [
    {
      "title": "Quantum Computing: A Survey",
      "summary": "Overview of quantum computing principles...",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }
  ]
}
```

### 2. Paper Analysis Example
```bash
curl -X POST "http://localhost:9000/api/v1/upload-paper" \
     -F "file=@research_paper.pdf"
```

Expected Response:
```json
{
  "status": "success",
  "analysis": {
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "summary": "Concise summary of the paper...",
    "key_findings": ["Finding 1", "Finding 2"]
  }
}
```

## API Endpoints

### 1. Research Endpoint
- **URL**: `/api/v1/research`
- **Method**: POST
- **Purpose**: Conduct research on a specific topic
- **Request Body**:
  ```json
  {
    "query": "Your research topic",
    "max_papers": 5
  }
  ```

### 2. Upload Paper Endpoint
- **URL**: `/api/v1/upload-paper`
- **Method**: POST
- **Purpose**: Upload and analyze a research paper
- **Request**: Multipart form with PDF file

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd research_assistant
   ```

2. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # if available
   ```

3. **Run tests** (if available):
   ```bash
   pytest
   ```

4. **Code style**:
   ```bash
   black .  # Format code
   flake8 .  # Lint code
   ```

## Project Structure

```
research_assistant/
├── src/
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── task_planner.py
│   │   └── __init__.py
│   ├── api/
│   │   ├── routes.py
│   │   └── __init__.py
│   ├── tools/
│   │   ├── paper_search.py
│   │   ├── pdf_parser.py
│   │   ├── summarizer.py
│   │   └── __init__.py
│   └── config.py
├── main.py
├── requirements.txt
├── .env
└── run_server.bat
```

## Technologies Used

- **Backend Framework**: FastAPI
- **AI Model**: Gemma (via Ollama)
- **PDF Processing**: PyPDF2
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers
- **API Documentation**: Swagger UI

## Troubleshooting

1. **Server won't start**:
   - Ensure Ollama is running
   - Check if port 9000 is available
   - Verify all dependencies are installed

2. **Model not responding**:
   - Check if Ollama is running: `ollama list`
   - Verify Gemma model is available
   - Restart Ollama if needed

3. **API not accessible**:
   - Ensure server is running
   - Check if you can access `http://localhost:9000/docs`
   - Verify no firewall is blocking the port

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

## Acknowledgments

- Ollama team for the local AI model server
- Google for the Gemma model
- All open-source libraries used in this project 
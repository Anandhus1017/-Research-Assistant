# Research Assistant 🧠

A powerful AI-powered research assistant that helps you conduct research and analyze academic papers using the Gemma model through Ollama. This tool is designed to make academic research more efficient and accessible.

## 🌟 Key Features

- **Research Query**: Conduct research on any topic using AI-powered analysis
- **Paper Analysis**: Upload and analyze research papers in PDF format
- **Smart Summarization**: Get concise summaries of research papers
- **Local Processing**: All processing is done locally using Ollama and Gemma model
- **Vector Storage**: Store and retrieve papers efficiently using ChromaDB
- **Multi-source Search**: Search across Arxiv and Google Scholar simultaneously

## 🚀 Quick Start

1. **Install Ollama and pull the Gemma model**:
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull gemma
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   # Windows
   .\run_server.bat
   
   # Unix/MacOS
   python -m uvicorn main:app --host 127.0.0.1 --port 9000
   ```

4. **Access the API**:
   - Open your browser and go to: `http://localhost:9000/docs`
   - Explore the interactive API documentation

## 💻 System Requirements

- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space (5GB for Gemma model)
- **OS**: Windows 10+, macOS 10.15+, or Linux

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **Ollama**
   - Download from [ollama.ai](https://ollama.ai/)
   - Install and ensure it's running
   - Pull the Gemma model: `ollama pull gemma`
   - Verify installation: `ollama list`

3. **Git** (optional)
   - Download from [git-scm.com](https://git-scm.com/downloads)

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd research_assistant
   ```

2. **Create a virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows
   .\venv\Scripts\activate
   # Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your settings
   PROJECT_NAME=Research Assistant
   VERSION=1.0.0
   OLLAMA_HOST=http://localhost:11434
   OLLAMA_MODEL=gemma
   ```

## 🎯 Usage Examples

### 1. Upload and Analyze a Research Paper
```bash
curl -X POST "http://localhost:9000/api/v1/upload-paper" \
     -F "file=@research_paper.pdf"
```

### 2. Check Processing Status
```bash
curl -X GET "http://localhost:9000/api/v1/task-status/{task_id}"
```

### 3. Search for Related Papers
```bash
curl -X POST "http://localhost:9000/api/v1/research" \
     -H "Content-Type: application/json" \
     -d '{"query": "quantum computing applications", "max_papers": 3}'
```

## 📚 API Documentation

### Endpoints

1. **Upload Paper**
   - **URL**: `/api/v1/upload-paper`
   - **Method**: POST
   - **Purpose**: Upload and analyze a research paper
   - **Request**: Multipart form with PDF file
   - **Response**: Task ID for status tracking

2. **Task Status**
   - **URL**: `/api/v1/task-status/{task_id}`
   - **Method**: GET
   - **Purpose**: Check processing status
   - **Response**: Current status and results if completed

3. **Research Query**
   - **URL**: `/api/v1/research`
   - **Method**: POST
   - **Purpose**: Search for related papers
   - **Request Body**: JSON with query and max_papers
   - **Response**: List of related papers

## 🏗️ Project Structure

```
research_assistant/
├── src/
│   ├── agents/           # AI agents for research and planning
│   ├── api/             # API routes and endpoints
│   ├── tools/           # Utility functions and tools
│   └── config.py        # Configuration settings
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── run_server.bat     # Windows server startup script
```

## 🛠️ Development Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd research_assistant
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

3. **Code style**:
   ```bash
   black .  # Format code
   flake8 .  # Lint code
   ```

## 🔍 How It Works

1. **PDF Upload and Processing**:
   - PDF is uploaded and parsed
   - Text is extracted and structured
   - Sections are identified and processed

2. **Analysis Pipeline**:
   - Content is summarized
   - Key points are extracted
   - Paper is stored in vector database

3. **Search and Retrieval**:
   - Papers can be searched semantically
   - Related papers are found across sources
   - Results are ranked by relevance

## 🆘 Troubleshooting

1. **Server Issues**:
   - Ensure Ollama is running: `ollama list`
   - Check port 9000 availability
   - Verify all dependencies are installed

2. **Model Issues**:
   - Verify Gemma model: `ollama list`
   - Check model size and compatibility
   - Restart Ollama if needed

3. **API Issues**:
   - Check server logs
   - Verify endpoint URLs
   - Ensure correct request format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Ollama for providing the Gemma model
- FastAPI for the web framework
- ChromaDB for vector storage
- All contributors and users 












Now I can explain the complete flow of what happens when you upload a PDF file:
Initial Upload (main.py)
When you upload a PDF file to /api/v1/upload-paper, the upload_paper endpoint is triggered
A unique task ID is generated
The file content is read
A background task is created using asyncio.create_task(process_paper(task_id, content))
PDF Processing Flow (in order):
PDF Parser (pdf_parser.py)
The PDFParserTool processes the PDF file
Extracts text from each page
Identifies and extracts different sections:
Title
Abstract
Introduction
Methods
Results
Discussion
Figures
References
Research Agent (research_agent.py)
The ResearchAgent coordinates the entire process
Takes the parsed content and:
Combines key sections (abstract, introduction, methods, results, discussion) into a single text
Generates a summary using the SummarizerTool
Extracts key points from the paper
Stores the paper in the vector store for future reference
Processing Steps in Detail:
PDF Parsing Stage:
Processes each page of the PDF
Uses regex patterns to identify different sections
Extracts figures and references
Logs progress and timing for each step
Text Processing Stage:
Combines relevant sections for analysis
Generates a concise summary
Extracts key points and findings
Stores the processed content in a structured format
Storage Stage:
The processed paper is stored in the vector store
This allows for future semantic search and comparison
Status Updates:
Throughout the process, the task status is updated
You can check the status using /api/v1/task-status/{task_id}
Status changes from "pending" → "processing" → "completed" (or "error" if something fails)
Final Output:
The processed paper returns a structured response with:
Title
Summary
Key points
Figures
References
The entire process is asynchronous, meaning it runs in the background while you can continue using the application. You can check the status of your upload at any time using the task ID.
Would you like me to explain any specific part of this process in more detail?

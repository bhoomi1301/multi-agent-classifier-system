# Multi-Agent Classifier System

A sophisticated document processing system that classifies and routes various types of documents (PDFs, Emails, JSON) to specialized agents for processing based on their content and intent.

## Features

- **Multi-Format Support**: Processes PDFs, Emails, and JSON documents
- **Intelligent Classification**: Automatically classifies documents by type and intent
- **Specialized Agents**: Routes to specialized agents based on document type and content
- **REST API**: Easy integration with other systems via a FastAPI-based REST interface
- **Conversation Tracking**: Maintains context with conversation IDs
- **Memory Store**: Persists conversation history and processing results

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bhoomi1301/multi-agent-classifier-system.git
   cd multi-agent-classifier-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Unix/macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Ollama (for local LLM processing):
   - Download and install Ollama from [ollama.ai](https://ollama.ai/)
   - Pull the required model (default is "mistral"):
     ```bash
     ollama pull mistral
     ```

## Usage

### Command Line Interface

Run the main application:
```bash
python main.py
```

### API Server

Start the FastAPI server:
```bash
uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Process PDF
```
POST /process/pdf
```
**Headers:**
- `X-API-Key: internship123`

**Form Data:**
- `file`: PDF file to process
- `sender`: (Optional) Sender identifier
- `conversation_id`: (Optional) Conversation ID for tracking

#### Process Text
```
POST /process/text
```
**Headers:**
- `X-API-Key: internship123`
- `Content-Type: application/x-www-form-urlencoded`

**Form Data:**
- `text`: Text content to process
- `sender`: (Optional) Sender identifier
- `conversation_id`: (Optional) Conversation ID for tracking

#### Process Email
```
POST /process/email
```
**Headers:**
- `X-API-Key: internship123`
- `Content-Type: application/x-www-form-urlencoded`

**Form Data:**
- `email_text`: Email content to process
- `sender`: (Optional) Sender identifier
- `conversation_id`: (Optional) Conversation ID for tracking

#### Process JSON
```
POST /process/json
```
**Headers:**
- `X-API-Key: internship123`
- `Content-Type: application/x-www-form-urlencoded`

**Form Data:**
- `json_data`: JSON string to process
- `sender`: (Optional) Sender identifier
- `conversation_id`: (Optional) Conversation ID for tracking

## Architecture

The system is built around a central `AgentOrchestrator` that routes incoming documents to specialized agents:

1. **Classifier Agent**: Analyzes the input and determines the document type and intent
2. **Email Agent**: Processes email content
3. **JSON Agent**: Handles JSON data
4. **PDF Agent**: Processes PDF documents
5. **Specialized Processors**: Handle specific intents (RFQ, Complaints, Regulations, etc.)
6. **Memory Store**: Maintains conversation history and processing results

## Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```
OLLAMA_API_URL=http://localhost:11434
MODEL_NAME=mistral
API_KEY=internship123
```

## Testing

Run the test suite:
```bash
python -m pytest
```

## Dependencies

- FastAPI - Web framework for building APIs
- Uvicorn - ASGI server
- PyMuPDF - PDF processing
- Ollama - Local LLM for document classification
- python-dotenv - Environment variable management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

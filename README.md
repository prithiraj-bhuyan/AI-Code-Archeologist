# AI-Code-Archeologist

## Overview

AI-Code-Archeologist is a full-stack application designed to analyze, visualize, and interact with codebases using AI-powered tools. It consists of a FastAPI backend and a React frontend. Developed to analyze GitHub repositories, providing intelligent summaries, architectural insights, and potential code improvements. Integrated LLM-powered code parsing and natural language generation with a CI/CD pipeline built on Google Dataflow and GitHub, automating deep analysis of unfamiliar codebases to improve developer onboarding and code review efficiency.


---

## Features

- AI-powered code analysis and visualization
- Modern React-based UI
- RESTful API backend with FastAPI
- Docker support for backend
- Environment variable management
- Testing and linting tools

---

## Project Structure

```
AI-Code-Archeologist/
├── backend/      # FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
├── frontend/     # React frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── README.md
```

---

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm
- Docker (optional, for backend containerization)
- Git

---

## Backend Setup (FastAPI)

1. **Install dependencies:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update values as needed.

3. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   - The API will be available at `http://localhost:8000`.

4. **(Optional) Run with Docker:**
   ```bash
   docker build -t ai-code-archeologist-backend .
   docker run -p 8000:8000 --env-file .env ai-code-archeologist-backend
   ```

---

## Frontend Setup (React)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```
   - The app will be available at `http://localhost:3000`.

3. **Build for production:**
   ```bash
   npm run build
   ```

---

## Running the Full Application Locally

1. Start the backend server (see above).
2. Start the frontend server (see above).
3. The frontend will communicate with the backend via API endpoints (update API URLs in frontend config if needed).

---

## Testing

- **Backend:**  
  Run tests with pytest:
  ```bash
  cd backend
  pytest
  ```

- **Frontend:**  
  Run tests with npm:
  ```bash
  cd frontend
  npm test
  ```

---

## Linting & Formatting

- **Backend:**  
  ```bash
  black .
  flake8 .
  isort .
  ```

- **Frontend:**  
  ESLint is configured via `react-scripts`.

---

## License

MIT

# Idea-to-Deploy Platform

This project is a modern end-to-end AI automation platform that converts product ideas into deployable applications.

## 🏗️ Project Structure
- **`/frontend`**: Next.js application (React, TailwindCSS, Lucide).
- **`/backend`**: Python FastAPI application (Pydantic, OpenAI, Uvicorn).
- **`/backend/data`**: JSON database storing project metadata and artifacts.

## 🚀 Getting Started

### 1. Backend (Python)
Navigate to the backend directory and install dependencies:
```bash
cd apps/api
pip install -r requirements.txt
```
Run the backend server:
```bash
uvicorn main:app --reload --port 4000
```

### 2. Frontend (Next.js)
Navigate to the frontend directory and install dependencies:
```bash
cd apps/web
npm install
```
Run the frontend development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## 🛠️ Features
- **AI Analysis**: Converts text ideas into full PMP-compliant documentation.
- **AI Design**: Generates UI/UX designs and high-fidelity mockups.
- **AI Builder**: Scaffolds full-stack codebase automatically.
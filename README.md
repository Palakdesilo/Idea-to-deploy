# Idea-to-Deploy Platform

An AI-powered automation platform that converts raw product ideas into fully deployable applications.

## Structures

- **apps/web**: Next.js 14 + Tailwind CSS Frontend.
- **apps/api**: Node.js Express Backend.
- **packages/engine**: Core AI Logic and Generators.

## Workflow

1. **Idea Input**: User submits a project idea.
2. **Analysis**: System generates 7 core requirement documents.
3. **Planning**: System generates User Stories, Tasks, and Timelines.
4. **Design**: System generates UI Mockups (Visuals).
5. **Coding**: System scouts and generates the target codebase.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run Development Environment:
   ```bash
   npm run dev
   ```

3. ##for Run Backend (API Server running on port 4000)
   ```bash
   npm run dev --workspace=@idea-to-deploy/api 
   ```
# CommercePulse — Azure Production Suite

This directory contains the core services and infrastructure for the CommercePulse platform on Azure.

## 🏗️ Production Services
- **[backend/](./backend)**: FastAPI Analytics & Ingestion Engine (Port 8010)
- **[frontend/](./frontend)**: React + Vite + TailwindCSS Dashboard (Port 4000)
- **[ai_agents/](./ai_agents)**: LangGraph Multi-Agent Strategic Engine (Port 8002 locally; 8001 in Docker)

## 🛠️ Infrastructure & Data
- **[infrastructure/](./infrastructure)**: Deployment templates and container configurations.
- **[commercepulse_testdata.xlsx](./commercepulse_testdata.xlsx)**: Standardized dataset for onboarding and validation.

## 🧠 Research & Assets
- **[Brainstorming/](./Brainstorming)**: Architecture diagrams and strategy notes.
- **[MENTOR.md](./MENTOR.md)**: Project guidelines and feedback logs.

---

### 🚀 Local Development
1. Start the **Backend**: `cd backend && python -m uvicorn app.main:app --port 8010`
2. Start the **AI Agents**: `cd ai_agents && python -m uvicorn main:app --port 8002`
3. Start the **Frontend**: `cd frontend && npm run dev`

*Ensure `.env` files are configured in each service directory using the provided `.env.example` templates.*

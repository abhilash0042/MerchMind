---
title: CommercePulse AI Agents
emoji: 🧠
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# CommercePulse AI Agents Strategic Engine - Hugging Face Spaces Deployment

This folder contains the LangGraph Multi-Agent strategic recommendation engine. It runs on a separate port (`8001`) and is hosted as a separate **Hugging Face Space** for free ($0/month).

## 🚀 Deployment Steps (AI Agents Space)

### 1. Create a Space on Hugging Face
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set your **Space Name** (e.g., `commercepulse-ai-agents`).
3. Select **Docker** as the SDK.
4. Select the **Blank** template.
5. Select **CPU Basic (Free)** as the hardware tier.
6. Set the visibility to **Public**.
7. Click **Create Space**.

### 2. Configure Secrets in Space Settings
Go to your Space's **Settings** > **Variables and secrets** and click **New secret** to add:
- `GROQ_API_KEY`: Your primary Groq API key.
- `GROQ_API_KEY_2`: Your primary Groq API key (used for fallback).
- `GROQ_API_KEY_3`: Fallback Groq key.
- `SUPABASE_URL`: Your Supabase API Endpoint.
- `SUPABASE_KEY`: Your Supabase Service Role Key.
- `SUPABASE_DATABASE_URL`: Direct Supabase PostgreSQL URL.
- `COMMERCE_API_KEY`: `dev-api-key` (Must match the `API_KEY` of the Ingestion Backend).
- `BACKEND_API_URL`: The URL of your **Ingestion Backend Space** (e.g., `https://thundarstrom-ecommerce.hf.space`).

### 3. Initialize Git & Push Code
Open your terminal, navigate to this `ai_agents` folder, and run:
```bash
git init
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# Stage and commit the files
git add app/ main.py requirements.txt Dockerfile README.md
git commit -m "Deploy LangGraph strategic agents"

# Push to Hugging Face
git push -f hf main
```

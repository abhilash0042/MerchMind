---
title: CommercePulse Backend
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# CommercePulse Ingestion & Analytics API - Hugging Face Spaces Deployment

## 🚀 Deployment Steps (Hugging Face Spaces)

### 1. Create a Space on Hugging Face
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set your **Space Name** (e.g., `commercepulse-backend`).
3. Select **Docker** as the SDK.
4. Select the **Blank** template.
5. Select **CPU Basic (Free)** as the hardware tier.
6. Set the visibility to **Public** (required for the free tier).
7. Click **Create Space**.

### 2. Configure Secrets in Space Settings
Go to your Space's **Settings** > **Variables and secrets** and click **New secret** to add:
- `DATABASE_URL`: Your Supabase connection string.
- `GROQ_API_KEY`: Your Groq API key for LLM tasks.
- `API_KEY`: Your custom security API key (e.g., `dev-api-key`).

### 3. Initialize Git & Push Code
You can push this directory to Hugging Face's Git repository.

Open your terminal, navigate to this `backend` folder, and run:
```bash
# Initialize git if not already initialized in this directory
# (Or check out the Space repo and copy these files into it)
git init
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# Stage and commit the backend files
git add app/ workers/ requirements.txt Dockerfile README.md
git commit -m "Deploy FastAPI backend to Hugging Face"

# Push to Hugging Face (will trigger automatic Docker build & deploy)
git push -f hf main
```

*(Note: Hugging Face uses your Hugging Face username and an [Access Token](https://huggingface.co/settings/tokens) as your git password when pushing.)*

## 🐳 Docker Customizations

The included [Dockerfile](./Dockerfile) is pre-configured to build the app, load the CPU-only PyTorch library efficiently, and start Uvicorn.

To set the port Hugging Face binds to, Hugging Face reads metadata from the top of the repository's `README.md`. Hugging Face will read this file's YAML header:

```yaml
---
title: CommercePulse Backend
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---
```
*(Keep this block at the very top of the `README.md` file in the root of the Hugging Face Space).*

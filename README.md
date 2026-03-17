# AI Brand Identity Builder

A multi-agent AI platform that transforms raw business ideas into complete brand identities. The system uses a 10-agent pipeline with LLMs to generate brand strategies, design directions, logos, content, and comprehensive brand guidelines.

## Features

- **10-Agent Pipeline**: Sequential AI agents that progressively refine and build your brand
  - Idea Discovery & Refinement
  - Market Research
  - Competitor Analysis
  - Brand Strategy
  - Brand Naming
  - Design Direction
  - Logo Generation
  - Content Creation
  - Brand Guidelines
  - Export & Packaging

- **Real-time Progress Tracking**: Visual timeline showing each agent's status and outputs
- **Step-by-Step or Full Automation**: Run agents one at a time or execute the entire pipeline
- **Regeneration Support**: Refine specific brand elements (design, logo, content) with feedback
- **Multi-format Export**: Download brand kits as PDF and DOCX documents

## Tech Stack

### Backend
- **FastAPI** 0.115.0 - REST API framework
- **SQLAlchemy 2.0** - ORM with async support
- **SQLite** - Development database
- **Groq API** (Llama 3.3-70B) - LLM backbone
- **HuggingFace API** - Image generation
- **Python-docx & ReportLab** - Document generation

### Frontend
- **React** 19.2.4 - UI framework
- **Vite** 8.0.0 - Build tool & dev server
- **Tailwind CSS** 3.4.19 - Styling
- **Axios** - HTTP client

## Getting Started

### Prerequisites
- Python 3.12+ (or use `.venv312` that's already configured)
- Node.js 18+
- Groq API key (free from https://console.groq.com)
- HuggingFace API token (optional, for image generation)

### Installation

1. **Backend Setup**
   ```bash
   cd backend
   # Dependencies already installed in .venv312
   # If you need to reinstall:
   ..\.venv312\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Environment Variables**
   - Backend `.env` is pre-configured with example API keys
   - Frontend `.env` is configured to reach backend at `http://127.0.0.1:8000`

### Running the Application

**Terminal 1 - Backend**
```bash
cd backend
..\.venv312\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Then open your browser to the URL shown by Vite (typically `http://127.0.0.1:5174` or similar).

## API Documentation

Once the backend is running, interactive API docs are available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                           │
│            (Vite Dev Server + Tailwind CSS)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ (Axios HTTP)
                       ↓
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  10-Agent Pipeline (Sequential Execution)           │   │
│  │  - idea_discovery → market_research → ... → export  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────┐
        │  SQLite Database         │
        │  (Projects & Outputs)    │
        └──────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────┐
        │  LLM: Groq (Llama 70B)   │
        │  Image Gen: HuggingFace  │
        └──────────────────────────┘
```

## Project Structure

```
BIDS_AI_2/
├── backend/
│   ├── app/
│   │   ├── agents/          # 10 AI agent implementations
│   │   ├── api/             # REST endpoints
│   │   ├── db/              # Database models & config
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── utils/           # Helpers (LLM, search, export)
│   │   ├── workflows/       # Agent pipeline orchestration
│   │   └── main.py          # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components
│   │   ├── pages/           # Page components (Home, Dashboard)
│   │   ├── services/        # API client
│   │   ├── styles/          # Global CSS & animations
│   │   ├── App.jsx          # Root component
│   │   └── main.jsx         # Vite entry point
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # Tailwind configuration
│   └── .env                 # Frontend environment
└── .gitignore
```

## Configuration

### Backend Environment (.env)
```
GROQ_API_KEY=your_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
HUGGINGFACE_API_KEY=your_hf_token
DATABASE_URL=sqlite+aiosqlite:///./brand_builder.db
FRONTEND_URL=http://127.0.0.1:5173
```

### Frontend Environment (.env)
```
VITE_API_URL=http://127.0.0.1:8000
```

## Common Issues

**"Failed to create project. Is the backend running?"**
- Ensure backend is running on port 8000
- Check frontend `.env` has correct `VITE_API_URL`
- Hard refresh browser (Ctrl+Shift+R)

**Backend won't start with `.venv`**
- Use `.venv312` instead (Python 3.14 had compatibility issues)
- Run: `..\.venv312\Scripts\python.exe -m uvicorn ...`

## Future Enhancements

- [ ] Multi-language support
- [ ] Brand template library
- [ ] Team collaboration features
- [ ] Advanced brand analytics
- [ ] API for third-party integrations
- [ ] Mobile app companion

## License

MIT License - feel free to use this in your projects!

## Contributing

Pull requests welcome. For major changes, please open an issue first.

---

Built with ❤️ using FastAPI, React, and AI

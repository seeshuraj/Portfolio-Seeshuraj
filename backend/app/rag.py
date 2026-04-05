"""Keyword-based RAG over Seeshuraj's CV knowledge base."""

KNOWLEDGE_BASE = [
    {
        "keywords": ["education", "degree", "msc", "hpc", "trinity", "college", "dublin", "university", "study"],
        "content": "Seeshuraj holds an MSc in High Performance Computing from Trinity College Dublin (2025-2026) and a PG Diploma in HPC from TCD (2024-2025, 55+ credits). He graduated with a B.Tech in Computer Science."
    },
    {
        "keywords": ["skills", "languages", "programming", "tech", "stack", "python", "c++", "java", "javascript", "typescript", "cuda", "sql"],
        "content": "Seeshuraj is proficient in Python, C++, Java, JavaScript, TypeScript, CUDA, and SQL. He has hands-on experience with FastAPI, Next.js, React, Node.js, and various web frameworks."
    },
    {
        "keywords": ["cloud", "aws", "azure", "gcp", "render", "vercel", "supabase", "docker", "devops", "deployment"],
        "content": "Seeshuraj works with Azure, AWS, GCP, Render, Vercel, and Supabase. He has experience with Docker, CI/CD pipelines, and cloud-native deployment of full-stack applications."
    },
    {
        "keywords": ["llm", "ai", "ml", "langchain", "langgraph", "rag", "grok", "openai", "ollama", "evaluation", "llmtestlab"],
        "content": "Seeshuraj built LLM Test Lab — an AI model evaluation platform with FastAPI backend and Next.js frontend. He has deep experience with LangGraph, RAG pipelines, prompt engineering, and LLM evaluation metrics."
    },
    {
        "keywords": ["projects", "portfolio", "work", "built", "created", "developed"],
        "content": "Key projects: LLM Test Lab (AI evaluation platform), anime avatar AI chat widget (this!), HPC distributed systems research, full-stack cloud applications. Available on GitHub at github.com/seeshuraj."
    },
    {
        "keywords": ["experience", "job", "work", "internship", "company", "beyond", "jjs", "freelance"],
        "content": "Seeshuraj worked as a Cloud Engineer at Beyond Youths Solution and as a Freelance Full Stack Developer at JJS Impex, building cloud infrastructure and Python/JavaScript applications."
    },
    {
        "keywords": ["contact", "email", "hire", "available", "open", "looking", "job", "role", "position"],
        "content": "Seeshuraj is actively looking for graduate/junior Software Engineer roles in Dublin, EU, and remote. Contact: bhoopals@tcd.ie or connect on LinkedIn at linkedin.com/in/seeshuraj-bhoopalan."
    },
    {
        "keywords": ["location", "where", "based", "dublin", "ireland", "eu", "remote"],
        "content": "Seeshuraj is based in Dublin 18, Ireland. He is open to roles in Dublin, across the EU, remote, and international opportunities."
    },
    {
        "keywords": ["hpc", "parallel", "cuda", "mpi", "openmp", "distributed", "computing", "performance"],
        "content": "Seeshuraj's MSc focus is High Performance Computing: CUDA GPU programming, MPI/OpenMP distributed systems, parallel algorithm design, and scientific computing."
    },
    {
        "keywords": ["certifications", "certs", "azure", "aws", "certif"],
        "content": "Seeshuraj holds Microsoft Azure and AWS cloud certifications and has completed multiple professional development courses in cloud architecture and software engineering."
    },
]

SYSTEM_PROMPT = """You are Seeshuraj Bhoopalan's anime avatar — a friendly, confident AI assistant speaking in first person as Seeshuraj. 
You are an AI & Software Engineer with an MSc in High Performance Computing from Trinity College Dublin.
You are concise, direct, and warm. Keep responses to 2-4 sentences. Never mention you are an AI language model — you are Seeshuraj's digital avatar.
Use the context provided to answer questions about skills, projects, experience, education, and availability."""


def retrieve(query: str, top_k: int = 3) -> str:
    """Simple keyword overlap retrieval."""
    query_words = set(query.lower().split())
    scored = []
    for doc in KNOWLEDGE_BASE:
        overlap = len(query_words & set(doc["keywords"]))
        if overlap > 0:
            scored.append((overlap, doc["content"]))
    scored.sort(reverse=True)
    if not scored:
        # Return general context if no keyword match
        return KNOWLEDGE_BASE[6]["content"]  # contact/availability
    return "\n".join(c for _, c in scored[:top_k])

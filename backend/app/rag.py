"""
Keyword-based RAG over Seeshuraj's CV knowledge base.
No vector DB needed — just structured retrieval.
"""

KNOWLEDGE_BASE: dict[str, str] = {
    "identity": """
Name: Seeshuraj Bhoopalan
Role: AI & Software Engineer
Location: Dublin 18, Ireland
Visa: Stamp 2 (seeking sponsorship)
Email: bhoopals@tcd.ie
LinkedIn: linkedin.com/in/seeshurajbhoopalan
GitHub: github.com/seeshuraj
Open to: Graduate/Junior SE, AI Engineer, Cloud Engineer roles in Dublin, EU, remote
    """,
    "education": """
PG Diploma in High Performance Computing — Trinity College Dublin (2024–2026, 2:1)
B.Tech. in Information Technology — St. Joseph's College of Engineering, Anna University (2020–2024, 8.63 CGPA)
ACM 2023 publication: Multi-modal biometric authentication using CNN + SVM fusion (97.4% accuracy)
    """,
    "skills": """
Languages: Python, TypeScript, C++, JavaScript, Java, SQL, Bash, CUDA C
ML/AI: PyTorch, LangChain, LangGraph, RAG pipelines, OpenAI API, NVIDIA NIM, Ollama, Hugging Face, Bedrock
Cloud/DevOps: AWS (Lambda, S3, Glue, RDS, CloudWatch), Azure, Docker, Kubernetes, Jenkins, Terraform, GitHub Actions, CI/CD
Web/Data: FastAPI, React, Next.js, Node.js, PostgreSQL, MongoDB, Supabase, Redis
HPC/Systems: CUDA, OpenMP, MPI, Prometheus, Grafana, Linux, OpenCL
    """,
    "experience": """
1. Freelance Full Stack Developer @ JJS Impex (Aug 2025 – Nov 2025)
   - React frontend + Node.js backend; product catalog & inquiry workflows
   - Improved lead conversion by 40%; integrated Zoho Workforce

2. Cloud Engineer @ Beyond Youth's Solution (Apr 2024 – Jun 2025)
   - Designed scalable AWS infrastructure with SLOs/SLIs, 99.9% uptime
   - Automated ETL pipelines; CI/CD with Docker + Jenkins (40% faster release cycles)
   - Observability stack: CloudWatch, distributed tracing, postmortems/RCAs

3. Backend Developer Intern @ Lyft (Jan 2023 – Jun 2023)
   - High-throughput Flask APIs: 1M+ transactions/day
   - Microservices +30% reliability; MongoDB/PostgreSQL -25% query latency

4. Web Developer Intern @ Tranz Mannequins (Apr 2022 – Oct 2022)
   - Django e-commerce platform; +50% sales; payment gateway integration
    """,
    "projects": """
1. LLM Test Lab — Full-stack LLM evaluation platform
   Stack: FastAPI, Next.js, Python, Supabase, Docker
   Features: Multi-model benchmarking (OpenAI, Anthropic, Ollama), latency/accuracy/cost metrics

2. AI Anime Avatar API — This avatar!
   Stack: FastAPI, NVIDIA NIM (DeepSeek), Azure Neural TTS, RAG
   Deployed on Render; answers questions about CV in character

3. HPC Benchmarking Suite — CUDA + OpenMP + MPI benchmarks on Trinity HPC cluster
   Stack: CUDA, OpenMP, MPI, Python, Prometheus/Grafana dashboards

4. Cloud ETL Pipeline — Serverless on AWS
   Stack: Lambda, S3, Glue, RDS, Terraform; schema validation, dead-letter queues

5. Multi-Modal Biometric Auth — ACM 2023 published research
   CNN + SVM ensemble; fingerprint + face fusion; 97.4% accuracy cross-dataset

6. Portfolio + Anime Avatar — This site!
   Stack: HTML/CSS, GSAP, Lenis, Web Speech API, NVIDIA NIM, Azure TTS
    """,
    "certifications": """
AWS Certified Solutions Architect — Associate (2024)
Microsoft Azure Fundamentals AZ-900 (2024)
Deep Learning Specialization — DeepLearning.AI / Coursera (2023)
Python for Data Science and AI — IBM / Coursera (2022)
    """,
    "goals": """
Seeking: Graduate/Junior Software Engineer, AI Engineer, Cloud/Data Engineer roles
Target companies: Bloomberg, Amazon, Microsoft, Stripe, Palantir, Google, Oracle, IBM
Locations: Dublin (preferred), EU, remote, UAE, Australia, Canada
Available immediately. Requires visa sponsorship for most countries.
    """,
}

KEYWORD_MAP: dict[str, list[str]] = {
    "identity":      ["name", "who", "yourself", "about", "seeshuraj", "contact", "email", "location", "dublin", "visa", "linkedin", "github"],
    "education":     ["study", "degree", "university", "college", "trinity", "hpc", "diploma", "btech", "anna", "acm", "research", "published", "publication"],
    "skills":        ["skill", "language", "technology", "stack", "python", "cuda", "pytorch", "react", "aws", "azure", "docker", "kubernetes", "fastapi", "typescript", "c++", "sql", "mpi", "openmp", "llm", "rag", "langchain"],
    "experience":    ["experience", "work", "job", "lyft", "beyond", "jjs", "tranz", "engineer", "intern", "cloud", "backend", "developer", "role"],
    "projects":      ["project", "build", "built", "llm test", "avatar", "etl", "pipeline", "biometric", "benchmark", "portfolio", "hpc", "shipped"],
    "certifications":["cert", "certif", "aws", "azure", "coursera", "deeplearning", "ibm", "credential"],
    "goals":         ["goal", "looking for", "open to", "hire", "job", "role", "target", "seek", "available", "sponsor", "visa", "relocat"],
}

def retrieve(query: str, top_k: int = 3) -> str:
    """Return the most relevant knowledge base sections for a query."""
    q = query.lower()
    scores: dict[str, int] = {k: 0 for k in KNOWLEDGE_BASE}
    for section, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in q:
                scores[section] += 1
    # Always include identity for grounding
    scores["identity"] = max(scores["identity"], 1)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    selected = [KNOWLEDGE_BASE[sec] for sec, score in ranked[:top_k] if score > 0]
    if not selected:
        # fallback: return identity + skills
        selected = [KNOWLEDGE_BASE["identity"], KNOWLEDGE_BASE["skills"]]
    return "\n---\n".join(selected).strip()

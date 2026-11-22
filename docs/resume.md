# TaxSaathi: resume bullets

**TaxSaathi: AI income tax assistant for freshers** | Python, FastAPI, Chroma, LangGraph, Groq, Docker
Live API: https://taxsaathi-api.onrender.com | Code: https://github.com/Kunalshinde2627/gen_ai

- Built a RAG question-answering system over Income Tax Department help pages: chunked and embedded the text into a Chroma vector store, and answered with [n] citations from a Groq LLM. It says "I don't know" when no source matches, instead of guessing. Scored 13/15 on my own 15-question evaluation set, and 3 retrieved chunks beat 5 (11/15).
- Added a LangGraph agent that calls tax calculator tools (new and old regime, 87A rebate, 4% cess) and asks for human approval before finishing, exposed through FastAPI endpoints (`/ask`, `/agent`).
- Shipped it like a real service: deployed on Render, Dockerfile, GitHub Actions CI (ruff, 31 pytest tests, Docker build), request logging, an answer cache and input limits. In local tests the cache hit rate was 50%, uncached answers took about 1.5 s, and an LLM call used about 600 tokens.
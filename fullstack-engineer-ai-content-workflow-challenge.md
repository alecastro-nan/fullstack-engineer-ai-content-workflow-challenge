# Fullstack Engineer Challenge — AI Content Workflow

> Source repository: `fullstack-engineer-ai-content-workflow-challenge`
> Organization: NaN Labs (NaN LABS S.A.)
> License: MIT

---

## 1. Repository Purpose

This is a **coding challenge repository** published by **NaN Labs** for hiring fullstack engineers. The challenge asks candidates to build an AI-powered content creation and review workflow system for a fictional company called **ACME GLOBAL MEDIA**.

The goal is to evaluate a candidate's ability to work across the full stack (backend API, frontend UI, database, containerization, AI integration) while following good software engineering practices.

---

## 2. Problem Context

ACME GLOBAL MEDIA produces ads, micro-sites, and marketing materials in multiple languages. Their traditional content creation and translation process is slow and error-prone. They want to experiment with Large Language Models (LLMs) to:

- **Generate** initial content drafts (headlines, product descriptions, etc.)
- **Translate and localize** content into multiple languages
- **Extract structured data** from content (keywords, tone, sentiment)
- **Maintain a human review workflow** where operators can accept, edit, or reject AI suggestions

Candidates must build a system capable of:

1. Managing **campaigns**, each containing multiple content pieces
2. Generating **AI-powered drafts** via OpenAI or Anthropic
3. Providing **translation/localization suggestions** via AI
4. Tracking a **review state machine**: Draft → Suggested by AI → Reviewed → Approved / Rejected
5. Broadcasting updates to all users in **real-time**

---

## 3. Folder Structure

```
fullstack-engineer-ai-content-workflow-challenge/
├── .github/
│   ├── workflows/              # (Optional) GitHub Actions CI pipeline
│   └── PULL_REQUEST_TEMPLATE.md # PR template for submissions
├── docs/                        # Diagrams, workflows, extra notes
├── backend/
│   ├── src/                     # Backend application source code
│   ├── test/                    # Backend tests
│   └── Dockerfile               # Backend container definition
├── frontend/
│   ├── src/                     # React application source code
│   ├── public/                  # Static assets
│   └── Dockerfile               # Frontend container definition
├── compose.yml                  # Docker Compose file (or docker-compose.yml)
├── .env.example                 # Environment variable template
├── README.md                    # Challenge description and instructions
├── biome.json                   # Lint & format (Biome — fast, zero-config)
└── ...                          # Other config files as needed
```

### Current State

As of this document, the repository contains only the **scaffold**:

- `README.md` — Full challenge description
- `.github/PULL_REQUEST_TEMPLATE.md` — PR submission template
- `LICENSE` — MIT License
- `.git/` — Git history

The `backend/`, `frontend/`, `docs/`, `compose.yml`, `.env.example`, and configuration files are **expected to be created by the candidate** as part of the submission.

---

## 4. Technology Stack (Required)

| Tier | Required Technologies |
|---|---|
| **Backend** | TypeScript + NestJS (or Fastify/Koa), **or** Python + FastAPI (or Flask/Django), **or** Go + Fiber (or Gin/Echo) |
| **API Style** | REST and/or GraphQL (candidate must justify if choosing only one) |
| **Frontend** | React via Next.js, Remix, or Vite |
| **Database** | PostgreSQL (primary), MongoDB (optional supplement) |
| **Containerization** | Docker (required — `compose.yml` to run everything locally) |
| **AI Integration** | OpenAI and/or Anthropic SDKs |
| **Real-time** | WebSockets, GraphQL Subscriptions, or Server-Sent Events (bonus) |

### Bonus / Nice-to-Have Technologies

- **LangChain** — chaining AI tasks (generate → translate → summarize)
- **Multi-model comparison** — OpenAI vs Anthropic side-by-side
- **Redis / Kafka** — async event messaging
- **Kubernetes / ArgoCD** — deployment manifests
- **CI pipeline** — GitHub Actions automated testing
- **Unit / integration tests** — especially for API and AI logic

---

## 5. Business Domain & Data Model (Implied)

The challenge describes these core entities:

### Campaign
- A marketing campaign containing multiple content pieces
- Acts as the top-level grouping entity

### Content Piece
- Belongs to a Campaign
- Has fields like headline, description, body, etc.
- Supports multiple language variants (translation/localization)

### Review State Machine

```
[Draft] ──(generate AI draft)──> [Suggested by AI]
                                     │
                          ┌──────────┼──────────┐
                          ▼          ▼          ▼
                     [Reviewed]  [Edited]   [Rejected]
                          │
                          ▼
                     [Approved]
```

### AI Operations
- Draft generation (headlines, product descriptions)
- Translation / localization into target languages
- Structured data extraction (keywords, tone, sentiment)

---

## 6. Key Architectural Considerations

Candidates are expected to document their decisions around:

- **API design**: REST vs GraphQL (or both) and the reasoning
- **AI integration layer**: how AI calls are abstracted, error handling, retries, prompt management
- **Real-time updates**: mechanism chosen (WebSockets, SSE, GraphQL Subscriptions)
- **State machine**: how review states are enforced (DB enum, state pattern, workflow engine)
- **Human-in-the-loop**: UX for accepting, editing, or rejecting AI suggestions
- **Testing strategy**: what to test and how
- **Async processing**: potential use of queues (Redis/Kafka) for long-running AI generation

---

## 7. Evaluation Criteria

Reviewers assess submissions on:

1. **Cross-stack competence** — backend (NestJS/FastAPI/Go) + PostgreSQL + React
2. **AI integration quality** — clean, modular, well-abstracted
3. **Data modeling** — clear schema, workflow management
4. **Human-in-the-loop UX** — intuitive review interface
5. **Documentation** — assumptions, tradeoffs, AI design choices
6. **Creativity** — unexpected/innovative uses of AI to enhance the workflow

---

## 8. Submission Workflow

1. **Fork** this repository
2. **Create a feature branch** for the implementation
3. **Commit changes** with meaningful commit messages
4. **Open a Pull Request** using the provided PR template
5. NaN Labs team reviews and provides feedback

The PR template requests:
- Summary of changes and related issue
- Type of change (bug, feature, breaking, docs)
- Testing description
- Self-review checklist

---

## 9. Repository Metadata

- **Owner**: NaN Labs (NaN LABS S.A.)
- **License**: MIT (Copyright 2025 NaN Labs)
- **Language**: English (all documentation, commit messages)
- **Template origin**: NaN Labs hiring challenge template
- **PR template**: Standard feature PR checklist

---

## 10. Related Skills & Ecosystem

This challenge sits within the **NaN Labs hiring ecosystem**. NaN Labs (also stylized as NaNLABS) is a technology consultancy. Related tools and conventions used internally include:

- `nan-` prefixed CLI helpers (e.g., `nan-doctor`, `nan-skills`)
- Subagents for code review, security audit, architecture, TDD, etc.
- Confluence and JIRA CLIs for project management
- Internal skill packs for common workflows

---

*Generated from repository contents at commit time*

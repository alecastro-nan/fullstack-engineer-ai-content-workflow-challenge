# ACME Content Workflow — Architecture

## Overview

```
User (Browser)  ───>  React/Vite (Frontend)  ──HTTP/WS──>  Django + Strawberry GraphQL (Backend)  ──SQL──>  PostgreSQL
                                                                │
                                                                ├── OpenAI SDK ──> GPT-4o
                                                                └── Anthropic SDK ──> Claude
```

## System Context

```mermaid
C4Context
  Person(user, "Content Manager", "Creates campaigns, reviews AI drafts, manages translations")
  System_Boundary(acme, "ACME Platform") {
    System(frontend, "React Frontend", "Vite + Tailwind + Apollo Client")
    System(backend, "Django Backend", "Strawberry GraphQL + Django ORM + Channels")
    SystemDb(db, "PostgreSQL", "Campaigns, Content, Users, State History")
  }
  System_Ext(openai, "OpenAI API", "GPT-4o for drafts & translations")
  System_Ext(anthropic, "Anthropic API", "Claude for drafts & translations")

  Rel(user, frontend, "HTTPS/WS", "Browser")
  Rel(frontend, backend, "GraphQL/WSS", "API calls + real-time")
  Rel(backend, db, "SQL", "Django ORM")
  Rel(backend, openai, "HTTPS", "AI SDK")
  Rel(backend, anthropic, "HTTPS", "AI SDK")
```

## Container Diagram

```mermaid
C4Container
  Person(user, "Content Manager")

  System_Boundary(fe, "Frontend") {
    Container(nginx, "nginx", "Reverse proxy", "Serves static assets, proxies /graphql and /ws to backend")
    Container(spa, "React SPA", "Vite + TypeScript", "Campaign dashboard, detail page, AI draft panel, review UI, translation panel")
  }

  System_Boundary(be, "Backend") {
    Container(django, "Django App", "Python + uvicorn/gunicorn", "GraphQL schema, business logic, ORM models")
    Container(channels, "Django Channels", "Python + Redis", "WebSocket connections, group broadcasts, real-time state change events")
    ContainerDb(db, "PostgreSQL", "Relational DB", "Campaigns, Content Pieces, Users, State History (journal table)")
  }

  System_Ext(openai, "OpenAI API")
  System_Ext(anthropic, "Anthropic API")

  Rel(user, nginx, "HTTP/WS")
  Rel(nginx, spa, "Static files")
  Rel(nginx, django, "Reverse proxy /graphql and /ws")
  Rel(django, db, "Django ORM")
  Rel(django, openai, "OpenAI SDK")
  Rel(django, anthropic, "Anthropic SDK")
  Rel(channels, db, "Django ORM")
```

## Data Flow — Content Workflow

```mermaid
sequenceDiagram
  participant U as Content Manager
  participant FE as React Frontend
  participant BE as Django Backend
  participant AI as AI Provider
  participant DB as PostgreSQL

  U->>FE: Create Campaign
  FE->>BE: GraphQL createCampaign
  BE->>DB: INSERT campaign
  DB-->>BE: campaign
  BE-->>FE: campaign created
  FE-->>U: Campaign visible

  U->>FE: Add Content Piece
  FE->>BE: GraphQL createContentPiece
  BE->>DB: INSERT content (state=draft)
  DB-->>BE: content piece
  BE-->>FE: content created

  U->>FE: Generate AI Draft
  FE->>BE: GraphQL generateDraft
  BE->>AI: generate_draft(brief)
  AI-->>BE: headline + description
  BE->>DB: UPDATE state=suggested_by_ai
  BE->>DB: UPDATE body
  BE->>BE: Broadcast state_change via WebSocket
  BE-->>FE: draft result
  FE-->>U: Preview AI draft

  U->>FE: Approve / Reject / Request Edits
  FE->>BE: GraphQL reviewContent
  BE->>DB: UPDATE state
  BE->>BE: Broadcast state_change via WebSocket
  BE-->>FE: review result
  FE-->>U: State badge updated

  U->>FE: Request Translation
  FE->>BE: GraphQL translateContent
  BE->>AI: translate(content, targetLanguage)
  AI-->>BE: translated content
  BE->>DB: INSERT translated content (originalId FK, state=suggested_by_ai)
  BE->>BE: Broadcast new content via WebSocket
  BE-->>FE: translation created
  FE-->>U: Translated content visible
```

## Key Architecture Decisions

| Decision | Choice | ADR |
|---|---|---|
| API style | Strawberry GraphQL | ADR-001 |
| AI providers | OpenAI + Anthropic (abstraction layer) | ADR-002 |
| Real-time mechanism | Django Channels WebSockets | ADR-003 |
| Database schema | Django ORM models with migrations | ADR-004 |
| Backend framework | Django + Strawberry GraphQL | ADR-005 |
| Authentication | JWT (PyJWT) with httpOnly cookies, rate limiting, WS origin check | ADR-007, ADR-010 |
| Security controls | Depth limits, CSP, prompt injection guards | ADR-008 |
| Production hardening | mypy strict, CORS multi-origin, XSS sanitization | ADR-010 |

## State Machine

```
[Draft] ──generate AI──> [Suggested by AI]
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
              [Reviewed]            [Rejected]
                   │                     │
            ┌──────┼──────┐             │
            ▼      ▼      ▼             │
       [Approved] [Rejected] ─>[Suggested by AI]──┘
                              (re-edit)
```

Valid transitions enforced at model layer via `VALID_TRANSITIONS` map. Invalid transitions raise `ValidationError`.

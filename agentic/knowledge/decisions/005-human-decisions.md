# Decision: 2026-06-18 - Human Decisions for F-002

## Context
Before starting F-002 (Install Django + Strawberry GraphQL), the tech lead needed human input on multiple design decisions per AGENTS.md section 12.

## Decisions

| # | Question | Chosen Option | Rationale |
|---|---|---|---|
| H-002 | AI Provider(s) | OpenAI + Anthropic (both) | Flexibility, fallback support, both SDKs similarly easy to integrate |
| H-003 | React Framework | Vite | Lightweight, fast, scaffold already partially exists |
| H-006 | Real-time mechanism | Django Channels (WebSockets) | Full-duplex communication, native Django integration |
| H-011 | Delete strategy | Soft delete (`isDeleted` flag) | Safe, reversible, maintains referential integrity |
| H-012 | AI Generation | Synchronous | Simpler to implement, sufficient for MVP |
| H-013 | State management | Zustand | Lightweight, minimal boilerplate |
| H-014 | Styling approach | Tailwind CSS | Utility-first, rapid prototyping |

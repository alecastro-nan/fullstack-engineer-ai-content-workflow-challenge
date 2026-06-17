# Evaluation Rubric

## Quality Gates for Code

### Backend API (40 points)
| Criterion | Points | Description |
|---|---|---|
| Campaign CRUD | 8 | All endpoints work, input validation, error handling |
| Content CRUD | 8 | All endpoints work, input validation, error handling |
| AI Integration | 10 | Provider abstraction, fallback, prompt management |
| Review State Machine | 8 | State transitions, guards, error handling |
| Real-time Events | 6 | WebSocket/SSE setup, event broadcasting |

### Frontend (30 points)
| Criterion | Points | Description |
|---|---|---|
| Dashboard | 6 | Campaigns list, create campaign |
| Campaign Detail | 6 | Content pieces, state badges |
| AI Draft Panel | 6 | Trigger generation, preview, accept/reject |
| Review UI | 6 | Approve/reject/edit, state updates |
| Real-time | 6 | Live state updates, connection status |

### Infrastructure (15 points)
| Criterion | Points | Description |
|---|---|---|
| Docker Compose | 5 | Single command starts all services |
| Dockerfiles | 5 | Multi-stage, non-root, minimal images |
| CI Pipeline | 5 | Lint, typecheck, tests pass |

### Documentation (15 points)
| Criterion | Points | Description |
|---|---|---|
| ADRs | 6 | All 4 ADRs with Context, Decision, Consequences |
| README | 5 | Setup instructions, tech decisions, tradeoffs |
| Code Comments | 4 | Complex logic explained, no obvious missing docs |

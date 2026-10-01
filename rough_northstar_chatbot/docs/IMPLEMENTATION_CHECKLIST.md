
# IMPLEMENTATION_CHECKLIST.md

Version: 1.0

## Execution Order

### Foundation
- [ ] Create repository
- [ ] Install dependencies
- [ ] Copy documentation into docs/

### Database
- [ ] Implement SQLAlchemy models
- [ ] Execute DATABASE_SCHEMA.sql
- [ ] Repository pattern verified

### NLP
- [ ] Load MiniLM
- [ ] Build intent embeddings
- [ ] Validate supported intents

### Conversation
- [ ] Session state
- [ ] Intent routing
- [ ] Context preservation

### Services
- [ ] Order
- [ ] Returns
- [ ] Shipping
- [ ] Recommendations
- [ ] Handoff

### UI
- [ ] Streamlit chat
- [ ] Sidebar
- [ ] Session reset

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests

## Acceptance Criteria

- Runs completely offline
- No direct database access outside repository
- Uses sentence-transformers/all-MiniLM-L6-v2
- Assignment order IDs behave exactly as specified
- Clean architecture maintained
- Documentation and implementation remain synchronized

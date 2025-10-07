
#### `docs/admin.md`
```markdown
# Admin & Observability

## JSON Endpoints (staff only)
- `/edge-isr/status/?tag=<tag>` → `{"tag": "...","urls": ["..."]}`
- `/edge-isr/status/?url=<url>` → `{"url": "...","tags": ["..."]}`

Use them to inspect mappings, debug invalidations, or replay warmups.

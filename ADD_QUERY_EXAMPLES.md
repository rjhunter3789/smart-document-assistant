# How to Teach the AI New Query Patterns

## Quick Guide

When the AI doesn't understand a query properly, you can teach it by adding examples to `query_patterns.json`.

### Example 1: Teaching Product Names

If you say "Tell me about Impel" and it doesn't work well, add:
```json
"entity_synonyms": {
  "impel": ["impel ai", "impel platform", "impel tool"]
}
```

### Example 2: Teaching New Question Types

If you often ask "What's the latest on [topic]", add to patterns:
```json
"status_update": {
  "triggers": ["what's the latest on", "recent updates about"],
  "examples": [
    {"input": "What's the latest on Impel", "intent": "status_update", "entity": "Impel"}
  ]
}
```

### Example 3: Industry-Specific Terms

Add Ford/automotive specific terms:
```json
"context_clues": {
  "ford_products": ["f-150", "mustang", "explorer", "bronco", "escape"],
  "vendor_names": ["impel", "epsilon", "dealer teamwork", "dealer inspire"]
}
```

## Testing Your Changes

After editing query_patterns.json, test with:
- "Tell me about [new term]"
- "What is [new term]"
- "Show me information on [new term]"

## Common Patterns to Add

1. **Your specific products/vendors**
2. **Regional terms** (Pacific Northwest specific)
3. **Industry acronyms** (DMS, CRM, OEM, etc.)
4. **Action phrases you commonly use**

The AI will immediately use these patterns after you save the file!
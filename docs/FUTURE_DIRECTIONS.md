# Future Directions: AI-Powered File Organization

This document outlines future enhancements for TidyUp that leverage AI/LLM capabilities for smarter file categorization. These features are planned for post-v1.0 releases.

## Current State (v1.0)

TidyUp uses a layered detection approach:

```
File → Detector Chain → Category → Folder
```

**Detectors** are rule-based and deterministic:
- ScreenshotDetector: Filename patterns
- InvoiceDetector: PDF content keywords
- BookDetector: ISBN, ebook extensions
- ArxivDetector: Paper ID patterns
- GenericDetector: Extension mapping (fallback)

**Limitation:** Detectors return hardcoded category names. Custom categories require manual configuration.

---

## Planned Enhancements

### Level 4: LLM-Powered Detection

Use a language model to classify files semantically when rule-based detection is uncertain.

**How it works:**

```
File: "quarterly_strategy_review.pdf"
         ↓
┌─────────────────────────────────────────────────────────────┐
│  Rule-based detectors run first                             │
│  GenericDetector → "Documents" (low confidence)             │
└─────────────────────────────────────────────────────────────┘
         ↓ (confidence < threshold)
┌─────────────────────────────────────────────────────────────┐
│  LLM Classification                                          │
│                                                              │
│  System: Classify this file into one of the user's          │
│          categories: [Documents, Work, Client Projects,     │
│          Personal, Finance, ...]                            │
│                                                              │
│  File: quarterly_strategy_review.pdf                        │
│  Content preview: "Q3 2024 Strategic Review... revenue      │
│  targets... market expansion..."                            │
│                                                              │
│  Response: "Work" (confidence: 0.92)                        │
│  Reasoning: "Business strategy document, quarterly review"  │
└─────────────────────────────────────────────────────────────┘
```

**Capabilities:**

| Use Case | Rule-Based | LLM-Powered |
|----------|-----------|-------------|
| Known patterns (screenshots) | ✅ Fast, accurate | Overkill |
| Technical vs Fiction books | ❌ Can't distinguish | ✅ Understands content |
| Novel category names | ❌ No rules exist | ✅ Infers from description |
| Ambiguous files | Falls to Unsorted | ✅ Makes educated guess |

**Configuration:**

```yaml
detection:
  llm:
    enabled: true
    provider: anthropic  # or openai, local
    model: claude-3-haiku  # Fast, cheap for classification
    threshold: 0.6  # Use LLM when rule confidence < 60%
    cache: true  # Cache results by file hash
    max_content_chars: 2000  # Limit content sent to API
    fallback_on_error: Unsorted
```

---

### Level 5: Hybrid Architecture

The full vision combines all approaches in a confidence-based pipeline:

```
File: "document.pdf"
         ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Fast Deterministic (existing detectors)           │
│  Priority-ordered detector chain                            │
│  → High confidence (>90%)? DONE                             │
│  → Medium confidence? Continue to Layer 2                   │
│  → No match? Continue to Layer 2                            │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: User Rules (config-based)                         │
│  Check category rules (keywords, patterns)                  │
│  → Match found? DONE                                         │
│  → No match? Continue to Layer 3                            │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: LLM Classification (if enabled)                   │
│  Send file info + content preview to LLM                    │
│  → Returns category + confidence + reasoning                │
│  → Cache result for identical files                         │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: Fallback                                          │
│  GenericDetector extension mapping → "Unsorted"             │
└─────────────────────────────────────────────────────────────┘
```

**Benefits of hybrid approach:**
- Fast for common cases (no API calls)
- LLM only used when needed
- Graceful degradation offline
- User rules take precedence over LLM

---

## Implementation Considerations

### API Costs and Latency

| Model | Cost per 1K tokens | Latency | Use Case |
|-------|-------------------|---------|----------|
| claude-3-haiku | ~$0.00025 | ~200ms | Best for classification |
| claude-3-sonnet | ~$0.003 | ~500ms | Complex reasoning |
| gpt-4o-mini | ~$0.00015 | ~300ms | Alternative |
| Local (Ollama) | Free | ~1-5s | Privacy-focused |

**Cost estimate:** Organizing 1000 files with 20% needing LLM = ~200 API calls = ~$0.05

### Privacy Considerations

```yaml
detection:
  llm:
    # What to send to API
    send_filename: true
    send_content: true
    max_content_chars: 2000  # Limit exposure

    # Privacy mode - only send metadata
    privacy_mode: false  # If true, only send filename and extension
```

**Privacy modes:**
1. **Full content:** Send filename + content preview (best accuracy)
2. **Metadata only:** Send filename + extension (reduced accuracy)
3. **Local only:** Use local LLM (Ollama) for complete privacy

### Caching Strategy

```python
# Cache by file hash to avoid re-classifying identical files
cache_key = f"{file_hash}:{categories_hash}"

# Cache stores:
# - Category result
# - Confidence score
# - LLM reasoning (for debugging)
# - Timestamp

# Cache invalidation:
# - File content changes (different hash)
# - Category list changes (different categories_hash)
# - Manual cache clear
```

### Offline Fallback

When LLM is unavailable:
1. Use cached results if available
2. Fall back to rule-based detection
3. Route to Unsorted with low confidence flag
4. Queue for LLM classification when online

---

## Alternative Approaches Considered

### WordNet/Thesaurus Lookup

```python
from nltk.corpus import wordnet

# "Technical Books" → find related terms
# "technical" → specialized, technological
# "book" → textbook, manual, novel
```

**Rejected because:**
- ~100MB NLTK dependency
- Noisy results (too many synonyms)
- Doesn't understand context

### Word Embeddings

```python
from gensim.models import KeyedVectors

# Find semantically similar words
model.most_similar("technical", topn=10)
# → engineering, scientific, professional
```

**Rejected because:**
- 1-3GB model file
- Overkill for this use case
- Doesn't understand category intent

### Corpus-Based Learning

```python
# Analyze user's existing organized files
# Learn patterns from their organization
# Suggest based on similar files
```

**Deferred because:**
- Complex implementation
- Requires existing organized files
- Cold start problem

---

## Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| Current | Rule-based detection | ✅ Complete |
| v1.1 | Level 1: Remap | 🔲 Planned |
| v1.1 | Level 2: Config rules | 🔲 Planned |
| v1.1 | Level 3a: Static dictionary suggestions | 🔲 Planned |
| v1.2 | Level 4: LLM integration (optional) | 🔲 Future |
| v1.3 | Level 5: Hybrid architecture | 🔲 Future |
| v2.0 | Local LLM support (Ollama) | 🔲 Future |

---

## Configuration Reference (Future)

```yaml
# ~/.tidy/config.yaml - Future LLM configuration

detection:
  llm:
    # Enable/disable LLM detection
    enabled: false

    # Provider configuration
    provider: anthropic  # anthropic, openai, ollama
    model: claude-3-haiku
    api_key_env: ANTHROPIC_API_KEY  # Read from environment

    # When to use LLM
    threshold: 0.6  # Use when rule confidence < 60%
    always_for: [Unsorted]  # Always try LLM for these categories

    # Performance
    cache: true
    cache_ttl_days: 30
    timeout_seconds: 10
    max_retries: 2

    # Privacy
    send_content: true
    max_content_chars: 2000
    privacy_mode: false  # If true, only send filename

    # Fallback
    fallback_on_error: Unsorted
    offline_mode: cache_only  # cache_only, rules_only, skip

# Category descriptions for LLM context
categories:
  - name: Technical Books
    description: "Books about programming, software development, technology"

  - name: Client Projects
    description: "Documents related to client work and consulting projects"
```

---

## Related Documentation

- [BACKLOG.md](BACKLOG.md) - Implementation tasks
- [USER_GUIDE.md](USER_GUIDE.md) - Current feature documentation
- [DEVELOPMENT.md](DEVELOPMENT.md) - Contributing guide

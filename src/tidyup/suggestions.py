"""Smart suggestions for category creation.

Provides keyword and parent suggestions based on category names.
Uses a static dictionary approach for fast, deterministic suggestions
without external dependencies.
"""

from dataclasses import dataclass

# Keywords commonly associated with category name patterns
# Maps partial category names (lowercase) to suggested keywords
CATEGORY_SUGGESTIONS: dict[str, list[str]] = {
    # Programming/Tech
    "tech": ["programming", "software", "code", "developer", "api", "framework", "technical"],
    "programming": ["code", "software", "developer", "function", "class", "module", "programming"],
    "code": ["programming", "software", "script", "function", "library", "code"],
    "software": ["programming", "code", "application", "developer", "software"],
    "developer": ["programming", "code", "software", "api", "developer"],
    "engineering": ["software", "code", "system", "design", "engineering"],
    "data": ["data", "database", "sql", "csv", "json", "analytics", "dataset"],
    "database": ["sql", "database", "table", "query", "schema"],
    "web": ["html", "css", "javascript", "web", "http", "api", "frontend"],
    "api": ["api", "rest", "endpoint", "json", "request", "response"],
    "devops": ["docker", "kubernetes", "ci", "cd", "deployment", "devops"],
    "cloud": ["aws", "azure", "gcp", "cloud", "serverless", "infrastructure"],
    "security": ["security", "encryption", "vulnerability", "authentication", "password"],
    "machine": ["machine", "learning", "ml", "ai", "model", "neural", "training"],
    "learning": ["machine", "learning", "ml", "ai", "model", "training", "deep"],
    "ai": ["artificial", "intelligence", "ai", "ml", "model", "neural", "gpt"],

    # Design
    "design": ["design", "figma", "sketch", "ui", "ux", "mockup", "wireframe"],
    "ui": ["ui", "interface", "design", "button", "component", "layout"],
    "ux": ["ux", "user", "experience", "research", "usability", "flow"],
    "graphic": ["graphic", "design", "photoshop", "illustrator", "logo", "visual"],
    "branding": ["brand", "logo", "identity", "design", "style", "guideline"],

    # Finance/Business
    "invoice": ["invoice", "receipt", "bill", "payment", "amount", "total", "due"],
    "receipt": ["receipt", "invoice", "purchase", "payment", "transaction", "total"],
    "bill": ["bill", "invoice", "payment", "amount", "due", "utility", "statement"],
    "finance": ["invoice", "receipt", "bank", "payment", "transaction", "account", "finance"],
    "tax": ["tax", "return", "deduction", "income", "irs", "w2", "1099"],
    "bank": ["bank", "statement", "account", "transaction", "balance", "transfer"],
    "expense": ["expense", "receipt", "reimbursement", "cost", "spending"],
    "budget": ["budget", "expense", "income", "forecast", "spending", "allocation"],
    "payroll": ["payroll", "salary", "wage", "employee", "pay", "stub"],

    # Work/Business
    "work": ["project", "report", "meeting", "client", "business", "presentation", "work"],
    "project": ["project", "deliverable", "milestone", "task", "client", "proposal"],
    "client": ["client", "project", "proposal", "contract", "invoice", "meeting"],
    "meeting": ["meeting", "agenda", "minutes", "notes", "attendee", "action"],
    "report": ["report", "summary", "analysis", "quarterly", "annual", "status"],
    "presentation": ["presentation", "slide", "deck", "powerpoint", "keynote"],
    "proposal": ["proposal", "bid", "rfp", "quote", "estimate", "scope"],
    "contract": ["contract", "agreement", "terms", "signature", "legal", "binding"],
    "business": ["business", "company", "corporate", "enterprise", "organization"],

    # Personal
    "personal": ["family", "vacation", "photo", "home", "private", "personal"],
    "vacation": ["travel", "trip", "holiday", "photo", "destination", "vacation"],
    "family": ["family", "photo", "birthday", "celebration", "event", "reunion"],
    "home": ["home", "house", "apartment", "mortgage", "lease", "utility"],
    "health": ["health", "medical", "doctor", "prescription", "insurance", "wellness"],
    "medical": ["medical", "health", "doctor", "prescription", "diagnosis", "treatment"],
    "insurance": ["insurance", "policy", "claim", "coverage", "premium", "benefit"],

    # Academic/Research
    "paper": ["paper", "research", "study", "abstract", "doi", "journal", "arxiv"],
    "research": ["research", "study", "paper", "analysis", "data", "experiment"],
    "academic": ["paper", "thesis", "dissertation", "journal", "publication", "academic"],
    "thesis": ["thesis", "dissertation", "research", "chapter", "defense", "advisor"],
    "journal": ["journal", "paper", "publication", "peer", "review", "article"],
    "study": ["study", "research", "analysis", "findings", "methodology", "results"],
    "science": ["science", "research", "experiment", "hypothesis", "data", "analysis"],

    # Books/Reading
    "book": ["chapter", "author", "isbn", "publisher", "edition", "book"],
    "fiction": ["novel", "story", "fantasy", "romance", "mystery", "thriller", "fiction"],
    "nonfiction": ["guide", "manual", "reference", "handbook", "tutorial", "nonfiction"],
    "novel": ["novel", "fiction", "story", "chapter", "author", "narrative"],
    "textbook": ["textbook", "education", "chapter", "exercise", "course", "learning"],
    "manual": ["manual", "guide", "instruction", "reference", "howto", "documentation"],
    "cookbook": ["recipe", "cooking", "food", "ingredient", "cuisine", "chef"],
    "biography": ["biography", "memoir", "life", "story", "person", "history"],
    "history": ["history", "historical", "war", "century", "civilization", "era"],
    "philosophy": ["philosophy", "ethics", "logic", "metaphysics", "epistemology"],
    "psychology": ["psychology", "behavior", "mind", "cognitive", "therapy", "mental"],
    "self": ["self", "help", "improvement", "motivation", "habit", "productivity"],

    # Media
    "photo": ["photo", "image", "picture", "camera", "shot", "photography"],
    "image": ["image", "photo", "picture", "graphic", "visual", "png", "jpg"],
    "video": ["video", "clip", "movie", "recording", "footage", "mp4"],
    "movie": ["movie", "film", "cinema", "director", "actor", "scene"],
    "music": ["music", "song", "audio", "track", "album", "artist"],
    "podcast": ["podcast", "episode", "audio", "interview", "host", "series"],
    "audio": ["audio", "sound", "music", "recording", "mp3", "wav"],

    # Legal
    "legal": ["legal", "contract", "agreement", "law", "court", "attorney"],
    "contract": ["contract", "agreement", "terms", "signature", "legal", "party"],
    "agreement": ["agreement", "contract", "terms", "parties", "signed", "binding"],
    "license": ["license", "permit", "agreement", "terms", "rights", "usage"],
    "patent": ["patent", "invention", "claim", "intellectual", "property", "filing"],
    "trademark": ["trademark", "brand", "registration", "mark", "intellectual"],
    "compliance": ["compliance", "regulation", "policy", "audit", "requirement"],

    # Education
    "education": ["education", "course", "learning", "student", "teacher", "curriculum"],
    "course": ["course", "lesson", "module", "assignment", "grade", "syllabus"],
    "tutorial": ["tutorial", "guide", "howto", "learn", "step", "instruction"],
    "training": ["training", "course", "workshop", "certification", "skill"],
    "certificate": ["certificate", "certification", "credential", "completion", "award"],

    # Communication
    "email": ["email", "message", "inbox", "reply", "forward", "attachment"],
    "letter": ["letter", "correspondence", "dear", "sincerely", "regards"],
    "memo": ["memo", "memorandum", "notice", "internal", "announcement"],
    "newsletter": ["newsletter", "update", "subscribe", "edition", "weekly"],

    # Real Estate
    "real": ["real", "estate", "property", "house", "apartment", "mortgage"],
    "property": ["property", "real", "estate", "deed", "title", "ownership"],
    "lease": ["lease", "rent", "tenant", "landlord", "agreement", "term"],
    "mortgage": ["mortgage", "loan", "interest", "payment", "principal", "amortization"],

    # Archives/Backup
    "archive": ["archive", "backup", "old", "historical", "legacy", "storage"],
    "backup": ["backup", "archive", "copy", "restore", "recovery", "snapshot"],
    "old": ["old", "archive", "legacy", "previous", "historical", "dated"],
    "legacy": ["legacy", "old", "archive", "deprecated", "historical", "migration"],
}

# Maps category name patterns to likely parent categories
PARENT_INFERENCE: dict[str, str] = {
    # Book subcategories
    "book": "Books",
    "fiction": "Books",
    "nonfiction": "Books",
    "novel": "Books",
    "textbook": "Books",
    "manual": "Books",
    "cookbook": "Books",
    "biography": "Books",
    "technical book": "Books",
    "tech book": "Books",

    # Document subcategories
    "invoice": "Documents",
    "receipt": "Documents",
    "bill": "Documents",
    "contract": "Documents",
    "agreement": "Documents",
    "report": "Documents",
    "letter": "Documents",
    "memo": "Documents",
    "certificate": "Documents",
    "license": "Documents",

    # Image subcategories
    "photo": "Images",
    "picture": "Images",
    "graphic": "Images",
    "screenshot": "Screenshots",
    "scan": "Images",

    # Video subcategories
    "movie": "Videos",
    "clip": "Videos",
    "recording": "Videos",
    "tutorial video": "Videos",

    # Audio subcategories
    "music": "Audio",
    "song": "Audio",
    "podcast": "Audio",
    "recording": "Audio",

    # Paper subcategories
    "research": "Papers",
    "study": "Papers",
    "journal": "Papers",
    "thesis": "Papers",
    "dissertation": "Papers",
    "academic": "Papers",

    # Code subcategories
    "script": "Code",
    "program": "Code",
    "source": "Code",
    "module": "Code",

    # Data subcategories
    "dataset": "Data",
    "database": "Data",
    "spreadsheet": "Data",
    "csv": "Data",
    "json": "Data",
}


@dataclass
class SuggestionResult:
    """Result from suggest_rules() function.

    Attributes:
        parent: Suggested parent category, or None.
        keywords: List of suggested keywords.
        confidence: How confident we are in the suggestions (0-1).
    """

    parent: str | None
    keywords: list[str]
    confidence: float

    @property
    def has_suggestions(self) -> bool:
        """Returns True if any suggestions were found."""
        return self.parent is not None or len(self.keywords) > 0


def suggest_rules(category_name: str) -> SuggestionResult:
    """Suggest parent and keywords based on category name.

    Analyzes the category name to find matching patterns in the
    static dictionaries and returns suggestions.

    Args:
        category_name: The name of the category being created.

    Returns:
        SuggestionResult with parent, keywords, and confidence.
    """
    name_lower = category_name.lower()
    words = name_lower.split()

    # Find parent suggestion
    parent = None
    for pattern, suggested_parent in PARENT_INFERENCE.items():
        if pattern in name_lower:
            parent = suggested_parent
            break

    # Collect keyword suggestions
    keywords: set[str] = set()
    matches_found = 0

    # Check each word in the name
    for word in words:
        if word in CATEGORY_SUGGESTIONS:
            keywords.update(CATEGORY_SUGGESTIONS[word])
            matches_found += 1

    # Also check full name and partial matches
    for pattern, suggested_keywords in CATEGORY_SUGGESTIONS.items():
        if pattern in name_lower and pattern not in words:
            keywords.update(suggested_keywords)
            matches_found += 1

    # Calculate confidence based on matches
    if matches_found == 0:
        confidence = 0.0
    elif matches_found == 1:
        confidence = 0.6
    elif matches_found == 2:
        confidence = 0.8
    else:
        confidence = 0.9

    # Sort keywords for consistent output
    keyword_list = sorted(keywords)

    # Limit to top 10 most relevant (keep it manageable)
    if len(keyword_list) > 10:
        keyword_list = keyword_list[:10]

    return SuggestionResult(
        parent=parent,
        keywords=keyword_list,
        confidence=confidence,
    )


def get_all_suggestion_patterns() -> list[str]:
    """Return all patterns that have suggestions.

    Useful for documentation and testing.

    Returns:
        Sorted list of all patterns in CATEGORY_SUGGESTIONS.
    """
    return sorted(CATEGORY_SUGGESTIONS.keys())


def get_all_parent_patterns() -> list[str]:
    """Return all patterns that have parent inference.

    Useful for documentation and testing.

    Returns:
        Sorted list of all patterns in PARENT_INFERENCE.
    """
    return sorted(PARENT_INFERENCE.keys())

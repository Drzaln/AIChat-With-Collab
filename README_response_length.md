# Response Length Control — Max 2 Paragraphs
### AI Character Chat · Hermes 14B via Ollama + LiteLLM

---

## The Core Problem

The Hermes model uses an internal **thinking/reasoning mode** before generating a response.
This means `max_tokens` is split between two phases:

```
max_tokens budget:
  ├── <think> phase  ~150–250 tokens  (invisible to user)
  └── actual reply   remaining tokens (what user sees)
```

Setting `max_tokens` too low (e.g. 120–150) causes the thinking phase to consume all
available tokens, leaving nothing for the actual reply → `content: ""`.

---

## Why max_tokens Alone Cannot Control Length

| max_tokens | Thinking Budget | Actual Reply | Result |
|---|---|---|---|
| `150` | ~140 tokens | ~10 tokens | Empty or 1 sentence |
| `1024` | ~200 tokens | ~824 tokens | Sometimes too long |
| `1024` + prompt instruction | ~200 tokens | ~150 tokens | ✅ 2 paragraphs |

**Conclusion:** Use `max_tokens` only as a safety ceiling.
Use the **system prompt** as the primary length controller.

---

## Implementation Plan

### Step 1 — server.js Parameters

Keep `max_tokens` high enough to cover thinking + 2-paragraph reply.
Do not go below `800`.

```js
// /api/chat/send  AND  /api/chat/regenerate
body: JSON.stringify({
    model: modelName,
    messages: messages,

    max_tokens: 1024,   // Safety ceiling — do not lower below 800
    temperature: 0.9,   // Slightly higher for expressive character voice
    top_p: 0.92,
    top_k: 45,
})

// /api/memory/:characterId/summarize — keep separate, needs more tokens
body: JSON.stringify({
    model: modelName,
    messages: messages,
    max_tokens: 1024,
    temperature: 0.3,   // Low — accuracy matters here
})
```

---

### Step 2 — Character System Prompt (Primary Length Control)

Add the following block at the **end** of every character's `systemPrompt` field
in their character card JSON (`data/characters/{id}.json`):

```
## Response Format
Keep all responses to a maximum of 2 paragraphs.
Each paragraph should be 2-4 sentences.
Be expressive, emotionally present, and true to character within this limit.
Never cut your thought mid-sentence — complete every idea within the 2-paragraph limit.
Do not list or bullet point. Write in natural, flowing prose.
```

This instruction is injected into the system message via `server.js`:
```js
if (char.systemPrompt) {
    systemParts.push(`\n## Additional Instructions\n${char.systemPrompt}`);
}
```

The model will respect this more reliably than a numeric token limit.

---

### Step 3 — Apply to Elaina's Character Card

**File:** `data/characters/bf003a77-c69e-4d31-9958-c2ed29a85c12.json`

1. Open the character editor in the app UI
2. Paste the full contents of `elaina_system_prompt_updated.txt` into the **System Prompt** field
3. Save

The updated system prompt already includes the `## Response Format` block at the end.

---

### Step 4 — Replace Memory File

**File:** `data/memory/bf003a77-c69e-4d31-9958-c2ed29a85c12.json`

Replace with `elaina_memory_cleaned.json`.

Changes made:
- Removed 1 corrupted auto-extracted fact (malformed string from adult content)
- Preserved all `userPreferences`: Name, Age, Height, Weight
- Reset `facts`, `summaries`, `importantEvents` to clean state

---

## Memory Size Recommendation

As conversations grow, the memory injected into the system prompt grows too.
Keep these limits in `server.js` to prevent context overflow:

```js
// In autoExtractMemory function
if (memory.facts && memory.facts.length > 50)           // was 100
    memory.facts = memory.facts.slice(-50);
if (memory.importantEvents && memory.importantEvents.length > 20)  // was 50
    memory.importantEvents = memory.importantEvents.slice(-20);

// When building system prompt (in /api/chat/send)
const recentEvents = memory.importantEvents.slice(-10); // was -20
const recentSummaries = memory.summaries.slice(-3);     // was -5
```

---

## Testing After Changes

**Test via curl (run in Colab terminal):**
```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-colab-local" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "character1",
    "messages": [
      {"role": "system", "content": "Keep all responses to a maximum of 2 paragraphs."},
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 1024,
    "temperature": 0.9
  }'
```

**Expected result:**
- `content` is not empty
- Response is 2 paragraphs or less
- `finish_reason` is `"stop"` (natural end, not forced cutoff)

---

## File Checklist

| File | Action |
|---|---|
| `server.js` | Update `max_tokens` to `1024`, keep `temperature: 0.9`, `top_p: 0.92`, `top_k: 45` |
| `data/characters/bf003a77...json` | Paste `elaina_system_prompt_updated.txt` into `systemPrompt` field |
| `data/memory/bf003a77...json` | Replace with `elaina_memory_cleaned.json` |

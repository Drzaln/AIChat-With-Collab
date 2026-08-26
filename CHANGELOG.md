# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased] — llama.cpp migration + stability pass

### Added
- **`Collab-Llama.py`** — new one-click Colab notebook script. Runs `llama-server`
  (llama.cpp) directly, no Ollama/LiteLLM in the path.
- **`Kaggle-Llama.py`** — same, for Kaggle's dual-T4 environment. Preserves the
  original `kaggle_llm_server.py`'s dual-GPU verification and RAM/VRAM cleanup
  handler (`atexit`/`SIGTERM`).
- **`Build-Llama-CUDA-Release.py`** — one-time builder that packages a portable
  `llama-server` (CUDA) tarball for upload to your own GitHub Release, so
  future runs can skip compiling from source.
- **CUDA driver linking fix** (`find_cuda_driver_lib()` / `cuda_driver_cmake_flags()`)
  in all three build scripts above: works around `CUDA::cuda_driver` target
  not found during CMake configure on Kaggle/Colab images that don't expose
  an unversioned `libcuda.so`. Two-tier fallback — symlink a found driver lib
  first, or disable the CUDA VMM allocator (`GGML_CUDA_NO_VMM=ON`) as a last
  resort if no driver library is discoverable at all. Verified against a
  real Kaggle T4 build.
- `safePath()` helper in `server.js` — strict UUID-allowlist path
  construction, applied to every character/chat/memory file endpoint.
- Native llama.cpp sampling parameters in `server.js` / `.env.example`:
  `TOP_K`, `TOP_P`, `MIN_P`, `TYPICAL_P`, `TFS_Z`, `TOP_N_SIGMA`,
  `REPEAT_LAST_N`, `REPEAT_PENALTY`, `DRY_*` (full DRY sampling),
  `XTC_*`, `DYNATEMP_*`, `MIROSTAT*`, `SEED`, `SAMPLERS` — with type/range/
  NaN/Infinity validation on every value (logs a warning and falls back to
  default instead of silently misbehaving or crashing).
- "Unread" indicator (sidebar dot) in `app.js` for chats whose reply arrived
  while you were viewing a different chat.
- Character/chat ownership check in `send`/`regenerate`/`summarize` — a chat
  can no longer be processed under the wrong character's persona/memory.

### Changed
- **Default LLM stack is now `llama-server` (llama.cpp) via Cloudflare
  Tunnel** — no LiteLLM proxy, no Ollama. README and `.env.example` rewritten
  to describe this as the primary path.
- `server.js`'s `getModelParams()` fully rewritten: one canonical native
  param set instead of an OpenAI/Ollama-flavored mix.
- Model download (in the new notebooks) uses `huggingface_hub`'s
  `snapshot_download(local_dir=...)` directly instead of relying on
  `llama-server`'s built-in `-hf` downloader — keeps the model out of the
  default HF cache entirely (no duplicate on-disk copy), with Xet chunk
  caching disabled by default (`HF_XET_CHUNK_CACHE_SIZE_BYTES=0`).
- Notebook readiness check replaced with an explicit state machine
  (`PROCESS_STARTED → MODEL_LOADING → HEALTH_READY → TUNNEL_READY`) using
  `llama-server`'s real `/health` semantics (503 while loading, 200 once
  ready) instead of a generic "any non-5xx" guess. "SERVER IS READY" is only
  printed after a real 1-token completion request succeeds end-to-end.
- `.env` writer (`POST /api/config`) no longer uses a raw string in
  `String.replace()` — a pasted URL containing `$&`/`$1` used to corrupt the
  `.env` file; now uses a replacer function.
- `writeJSON()` is atomic (write to `.tmp`, then rename) — an interrupted
  write can no longer leave a truncated/corrupted chat or character file.
- `/api/chat/send` and `/api/chat/regenerate` now re-read the chat from disk
  immediately before writing, instead of reusing the copy loaded before the
  5–120s LLM call — an edit or regenerate made on the same chat while
  waiting is no longer silently reverted.
- Regenerate's alternate-resolution now happens *before* building the
  message history sent to the model, not after — a rejected/stale reply is
  no longer resent to the model on the next turn.
- `appendMessage()` in `app.js` now sets `data-index` on creation — the
  edit (✏️) button works immediately instead of only after a chat
  switch/reload.
- `escapeHtml()` now also escapes quotes (`"`/`'`), not just `&`/`<`/`>` —
  fixes several call sites that interpolate its output inside quoted HTML
  attributes.
- Avatar `src` values are now escaped before interpolation — a malformed or
  malicious avatar string (e.g. from an imported character card) can no
  longer break out of the `<img>` tag.
- `api()` in `app.js` now checks `res.ok` and handles non-JSON error bodies
  instead of throwing an unhandled parse error that silently broke the
  init chain (empty sidebar, dead buttons, no visible error).
- `sendMessage()`/`regenerateLastMessage()` capture `state.currentChatId`/
  `state.currentCharacterId` into local variables before any `await`, and
  re-check before rendering — switching chats mid-request no longer renders
  (or saves) a reply into the wrong chat.
- Failed sends now remove the optimistic "phantom" user bubble and restore
  the typed text, instead of leaving a bubble on screen for a message that
  was never actually saved.

### Fixed
- **Path traversal (C1)** — every file-path construction from user input now
  goes through `safePath()`. Verified with a live server against `../`,
  `../../`, `..%2f`, `%2e%2e`, `..%5c`, absolute paths, `package.json`,
  `karakter`, and more — all correctly rejected with 400, no file touched,
  server stays up.
- **Crash on malformed `chat.messages` (C2)** — `PUT /api/chat/:chatId` now
  rejects a non-array `messages` field at the source; defensive guards added
  in `send`/`regenerate`/`summarize` for any already-corrupted data.
- **Crash on `null` entries in `importantEvents` (C3)** — filtered at save
  time and defensively at read time.
- **Prototype pollution via `messageIndex` (H1)** — `messageIndex` is now
  validated as a real non-negative integer before use; `"__proto__"` and
  similar can no longer reach `Array.prototype`.
- **Double-click race in alternate navigation** — concurrent clicks used to
  each read a stale `selectedAlternate` and could overwrite each other,
  leaving the counter stuck. Now guarded with a per-message in-flight lock.
- **Regenerate had no busy-state feedback** — pressing Enter during a
  regenerate silently no-op'd; now shows a toast and disables the send
  button.
- **Regenerating a chat's first message sent zero conversation turns** to
  the model (only the system prompt) — now injects a minimal opening
  instruction so the model always has something to respond to.
- **Heuristic memory-extraction false positive** — `"hai suka gak sama
  aku?"` was misread as a "likes" fact because the pronoun pattern lacked a
  word boundary (matched the trailing "i" in "hai"). Fixed with `\b`.
- **`abort` timer leak** on every failed/errored LLM fetch attempt (was only
  cleared on the success path).
- **API key mismatch confusion (H11)** — Colab and Kaggle notebooks issue
  different default keys (`sk-colab-local` / `sk-kaggle-local`); a 401 now
  gets an explicit, actionable error message instead of a generic failure.
- **Kaggle warm-up check accepted a 404 as "ready" (H12)** — now requires an
  exact `200`.
- **Colab's `ollama pull` died on a known transient blob-race error (H10)**
  — retry logic ported from the Kaggle script; stale server processes from a
  re-run are now killed before starting a fresh one.
- Hardcoded `lang="id"` in `index.html` → now defaults to `en` and is set
  dynamically once the actual UI language loads; RTL (`dir="rtl"`) applied
  for Arabic.
- `[data-i18n-title]` attributes (4 elements) were never translated —
  handler added.
- `state.config` lost `uiLang`/`showLangWarning` after saving settings
  (object replacement instead of merge) — fixed.

### Deprecated
- `colab_llm_server.py` / `colab_llm_server.ipynb` / `kaggle_llm_server.py`
  (the Ollama + LiteLLM stack) are kept in the repo as an explicitly-labeled
  optional alternative — no longer the default path, not actively developed
  further.

### Known remaining issues (see project bug tracker / next session)
- Memory write-back (`autoExtractMemory`, `/summarize`) still writes using
  the copy of `memory` loaded at the start of the request rather than
  re-reading fresh immediately before `writeJSON` — a manual memory edit
  made while the LLM is generating can still be overwritten. (Chat writes
  already got this fix; memory did not yet.)
- Frontend async race-condition audit (capture-ID-before-`await` pattern) not
  yet confirmed complete for every async function — only `sendMessage`,
  `regenerateLastMessage`, and `changeAlternate` are confirmed fixed.
- Full `app.js` XSS audit (memory fields, event dates, facts, preferences,
  locale values) not yet done end-to-end.
- LLM request retry/timeout audit (distinguishing timeout from HTTP failure,
  unsafe POST retries) not yet done.

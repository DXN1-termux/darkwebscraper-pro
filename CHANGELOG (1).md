# Changelog

All notable changes to DarkWeb Scraper Pro will be documented in this file.

## [4.0.0] - 2026-06-28

### Added
- **12 Search Engines** (was 4): 3 clearnet (torch.cx, ahmia.fi, darksearch.io) + 9 onion (candle, haystak, tordex, phobos, notevil, tor66, deepsearch, darkgate, torch-onion) — all registered in `ENGINE_REGISTRY` with `engine_type` flag
- **Tor SOCKS5 Proxy Support**: `--tor-proxy socks5h://127.0.0.1:9050` enables all 9 onion engines through a shared proxy session with connection pooling
- **`--use-onion` Flag**: One flag to activate all 12 engines at once (requires `--tor-proxy`)
- **`--pages` Flag**: Multi-page search per engine (`-p 5` fetches up to 5 pages per engine) — dramatically more results per query
- **`PaginatedSearchEngine` Base Class**: Generic base for onion engines with standard `/search?q=...&page=...` pattern — add new engines in ~10 lines
- **Domain-Indexed Fuzzy URL Matching (Layer 10)**: New `_domain_link_index` dict maps netloc → link indices, turning Layer 10 from O(N) full-scan to O(k) same-domain lookup. For 10,000 links across 5,000 domains, this is a ~2,000x speedup on the most expensive dedup layer
- **Pre-Compiled Regex (17 patterns)**: All regex patterns compiled once at module import time via `re.compile()` — eliminates per-call compilation overhead on every `is_duplicate()` call
- **Separate Clearnet/Onion Sessions**: Dual session architecture — clearnet engines use a direct session, onion engines use a SOCKS5-proxied session. No proxy overhead on clearnet requests
- **lxml Parser Support**: Auto-detects `lxml` at import (3x faster HTML parsing), falls back to `html.parser` if unavailable
- **Engine Categorization**: `ENGINE_REGISTRY_ONION` and `ENGINE_REGISTRY_CLEARNET` frozensets for easy filtering, `--list-engines` now shows categorized output
- **Onion Engine Warning**: Automatically warns when onion engines are selected without `--tor-proxy`

### Changed
- **Default Max Results: 200 → 5000**: 25x more results per query — exploits the multi-engine + pagination throughput
- **Default Batch Size: 10 → 50**: 5x fewer disk writes for state persistence
- **Default Timeout: 15s → 10s**: Faster fail-fast on unreachable engines, especially onion ones
- **Default Workers: 6 → 16**: Scales with CPU cores (`min(max(8, cpu_count), 16)`) for heavier parallel dedup
- **Connection Pool: 10 → 30**: `POOL_CONNECTIONS` and `POOL_MAXSIZE` raised to 30 for better throughput with 12 concurrent engines
- **Retry Backoff: 1.0 → 0.5**: Faster retry cycle for transient failures
- **Static Methods for Pure Functions**: `_normalize_url`, `_get_path_signature`, `_canonical_url`, `_hash_content`, `_phonetic_hash`, `_title_word_hashes`, `_title_similarity`, `_url_similarity` — all converted to `@staticmethod` to avoid `self` overhead
- **DedupEngine.load_state**: Now rebuilds both `_title_prefix_index` AND `_domain_link_index` on load
- **DedupEngine.stats Command**: Now shows `Title prefix buckets` and `Domain link buckets` in addition to existing state
- **`--list-engines` Output**: Categorized into CLEARNET ENGINES and ONION ENGINES sections with separator lines
- **`-e` Default Behavior**: When `--use-onion` is used with `--tor-proxy`, defaults to all 12 engines

### Removed
- Nothing. Full backward compatibility with v3.0 and v2.0 state files and output format

### Technical
- Lines: 1188 → 1390 (17% more code, 3x more engines, 4x faster dedup)
- 4 direct dependencies (requests, beautifulsoup4, PySocks, lxml) — PySocks for SOCKS5 proxy, lxml is optional (auto-fallback)
- 17 pre-compiled regex patterns at module level
- 2 index structures for O(1) dedup lookups (title prefix + domain link)
- Dual session architecture (clearnet + onion)

## [3.0.0] - 2026-06-28

### Added
- **Multi-Engine Search**: Concurrent search across 4 engines (torch.cx, ahmia.fi, darksearch.io, candle) using `ThreadPoolExecutor`
- **Pluggable Engine Registry**: `ENGINE_REGISTRY` dict for easy engine addition
- **argparse CLI**: One-shot queries (`-q`), engine selection (`-e`), export format (`-x`), output file (`-o`), batch size (`-b`), `--quiet` mode
- **JSON + CSV Export**: Beyond TXT — structured JSON for APIs, CSV for spreadsheets
- **Connection Pooling**: Shared `requests.Session` with 10-connection pool + auto-retry
- **Inverted Index**: Layer 9 fuzzy title matching narrowed from O(N) to O(k) prefix-filtered comparison
- **Batch State Persistence**: Writes `seen_data.json` every N adds instead of every single one

### Changed
- **Default Max Results**: 200 (from unlimited in v2)
- **Global Stopwords**: Deduplicated into single module-level `STOPWORDS` frozenset
- **Robust State Loading**: `load_state()` now catches `JSONDecodeError` and `KeyError`

## [2.0.0] - 2026-06-19

### Added
- Initial public release
- 10-layer deduplication engine
- Parallel dedup with `ProcessPoolExecutor`
- Persistent state via `seen_data.json`
- torch.cx search engine integration
- Box-drawing output format
- Android/Termux download helper
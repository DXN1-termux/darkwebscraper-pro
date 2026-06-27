## DarkWeb Scraper Pro v4.0 - Release Notes

### The Big Four

**1. 12 Search Engines (was 4) — 3 Clearnet + 9 Onion**

v3 searched 4 engines. v4 searches 12 — torch.cx, ahmia.fi, darksearch.io on clearnet, plus haystak, tordex, phobos, notevil, tor66, deepsearch, darkgate, candle, and torch-onion on the Tor network. Onion engines require `--tor-proxy` (SOCKS5). All 12 fire concurrently.

**2. Tor SOCKS5 Proxy Support**

New `--tor-proxy socks5h://127.0.0.1:9050` flag routes all onion engine traffic through Tor. The tool creates a separate proxied session with its own 30-connection pool — zero proxy overhead on clearnet requests. Use `--use-onion` to enable all 12 engines in one shot.

**3. Pre-Compiled Regex + Domain Index = 4x Faster Dedup**

Every regex pattern (17 total) is now compiled once at import time — no per-call compilation. Layer 10 (fuzzy URL) now uses a domain-indexed lookup (`netloc → link indices`) instead of scanning every link. For 10K links across 5K domains, Layer 10 drops from O(N) to O(k) where k ≈ 2. Combined with the v3 inverted index on Layer 9, dedup is ~4x faster overall.

**4. Multi-Page Search + 5000 Default Results**

New `--pages N` flag fetches up to N pages per engine. With 12 engines × 3 pages = 36 page fetches per query, all concurrent. Default max results raised from 200 to 5000. Same wall-clock time, massively more results.

### Full Changelog

- Added 9 new search engines (haystak, tordex, phobos, notevil, tor66, deepsearch, darkgate, torch-onion, candle)
- Added Tor SOCKS5 proxy support with dual-session architecture
- Added `--tor-proxy` and `--use-onion` CLI flags
- Added `--pages` flag for multi-page search per engine
- Added `PaginatedSearchEngine` base class for rapid engine additions
- Added domain-indexed Layer 10 fuzzy URL matching
- Added 17 pre-compiled regex patterns at module level
- Added lxml parser auto-detection (3x faster HTML parsing)
- Added engine categorization (clearnet vs onion)
- Increased default max results to 5000 (was 200)
- Increased default batch size to 50 (was 10)
- Increased connection pool to 30 (was 10)
- Reduced default timeout to 10s (was 15s)
- Increased default workers to 16 (was 6)
- Converted pure functions to @staticmethod for reduced overhead
- Fully backward compatible with v2.0/v3.0 state files and output
- Added PySocks and lxml to requirements

### Quick Start

```bash
git clone https://github.com/DXN1-termux/darkwebscraper-pro.git
cd darkwebscraper-pro
pip install -r requirements.txt
python3 darkwebscraper-pro.py
```

### With Tor (all 12 engines)

```bash
# Make sure Tor is running with SOCKS5 on port 9050
python3 darkwebscraper-pro.py --use-onion --tor-proxy socks5h://127.0.0.1:9050
```

### One-Shot Examples

```bash
# Clearnet engines, 5000 results, 3 pages per engine
python3 darkwebscraper-pro.py -q "darknet markets" -p 3

# All 12 engines through Tor, JSON export
python3 darkwebscraper-pro.py -q "hacking tools" --use-onion --tor-proxy socks5h://127.0.0.1:9050 -x json

# Specific onion engines only
python3 darkwebscraper-pro.py -q "forums" -e haystak,tordex,tor66 --tor-proxy socks5h://127.0.0.1:9050

# Cleanup mode (unchanged)
python3 darkwebscraper-pro.py --clean
```

### Migration from v3.0

No migration needed. `seen_data.json`, `darkweb.txt`, and all state files are fully compatible. The v4 dedup engine adds `_domain_link_index` at runtime (rebuilt from existing state on load). Just pull, install new deps (`pip install PySocks lxml`), and run.

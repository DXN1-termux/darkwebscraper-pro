<div align="center">

```
██████╗  █████╗ ██████╗ ██╗  ██╗    ██╗    ██╗███████╗██████╗ 
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██║    ██║██╔════╝██╔══██╗
██║  ██║███████║██████╔╝█████╔╝     ██║ █╗ ██║█████╗  ██████╔╝
██║  ██║██╔══██║██╔══██╗██╔═██╗     ██║███╗██║██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║  ██║██║  ██╗    ╚███╔███╔╝███████╗██████╔╝
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══╝╚══╝ ╚══════╝╚═════╝ 
                                                                
███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗        
██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗       
███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝       
╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗       
███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║       
╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝  PRO
```

<h3>🕸️ The Most Advanced Onion Link Intelligence Engine 🕸️</h3>

---

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux%20%7C%20macOS-orange?style=for-the-badge&logo=linux&logoColor=white)](https://termux.dev)
[![Tor](https://img.shields.io/badge/Tor-Compatible-7D4698?style=for-the-badge&logo=tor-project&logoColor=white)](https://www.torproject.org)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)]()
[![Dedup Layers](https://img.shields.io/badge/Dedup%20Layers-10-red?style=for-the-badge&logo=databricks&logoColor=white)]()
[![CPU](https://img.shields.io/badge/Multicore-Parallel-blueviolet?style=for-the-badge&logo=intel&logoColor=white)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-ff69b4?style=for-the-badge)](https://github.com/DXN1-termux/darkwebscraper-pro/pulls)

---

<img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=700&size=22&pause=1000&color=7D4698&center=true&vCenter=true&width=700&lines=10-Layer+Deduplication+Engine;Parallel+Multicore+Processing;Live+Onion+Link+Harvesting;Smart+Fuzzy+%26+Phonetic+Matching;Auto+Integrity+Validation;Termux+%26+Android+Native+Support" alt="Typing SVG" />

</div>

---

## ⚡ What is DarkWeb Scraper Pro?

**DarkWeb Scraper Pro** (`bb.py`) is a blazing-fast, intelligence-grade `.onion` link harvester and deduplication engine. It doesn't just scrape — it **understands** what it collects. Built for OSINT researchers, security professionals, and privacy enthusiasts who need clean, verified dark web data without the noise.

> ⚠️ **Disclaimer:** This tool is for **educational and research purposes only**. Always comply with your local laws and regulations. The author takes no responsibility for misuse.

---

## 🧠 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   DarkWeb Scraper Pro v2.0                      │
├────────────────┬────────────────────┬───────────────────────────┤
│  Search Engine │   Dedup Engine v2  │    Parallel Processor     │
│  ─────────────│  ─────────────────│  ────────────────────────  │
│  torch.cx API  │  10-Layer Dedup    │  ProcessPoolExecutor       │
│  HTML Parser   │  Hash + Fuzzy      │  Auto CPU Detection        │
│  Link Extract  │  Phonetic Match    │  Cross-chunk Merge         │
│  URL Decode    │  Canonical URL     │  State Persistence         │
└────────────────┴────────────────────┴───────────────────────────┘
```

---

## 🔥 Features

| Feature | Description |
|---|---|
| 🔍 **Live Search** | Queries `torch.cx` (Tor-accessible search engine) in real time |
| 🧹 **10-Layer Deduplication** | Exact hash → Domain → Normalized URL → Path signature → Content fingerprint → Phonetic → Canonical → Word overlap → Fuzzy title → Fuzzy URL |
| ⚡ **Parallel Processing** | Automatically uses up to 6 CPU cores with `ProcessPoolExecutor` |
| 💾 **Persistent State** | Saves dedup state to `seen_data.json` — never re-collects what you already have |
| 🔗 **Integrity Validation** | Flags links that don't correctly resolve to `.onion` domains |
| 📊 **Rich Stage Output** | Emoji-annotated, timestamped progress printer with stats boxes |
| 📂 **Structured Output** | Saves to beautifully formatted `darkweb.txt` with box-drawing characters |
| 📥 **One-Command Export** | Type `download` to copy results straight to your Android Downloads folder |
| 🔄 **Incremental Runs** | Re-run anytime; only new, unique results get added |
| 🤖 **Smart Fuzzy Match** | Jaccard similarity + SequenceMatcher + Soundex-style phonetic hashing |

---

## 📦 Installation

### 🐧 Termux (Android) — Recommended

```bash
# 1. Install system dependencies
pkg update -y && pkg install python git -y

# 2. Clone the repo
git clone https://github.com/DXN1-termux/darkwebscraper-pro.git
cd darkwebscraper-pro

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run it
python bb.py
```

### 🐧 Linux / macOS

```bash
# 1. Clone
git clone https://github.com/DXN1-termux/darkwebscraper-pro.git
cd darkwebscraper-pro

# 2. (Optional) Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch
python3 bb.py
```

### 🔁 One-liner (Linux/macOS)

```bash
git clone https://github.com/DXN1-termux/darkwebscraper-pro.git && cd darkwebscraper-pro && pip install -r requirements.txt && python3 bb.py
```

---

## 🚀 Usage

```
python bb.py
```

Once running, you'll see the startup banner and system stats. Then enter any query:

```
  ────────────────────────────────────────────────────────
  🔎  Query (or 'quit'): hacking forums
  ────────────────────────────────────────────────────────
```

### Special Commands

| Command | Action |
|---|---|
| `quit` / `q` / `exit` | Runs final dedup cleanup and exits |
| `download` | Deduplicates and copies `darkweb.txt` to your Downloads folder |

---

## 📄 Output Format

Results are saved to `darkweb.txt` in a clean, structured format:

```
┌────────────────────────────────────────────────────┐
│  📌  Some Hidden Service Title                     │
│  🔗  http://example1234567890.onion/page           │
│  🕐  2026-06-19 19:00:00                           │
└────────────────────────────────────────────────────┘
```

---

## 🧩 Deduplication — 10 Layers Explained

```
Layer 01 ── Exact Content Hash         (MD5 of title+URL)
Layer 02 ── Domain Duplicate           (same .onion base domain)
Layer 03 ── Normalized URL             (strips tracking params, trailing slashes)
Layer 04 ── Path Signature             (numeric segments → {num}, lowercased)
Layer 05 ── Content Fingerprint        (domain + top 5 title keywords)
Layer 06 ── Phonetic Match             (Soundex-style hash of title)
Layer 07 ── Canonical URL              (strips index/home/version pages)
Layer 08 ── Word Overlap (Bigrams)     (title bigram hash comparison)
Layer 09 ── Fuzzy Title                (Jaccard + SequenceMatcher ≥ 90%)
Layer 10 ── Fuzzy URL                  (same host + path similarity ≥ 90%)
```

---

## 📊 System Stats (at startup)

```
  ┌──────────────────────────────────────────────────────┐
  │  🔎  System                                          │
  ├──────────────────────────────────────────────────────┤
  │    CPU cores detected: 8                             │
  │    Cores being used: 6                               │
  │    Deduplication layers: 10                          │
  │    Parallel threshold: 50+ entries                   │
  │    Output file: darkweb.txt                          │
  └──────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
darkwebscraper-pro/
├── bb.py               # Main script (search + dedup + output)
├── requirements.txt    # Python dependencies
├── .gitignore          # Ignored files
├── LICENSE             # MIT License
├── README.md           # This file
├── seen_data.json      # (auto-generated) Dedup state persistence
└── darkweb.txt         # (auto-generated) Collected results
```

---

## 🛠️ Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client for fetching search results |
| `beautifulsoup4` | HTML parsing and result extraction |
| `re`, `hashlib` | Regex processing and MD5 fingerprinting |
| `difflib` | SequenceMatcher for fuzzy URL/title comparison |
| `concurrent.futures` | ProcessPoolExecutor for parallel dedup |
| `json` | Persistent state serialization |

All stdlib except `requests` and `beautifulsoup4`.

---

## 🤝 Contributing

PRs are welcome! Fork the repo, make your changes, and open a pull request.

```bash
git clone https://github.com/DXN1-termux/darkwebscraper-pro.git
cd darkwebscraper-pro
git checkout -b feature/my-awesome-feature
# make your changes
git commit -m "feat: add my awesome feature"
git push origin feature/my-awesome-feature
```

---

## ⚠️ Legal Disclaimer

> This tool is intended **solely for educational, research, and authorized security testing purposes**. Accessing the dark web may be restricted or illegal in your jurisdiction. The author assumes **zero liability** for any illegal or unethical use of this software. Always obtain proper authorization before scraping any network.

---

<div align="center">

Made with 🖤 by [DXN1-termux](https://github.com/DXN1-termux)

[![GitHub stars](https://img.shields.io/github/stars/DXN1-termux/darkwebscraper-pro?style=social)](https://github.com/DXN1-termux/darkwebscraper-pro/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/DXN1-termux/darkwebscraper-pro?style=social)](https://github.com/DXN1-termux/darkwebscraper-pro/network/members)

</div>

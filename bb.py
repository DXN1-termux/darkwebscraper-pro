import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote, urlparse, urlunparse, parse_qs, urlencode
from difflib import SequenceMatcher
from collections import defaultdict
import hashlib
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import sys
import time
import shutil
import json

# =============================================================================
# CONFIG
# =============================================================================
CPU_COUNT = min(max(4, os.cpu_count() or 4), 6)

# =============================================================================
# RICH PROGRESS PRINTER
# =============================================================================

class StagePrinter:
    STAGES = {
        'init': '🔧', 'dedup': '🧹', 'load': '📂', 'search': '🔍',
        'parse': '📄', 'filter': '⚡', 'save': '💾', 'done': '✅',
        'error': '❌', 'warn': '⚠️', 'info': 'ℹ️', 'skull': '💀',
        'fire': '🔥', 'star': '⭐', 'cpu': '🖥️', 'time': '⏱️',
        'rocket': '🚀', 'sparkle': '✨', 'mag': '🔎',
    }

    def __init__(self):
        self.stage_count = 0
        self.stage_times = {}

    def _now(self):
        return time.time()

    def _fmt_time(self, seconds):
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            return f"{seconds//60:.0f}m {seconds%60:.0f}s"

    def _print(self, emoji, msg, detail="", timing=""):
        self.stage_count += 1
        prefix = f"[{self.stage_count:02d}]"
        parts = [prefix, emoji, msg]
        if detail:
            parts.append(f"→ {detail}")
        if timing:
            parts.append(f"({timing})")
        print("  ".join(parts))
        sys.stdout.flush()

    def stage(self, name, msg, detail=""):
        emoji = self.STAGES.get(name, '•')
        self.stage_times[msg] = self._now()
        self._print(emoji, msg, detail)

    def stage_done(self, msg):
        if msg in self.stage_times:
            elapsed = self._now() - self.stage_times[msg]
            print(f"       └─> {self.STAGES['time']} Done in {self._fmt_time(elapsed)}")
            sys.stdout.flush()
            del self.stage_times[msg]

    def found(self, count, what):
        if count > 0:
            print(f"       └─> {self.STAGES['star']} Found {count} {what}")
        else:
            print(f"       └─> {self.STAGES['warn']} No {what} found")
        sys.stdout.flush()

    def removed(self, count, reason):
        print(f"       └─> {self.STAGES['skull']} Removed {count} duplicates ({reason})")
        sys.stdout.flush()

    def kept(self, count):
        print(f"       └─> {self.STAGES['done']} Kept {count} unique entries")
        sys.stdout.flush()

    def skipped(self, count, reason):
        print(f"       └─> {self.STAGES['skull']} Skipped {count} ({reason})")
        sys.stdout.flush()

    def saved(self, count):
        print(f"       └─> {self.STAGES['save']} Saved {count} new results")
        sys.stdout.flush()

    def cpu_info(self, cores):
        print(f"       └─> {self.STAGES['cpu']} Using {cores} CPU cores for parallel dedup")
        sys.stdout.flush()

    def divider(self):
        print(f"\n  {'·' * 56}\n")
        sys.stdout.flush()

    def banner(self, text):
        width = 60
        print(f"\n╔{'═' * (width - 2)}╗")
        print(f"║  {self.STAGES['fire']}  {text:<{width - 8}}║")
        print(f"╚{'═' * (width - 2)}╝\n")
        sys.stdout.flush()

    def stats_box(self, title, items):
        width = 54
        print(f"\n  ┌{'─' * width}┐")
        print(f"  │  {self.STAGES['mag']}  {title:<{width - 5}}│")
        print(f"  ├{'─' * width}┤")
        for key, val in items:
            line = f"  {key}: {val}"
            print(f"  │  {line:<{width - 2}}│")
        print(f"  └{'─' * width}┘")
        sys.stdout.flush()


_printer = StagePrinter()

# =============================================================================
# ROBUST FILE PARSER
# =============================================================================

def _parse_file_lines(lines):
    entries = []
    broken_count = 0
    temp_title = None

    for line in lines:
        if '📌' in line:
            parts = line.split('📌', 1)
            if len(parts) > 1:
                content = parts[1].split('│')[0].strip()
                temp_title = content
        elif '🔗' in line and temp_title:
            parts = line.split('🔗', 1)
            if len(parts) > 1:
                link = parts[1].split('│')[0].strip()
                
                # Integrity Check: Flag as broken if it doesn't end in .onion/ or .onion
                if not (link.endswith('.onion') or link.endswith('.onion/')):
                    broken_count += 1
                
                entries.append((temp_title, link))
                temp_title = None
    return entries, broken_count


# =============================================================================
# DEDUP ENGINE v2 (10 LAYERS)
# =============================================================================

class DedupEngine:
    def __init__(self, state_file="seen_data.json", load_state=True):
        self.state_file = state_file
        self.seen_domains = set()
        self.seen_paths = set()
        self.seen_hashes = set()
        self.seen_titles = []
        self.seen_links = []
        self.seen_phonetic = set()
        self.seen_canonical = set()
        self.seen_title_hashes = set()
        if load_state:
            self.load_state()

    def save_state(self):
        state = {
            "hashes": list(self.seen_hashes),
            "domains": list(self.seen_domains),
            "paths": list(self.seen_paths),
            "titles": self.seen_titles,
            "links": self.seen_links,
            "phonetic": list(self.seen_phonetic),
            "canonical": list(self.seen_canonical),
            "title_hashes": list(self.seen_title_hashes)
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def load_state(self):
        if not os.path.exists(self.state_file): return
        with open(self.state_file, 'r') as f:
            state = json.load(f)
            self.seen_hashes = set(state.get("hashes", []))
            self.seen_domains = set(state.get("domains", []))
            self.seen_paths = set(state.get("paths", []))
            self.seen_titles = state.get("titles", [])
            self.seen_links = state.get("links", [])
            self.seen_phonetic = set(state.get("phonetic", []))
            self.seen_canonical = set(state.get("canonical", []))
            self.seen_title_hashes = set(state.get("title_hashes", []))

    def _extract_domain(self, url):
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        match = re.search(r'([a-z2-7]{16}|[a-z2-7]{56})\.onion', hostname, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        return hostname.lower()

    def _normalize_url(self, url):
        parsed = urlparse(url)
        tracking_params = {'ref', 'utm_source', 'utm_medium', 'utm_campaign', 
                          'utm_term', 'utm_content', 'fbclid', 'gclid',
                          'track', 'source', 'referrer', 'session', 'id'}
        query = parse_qs(parsed.query)
        filtered_query = {k: v for k, v in query.items() 
                         if k.lower() not in tracking_params}
        sorted_query = urlencode(sorted(filtered_query.items()), doseq=True)
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/'),
            parsed.params,
            sorted_query,
            ''
        ))
        return normalized

    def _get_path_signature(self, url):
        parsed = urlparse(url)
        path = parsed.path.lower().strip('/')
        path = re.sub(r'/+', '/', path)
        path = re.sub(r'\d+', '{num}', path)
        return path

    def _content_fingerprint(self, title, url):
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                     'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
                     'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                     'will', 'would', 'could', 'should', 'may', 'might', 'must',
                     'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
                     'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
        significant = [w for w in words if w not in stopwords]
        domain = self._extract_domain(url)
        fingerprint = f"{domain}:{'|'.join(sorted(significant[:5]))}"
        return fingerprint

    def _hash_content(self, title, url):
        normalized = f"{title.lower().strip()}|{self._normalize_url(url)}"
        return hashlib.md5(normalized.encode()).hexdigest()

    def _phonetic_hash(self, text):
        text = re.sub(r'[^a-z]', '', text.lower())
        if not text:
            return ""
        result = [text[0]]
        mappings = {
            'bfpv': '1', 'cgjkqsxz': '2', 'dt': '3',
            'l': '4', 'mn': '5', 'r': '6'
        }
        for char in text[1:]:
            for group, code in mappings.items():
                if char in group:
                    if result[-1] != code:
                        result.append(code)
                    break
        while len(result) < 4:
            result.append('0')
        return ''.join(result[:4])

    def _canonical_url(self, url):
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        path = parsed.path.lower().strip('/')
        path = re.sub(r'^index\.(php|html?|asp|jsp)?$', '', path)
        path = re.sub(r'^home$', '', path)
        path = re.sub(r'^default\.(php|html?|asp)?$', '', path)
        path = re.sub(r'v?\d+\.\d+([\.\d]*)', '{ver}', path)
        path = re.sub(r'[/\-]?(id|page|p|item|product)[/\-]?\d+', '/{id}', path)
        parts = [p for p in path.split('/') if p]
        canonical = f"{hostname.lower()}/{'/'.join(parts)}"
        return canonical.rstrip('/')

    def _title_word_hashes(self, title):
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                     'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
                     'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                     'will', 'would', 'could', 'should', 'may', 'might', 'must',
                     'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
                     'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
                     'his', 'her', 'its', 'our', 'their'}
        words = re.findall(r'\b[a-z]{3,}\b', title.lower())
        significant = [w for w in words if w not in stopwords]
        hashes = set()
        for i in range(len(significant) - 1):
            bigram = f"{significant[i]}_{significant[i+1]}"
            hashes.add(hashlib.md5(bigram.encode()).hexdigest()[:8])
        for word in significant[:3]:
            hashes.add(hashlib.md5(word.encode()).hexdigest()[:8])
        return hashes

    def _title_similarity(self, a, b):
        a_clean = re.sub(r'[^\w\s]', '', a.lower()).strip()
        b_clean = re.sub(r'[^\w\s]', '', b.lower()).strip()
        if a_clean == b_clean:
            return True
        a_words = set(a_clean.split())
        b_words = set(b_clean.split())
        if a_words and b_words:
            intersection = len(a_words & b_words)
            union = len(a_words | b_words)
            jaccard = intersection / union if union > 0 else 0
            if jaccard > 0.85:
                return True
        if SequenceMatcher(None, a_clean, b_clean).ratio() > 0.90:
            return True
        return False

    def _url_similarity(self, a, b):
        pa, pb = urlparse(a), urlparse(b)
        if pa.netloc != pb.netloc:
            return False
        path_ratio = SequenceMatcher(None, pa.path, pb.path).ratio()
        if path_ratio > 0.90:
            return True
        if pa.path == pb.path:
            qa = parse_qs(pa.query)
            qb = parse_qs(pb.query)
            if set(qa.keys()) == set(qb.keys()):
                return True
        return False

    def is_duplicate(self, title, link):
        # FAST PATH: Normalize and extract first to avoid re-doing work
        domain = self._extract_domain(link)
        normalized = self._normalize_url(link)
        content_hash = self._hash_content(title, link)
        path_sig = self._get_path_signature(link)
        canonical = self._canonical_url(link)
        phonetic = self._phonetic_hash(title)
        fingerprint = self._content_fingerprint(title, link)
        
        # Layer 1: Set/Hash lookups (Cheapest)
        if content_hash in self.seen_hashes: return True, "exact_hash"
        if domain in self.seen_domains: return True, "domain_duplicate"
        if normalized in self.seen_links: return True, "normalized_url"
        if path_sig in self.seen_paths and path_sig: return True, "path_signature"
        if fingerprint in self.seen_hashes: return True, "content_fingerprint"
        if phonetic in self.seen_phonetic: return True, "phonetic_match"
        if canonical in self.seen_canonical: return True, "canonical_url"

        # Layer 2: Expensive checks (Fuzzy/Complex)
        word_hashes = self._title_word_hashes(title)
        if word_hashes & self.seen_title_hashes:
            overlap = len(word_hashes & self.seen_title_hashes)
            total = len(word_hashes | self.seen_title_hashes)
            if total > 0 and overlap / total > 0.6: return True, "word_overlap"
        
        for existing_title in self.seen_titles:
            if self._title_similarity(title, existing_title): return True, "fuzzy_title"

        for existing_link in self.seen_links:
            if self._url_similarity(normalized, existing_link): return True, "fuzzy_link"

        return False, None

    def add(self, title, link):
        self.seen_hashes.add(self._hash_content(title, link))
        self.seen_domains.add(self._extract_domain(link))
        self.seen_paths.add(self._get_path_signature(link))
        self.seen_hashes.add(self._content_fingerprint(title, link))
        self.seen_titles.append(title)
        self.seen_links.append(self._normalize_url(link))
        self.seen_phonetic.add(self._phonetic_hash(title))
        self.seen_canonical.add(self._canonical_url(link))
        self.seen_title_hashes.update(self._title_word_hashes(title))
        self.save_state()

    def load_from_file(self, filename="darkweb.txt"):
        try:
            if not os.path.exists(filename):
                _printer.stage('info', "No file found", "starting fresh")
                return

            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            entries, broken = _parse_file_lines(lines)
            for title, link in entries:
                self.add(title, link)
            
            _printer.stage('done', "Engine loaded", f"{len(self.seen_titles)} entries ({broken} seem broken)")
        except Exception as e:
            _printer.stage('error', "Load failed", str(e))


# =============================================================================
# PARALLEL DEDUP
# =============================================================================

def _check_chunk(chunk_data):
    engine = DedupEngine(load_state=False)
    unique = []
    stats = defaultdict(int)
    for title, link in chunk_data:
        is_dup, reason = engine.is_duplicate(title, link)
        if is_dup:
            stats[reason] += 1
        else:
            engine.add(title, link)
            unique.append((title, link))
    return unique, stats, engine


def parallel_dedup(entries, num_workers=CPU_COUNT):
    if len(entries) < 50 or num_workers == 1:
        engine = DedupEngine()
        unique = []
        stats = defaultdict(int)
        for title, link in entries:
            is_dup, reason = engine.is_duplicate(title, link)
            if is_dup:
                stats[reason] += 1
            else:
                engine.add(title, link)
                unique.append((title, link))
        return unique, stats

    chunk_size = max(1, len(entries) // num_workers)
    chunks = [entries[i:i+chunk_size] for i in range(0, len(entries), chunk_size)]

    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(_check_chunk, chunk): i for i, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            chunk_idx = futures[future]
            unique, stats, engine = future.result()
            results.append((chunk_idx, unique, stats, engine))

    results.sort(key=lambda x: x[0])
    all_unique = []
    all_stats = defaultdict(int)
    final_engine = DedupEngine()

    for _, chunk_unique, chunk_stats, chunk_engine in results:
        for title, link in chunk_unique:
            is_dup, reason = final_engine.is_duplicate(title, link)
            if is_dup:
                all_stats[f"cross_chunk_{reason}"] += 1
            else:
                final_engine.add(title, link)
                all_unique.append((title, link))
        for reason, count in chunk_stats.items():
            all_stats[reason] += count

    return all_unique, all_stats


# =============================================================================
# FILE OPS
# =============================================================================

def load_existing_data(filename="darkweb.txt"):
    try:
        if not os.path.exists(filename):
            return [], []
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        entries, _ = _parse_file_lines(lines)
        titles = [e[0] for e in entries]
        links = [e[1] for e in entries]
        return titles, links
    except Exception:
        return [], []


def save_deduplicated_file(filename="darkweb.txt"):
    _printer.divider()
    _printer.stage('dedup', "CLEANING existing file", filename)
    _printer.cpu_info(CPU_COUNT)

    try:
        if not os.path.exists(filename):
            _printer.stage('info', "No file", "nothing to clean")
            _printer.divider()
            return

        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        entries, broken_count = _parse_file_lines(lines)
        _printer.found(len(entries), "existing entries")
        if broken_count > 0:
            _printer.stage('warn', "Integrity Check", f"Found {broken_count} potentially broken links")

        if not entries:
            _printer.stage('info', "No data", "starting fresh")
            _printer.divider()
            return

        _printer.stage('cpu', "Running parallel dedup...")
        unique_entries, stats = parallel_dedup(entries, CPU_COUNT)
        _printer.stage_done("Running parallel dedup...")

        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, 'w', encoding='utf-8') as f:
            for title, link in unique_entries:
                width = max(len(title), len(link), len(ts), 50) + 8
                border = "─" * (width - 2)
                f.write(f"┌{border}┐\n")
                f.write(f"│  📌  {title:<{width-8}}  │\n")
                f.write(f"│  🔗  {link:<{width-8}}  │\n")
                f.write(f"│  🕐  {ts:<{width-8}}  │\n")
                f.write(f"└{border}┘\n\n")

        total_removed = sum(stats.values())
        if total_removed > 0:
            _printer.removed(total_removed, ", ".join(f"{k}:{v}" for k,v in sorted(stats.items(), key=lambda x: -x[1])))
        _printer.kept(len(unique_entries))

        if stats:
            _printer.stats_box("Breakdown", sorted(stats.items(), key=lambda x: -x[1]))

    except Exception as e:
        _printer.stage('error', "Cleanup failed", str(e))

    _printer.divider()


def get_onion_links_and_titles(query, max_new_links=200, dedup_engine=None):
    if dedup_engine is None:
        dedup_engine = DedupEngine()

    _printer.stage('search', "Searching torch.cx", f"query='{query}'")

    url = f"https://torch.cx/search?q={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        _printer.stage('info', "Fetching page...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        _printer.stage_done("Fetching page...")
        _printer.stage('done', "Response received", f"{len(response.text)//1024}KB")
    except requests.RequestException as e:
        _printer.stage('error', "Failed", str(e))
        return []

    _printer.stage('parse', "Parsing HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')
    raw_results = soup.select('div.result, li.result, div.g, div.rc')
    _printer.stage_done("Parsing HTML...")
    _printer.found(len(raw_results), "raw results")

    _printer.stage('filter', "Filtering + deduping (10 layers)...")
    results = []
    skipped = defaultdict(int)

    for result in raw_results:
        # Improved title extraction
        title_tag = result.find(['h3', 'a', 'b'])
        title = title_tag.get_text(strip=True) if title_tag else result.get_text(strip=True)
        if not title:
            title = "No title found"

        link = result.find('a', href=True)
        if link and ('/search/redirect?' in link['href'] or 'onion' in link['href']):
            onion_link = ""
            if '/search/redirect?' in link['href']:
                redirect_url = re.search(r'redirect_url=(.+)', link['href'])
                if redirect_url:
                    decoded_url = unquote(redirect_url.group(1))
                    onion_url_match = re.search(r'(http[s]?://[^&\s]+?\.onion[^\s&]*)', decoded_url)
                    if onion_url_match:
                        onion_link = onion_url_match.group(1)
            else:
                onion_link = link['href']

            if onion_link:
                is_dup, reason = dedup_engine.is_duplicate(title, onion_link)
                if is_dup:
                    skipped[reason] += 1
                    continue
                dedup_engine.add(title, onion_link)
                results.append((title, onion_link))
                if len(results) >= max_new_links:
                    _printer.stage('warn', "Max limit hit", f"{max_new_links}")
                    break

    _printer.stage_done("Filtering + deduping (10 layers)...")

    if skipped:
        for reason, count in sorted(skipped.items(), key=lambda x: -x[1]):
            _printer.skipped(count, reason)

    _printer.found(len(results), "NEW unique links")
    return results


def save_results_to_file(results, filename="darkweb.txt"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, 'a', encoding='utf-8') as f:
        for i, (title, link) in enumerate(results, 1):
            width = max(len(title), len(link), len(ts), 50) + 8
            border = "─" * (width - 2)
            f.write(f"┌{border}┐\n")
            f.write(f"│  📌  {title:<{width-8}}  │\n")
            f.write(f"│  🔗  {link:<{width-8}}  │\n")
            f.write(f"│  🕐  {ts:<{width-8}}  │\n")
            f.write(f"└{border}┘\n\n")
    _printer.saved(len(results))
    _printer.divider()




# =============================================================================
# DOWNLOAD HELPERS
# =============================================================================

def copy_output_to_downloads(filename="darkweb.txt"):
    """
    Copy the current output file to the user's Downloads folder.
    Works in Termux and standard Android shared storage layouts.
    """
    candidates = [
        os.path.expanduser("~/storage/downloads"),
        os.path.expanduser("~/downloads"),
        "/storage/emulated/0/Download",
        "/storage/emulated/0/Downloads",
    ]

    source = os.path.abspath(filename)
    if not os.path.exists(source):
        _printer.stage('error', "Copy failed", f"{filename} not found")
        return False

    for dest_dir in candidates:
        try:
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, os.path.basename(filename))
            shutil.copy2(source, dest)
            _printer.stage('save', "Copied file", dest)
            return True
        except Exception:
            continue

    _printer.stage('error', "Copy failed", "no writable Downloads path found")
    return False

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    _printer.banner("🕸  Dark Web Scraper  ·  v2.0")
    _printer.stats_box("System", [
        ("CPU cores detected", os.cpu_count() or "unknown"),
        ("Cores being used", CPU_COUNT),
        ("Deduplication layers", "10"),
        ("Parallel threshold", "50+ entries"),
        ("Output file", "darkweb.txt"),
    ])

    save_deduplicated_file()

    _printer.stage('load', "Loading engine...")
    engine = DedupEngine()
    engine.load_from_file()

    while True:
        print(f"\n  {'─' * 56}")
        query = input("  🔎  Query (or 'quit'): ").strip()
        print(f"  {'─' * 56}")
        normalized_query = query.lower().strip()

        if normalized_query in ('quit', 'q', 'exit'):
            _printer.divider()
            _printer.stage('dedup', "Final cleanup...")
            save_deduplicated_file()
            _printer.banner("Done  👋")
            break

        if normalized_query in ('download', 'download as', 'download file', 'save file'):
            _printer.stage('info', "Download requested", "copying darkweb.txt to Downloads")
            save_deduplicated_file()
            copy_output_to_downloads("darkweb.txt")
            continue

        results = get_onion_links_and_titles(query, max_new_links=200, dedup_engine=engine)

        if results:
            print()
            for i, (title, link) in enumerate(results, 1):
                print(f"  [{i:02d}]  📌  {title}")
                print(f"        🔗  {link}")
                print()
            save_results_to_file(results)
            for title, link in results:
                engine.add(title, link)
            _printer.stage('done', f"Session total: {len(engine.seen_titles)} unique entries")
        else:
            _printer.stage('warn', "No results", "try another query")

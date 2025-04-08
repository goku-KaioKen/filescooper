#!/usr/bin/env python3
import os
import argparse
import requests
import time
import random
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm, TqdmExperimentalWarning
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)

DESKTOP_USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; rv:115.0) Gecko/20100101 Firefox/115.0', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15']
MOBILE_USER_AGENTS = ['Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1', 'Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36', 'Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1']

def parse_headers(header_list):
    headers = {}
    for item in header_list:
        if ':' in item:
            key, value = item.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def read_urls_from_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[✗] Failed to read file '{filepath}': {e}")
        return []

class Color:
    def __init__(self, enable=True):
        if enable:
            self.BOLD = "\033[1m"
            self.GREEN = "\033[92m"
            self.YELLOW = "\033[93m"
            self.RED = "\033[91m"
            self.RESET = "\033[0m"
        else:
            self.BOLD = ""
            self.GREEN = ""
            self.YELLOW = ""
            self.RED = ""
            self.RESET = ""

def colorize_status(code, color):
    if 200 <= code < 300:
        return f"{color.GREEN}{code}{color.RESET}"
    elif 300 <= code < 400:
        return f"{color.YELLOW}{code}{color.RESET}"
    else:
        return f"{color.RED}{code}{color.RESET}"

def get_unique_filename(output_dir, base_filename):
    base, ext = os.path.splitext(base_filename)
    counter = 1
    unique_filename = base_filename
    while os.path.exists(os.path.join(output_dir, unique_filename)):
        unique_filename = f"{base}_{counter}{ext}"
        counter += 1
    return unique_filename

def allowed_extension(filename, allowed_types):
    if allowed_types == {"*"}:
        return True
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    return ext in allowed_types


def format_size(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def parse_size(size_str):
    if not size_str:
        return None
    size_str = size_str.strip().upper()
    multiplier = 1
    if size_str.endswith('KB'):
        multiplier = 1024
        size_str = size_str[:-2]
    elif size_str.endswith('MB'):
        multiplier = 1024 ** 2
        size_str = size_str[:-2]
    elif size_str.endswith('GB'):
        multiplier = 1024 ** 3
        size_str = size_str[:-2]
    return int(float(size_str) * multiplier)

def download_file(url, headers, output_dir, proxies=None, retries=3, color=None, allowed_types=None, min_size=None, max_size=None, random_ua=False):
    for attempt in range(1, retries + 1):
        try:
            if random_ua == 'desktop':
                headers['User-Agent'] = random.choice(DESKTOP_USER_AGENTS)
            elif random_ua == 'mobile':
                headers['User-Agent'] = random.choice(MOBILE_USER_AGENTS)

            response = requests.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
            status_colored = colorize_status(response.status_code, color)

            content_length = len(response.content)
            if min_size and content_length < min_size:
                return f"[!] Skipped (too small < {format_size(min_size)}): {url}"
            if max_size and content_length > max_size:
                return f"[!] Skipped (too large > {format_size(max_size)}): {url}"


            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            if not filename:
                return f"[!] Skipped (no filename): {url}"

            if not allowed_extension(filename, allowed_types):
                return f"[!] Skipped (not allowed type): {url}"

            os.makedirs(output_dir, exist_ok=True)
            filename = get_unique_filename(output_dir, filename)
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)
            size_str = format_size(len(response.content))
            return f"[✓] {filename:<30} → {status_colored} ({size_str})  ({url})", response.status_code, content_length
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                return f"[✗] Failed to download {url} after {retries} attempt(s): {e}"

def setup_log_file(log_path=None):
    os.makedirs("logs", exist_ok=True)
    if not log_path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = os.path.join("logs", f"filescooper_{timestamp}.log")
    return open(log_path, 'w', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="📦 FileScooper - Flexible multithreaded downloader for JS/CSS/images/binaries.")
    parser.add_argument('-u', '--urls', nargs='*', help='One or more URLs to download')
    parser.add_argument('-f', '--file', help='Read URLs from a text file (one per line)')
    parser.add_argument('-o', '--output', default='downloads', help='Directory to save the downloaded files')
    parser.add_argument('-H', '--header', action='append', default=[], help='Custom header (e.g., "Cookie: foo=bar")')
    parser.add_argument('-x', '--proxy', help='Proxy server (e.g., http://127.0.0.1:8080)')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Number of parallel download threads')
    parser.add_argument('--retries', type=int, default=3, help='Number of retry attempts per failed download')
    parser.add_argument('--log-file', help='Path to log file (default: logs/filescooper_TIMESTAMP.log)')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--types', default='js', help='Comma-separated list of allowed extensions (e.g., js,css,png), or "*" to allow all')
    parser.add_argument('--random-useragent', action='store_true', help='Use a random desktop User-Agent')
    parser.add_argument('--min-size', help='Minimum file size to keep (e.g., 10KB, 1MB)')
    parser.add_argument('--max-size', help='Maximum file size to keep (e.g., 5MB, 500KB)')
    parser.add_argument('--mobile-useragent', action='store_true', help='Use a random mobile User-Agent')

    args = parser.parse_args()
    headers = parse_headers(args.header)
    proxies = {'http': args.proxy, 'https': args.proxy} if args.proxy else None
    color = Color(enable=not args.no_color)
    allowed_types = {t.strip().lower() for t in args.types.split(',')}

    urls = args.urls or []
    if args.file:
        urls.extend(read_urls_from_file(args.file))

    
    if args.random_useragent and args.mobile_useragent:
        print("[!] You cannot use --random-useragent and --mobile-useragent at the same time.")
        return

    
    min_size = parse_size(args.min_size)
    max_size = parse_size(args.max_size)

    total_downloaded = 0
    total_bytes = 0

    if not urls:
        print("[!] No URLs provided. Use -u or -f.")
        return

    print(f"\n📥 Downloading {len(urls)} file(s) with {args.threads} threads...\n")
    log_file = setup_log_file(args.log_file)
    results = []

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [
            executor.submit(download_file, url, headers.copy(), args.output, proxies, args.retries, color, allowed_types, min_size, max_size, 'desktop' if args.random_useragent else ('mobile' if args.mobile_useragent else False))
            for url in urls
        ]

        progress_bar = tqdm(
            as_completed(futures),
            total=len(futures),
            desc="⏳ Progress",
            ncols=100,
            unit="file",
            bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed} @ {rate_fmt}]"
        )

    for future in progress_bar:
        result, status, size = future.result()
        results.append(result)
        log_file.write(result + '\n')
        if status == 200 and size > 0:
            total_downloaded += 1
            total_bytes += size
    successes = [r for r in results if r.startswith("[✓]")]
    skips     = [r for r in results if r.startswith("[!]")]
    failures  = [r for r in results if r.startswith("[✗]")]

    print(f"\n📄 {color.BOLD}Download Summary:{color.RESET}\n")

    if successes:
        print(f"{color.GREEN}✅ Successfully downloaded:{color.RESET}\n")
        for r in successes:
            print(r)
        print()

    if skips:
        print(f"{color.YELLOW}⚠️ Skipped files:{color.RESET}\n")
        for r in skips:
            print(r)
        print()

    if failures:
        print(f"{color.RED}❌ Failed downloads:{color.RESET}\n")
        for r in failures:
            print(r)
        print()

    log_file.close()
    print(f"📁 Saved to: {args.output}/")
    print(f"📝 Log saved to: {log_file.name}")
    
    if total_downloaded:
        print(f"📦 Total downloaded: {total_downloaded} file(s), {format_size(total_bytes)}")


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()

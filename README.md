# 🧰 FileScooper

**FileScooper** is a flexible, fast, and scriptable multithreaded downloader for hackers, recon workflows, developers, and automation pipelines. It supports custom headers, proxies, file type filtering, retries, and much more — all wrapped in a clean CLI with progress bars and logs.

---

## 🚀 Features

- ✅ **Multithreaded** downloads (with customizable thread count)
- 🌐 **Custom headers** and proxy support (great for Burp/ZAP/etc.)
- 🔁 **Retry logic** with exponential backoff
- 📁 **Flexible file type support** via `--types` (e.g. `.js`, `.css`, `.png`, `.jpg`, binaries)
- 📦 **Unique filenames** (auto-deduplicates)
- 📊 **Live progress bar** with speed, ETA, and count
- 🎨 **Colorized output** for easy scanning (optional `--no-color`)
- 📝 **Automatic logging** to timestamped files
- 🧼 **Grouped download summary**: successes, skips, and failures
- 🔄 **Automatic handling of HTTP redirects** (e.g. 302 responses)
- 🚫 **Graceful error handling** for client-side (4xx) and server-side (5xx) errors with retry support
- 🧮 **File size-based filtering** via `--min-size` and `--max-size`
- 📊 **Total download summary** (number of files, total size)

---

## 🛠️ Installation

Clone the repo and install dependencies (just `requests` and `tqdm`):

```bash
git clone https://github.com/goku-KaioKen/filescooper.git
cd filescooper
pip install -r requirements.txt
```

Or just run the script directly if you already have Python 3:

```bash
python filescooper.py ...
```

---

## ⚙️ Usage

### 🔽 Basic

```bash
python filescooper.py -f urls.txt
```

Downloads all `.js` files from the file `urls.txt` using 5 threads (default), saved into `downloads/`.

---

### 📂 File Type Filtering

```bash
python filescooper.py -f urls.txt --types js,css,png
```

Only downloads files ending in `.js`, `.css`, or `.png`.

```bash
python filescooper.py -f urls.txt --types *
```

Downloads **everything**, including binaries and images.

---

### 🧵 Set Number of Threads

```bash
python filescooper.py -f urls.txt -t 20
```

Use 20 parallel threads for faster downloading.

---

### 🌐 Use Proxy and Headers

```bash
python filescooper.py -f urls.txt -x http://127.0.0.1:8080 \
  -H "User-Agent: custom" -H "Authorization: Bearer xyz"
```

Useful for proxy-based inspection or authenticated APIs.

---

### 🪵 Logging

```bash
python filescooper.py -f urls.txt --log-file logs/output.log
```

All output (success, skipped, failed) is also logged to a file. If not specified, FileScooper creates one in `logs/filescooper_YYYY-MM-DD_HH-MM-SS.log`.

---

### 🧱 Disable Colors for CI Logs

```bash
python filescooper.py -f urls.txt --no-color
```

---

### 💡 Size-Based Filtering (`--min-size`, `--max-size`)

```bash
python filescooper.py -f urls.txt --min-size 20KB --max-size 2MB
```

Downloads files only between the specified sizes (e.g., at least `20KB` but no more than `2MB`).

---

### 🌍 Handle HTTP Redirects and Errors

By default, **FileScooper** handles HTTP redirects (302) automatically.

You can also see which files have a `4xx` or `5xx` status and retry up to the specified number of retries.

---

## 📄 Example Output

```
📥 Downloading 50 file(s) with 10 threads...

⏳ Progress |███████████████████████████████████████| 50/50 [00:12 @ 4.1 file/s]

📄 Download Summary:

✅ Successfully downloaded:

[✓] app.js                    → 200 (87.2 KB)  (https://example.com/app.js)
[✓] style.css                 → 200 (412.7 KB) (https://example.com/style.css)

⚠️ Skipped files:

[!] Skipped (not allowed type): https://example.com/logo.svg

❌ Failed downloads:

[✗] Failed to download https://example.com/data.json after 3 attempt(s): Timeout

📦 Total downloaded: 12 file(s), 3.2 MB

📁 Saved to: downloads/
📝 Log saved to: logs/filescooper_2025-04-07_15-23-40.log
```

---

## 🧪 Test URLs Example (`urls.txt`)

```
https://example.com/script.js
https://example.com/styles.css
https://example.com/image.png
https://example.com/file.exe
```
---

## 📄 License

MIT License — free to use, fork, and contribute.

---

## 👤 Author

Made with ☕ and Python by **gokuKaioKen**  
Twitter: [@gokuKaioKen_](https://twitter.com/gokuKaioKen_)  
GitHub: [goku-KaioKen](https://github.com/goku-KaioKen)
*[Türkçe](README.md) · **English***

# M3U8 Studio

<img width="1062" height="792" alt="Ekran Alıntısı en" src="https://github.com/user-attachments/assets/5dddd4d8-cbce-45a7-a94f-c34c139ae097" />

A desktop application written with PyQt6 that downloads HLS (`.m3u8`) streams at the
highest available quality.

You paste a video link, the program parses the playlist, downloads the segments in
parallel, merges them into a single file and — optionally — converts the result to MP4
with ffmpeg.

**Highlights**

- **Automatically picks the highest quality** in a master playlist (resolution + bitrate)
- **Clipboard watcher** — copy an `.m3u8` link in your browser and a notification appears
  offering "Download Now" or "Add to Queue"
- **Download queue** and **bulk link adding**, with parallel downloads
- Decrypts **AES-128** protected streams; supports fMP4 and byte ranges
- Extracts a **live preview thumbnail** from the video while downloading
- **Resumes interrupted downloads** from where they stopped (segment cache)
- **Two languages**: English / Turkish, switchable instantly
- Sound effects and an animated dark theme

---

## 1. Requirements

| Requirement | Version | Note |
|---|---|---|
| Operating system | Windows 10 / 11 | Works on Linux and macOS too |
| Python | 3.9 or newer | Developed and tested with 3.11 |
| PyQt6 | 6.5+ | UI plus the audio/video engine (QtMultimedia is included) |
| requests | 2.28+ | HTTP downloading |
| pycryptodome | 3.17+ | Decrypting AES-128 streams |
| imageio-ffmpeg | 0.4.9+ | Ships the ffmpeg binary (for MP4 conversion, optional) |

Around 2 GB of free disk space is enough to get started. Because segments are stored
temporarily before merging, expect to need **roughly twice the size of the video** in
free space while it downloads.

---

## 2. Installing Python (first-time users)

If Python is not installed yet:

1. Download the Windows installer from <https://www.python.org/downloads/>.
2. On the first installer screen, tick **"Add python.exe to PATH"**. Without it the
   commands below will not work.
3. Open a new terminal (PowerShell or CMD) and verify:

```bash
python --version
```

You should see something like `Python 3.11.x`.

**Linux:** Python ships with most distributions. If it doesn't, install it with
`sudo apt install python3 python3-pip` (Debian/Ubuntu) or your package manager. You may
need to type `python3` and `pip3` instead of `python` and `pip`.

**macOS:** `brew install python`, or the macOS installer from python.org.

---

## 3. Installing the app

Open a terminal and run:

```bash
git clone https://github.com/espincom/m3u8_studio.git
```

```bash
cd m3u8_studio
```

```bash
pip install -r requirements.txt
```

If you don't use Git, download the project with the green **Code → Download ZIP** button
on GitHub, extract it, `cd` into that folder and run only the `pip install` command.

On Linux and macOS you may need `pip3` instead of `pip`.

To install the dependencies individually:

```bash
pip install PyQt6 requests pycryptodome imageio-ffmpeg
```

---

## 4. Running

```bash
python m3u8_downloader.py
```

The app starts in **English**. Click the 🇹🇷 flag in the top-right corner to switch to
Turkish; your choice is saved and restored on the next launch.

---

## 5. Usage

### Adding links

1. Copy the video's `.m3u8` link (in your browser: F12 → Network tab → filter for `.m3u8`).
2. Paste it into the input box.
3. **Download Now** starts immediately, **Add to Queue** puts it in line (start it later
   with the ⬇ button on the row).

With the **clipboard watcher** enabled you can skip step 2: a notification slides in as
soon as you copy the link, and you choose from there.

**Bulk Add** lets you paste many links at once, one per line. To set a file name:

```
https://site.com/video1/master.m3u8
https://site.com/video2/index.m3u8 | episode-2.mp4
```

### Settings

| Setting | What it does |
|---|---|
| **Save folder** | Where videos are downloaded. Stored permanently. |
| **Referer** | If the server returns 403: the address of the page playing the video. The Origin header is derived from it. |
| **Cookie** | The Cookie header copied from your browser, for sites that require a login. |
| **Segment connections** | How many segments are fetched at once (default 8). Lower it to 3–4 if the server rate limits you. |
| **Parallel videos** | How many videos download simultaneously (default 2). |
| **Start automatically when added** | Every link added to the queue starts downloading right away. |
| **Convert to MP4 with ffmpeg** | When off, the file is saved as raw `.ts`. |

---

## 6. About ffmpeg

ffmpeg is **not required**. Everything works without it; the output is simply a `.ts`
file (players such as VLC and MPC-HC open it without any trouble).

With ffmpeg you gain two things: the output becomes a real `.mp4`, and preview thumbnails
are extracted more reliably.

The easiest way to install it is already in `requirements.txt`:

```bash
pip install imageio-ffmpeg
```

The program looks for ffmpeg in this order:

1. A path you picked manually in the settings
2. The system `PATH`
3. The binary shipped by the `imageio-ffmpeg` package
4. `ffmpeg` / `ffmpeg.exe` next to the program (or under `ffmpeg/bin/`)

If none is found, the **ffmpeg…** button in the settings panel shows installation help,
where you can choose "Search Again" or "Pick File".

---

## 7. Where files live

| What | Where |
|---|---|
| Downloaded videos | The save folder you chose |
| Diagnostic log | `m3u8_studio.log` in the program folder |
| Segment cache | `m3u8studio_cache` in the system temp folder (Windows: `%TEMP%`, Linux/macOS: `/tmp`) — removed after a successful download; entries older than 3 days are cleaned automatically |
| Settings | Windows: `HKEY_CURRENT_USER\Software\m3u8studio` · Linux: `~/.config/m3u8studio` · macOS: `~/Library/Preferences` |

If you re-add an interrupted download, the segments still in the cache are not fetched
again — it continues where it stopped. This works even when the link is signed and has
changed in the meantime.

The **Show in folder** button on each row works on all three operating systems: Explorer
on Windows and Finder on macOS open with the file selected. On Linux the standard file
manager interface (`org.freedesktop.FileManager1`) is tried first, then Nautilus, Dolphin,
Nemo, Caja, Thunar and PCManFM; if none is available, the containing folder is opened.

---

## 8. Troubleshooting

**I get 403 Forbidden**
Put the address of the page playing the video into the **Referer** field. If needed, copy
the Cookie header from your browser as well.

**The download slowed down or stalled**
Read the text on the row. If the instantaneous speed drops while the *retry* count rises,
the server is throttling you — lower **Segment connections** to 3–4 and **Parallel
videos** to 1. If only the average speed falls while the instantaneous speed stays
steady, nothing is wrong.

**I ended up with a file marked "PARTIAL 73%"**
Some segments of that video are unreachable on the source server. Instead of throwing
away what was downloaded, the program saves it as `video (partial 73%).mp4` once all
retries are exhausted. Refresh the link in your browser and add it again to resume.

**The file is `.ts` instead of `.mp4`**
ffmpeg was not found, or the conversion failed. See section 6.

**There is no sound**
Make sure the four mp3 files (`Pop_app.mp3`, `Download.mp3`, `Downloaded.mp3`,
`Error.mp3`) are present in the `m3u8_studio` folder.

**The program doesn't start at all**
Run it from a terminal and read the error message. Uncaught errors are also recorded in
full detail in `m3u8_studio.log`.

---

## 9. Project layout

```
m3u8_studio/
├── m3u8_downloader.py      Launcher
├── requirements.txt
└── m3u8_studio/
    ├── app.py              Application entry point
    ├── config.py           Settings, logging, ffmpeg discovery
    ├── theme.py            Colors and stylesheet
    ├── i18n.py             Translation catalog (EN / TR)
    ├── hls.py              M3U8 parsing
    ├── downloader.py       Download engine (round-based retries, cooldown)
    ├── cache.py            Segment cache
    ├── thumbnail.py        Preview frame extraction
    ├── widgets.py          Custom-painted UI components
    ├── dialogs.py          Bulk add, clipboard notification
    ├── about.py            Developer page
    ├── models.py           Task model
    ├── mainwindow.py       Main window
    ├── sounds.py           Sound effects
    └── *.mp3               Sound files
```

---

## 10. Disclaimer

This tool is meant for downloading content you have the right to access. Downloading and
redistributing copyrighted material without permission may be illegal in your country.
Use it at your own responsibility.

---

## Contact

For bugs and feedback, please get in touch by mail.

**By espin0**
Gmail: kayhankafali@gmail.com
GitHub: <https://github.com/espincom>

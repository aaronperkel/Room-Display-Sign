# Room Status Display

A lightweight door‑sign system that lets you update a three‑line status message on a Waveshare 4.2" e‑paper display via a simple web interface.

---

## Features

- **Web interface**: Access via any browser on your network to update status lines.
- **Live preview**: See how your message and today's date will appear before sending.
- **E‑paper display**: Instantly pushes to the Waveshare epd4in2 (V2) for ultra‑low‑power always‑on signage.
- **Dynamic date**: Automatically shows the current date on the sign and in the preview.
- **Self‑contained**: Single Flask app; no database required (status persists until reboot).

---

## Requirements

- **Hardware**: Raspberry Pi (GPIO & SPI enabled), Waveshare EPD 4.2" V2 module
- **Software**:
  - Python 3.7+
  - Flask
  - spidev
  - RPi.GPIO
  - Pillow (PIL)
  - waveshare‑epd Python driver

---

## Installation

1. **Clone this repo** to your Pi:
   ```bash
   git clone https://github.com/aaronperkel/room‑status‑display.git
   cd room‑status‑display/display
   ```

2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3‑pip python3‑dev libjpeg‑dev
   pip3 install flask spidev RPi.GPIO pillow waveshare‑epd
   ```

3. **Enable SPI & GPIO** in `raspi‑config` and reboot.

4. **Wire your EPD** according to Waveshare’s docs (SPI pins + power).

---

## Usage

- **Run the server**:
  ```bash
  cd display
  nohup python3 app.py &
  ```
- **Open your browser** to `http://<raspberry‑pi‑ip>:8080`
- **Enter your three status lines**, click **Set Status** → watch it update on the e‑paper!

> **Note:** Status lines are stored in RAM only. To make them persistent, integrate a small file or database write in the `set_status` handler.

---

## Customization

- **Fonts & Layout**: Edit `app.py` to swap `ImageFont.truetype(...)` paths or sizes.
- **Preview & Styles**: Tweak `src/static/styles/custom.css` and the Jinja template in `src/templates/index.html`.
- **Port/Host**: Change `app.run(...)` arguments or deploy under Gunicorn, Docker, or your favorite WSGI.

---

## Project Structure

```
.display/
├── app.py           # Flask application + display logic
├── templates/
│   └── index.html   # Jinja2 web UI
└── static/
    └── styles/
        └── custom.css  # Fresh card‑based styling

.gitignore
README.md
```

---

## License

[MIT License](LICENSE)


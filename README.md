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
  - Python 3.7+
  - See `requirements.txt` for Python package dependencies.
  - `git` for cloning the repository.

---

## Installation

1.  **Clone this repo** to your Pi:
    ```bash
    git clone https://github.com/aaronperkel/room-status-display.git # Replace with the actual repo URL if different
    cd room-status-display
    ```

2.  **Set up a Python virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    sudo apt update
    sudo apt install python3-dev libjpeg-dev # System dependencies for Pillow
    pip install -r requirements.txt
    ```
    *Note: `RPi.GPIO` and `spidev` might require `sudo pip install` or installation via `apt` if not using a virtual environment or if permissions issues arise. Ensure your user is part of the `gpio`, `spi`, and `i2c` groups if necessary (`sudo usermod -a -G gpio,spi,i2c your_username`).*

4.  **Enable SPI & I2C** in `raspi-config` (Interfacing Options) and reboot if you haven't already.

5.  **Wire your EPD** according to Waveshare’s documentation for the 4.2" V2 module (SPI pins + power).

---

## Running the Application

This project uses Gunicorn as a WSGI server and can be managed with systemd for robust background operation.

1.  **Configure the systemd service:**
    *   The provided `deployment/room-status.service` file is a template. You'll need to customize it first.
    *   Edit `deployment/room-status.service` and update the `User`, `Group`, and `WorkingDirectory` to match your setup.
        *   `User`: The user that will run the application (e.g., `pi`).
        *   `Group`: The group for the application (e.g., `www-data` or the same as `User`).
        *   `WorkingDirectory`: The absolute path to the project's root directory (e.g., `/home/pi/room-status-display`).
        *   Ensure the `ExecStart` path to `gunicorn` (e.g., `/home/pi/room-status-display/venv/bin/gunicorn`) is correct for your virtual environment location.

2.  **Install and enable the systemd service:**
    ```bash
    sudo cp deployment/room-status.service /etc/systemd/system/room-status.service
    sudo systemctl daemon-reload
    sudo systemctl enable room-status.service
    sudo systemctl start room-status.service
    ```

3.  **Access the application:**
    Open your browser to `http://<raspberry-pi-ip>:8000` (or the port you configured in the service file if different).

**Managing the Service:**
*   **Check status:** `sudo systemctl status room-status.service`
*   **Stop service:** `sudo systemctl stop room-status.service`
*   **Start service:** `sudo systemctl start room-status.service`
*   **View logs:** `sudo journalctl -u room-status.service -f` (for live logs)

---

## Customization

- **Fonts & Layout**: Edit `app.py` to swap `ImageFont.truetype(...)` paths or sizes.
- **Preview & Styles**: Tweak `src/static/styles/custom.css` and the Jinja template in `src/templates/index.html`.
- **Port/Host**: To change the port or host, modify the `ExecStart` line in the `deployment/room-status.service` file (specifically the `--bind` parameter for Gunicorn) and then run `sudo systemctl daemon-reload` and `sudo systemctl restart room-status.service`.

---

## Project Structure

```
room-status-display/    # Project Root
├── deployment/
│   └── room-status.service # Systemd service file template
├── src/
│   ├── app.py              # Flask application + display logic
│   ├── static/
│   │   ├── styles/
│   │   │   └── custom.css
│   │   └── favicon.ico.example
│   └── templates/
│       └── index.html      # Jinja2 web UI
├── .gitignore
├── README.md
└── requirements.txt        # Python package dependencies
```

---

## License

[MIT License](LICENSE)


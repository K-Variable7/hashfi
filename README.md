# HashFi Sentinel

**HashFi Sentinel** is a security-focused utility that maintains an ephemeral, cryptographically hashed session. It monitors system "threat levels" in real-time and automatically "burns" (wipes) the session if a threat threshold is breached.

## Features

*   **Ephemeral Session Hashing**: Generates a unique SHA-256 session key.
*   **Live Threat Monitor**: Monitors CPU and Network activity to calculate a Threat Score.
*   **Auto-Burn Protocol**: Automatically wipes the session key from memory if the Threat Score exceeds 90%.
*   **CLI Dashboard**: A futuristic terminal interface built with `rich`.
*   **Web Interface**: A lightweight, cyber-themed browser dashboard with a panic button.

## Installation

1.  Create a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### CLI Mode
Run the terminal sentinel:

```bash
python -m hashfi.main
```
*Press `p` at any time to trigger a PANIC BURN.*

### Web Mode
Run the web interface:

```bash
python -m hashfi.web.app
```
Open your browser to `http://localhost:8000`.

## Simulation

The system sensor currently includes a small amount of random "jitter" to simulate fluctuating threat levels for demonstration purposes.

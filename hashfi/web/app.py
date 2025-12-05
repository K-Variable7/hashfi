from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import threading
import time
import os
from datetime import datetime
import psutil
from faker import Faker
import subprocess
from hashfi.core.session import SessionManager
from hashfi.core.monitor import ThreatMonitor
from hashfi.sensors.system_sensor import SystemSensor
from hashfi.sensors.file_sensor import FileIntegritySensor
from hashfi.core.stegano import encode_lsb, decode_lsb
from hashfi.core.shredder import secure_shred

app = FastAPI()
fake = Faker()


# ...existing code...


# Spread the Word API (must be after app = FastAPI())
@app.post("/api/tools/spread")
async def spread_the_word(background_tasks: BackgroundTasks):
    def run_spread():
        try:
            result = subprocess.run(
                ["python3", os.path.join(project_root, "hashfi_spread_manual.py")],
                capture_output=True,
                text=True,
            )
            print(result.stdout)
        except Exception as e:
            print(f"Spread script error: {e}")

    background_tasks.add_task(run_spread)
    return {
        "message": "Spread script started! Check your terminal for manual post instructions."
    }


class ShredRequest(BaseModel):
    file_path: str


# Secure File Shredder API
@app.post("/api/tools/shred")
async def shred_file(request: ShredRequest):
    record_activity()
    if not session_manager.is_active:
        raise HTTPException(status_code=400, detail="Session burned")
    file_path = request.file_path
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    success = secure_shred(file_path)
    if success:
        add_log(f"File '{file_path}' securely shredded.", "CRITICAL")
        return {"status": "shredded"}
    else:
        raise HTTPException(status_code=500, detail="Failed to shred file")


class SecretItem(BaseModel):
    name: str
    content: str


class IdentityRequest(BaseModel):
    service_name: str


# Get absolute paths for static and templates
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")
project_root = os.path.dirname(os.path.dirname(base_dir))

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


# Global State
session_manager = SessionManager()
monitor = ThreatMonitor(threshold=0.9)
monitor.add_sensor(SystemSensor())
# Monitor the project root for unauthorized changes
monitor.add_sensor(FileIntegritySensor(target_dir=project_root))

logs = []

# Dead Man's Switch: triggers auto-panic after inactivity
DEADMAN_TIMEOUT = 300  # seconds (5 minutes)
last_activity = time.time()


def update_activity():
    global last_activity
    last_activity = time.time()


def deadman_loop():
    global last_activity
    while True:
        if session_manager.is_active:
            if time.time() - last_activity > DEADMAN_TIMEOUT:
                add_log(
                    "Dead Man's Switch: Inactivity detected. Auto-panic triggered.",
                    "CRITICAL",
                )
                session_manager.burn_session()
        time.sleep(5)


def add_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    logs.append({"time": timestamp, "level": level, "message": message})
    if len(logs) > 50:
        logs.pop(0)


def record_activity():
    update_activity()


# Background Monitor Loop
def monitor_loop():
    while True:
        if session_manager.is_active:
            monitor.check_threats()
            # Log significant threat changes or periodic status
            if monitor.current_threat_level > 0.5:
                add_log(
                    f"Elevated Threat Level: {monitor.current_threat_level:.2f}",
                    "WARNING",
                )
        time.sleep(1)


# Start monitor in background thread

monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
monitor_thread.start()
deadman_thread = threading.Thread(target=deadman_loop, daemon=True)
deadman_thread.start()


# Callback for auto-burn
def on_breach():
    add_log("THREAT THRESHOLD BREACHED! AUTO-BURN INITIATED.", "CRITICAL")
    session_manager.burn_session()


monitor.on_threshold_breach = on_breach


@app.on_event("startup")
async def startup_event():
    add_log("System Startup. Initializing Session...", "INFO")
    session_manager.start_session()
    add_log(f"Session Active. Hash: {session_manager.get_hash()[:8]}...", "INFO")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/status")
async def get_status():
    record_activity()
    # Cool Feature: Network Connection Count
    net_connections = len(psutil.net_connections())

    return {
        "is_active": session_manager.is_active,
        "hash": session_manager.get_hash(),
        "sandbox": session_manager.get_sandbox(),
        "threat_level": monitor.current_threat_level,
        "net_connections": net_connections,
    }


@app.get("/api/logs")
async def get_logs():
    record_activity()
    return logs


@app.get("/api/vault")
async def list_secrets():
    record_activity()
    return {"secrets": session_manager.get_secrets_list()}


@app.post("/api/vault")
async def store_secret(item: SecretItem):
    record_activity()
    if not session_manager.is_active:
        raise HTTPException(status_code=400, detail="Session burned")

    success = session_manager.store_secret(item.name, item.content)
    if success:
        add_log(f"Secret '{item.name}' encrypted and stored in vault.", "INFO")
        return {"status": "stored"}
    else:
        raise HTTPException(status_code=500, detail="Failed to store secret")


@app.get("/api/vault/{name}")
async def retrieve_secret(name: str):
    record_activity()
    content = session_manager.retrieve_secret(name)
    if content is None:
        raise HTTPException(
            status_code=404, detail="Secret not found or session burned"
        )

    add_log(f"Secret '{name}' retrieved and decrypted.", "WARNING")
    return {"name": name, "content": content}


@app.post("/api/identity/generate")
async def generate_identity(item: IdentityRequest):
    record_activity()
    if not session_manager.is_active:
        raise HTTPException(status_code=400, detail="Session burned")

    credential = session_manager.derive_service_credential(item.service_name)
    if credential:
        add_log(f"Generated Ghost Credential for '{item.service_name}'", "INFO")
        return {"service": item.service_name, "credential": credential}
    else:
        raise HTTPException(status_code=500, detail="Failed to generate credential")


@app.post("/api/panic")
async def trigger_panic():
    record_activity()
    add_log("MANUAL PANIC TRIGGERED BY USER", "CRITICAL")
    session_manager.burn_session()
    return {"status": "burned"}


@app.post("/api/regenerate")
async def regenerate_session():
    record_activity()
    session_manager.regenerate_session()
    add_log("Session Regenerated manually.", "INFO")
    return {"status": "regenerated", "hash": session_manager.get_hash()}


@app.get("/api/persona/generate")
async def generate_persona():
    record_activity()
    """Generates a fake persona."""
    profile = fake.profile()
    # Ensure birthdate is a string
    if "birthdate" in profile:
        try:
            profile["birthdate"] = profile["birthdate"].strftime("%Y-%m-%d")
        except Exception:
            profile["birthdate"] = str(profile["birthdate"])
    # Ensure current_location is serializable
    if "current_location" in profile:
        loc = profile["current_location"]
        if isinstance(loc, (list, tuple)) and len(loc) == 2:
            profile["current_location"] = [str(loc[0]), str(loc[1])]
        else:
            profile["current_location"] = str(loc)
    add_log("Generated Fake Persona", "INFO")
    return profile


@app.post("/api/tools/stegano/encode")
async def stegano_encode(text: str = Form(...), file: UploadFile = File(...)):
    record_activity()
    """Encodes text into an uploaded image."""
    try:
        output_image = encode_lsb(file.file, text)
        return StreamingResponse(output_image, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/stegano/decode")
async def stegano_decode(file: UploadFile = File(...)):
    record_activity()
    """Decodes text from an uploaded image."""
    try:
        text = decode_lsb(file.file)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start():
    uvicorn.run("hashfi.web.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()

import subprocess, os, requests, json, sqlite3, threading, re, time, random
from flask import Flask, request as freq
from datetime import datetime

START_TIME = time.time()
app = Flask(__name__)

# ── API Keys (rotated on 429) ─────────────────────────────────
# REPLACE THESE WITH YOUR OWN GEMINI API KEYS
API_KEYS = [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2",
]

# ── Models (rotated on rate limit) ───────────────────────────
MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
]

# ── Paths (Windows) ───────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WACLI    = os.path.join(BASE_DIR, "wacli.exe")
DB_PATH  = os.path.join(BASE_DIR, "memory.db")

COMFY_API_URL    = "http://127.0.0.1:8188"
# REPLACE WITH YOUR COMFYUI OUTPUT DIRECTORY
COMFY_OUTPUT_DIR = r"C:\Path\To\Your\ComfyUI\output" 

# ── Personality ───────────────────────────────────────────────
SYSTEM_RULES = (
    "Aap ek bahut vinammra assistant ho. "
    "Hamesha aap, aapko, aapka use karo. "
    "Hindi aur English mix mein baat karo. "
    "Maximum 15 words mein reply do. "
    "Bahut polite aur gentle raho. "
    "STRICT RULE: Reply mein kisi ka naam BILKUL mat use karo. "
    "Stored facts sirf tab use karo jab directly poocha jaye."
)

key_idx   = [0]
model_idx = [0]


# ── Memory DB ─────────────────────────────────────────────────

def init_db():
    c = sqlite3.connect(DB_PATH)
    c.execute("CREATE TABLE IF NOT EXISTS memory (sender TEXT, fact TEXT, ts TEXT)")
    c.commit()
    c.close()


def save_fact(sender, fact):
    c = sqlite3.connect(DB_PATH)
    c.execute("INSERT INTO memory VALUES (?,?,?)",
              (sender, fact, datetime.now().isoformat()))
    c.commit()
    c.close()


def get_facts(sender):
    c = sqlite3.connect(DB_PATH)
    rows = c.execute(
        "SELECT fact FROM memory WHERE sender=? ORDER BY ts DESC LIMIT 20",
        (sender,)
    ).fetchall()
    c.close()
    return [r[0] for r in rows]


def extract_facts_bg(sender, text):
    try:
        key = API_KEYS[key_idx[0]]
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               "gemini-2.0-flash-lite:generateContent?key=" + key)
        prompt = ('Extract personal facts from: "' + text + '". '
                  'Return JSON array like ["likes coffee"]. Return [] if none.')
        r   = requests.post(url,
                            json={"contents": [{"parts": [{"text": prompt}]}]},
                            timeout=10)
        raw = (r.json().get("candidates", [{}])[0]
                       .get("content", {})
                       .get("parts", [{}])[0]
                       .get("text", "[]"))
        m = re.search(r'\[.*?\]', raw, re.DOTALL)
        if m:
            for f in json.loads(m.group()):
                if f and len(str(f)) > 3:
                    save_fact(sender, str(f))
                    print("[mem] " + sender + ": " + str(f), flush=True)
    except Exception as e:
        print("[facts_err] " + str(e), flush=True)


# ── Gemini with key + model rotation ─────────────────────────

def ask_gemini(text, name, facts=None):
    ctx = SYSTEM_RULES
    if name:
        ctx += "\nSender ka WhatsApp naam: " + name
    if facts:
        ctx += "\nIs person ke baare mein:\n- " + "\n- ".join(facts)

    total = len(API_KEYS) * len(MODELS)
    for attempt in range(total):
        ki    = (key_idx[0]   + attempt // len(MODELS)) % len(API_KEYS)
        mi    = (model_idx[0] + attempt)                % len(MODELS)
        key   = API_KEYS[ki]
        model = MODELS[mi]
        try:
            url  = ("https://generativelanguage.googleapis.com/v1beta/models/"
                    + model + ":generateContent?key=" + key)
            body = {
                "system_instruction": {"parts": [{"text": ctx}]},
                "contents":           [{"parts": [{"text": text}]}],
            }
            r    = requests.post(url, json=body, timeout=15)
            resp = r.json()
            if "candidates" in resp:
                key_idx[0]   = ki
                model_idx[0] = mi
                print("[ok] key=" + str(ki) + " model=" + model, flush=True)
                return resp["candidates"][0]["content"]["parts"][0]["text"]
            code = resp.get("error", {}).get("code", 0)
            if code in (429, 403):
                print("[skip] key=" + str(ki) + " model=" + model, flush=True)
                continue
            print("[err] " + str(resp.get("error", "")), flush=True)
        except Exception as e:
            print("[ex] " + str(e), flush=True)
    return "Maafi chahta hoon, abhi thodi takleef hai. Thodi der mein try karein."


# ── Send message ──────────────────────────────────────────────

def send_text(to, msg):
    r = subprocess.run(
        [WACLI, "send", "text", "--to", to, "--message", msg],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print("[send_err] " + r.stderr[:100], flush=True)

def send_file(to, filepath):
    r = subprocess.run(
        [WACLI, "send", "file", "--to", to, "--file", filepath],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print("[send_err] " + r.stderr[:100], flush=True)


# ── ComfyUI Integration ───────────────────────────────────────

COMFY_PROC = None  # track the running ComfyUI process

def start_comfy():
    """Start ComfyUI server and wait until it's ready."""
    global COMFY_PROC
    if COMFY_PROC and COMFY_PROC.poll() is None:
        print("[comfy] Already running", flush=True)
        return True
    print("[comfy] Starting ComfyUI...", flush=True)
    # REPLACE WITH YOUR COMFYUI CWD PATH
    COMFY_PROC = subprocess.Popen(
        ["python", "main.py", "--cpu", "--use-split-cross-attention", "--disable-smart-memory"],
        cwd=r"C:\Path\To\Your\ComfyUI",
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    # Wait up to 60s for ComfyUI to be ready
    for _ in range(60):
        time.sleep(1)
        try:
            r = requests.get(f"{COMFY_API_URL}/system_stats", timeout=2)
            if r.status_code == 200:
                print("[comfy] Server ready!", flush=True)
                return True
        except:
            pass
    print("[comfy] Server failed to start", flush=True)
    return False

def stop_comfy():
    """Kill ComfyUI to free RAM after generation."""
    global COMFY_PROC
    if COMFY_PROC and COMFY_PROC.poll() is None:
        COMFY_PROC.terminate()
        try:
            COMFY_PROC.wait(timeout=5)
        except:
            COMFY_PROC.kill()
        print("[comfy] Server stopped. RAM freed.", flush=True)
    COMFY_PROC = None

def generate_and_send_image(chat, prompt_text):
    print(f"[comfy] Generating image for: {prompt_text}", flush=True)
    send_text(chat, "Aapki image generate ho rahi hai, kripya thodi der pratiksha karein...")

    if not start_comfy():
        send_text(chat, "Maafi chahta hoon, image server shuru nahi ho saka.")
        return

    prompt_workflow = {
      "3": {
        "inputs": {
          "seed": random.randint(1, 100000000000000),
          "steps": 6,
          "cfg": 7.5,
          "sampler_name": "euler",
          "scheduler": "normal",
          "denoise": 1,
          "model": ["4", 0],
          "positive": ["6", 0],
          "negative": ["7", 0],
          "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
      },
      "4": {
        "inputs": {
          "ckpt_name": "DreamShaper_8_pruned.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
      },
      "5": {
        "inputs": {
          "width": 512,
          "height": 512,
          "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
      },
      "6": {
        "inputs": {
          "text": prompt_text,
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "7": {
        "inputs": {
          "text": "asian, japanese, anime, manga, cartoon, illustration, 3d, render, painting, text, watermark, ugly, bad anatomy, bad hands, missing fingers",
          "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
      },
      "8": {
        "inputs": {
          "samples": ["3", 0],
          "vae": ["4", 2]
        },
        "class_type": "VAEDecode"
      },
      "9": {
        "inputs": {
          "filename_prefix": "wacli_bot",
          "images": ["8", 0]
        },
        "class_type": "SaveImage"
      }
    }

    try:
        r = requests.post(f"{COMFY_API_URL}/prompt", json={"prompt": prompt_workflow})
        r.raise_for_status()
        prompt_id = r.json()["prompt_id"]

        for _ in range(150):
            time.sleep(3)
            hist_req = requests.get(f"{COMFY_API_URL}/history/{prompt_id}")
            if hist_req.status_code == 200:
                history = hist_req.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        if "images" in node_output:
                            filename = node_output["images"][0]["filename"]
                            filepath = os.path.join(COMFY_OUTPUT_DIR, filename)
                            print(f"[comfy] Image saved to {filepath}", flush=True)
                            send_file(chat, filepath)
                            stop_comfy()  
                            return
        print("[comfy] Timeout waiting for image", flush=True)
        send_text(chat, "Maaf karna, image generate hone mein samay lag raha hai.")
    except requests.exceptions.ConnectionError:
        print("[comfy_err] ComfyUI is not running", flush=True)
        send_text(chat, "Maafi chahta hoon, mera image server abhi band hai.")
    except Exception as e:
        print(f"[comfy_err] {str(e)}", flush=True)
        send_text(chat, "Maafi chahta hoon, image generate nahi ho payi.")
    finally:
        stop_comfy()  


# ── Webhook ───────────────────────────────────────────────────

@app.route('/webhook', methods=['POST'])
def handle():
    data    = freq.get_json(force=True, silent=True) or {}
    text    = data.get('Text', '')
    chat    = data.get('Chat', '')
    from_me = data.get('FromMe', False)
    sender  = data.get('Sender') or chat
    name    = data.get('PushName') or data.get('Notify') or ''
    
    try:
        msg_ts = float(data.get('Timestamp', 0))
    except (ValueError, TypeError):
        msg_ts = 0

    print("[msg] name=" + name + " from_me=" + str(from_me) + " text=" + repr(text), flush=True)

    if msg_ts and msg_ts < START_TIME:
        print("[skip] Ignored historical message", flush=True)
        return "OK", 200

    if from_me or not text or "status@broadcast" in chat or "newsletter" in chat:
        return "OK", 200

    # ComfyUI Image Generation Command
    if text.lower().startswith("@imagine "):
        prompt_text = text[9:].strip()
        if prompt_text:
            threading.Thread(target=generate_and_send_image, args=(chat, prompt_text), daemon=True).start()
        else:
            send_text(chat, "Kripya @imagine ke baad kuch likhein.")
        return "OK", 200

    threading.Thread(target=extract_facts_bg, args=(sender, text), daemon=True).start()

    try:
        facts = get_facts(sender)
        reply = ask_gemini(text, name, facts)
        # Prevent the bot from calling the owner's name
        for banned in ["YOUR_NAME", "your_name"]:
            reply = reply.replace(banned, "aap")
        print("[reply] " + reply, flush=True)
        send_text(chat, reply)
    except Exception as e:
        print("[ERROR] " + str(e), flush=True)

    return "OK", 200

if __name__ == '__main__':
    init_db()
    print("[bot] Windows mode. Keys=" + str(len(API_KEYS)) + " Models=" + str(len(MODELS)), flush=True)
    app.run(host='0.0.0.0', port=5000)

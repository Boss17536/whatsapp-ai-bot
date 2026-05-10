# WhatsApp AI Bot (with Gemini & ComfyUI)

A complete end-to-end tutorial and setup for creating an AI-powered WhatsApp Bot. This bot integrates Google's Gemini AI for smart, conversational replies, and ComfyUI (Stable Diffusion) to generate and send images directly to WhatsApp!

## Features 🚀
- **AI Chatbot**: Uses Google's Gemini Models for fast and smart replies.
- **Image Generation**: Generates images locally using ComfyUI (triggered via `@imagine <prompt>`).
- **Memory System**: Remembers user facts in a local SQLite database.
- **Cross-Platform**: Run on Windows (via Batch) or Android (via Termux).
- **API Rotation**: Built-in API key rotation to handle rate-limiting.

## Prerequisites 🛠️
1. [Python 3.10+](https://www.python.org/downloads/) installed.
2. [WACLI (WhatsApp CLI)](https://github.com/openclaw/wacli) - You'll need the executable.
3. [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (Optional) - Required only if you want image generation features.

## Setup Instructions (Windows) 💻

1. **Clone this repository** (or download as ZIP).
2. **Download WACLI**: Download `wacli.exe` from their GitHub and place it in the same directory as the scripts.
3. **Configure the Bot**:
   - Open `server_windows.py`.
   - Replace the `API_KEYS` list with your actual Google Gemini API keys.
   - Update the `COMFY_OUTPUT_DIR` to point to your ComfyUI output folder.
4. **Link WACLI**: Open a terminal, run `./wacli.exe auth` and scan the QR code with your WhatsApp.
5. **Run**: Simply double-click `start_bot.bat`. It will automatically install dependencies, start the webhook server, and begin listening for messages!

## Setup Instructions (Android / Termux) 📱
If you want the bot to run 24/7 on an old Android phone using Termux:

1. Install Termux and open it.
2. Upload `termux_setup.sh` to your phone or curl it directly.
3. Run the setup: `bash termux_setup.sh`.
4. It will install Python, download the ARM64 WACLI, and set up an auto-start script in your `.bashrc`.
5. Run `cd ~/wacli && ./wacli auth` to link your WhatsApp.

## How it Works 🧠
- `wacli sync --follow` listens to incoming WhatsApp messages and forwards them to a local webhook.
- `server_windows.py` receives the webhook (`POST /webhook`), parses the text, and checks if it's a command (`@imagine`) or normal text.
- If normal text, it extracts facts using a background thread and asks Gemini for a reply.
- If `@imagine`, it spins up the ComfyUI process (in CPU/Split memory mode to save RAM), triggers the workflow via API, waits for the image, sends the image to WhatsApp using WACLI, and then kills ComfyUI to free memory.

## Disclaimer ⚠️
Do **NOT** share your API keys or `memory.db` file. Add them to your `.gitignore` before pushing to any public repository.

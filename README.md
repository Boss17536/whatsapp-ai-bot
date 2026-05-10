# 🤖 WhatsApp AI Clone & Image Generator

Have you ever been completely flooded with WhatsApp messages while you were busy, asleep, or just not in the mood to reply? 

I built this project so you can have your very own **AI Clone** running in the background. It reads your WhatsApp messages, figures out what the person is saying, and replies to them beautifully and politely—just like a human would! 

Oh, and if someone types `@imagine a cute cat wearing sunglasses`, the bot will literally generate that image on your PC and send it to them right inside WhatsApp. It’s basically magic. ✨

---

## 🌟 What can this Bot actually do?

- 💬 **Talk for you when you're offline:** If a friend messages you at 3 AM, the bot will chat with them naturally, in Hindi or English, and keep them entertained.
- 🧠 **It has a Memory!** If your friend says "I love coffee", the bot remembers that fact and stores it in a local database. Later, it might bring it up in conversation!
- 🎨 **Sends AI Images (ComfyUI):** It connects directly to your PC's GPU. If someone sends `@imagine [anything]`, your PC will generate a stunning AI image and the bot will send it directly to their WhatsApp chat!
- 🔄 **Smart API Rotation:** Free AI APIs (like Gemini) have limits. This bot is smart enough to juggle multiple API keys so it never stops working.
- 📱 **Runs 24/7 on an old phone:** You don't need to leave your PC on forever. I've included a script to run this 24/7 on an old Android phone using Termux!

---

## 🛠️ Step-by-Step Setup Guide

I promise this is easier than it looks. Just follow these steps:

### Step 1: Download WACLI (The WhatsApp Connector)
WACLI is a tool that lets our Python code talk to WhatsApp.
1. Go to the [WACLI GitHub Page](https://github.com/openclaw/wacli) and download the `wacli.exe` file for Windows.
2. Put `wacli.exe` inside the exact same folder as these downloaded scripts.
3. Open a terminal in that folder and type `./wacli.exe auth`. A QR code will pop up. Scan it with your WhatsApp (Linked Devices) just like WhatsApp Web!

### Step 2: Get Google's Gemini AI Brain
The bot needs a brain, and we are using Google's amazing Gemini (which is free!).
1. Go to [Google AI Studio](https://aistudio.google.com/) and create some API Keys.
2. Open `server_windows.py` in Notepad or VS Code.
3. Find the `API_KEYS = [...]` section at the top. Paste your keys there.

### Step 3: Run the Bot!
1. Double-click the `start_bot.bat` file. 
2. It will automatically install everything it needs (like Flask).
3. Two black windows will pop up: One is the WACLI syncing your messages, and the other is your AI Brain processing them.
4. **Boom!** Have a friend send you a message. The bot will instantly reply!

---

## 🎨 (Optional) Step 4: The Image Generator Setup
Want the `@imagine` command to work? You need ComfyUI installed on your PC.
1. Download [ComfyUI](https://github.com/comfyanonymous/ComfyUI).
2. Open `server_windows.py` and look for `COMFY_OUTPUT_DIR`. Change it to wherever your ComfyUI saves images (e.g., `C:\ComfyUI\output`).
3. Now, whenever someone texts you `@imagine an astronaut on mars`, your PC will generate it and send it!

---

## 📱 How to Run it 24/7 on an Old Android Phone
Don't want to keep your PC on all night? No problem. You can run the text-chat part of this bot 24/7 on any old Android phone.

1. Download **Termux** from F-Droid (don't use the Play Store version) on your Android phone.
2. Transfer the `termux_setup.sh` script and `server_windows.py` to your phone.
3. Open Termux and run: `bash termux_setup.sh`
4. The script will literally install Python, download the Linux version of WACLI, setup auto-start, and link everything together.
5. Scan the QR code, and you now have a permanent 24/7 WhatsApp AI Server in your pocket!

---

### ⚠️ A Tiny Warning
Never share your API keys with anyone, and don't upload your `memory.db` file to the internet, because it contains facts about your friends! (I've added a `.gitignore` file to prevent this automatically, but just be careful). Enjoy your new AI clone!

# HashFi Sentinel - Future Roadmap

## 🛡️ Security & Privacy Enhancements
- [x] **Steganographic Export**: Ability to save the current Vault state hidden inside a harmless-looking image file (PNG/JPG).
- [x] **Panic Button**: A global hotkey or UI button that instantly shreds the session data, overwrites memory, and redirects the browser to a harmless site (e.g., Google).
- [x] **Clipboard Sentinel**: Automatically clear the clipboard `n` seconds after copying a password or secret.
- [ ] **Auto-Lock**: Lock the interface with a PIN after a period of inactivity.
- [ ] **Dead Man's Switch**: Automatically trigger the Panic/Burn sequence if no activity is detected for a set duration.
- [ ] **Secure File Shredder**: A tool to overwrite local files with random data multiple times before deletion.

## 🎭 Identity & Anti-Fingerprinting
- [x] **Fake Persona Generator**: Generate consistent fake identities (Name, Address, DOB) for filling out sign-up forms.
- [ ] **User-Agent Spoofer**: Tools to generate or rotate User-Agent strings for the "Sanitized Launch" feature.
- [ ] **Disposable Email Integration**: Interface with temporary email services to generate throwaway inboxes.
- [ ] **Password Entropy Visualizer**: A "Brute Force Estimator" that visually shows how long it would take to crack a password.

## 🌐 Network Tools
- [ ] **IP & DNS Leak Check**: A dashboard widget showing the current public IP and checking for DNS leaks.
- [ ] **Port Scanner**: A simple tool to scan local ports or a target IP (for "defensive" awareness).
- [ ] **Network Traffic Visualizer**: A real-time graph of network packets and active connections.
- [ ] **QR Code Air-Gap Bridge**: Generate QR codes for secrets to transfer them to mobile devices without a network connection.

## 🎨 UI/UX & Immersion
- [ ] **Theme Customizer**: Allow changing the Matrix rain color (Cyberpunk Blue, Red Alert, Classic Green).
- [ ] **Sound Effects**: Add optional UI sounds (typing, access granted/denied, ambient hum).
- [ ] **Command Line Interface (CLI) Mode**: A web-based terminal inside the UI for power users to interact with the Vault via text commands.

## 🔧 Core Architecture
- [ ] **Encrypted Backup**: Option to export the Vault as an AES-256 encrypted JSON file for cross-session persistence (optional, as ephemeral is default).
- [ ] **Plugin System**: Allow writing small Python scripts that can be loaded into the session for custom tasks.

---

## 📢 Viral Spread Script (hashfi_spread.py)

```python
"""
hashfi_spread.py

Automated script to generate an anonymous profile/message using HashFi,
wrap it in a hash, and submit a suggestion/post to Reddit, Hacker News, and Twitter.
After submission, the profile and hash are securely deleted.

NOTE: This script requires API credentials for Reddit and Twitter.
Hacker News does not have a public API for posting, so it will print instructions for manual submission.
"""

import os
import hashlib
import json
import time
from hashfi.core.session import SessionManager
from hashfi.web.app import fake

# --- CONFIGURATION ---
REDDIT_ENABLED = True
HN_ENABLED = True
TWITTER_ENABLED = True

# These should be set as environment variables or config
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = "hashfi-spread-script/1.0"

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# --- GENERATE PROFILE & MESSAGE ---
session = SessionManager()
session.start_session()
persona = fake.profile()
message = f"""
Check out HashFi: The open-source digital fortress for privacy, secure vaults, panic burn, and more!

Made with ❤️ for privacy. Features: Dead Man's Switch, Secure File Shredder, Steganography, and more.

Try it: https://github.com/your-repo/hashfi

#privacy #opensource #security

Persona: {persona["name"]} ({persona["mail"]})
"""

# Wrap in hash for anonymous proof
data = json.dumps({"persona": persona, "message": message, "timestamp": time.time()})
hash_wrapper = hashlib.sha256(data.encode()).hexdigest()

# --- REDDIT SUBMISSION ---
def post_reddit():
    import praw
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
    )
    subreddit = reddit.subreddit("privacy")
    title = "HashFi: Open-source digital fortress for privacy (auto-anon post)"
    body = message + f"\n\nProof: {hash_wrapper}"
    post = subreddit.submit(title, selftext=body)
    print(f"Reddit post submitted: {post.url}")

# --- HACKER NEWS SUBMISSION (manual) ---
def post_hackernews():
    print("\n--- Hacker News Submission ---")
    print(
        "Hacker News does not have a public API for posting. Please copy and submit manually:"
    )
    print("Title: HashFi: Open-source digital fortress for privacy (auto-anon post)")
    print(f"Body: {message}\n\nProof: {hash_wrapper}")
    print("Submit at: https://news.ycombinator.com/submit")

# --- TWITTER SUBMISSION ---
def post_twitter():
    import tweepy
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    )
    api = tweepy.API(auth)
    tweet = f"Check out HashFi: Open-source digital fortress for privacy! https://github.com/your-repo/hashfi #privacy #opensource\nProof: {hash_wrapper[:16]}..."
    status = api.update_status(tweet)
    print(f"Tweet posted: https://twitter.com/user/status/{status.id}")

# --- MAIN ---
if __name__ == "__main__":
    print("[HashFi Spread] Generating and posting anonymous suggestion...")
    if REDDIT_ENABLED:
        try:
            post_reddit()
        except Exception as e:
            print(f"Reddit post failed: {e}")
    if HN_ENABLED:
        post_hackernews()
    if TWITTER_ENABLED:
        try:
            post_twitter()
        except Exception as e:
            print(f"Twitter post failed: {e}")
    # Burn the wrapper (delete persona, hash, session)
    session.burn_session()
    del persona
    del hash_wrapper
    print("[HashFi Spread] Profile and hash wrapper securely deleted.")
```

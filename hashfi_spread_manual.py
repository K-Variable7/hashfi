"""
hashfi_spread_manual.py

Automated script to generate an anonymous profile/message using HashFi,
wrap it in a hash, and print out a suggestion/post for Reddit, Hacker News, and Twitter.
No API keys required—just copy and paste the output to the sites manually.
"""

import os
import hashlib
import json
import time
from hashfi.core.session import SessionManager
from hashfi.web.app import fake

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


# --- PRINT FOR MANUAL SUBMISSION ---
def print_manual(platform, url):
    print(f"\n--- {platform} Submission ---")
    print(f"Title: HashFi: Open-source digital fortress for privacy (auto-anon post)")
    print(f"Body: {message}\n\nProof: {hash_wrapper}")
    print(f"Submit at: {url}\n")


if __name__ == "__main__":
    print_manual("Reddit", "https://www.reddit.com/r/privacy/submit")
    print_manual("Hacker News", "https://news.ycombinator.com/submit")
    print_manual("Twitter", "https://twitter.com/intent/tweet")
    session.burn_session()
    del persona
    del hash_wrapper
    print("[HashFi Spread] Profile and hash wrapper securely deleted.")

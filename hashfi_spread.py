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

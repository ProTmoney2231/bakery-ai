import os, re, sys
from dotenv import load_dotenv, find_dotenv, set_key, unset_key
from openai import OpenAI

def mask(k: str) -> str:
    return (k[:6] + "..." + k[-4:]) if k and len(k) >= 12 else "***"

def normalize(k: str) -> str:
    if k is None:
        return ""
    k = k.strip().strip('"').strip("'")
    return k

def looks_valid(k: str) -> bool:
    if not k: return False
    if any(ch.isspace() for ch in k): return False      # no spaces/newlines
    if not k.startswith("sk-"): return False            # OpenAI keys start with sk-
    return len(k) >= 20

def write_env(key: str):
    env_path = find_dotenv(usecwd=True)
    if not env_path:
        env_path = ".env"
        open(env_path, "a").close()
    set_key(env_path, "OPENAI_API_KEY", key)
    # If user had the wrong var name, remove it
    try:
        unset_key(env_path, "OPEN_API_KEY")
    except Exception:
        pass
    print(f"🔑 Wrote OPENAI_API_KEY to {env_path} ({mask(key)})")

def test_key(key: str) -> bool:
    try:
        client = OpenAI(api_key=key)
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":"Hello! Say 'pong'"}],
            max_tokens=5,
            temperature=0
        )
        msg = r.choices[0].message.content.strip()
        print("✅ API request succeeded. Model replied:", msg)
        return True
    except Exception as e:
        print("❌ API request failed:", str(e))
        return False

def main():
    load_dotenv(override=True)
    # Handle common mistake: OPEN_API_KEY vs OPENAI_API_KEY
    env_key = os.getenv("OPENAI_API_KEY")
    wrong_key = os.getenv("OPEN_API_KEY")

    if not env_key and wrong_key:
        print("⚠️ Found OPEN_API_KEY (wrong name). Fixing to OPENAI_API_KEY...")
        env_key = wrong_key

    env_key = normalize(env_key)

    if not looks_valid(env_key):
        print("⚠️ No valid OPENAI_API_KEY found in .env.")
        print("Paste your OpenAI key now (it starts with 'sk-'). It will be saved to .env:")
        try:
            env_key = normalize(input("> ").strip())
        except EOFError:
            print("No input provided. Exiting.")
            sys.exit(1)

    if not looks_valid(env_key):
        print("❌ That doesn't look like a valid key. Make sure it starts with 'sk-' and has no spaces/newlines.")
        sys.exit(1)

    write_env(env_key)

    print("🔍 Testing the key with a real API call...")
    ok = test_key(env_key)
    if not ok:
        print("\nIf this keeps failing, double-check:")
        print("• The key is current and active in your OpenAI account")
        print("• Billing is set up on the account")
        print("• There are no copy/paste line breaks or hidden characters")
        sys.exit(2)

    print("🎉 All set. You can restart your FastAPI server now.")
    sys.exit(0)

if __name__ == "__main__":
    main()

import os

# Simple .env loader (expects lines like KEY=VALUE)
def load_env(path):
    env = {}
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

env_vars = load_env(os.path.join(os.path.dirname(__file__), ".env"))
api_key = env_vars.get("SARVAM_API_KEY") or os.getenv("SARVAM_API_KEY")
if not api_key:
    raise RuntimeError("SARVAM_API_KEY not set in .env or environment")

from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key=api_key)

response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[{"role": "user", "content": "Hello, Sarvam!"}]
)

print(response.choices[0].message.content)


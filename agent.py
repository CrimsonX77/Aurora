import os
from pathlib import Path

def _load_dotenv(path: str = ".env") -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    # If file contains KEY=VALUE lines, parse them. Otherwise treat whole file as the API key.
    result = {}
    if "=" in text:
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            result[k.strip()] = v
        return result
    # Single-line file with just the key
    result["MISTRAL_API_KEY"] = text
    return result

# Load .env into environment only if variables are missing
for k, v in _load_dotenv(".env").items():
    os.environ.setdefault(k, v)

try:
    from mistralai import Mistral
except Exception as _err:
    Mistral = None
    _import_error = _err

api_key = os.environ.get("MISTRAL_API_KEY")
if api_key is None:
    raise RuntimeError("Environment variable MISTRAL_API_KEY is not set. Add it to your environment or put it into .env")

if Mistral is None:
    raise ImportError("Could not import 'mistralai'. Install it with: pip install mistralai") from _import_error

client = Mistral(api_key=api_key)

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import json

def _start_conversation(client, agent_id, inputs):
    return client.beta.conversations.start(agent_id=agent_id, inputs=inputs)

try:
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(_start_conversation, client, "API-<API_KEY>", "Hello there!")
        raw_response = fut.result(timeout=15)
except FutureTimeout:
    raise RuntimeError("Conversation request timed out (15s)")

# Try to convert the SDK response into a plain dict for easier inspection
parsed = None
if raw_response is None:
    parsed = None
elif hasattr(raw_response, "model_dump"):
    try:
        parsed = raw_response.model_dump()
    except Exception:
        parsed = None
elif hasattr(raw_response, "dict"):
    try:
        parsed = raw_response.dict()
    except Exception:
        parsed = None
elif isinstance(raw_response, dict):
    parsed = raw_response
else:
    # Try JSON parse of string representation
    try:
        parsed = json.loads(str(raw_response))
    except Exception:
        parsed = None

if parsed is None:
    # Fallback: print raw response representation
    print(raw_response)
else:
    # Pretty-print the parsed response; handle nested output types if present
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
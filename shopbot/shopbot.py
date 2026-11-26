"""ShopBot v1: Pebble & Pine support bot. The system under test from M01 onward.

v1 puts the whole knowledge base into every request (no retrieval yet; that's M06).
Usage: .venv/bin/python shopbot/shopbot.py "your question"
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ASSETS_DIR = Path(__file__).parent.parent / "assets"
SYSTEM_PROMPT_FILE = ASSETS_DIR / "system-prompt.md"
KB_DIR = ASSETS_DIR / "kb"
MAX_TOKENS = 512
CLASSIFIER_PROMPT = """You classify customer support tickets for Pebble & Pine Outfitters, an online outdoor-gear store.

## Category (pick exactly one)
- returns: refunds, exchanges, return eligibility, return shipping
- shipping: delivery times, shipping costs, tracking, late or lost packages, address changes
- warranty: manufacturing defects in a product (not wear and tear, not fit or size)
- loyalty: Trail Club points, rewards, tiers, Summit benefits
- other: anything else, including account security, privacy and payment questions

## Urgency (pick exactly one)
- high: payment or security issue
- medium: delivery, returns or shipping issue
- low: anything else

## Output
Respond with JSON only, no other text, in exactly this form:
{"category": "returns|shipping|warranty|loyalty|other", "urgency": "low|medium|high"}
"""
TICKET_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Ticket Classification",
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["returns", "shipping", "warranty", "loyalty", "other"],
        },
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
    },
    "required": ["category", "urgency"],
    "additionalProperties": False,
}
TICKET_GRAMMAR = r"""
root ::= "{\"category\": " category ", \"urgency\": " urgency "}"
category ::= "\"returns\"" | "\"shipping\"" | "\"warranty\"" | "\"loyalty\"" | "\"other\""
urgency ::= "\"low\"" | "\"medium\"" | "\"high\""
"""

client = OpenAI(base_url=os.environ["LLAMA_SUT_URL"], api_key="none")
_clients = {None: client}  # one client per model server; None = the default model under test


def get_client(base_url=None):
    # base_url: another llama-server (e.g. E2B on port 8083 in M03.4); None = LLAMA_SUT_URL
    if base_url not in _clients:
        _clients[base_url] = OpenAI(base_url=base_url, api_key="none")
    return _clients[base_url]


def load_knowledge_base():
    # sorted(): same file order on every run, so the prompt prefix stays identical and cacheable
    docs = [
        path.read_text(encoding="utf-8").strip() for path in sorted(KB_DIR.glob("*.md"))
    ]
    return "\n\n".join(docs)


def build_messages(question, system_prompt_file=SYSTEM_PROMPT_FILE):
    system_prompt = Path(system_prompt_file).read_text(encoding="utf-8").strip()
    knowledge_base = load_knowledge_base()
    return [
        {
            "role": "system",
            "content": f"{system_prompt}\n\n# Knowledge base\n\n{knowledge_base}",
        },
        {"role": "user", "content": question},
    ]


def answer(question: str, system_prompt_file=SYSTEM_PROMPT_FILE, base_url=None) -> str:
    # No temperature or seed here: the server's settings (start-servers.sh) are the production settings
    # system_prompt_file: default is the production prompt; M03.4 passes a variant to compare prompts
    # base_url: default is the model under test (LLAMA_SUT_URL); M03.4 passes another server to compare models
    response = get_client(base_url).chat.completions.create(
        model="gemma",
        messages=build_messages(question, system_prompt_file),
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content


def build_classifier_message(ticket):
    return [
        {
            "role": "system",
            "content": CLASSIFIER_PROMPT,
        },
        {"role": "user", "content": ticket},
    ]


def classify_raw(ticket, mode="prompt", base_url=None):
    if mode not in ("prompt", "schema", "grammar"):
        raise ValueError(f"Unsupported mode: {mode!r}")
    response_format = (
        {
            "type": "json_schema",
            "json_schema": {"name": "ticket", "strict": True, "schema": TICKET_SCHEMA},
        }
        if mode == "schema"
        else None
    )
    extra_body = {"grammar": TICKET_GRAMMAR} if mode == "grammar" else None

    response = get_client(base_url).chat.completions.create(
        model="gemma",
        messages=build_classifier_message(ticket),
        max_tokens=100,
        response_format=response_format,
        extra_body=extra_body,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python shopbot.py "your question"', file=sys.stderr)
        sys.exit(1)
    print(answer(sys.argv[1]))

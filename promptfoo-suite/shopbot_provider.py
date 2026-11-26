import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shopbot"))
from shopbot import answer, classify_raw, client, SYSTEM_PROMPT_FILE


def call_api(prompt, options, context):
    base_url = options["config"].get("base_url", None)
    warmup(base_url=base_url)
    expression = context["vars"]["question"]
    start = time.perf_counter()
    result = answer(
        expression,
        options["config"].get("system_prompt_file", SYSTEM_PROMPT_FILE),
        base_url=base_url,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    return {"output": result, "latencyMs": latency_ms}


def call_classify(prompt, options, context):
    base_url = options["config"].get("base_url", None)
    warmup(base_url=base_url)
    start = time.perf_counter()
    result = classify_raw(context["vars"]["ticket"], base_url=base_url)
    latency_ms = (time.perf_counter() - start) * 1000
    return {"output": result, "latencyMs": latency_ms}


def warmup(base_url):
    classify_raw(
        "warm-up", base_url=base_url
    )  # warm-up: first chat call has one-time setup; keep it out of the timed tests

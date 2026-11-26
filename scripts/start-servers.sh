#!/usr/bin/env bash
# Start one llama-server (Windows build, called from WSL through interop).
# Usage: bash scripts/start-servers.sh sut|sut-e2b|judge|judge-shared|embed|stop
# Run one chat model at a time: the 12B judge needs the whole GPU.

case "$1" in
  sut)    # Gemma 4 E4B, model under test, port 8080
    llama-server.exe -hf google/gemma-4-E4B-it-qat-q4_0-gguf:Q4_0 -fa on --jinja \
      --temp 1.0 --top-p 0.95 --top-k 64 -ngl 999 --parallel 1 --cache-ram 0 \
      --no-mmproj -c 8192 --port 8080 --reasoning off
    ;;
  sut-e2b)  # Gemma 4 E2B, smaller comparison model (M03.4, M10), same settings as sut, port 8083
            # E4B + E2B + embed fit together in 8 GB VRAM; check with nvidia-smi before timing anything
    llama-server.exe -hf google/gemma-4-E2B-it-qat-q4_0-gguf:Q4_0 -fa on --jinja \
      --temp 1.0 --top-p 0.95 --top-k 64 -ngl 999 --parallel 1 --cache-ram 0 \
      --no-mmproj -c 8192 --port 8083 --reasoning off
    ;;
  judge)  # Gemma 4 12B, local judge, port 8081
    llama-server.exe -hf google/gemma-4-12B-it-qat-q4_0-gguf:Q4_0 -fa on --jinja \
      --temp 0 -ngl 999 --parallel 1 --cache-ram 0 \
      --no-mmproj -c 8192 --port 8081 --reasoning off
    ;;
  judge-shared)  # same 12B judge, but only 24 layers on the GPU, so it fits next to sut (M05.2+)
                 # sut + judge-shared = 7356 MiB VRAM; judge ~25 s per G-Eval case (vs ~7 s on full GPU)
    llama-server.exe -hf google/gemma-4-12B-it-qat-q4_0-gguf:Q4_0 -fa on --jinja \
      --temp 0 -ngl 24 --parallel 1 --cache-ram 0 \
      --no-mmproj -c 8192 --port 8081 --reasoning off
    ;;
  embed)  # nomic-embed-text v1.5, embeddings, port 8082
    llama-server.exe -hf nomic-ai/nomic-embed-text-v1.5-GGUF:Q8_0 -ngl 999 \
      --embedding --port 8082
    ;;
  stop)   # Ctrl+C from WSL often does not reach the Windows process; this stops all servers
    taskkill.exe /IM llama-server.exe /F
    ;;
  *)
    echo "Usage: $0 sut|sut-e2b|judge|judge-shared|embed|stop" >&2
    exit 1
    ;;
esac

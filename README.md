# industrial-manual-assistant

> Offline-first RAG for industrial equipment manuals  
> Answers PLC error codes with exact section and page references

## Demo

[INSERTAR demo.gif — 30 segundos: escribir "Error F1 S7-1200" → respuesta con Manual §4.3 p.87]

## Corpus (included)

| Manual                     | Pages | Chunks |
|----------------------------|-------|--------|
| Siemens S7-1200 System     | 742   | 1,847  |
| Allen-Bradley Micro820     | 318   | 891    |

## Sample Query

**Input:** "What causes Error F1 on Siemens S7-1200 and how to resolve it?"

**Output:**
> Error F1 indicates a CPU fault in module slot 0. Resolution: [steps]
>
> *Source: Siemens S7-1200 System Manual, §7.2 Diagnostics, p. 312*
> *Confidence: 0.94 · Retrieved in 187ms*

## Architecture

BM25 + FAISS hybrid → CrossEncoder rerank → LLM with citation enforcement

## Edge Deployment

Optimized for NVIDIA Jetson Orin Nano 8GB (offline, no cloud dependency):
- Model: Qwen3-4B-Q4_K_M via llama.cpp
- RAM usage: ~5.2GB total
- Query latency: <2s end-to-end

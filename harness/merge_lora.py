"""Junta o adaptador LoRA ao Qwen3-8B (bf16) e salva o modelo completo em safetensors.
Uso: python3 merge_lora.py <adaptador_dir> <saida_dir> [--base Qwen/Qwen3-8B]
Depois: ollama create <nome> -f Modelfile  (FROM <saida_dir>, com --quantize q4_K_M)"""
import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

ap = argparse.ArgumentParser()
ap.add_argument("adapter")
ap.add_argument("out")
ap.add_argument("--base", default="Qwen/Qwen3-8B")
a = ap.parse_args()
tok = AutoTokenizer.from_pretrained(a.base)
model = AutoModelForCausalLM.from_pretrained(a.base, dtype=torch.bfloat16, device_map={"": 0})
model = PeftModel.from_pretrained(model, a.adapter)
model = model.merge_and_unload()
model.save_pretrained(a.out, safe_serialization=True)
tok.save_pretrained(a.out)
print("MERGE OK", a.out)

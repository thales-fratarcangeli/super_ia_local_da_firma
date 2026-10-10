"""QLoRA (4 bits) no Qwen3-8B com os exemplos verificados do dataset. Roda na GPU do pod.
Uso: python3 train_lora.py <dataset.jsonl> <saida_dir> [--epochs 3] [--lr 2e-4] [--r 16]
Formato do dataset: uma linha JSON com "prompt" e "completion" (o mesmo prompt que o usuário escreveria).
A perda só conta nos tokens da resposta (completion), não no prompt. Thinking desligado (igual à avaliação)."""
import argparse
import json
import random

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq, Trainer, TrainingArguments)

ap = argparse.ArgumentParser()
ap.add_argument("dataset")
ap.add_argument("out")
ap.add_argument("--base", default="unsloth/Qwen3-8B-bnb-4bit")
ap.add_argument("--epochs", type=float, default=3)
ap.add_argument("--lr", type=float, default=2e-4)
ap.add_argument("--r", type=int, default=16)
ap.add_argument("--maxlen", type=int, default=2048)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--no4bit", action="store_true", help="treina em bf16 puro (sem quantização), evita descompasso treino/merge")
ap.add_argument("--dropout", type=float, default=0.05)
args = ap.parse_args()
random.seed(args.seed)
torch.manual_seed(args.seed)

tok = AutoTokenizer.from_pretrained(args.base)
rows = [json.loads(l) for l in open(args.dataset, encoding="utf-8") if l.strip()]
data = []
for r in rows:
    prompt_text = tok.apply_chat_template([{"role": "user", "content": r["prompt"]}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    p_ids = tok(prompt_text, add_special_tokens=False)["input_ids"]
    c_ids = tok(r["completion"] + "<|im_end|>\n", add_special_tokens=False)["input_ids"]
    ids = p_ids + c_ids
    if len(ids) > args.maxlen:
        continue
    data.append({"input_ids": ids, "attention_mask": [1] * len(ids), "labels": [-100] * len(p_ids) + c_ids})
random.shuffle(data)
print(f"{len(data)}/{len(rows)} exemplos usados (<= {args.maxlen} tokens)")


class DS(torch.utils.data.Dataset):
    def __len__(self):
        return len(data)

    def __getitem__(self, i):
        return data[i]


model = AutoModelForCausalLM.from_pretrained(args.base, device_map={"": 0}, dtype=torch.bfloat16)
if args.no4bit:
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
else:
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
cfg = LoraConfig(r=args.r, lora_alpha=2 * args.r, lora_dropout=args.dropout, bias="none", task_type="CAUSAL_LM",
                 target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
model = get_peft_model(model, cfg)
model.print_trainable_parameters()

targs = TrainingArguments(output_dir=args.out + "_ckpt", per_device_train_batch_size=2, gradient_accumulation_steps=8,
                          num_train_epochs=args.epochs, learning_rate=args.lr, lr_scheduler_type="cosine", warmup_steps=0.05,
                          bf16=True, logging_steps=2, save_strategy="no", report_to=[], gradient_checkpointing=True,
                          remove_unused_columns=False, optim="paged_adamw_8bit", seed=args.seed)
Trainer(model=model, args=targs, train_dataset=DS(), data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100)).train()
model.save_pretrained(args.out)
tok.save_pretrained(args.out)
print("ADAPTADOR SALVO EM", args.out)

#!/bin/bash
# Ciclo v4 (RFT on-policy): aluno gera -> testes filtram -> treino -> pipeline (merge/convert/quantize/Ollama/medições).
exec > /root/rft_v4.log 2>&1
set -x
cd /root/lab
rm -f /root/v4.done
pkill -f '[p]ytest' 2>/dev/null
ollama rm elias-v3 2>/dev/null
ollama list | grep -q '^qwen3:8b' || ollama pull qwen3:8b
python3 harness/gen_rft.py data/rft_v4.jsonl data/d1.jsonl data/poly_js.jsonl data/poly_go.jsonl data/poly_c.jsonl data/poly_java.jsonl data/poly_sql.jsonl --k 8 --workers 6 > /root/gen_rft.log 2>&1
N=$(wc -l < data/rft_v4.jsonl)
if [ "$N" -lt 60 ]; then echo "poucos exemplos: $N" ; echo FAIL > /root/v4.done; exit 1; fi
# espera o usuário/agente liberar disco (artefatos do v3 baixados) antes do treino
while [ ! -f /root/disk_ok ]; do sleep 20; done
ollama stop qwen3:8b; ollama rm qwen3:8b
python3 harness/train_lora.py data/rft_v4.jsonl /root/lora_v4 --base Qwen/Qwen3-8B --no4bit --epochs 2 --lr 1e-4 --dropout 0.1 > /root/train_v4.log 2>&1
bash harness/pod_pipeline.sh v4 /root/lora_v4

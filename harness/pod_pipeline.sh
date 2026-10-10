#!/bin/bash
# Pipeline do pod: adaptador LoRA -> modelo completo -> GGUF Q4_K_M -> Ollama -> medições (3 suítes, sem e com RAG).
# Uso: bash pod_pipeline.sh <tag> <dir_adaptador> [base]    ex.: bash pod_pipeline.sh v3 /root/lora_v3
# Cuida do disco (31 GB): apaga cache do HF, f16 e o modelo anterior do Ollama no momento certo.
TAG=$1; LORA=$2; BASE=${3:-Qwen/Qwen3-8B}
L=/root/lab; LOG=/root/pipe_$TAG.log
exec > "$LOG" 2>&1
set -x
cd $L
while ! grep -q -E "ADAPTADOR SALVO|Traceback" /root/train_$TAG.log 2>/dev/null; do sleep 10; done
grep -q "ADAPTADOR SALVO" /root/train_$TAG.log || { echo "TREINO FALHOU"; echo FAIL > /root/$TAG.done; exit 1; }

# 1) merge (usa o cache do HF que o treino já baixou) e tokenizador original (o do transformers 5 quebra o conversor)
if [ ! -f /dev/shm/merged_$TAG/model.safetensors ]; then
rm -rf /dev/shm/merged_$TAG; mkdir -p /dev/shm/merged_$TAG
python3 harness/merge_lora.py $LORA /dev/shm/merged_$TAG --base $BASE || { echo FAIL > /root/$TAG.done; exit 1; }
python3 - <<EOF
from huggingface_hub import hf_hub_download
import shutil
for f in ['tokenizer_config.json','tokenizer.json','vocab.json','merges.txt','generation_config.json']:
    shutil.copy(hf_hub_download('$BASE', f), '/dev/shm/merged_$TAG/' + f)
EOF
rm -rf /root/.cache/huggingface/hub/* /root/.cache/huggingface/xet
fi

# 2) conversão em ambiente isolado (transformers 4.x) e quantização
ollama rm elias-v2 2>/dev/null; ollama rm elias-v3 2>/dev/null
/root/venv_conv/bin/python /root/llama.cpp/convert_hf_to_gguf.py /dev/shm/merged_$TAG --outfile /root/${TAG}_f16.gguf --outtype f16 || { echo FAIL > /root/$TAG.done; exit 1; }
rm -rf /dev/shm/merged_$TAG
/root/llama.cpp/build/bin/llama-quantize /root/${TAG}_f16.gguf /root/${TAG}_q4km.gguf Q4_K_M || { echo FAIL > /root/$TAG.done; exit 1; }
rm -f /root/${TAG}_f16.gguf

# 3) Ollama
sed "s#^FROM .*#FROM /root/${TAG}_q4km.gguf#" /root/Modelfile.v2 > /root/Modelfile.$TAG
ollama create elias-$TAG -f /root/Modelfile.$TAG || { echo FAIL > /root/$TAG.done; exit 1; }
mkdir -p /root/artefatos; mv /root/${TAG}_q4km.gguf /root/artefatos/elias_${TAG}_q4km.gguf 2>/dev/null || true

# 4) medições: 3 suítes sem RAG e depois com RAG
M=elias-$TAG
python3 harness/run_suite.py ${TAG}_dev $M --n 4 --temp 0.4 > /root/${TAG}_dev.log 2>&1
python3 harness/run_suite.py ${TAG}_held $M --suite heldout --n 4 --temp 0.4 > /root/${TAG}_held.log 2>&1
python3 harness/run_poly.py ${TAG}_poly $M --n 2 --temp 0.4 > /root/${TAG}_poly.log 2>&1
python3 harness/run_suite.py ${TAG}r_dev $M --n 4 --temp 0.4 --rag > /root/${TAG}r_dev.log 2>&1
python3 harness/run_suite.py ${TAG}r_held $M --suite heldout --n 4 --temp 0.4 --rag > /root/${TAG}r_held.log 2>&1
python3 harness/run_poly.py ${TAG}r_poly $M --n 2 --temp 0.4 --rag > /root/${TAG}r_poly.log 2>&1
echo OK > /root/$TAG.done

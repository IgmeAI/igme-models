

## Estructure

igme-models in cloud/
├── main.py
├── embedding_service.py
├── requirements.txt
└── .env  <-- ¡IMPORTANT!

## .env

API_KEY="yout API key"

## Setting up the Environment pod

cd /workspace

## Generate SSH key
ssh-keygen -t ed25519 -C "igmemarcial@gmail.com"
cat ~/.ssh/id_ed25519.pub

## Personal acces token 
git clone https://igmeMarcial:ghp_ABC123xyz456@github.com/IgmeAI/igme-models.git

## Clone the repository
git clone git@github.com:IgmeAI/igme-models.git
cd igme-models


24 GB de VRAM (e.g., RTX 3080, A4000)



## Creamos la carpeta de la caché
mkdir -p /workspace/huggingface_cache

## Exportamos la variable de entorno para que transformers la use.
## ¡Haz esto cada vez que inicies una nueva terminal!
export HF_HOME=/workspace/huggingface_cache
export HF_TOKEN="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" 


# (Opcional, pero buena práctica) Crear un entorno virtual
# python -m venv venv
# source venv/bin/activate

# Instalar todo desde requirements.txt
pip install -r requirements.txt


## Huggingface cache
huggingface-cli login

## run
uvicorn main:app --host 0.0.0.0 --port 8000

## verify

https://eio4zvjfnv5vdl-8000.proxy.runpod.net/gpu-check
https://eio4zvjfnv5vdl-8000.proxy.runpod.net/docs














https://eio4zvjfnv5vdl-8000.proxy.runpod.net/
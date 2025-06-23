# 🚀 Despliegue de Modelos en la Nube - Configuración Óptima

**Implementa modelos de IA en la nube con máxima eficiencia**  
Este repositorio contiene la configuración esencial para desplegar servicios de embedding y modelos de lenguaje en entornos cloud, optimizado para GPUs de alto rendimiento (24GB+ VRAM). Incluye:

- 🔐 Gestión segura de claves API y tokens
- 🐳 Configuración lista para Docker/RunPod
- 🤖 Soporte para modelos de HuggingFace
- ⚡ Endpoints API con Uvicorn
- 📊 Monitorización integrada

**Requisitos mínimos:** GPU con arquitectura CUDA ≥ 8.0 (recomendado RTX 3080/A4000+)

## 🔐 Configuración del Entorno

### Archivo `.env`
```ini
API_KEY="your_API_key_here"  # Reemplazar con tu clave real

```
## 🛠️ Configuración Inicial

# Navegar al directorio de trabajo
cd /workspace

# Generar clave SSH
ssh-keygen -t ed25519 -C "igmemarcial@gmail.com"
cat ~/.ssh/id_ed25519.pub

# Clonar repositorio (2 métodos)
git clone https://igmeMarcial:ghp_ABC123xyz456@github.com/IgmeAI/igme-models.git
# O
git clone git@github.com:IgmeAI/igme-models.git
cd igme-models


## 💾 Configuración de Caché

# Crear directorio para caché de HuggingFace
mkdir -p /workspace/huggingface_cache

# Configurar variables de entorno (ejecutar en cada nueva terminal)
export HF_HOME=/workspace/huggingface_cache
export HF_TOKEN="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"


## ⚙️ Instalación

# Opcional: Crear entorno virtual
# python -m venv venv
# source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Autenticación con HuggingFace
huggingface-cli login


## 🚀 Ejecución

uvicorn main:app --host 0.0.0.0 --port 8000



## 🔍 Verificación

- Comprobar GPU:
https://eio4zvjfnv5vdl-8000.proxy.runpod.net/gpu-check

- Documentación API:
https://eio4zvjfnv5vdl-8000.proxy.runpod.net/docs

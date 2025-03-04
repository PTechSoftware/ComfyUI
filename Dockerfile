FROM nvidia/cuda:12.2.0-devel-ubuntu22.04 AS base

# Instalar dependencias generales
RUN apt update && apt install -y \
    python3 python3-pip git wget curl \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Clonar ComfyUI
WORKDIR /app
RUN git clone https://github.com/IgnacioPerez98/ComfyUI.git .
#RUN pip3 install -r requirements.txt
RUN apt update
RUN apt install nano
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir boto3
RUN pip3 install --no-cache-dir minio
# Exponer el puerto de la API
EXPOSE 8188

# Comando para iniciar ComfyUI con compatibilidad GPU
CMD ["python3", "main.py", "--listen", "--port", "8188"]
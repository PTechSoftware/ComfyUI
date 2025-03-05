from datetime import datetime
from io import BytesIO
import io
from PIL import Image
import numpy as np
from minio import Minio
from minio.error import S3Error
import torch
import logging



# Configuración de MinIO
class SaveToMinIO:
    """
    Nodo personalizado para guardar imágenes en MinIO desde ComfyUI.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),                
                "host": ("STRING", {"default": "10.0.0.13:9000"}),
                "key": ("STRING", {"default": "s3key"}),
                "passwrd": ("STRING", {"default": "s3pass"}),
                "bucket_name": ("STRING", {"default": "kielcesa"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upload_to_minio"
    CATEGORY = "MinIO"

    def upload_to_minio(self, images,host,key,passwrd, bucket_name:str):
        """
        Convierte la imagen en un formato compatible y la sube a MinIO.
        """
        
        
        if isinstance(images, torch.Tensor):
            images = images.cpu().numpy()  # Convertir a NumPy
        
        if images.ndim == 3:  # Si solo hay una imagen, añadir batch dimensión
            images = np.expand_dims(images, axis=0)
        
        # Subir a MinIO
        # Conectar con MinIO (SIN región)
        client = Minio(host,
            access_key=key,
            secret_key=passwrd,
            secure=False,
        )
        for i, img in enumerate(images):
            
            # Si la forma es incorrecta, intentar ajustar (verificar en depuración)
            if img.shape[0] in [1, 3]:  # Si está en formato (C, H, W)
                img = np.moveaxis(img, 0, -1)  # Convertir a (H, W, C)
            elif img.shape[-1] == 1:  # Si es (H, W, 1), convertir a escala de grises
                img = img.squeeze(-1)

            # Normalizar a rango [0, 255] y convertir a uint8
            img = (img * 255).clip(0, 255).astype(np.uint8)

            # Crear imagen PIL
            pil_img = Image.fromarray(img)

            # Guardar en un buffer de memoria
            img_buffer = io.BytesIO()
            pil_img.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            found = client.bucket_exists(bucket_name)
            if not found:
                client.make_bucket(bucket_name)
                print("Created bucket", bucket_name)
            else:
                print("Bucket", bucket_name, "already exists")
            # Subir la imagen a MinIO
            file_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            client.put_object(
                bucket_name, 
                f"{file_name}.png", 
                img_buffer,
                content_type="image/png",
                length = img_buffer.getbuffer().nbytes  # Obtener el tamaño del buffer en bytes

            )
            logging.info(f"Imagen guardada en MinIO: {bucket_name}{file_name}")
            print(f"Imagen guardada en MinIO: {file_name}")
        return images

# Registrar el nodo en ComfyUI
NODE_CLASS_MAPPINGS = {
    "SaveToMinIO": SaveToMinIO
    }
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveToMinIO": "Save Image to MinIO"
    }

import logging
import time
import base64
import io
from typing import List

import numpy as np
import torch
from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
from PIL.Image import Image
from PIL.Image import open as open_image
from transformers.utils.import_utils import is_flash_attn_2_available

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ColpaliEmbeddingService:
    def __init__(self, model_name: str = "tsystems/colqwen2.5-3b-multilingual-v1.0", batch_size: int = 16):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing ColpaliEmbeddingService on device: {self.device}")
        if self.device == "cpu":
            logger.warning("WARNING: Running on CPU. This will be extremely slow.")

        start_time = time.time()
        
        self.model = ColQwen2_5.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map=self.device,
            attn_implementation="flash_attention_2" if is_flash_attn_2_available() and self.device == "cuda" else "eager",
        ).eval()

        self.processor: ColQwen2_5_Processor = ColQwen2_5_Processor.from_pretrained(model_name)
        
        self.batch_size = batch_size
        logger.info(f"Using batch size: {self.batch_size}")
        
        total_init_time = time.time() - start_time
        logger.info(f"Model '{model_name}' loaded in {total_init_time:.2f} seconds.")

    def _process_in_batches(self, items: List, process_function) -> List[np.ndarray]:
        """Helper para procesar cualquier tipo de input en batches."""
        all_embeddings = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(items)-1)//self.batch_size + 1} with {len(batch)} items.")
            
            start_batch_time = time.time()
            embeddings = process_function(batch)
            all_embeddings.extend(embeddings)
            
            batch_time = time.time() - start_batch_time
            logger.info(f"Batch processed in {batch_time:.2f}s ({batch_time/len(batch):.3f}s/item).")
        return all_embeddings

    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Genera embeddings para una lista de textos."""
        
        def _process_text_batch(batch_texts: List[str]):
            processed = self.processor.process_queries(batch_texts).to(self.device)
            with torch.no_grad():
                embeddings = self.model(**processed)
            return [emb for emb in embeddings.cpu().to(torch.float32).numpy()]

        return self._process_in_batches(texts, _process_text_batch)

    def embed_images(self, image_b64_strings: List[str]) -> List[np.ndarray]:
        """Genera embeddings para una lista de imágenes en formato base64."""
        
        def _process_image_batch(batch_b64: List[str]):
            images: List[Image] = []
            for b64_string in batch_b64:
                try:
                    image_bytes = base64.b64decode(b64_string)
                    # .convert('RGB') es importante para asegurar consistencia
                    image = open_image(io.BytesIO(image_bytes)).convert("RGB")
                    images.append(image)
                except Exception:
                    logger.warning("Could not decode an image. Using a blank placeholder.")
                    images.append(Image.new('RGB', (224, 224), color = 'white'))
            
            processed = self.processor.process_images(images).to(self.device)
            with torch.no_grad():
                embeddings = self.model(**processed)
            return [emb for emb in embeddings.cpu().to(torch.float32).numpy()]

        return self._process_in_batches(image_b64_strings, _process_image_batch)
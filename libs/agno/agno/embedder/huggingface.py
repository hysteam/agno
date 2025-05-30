from dataclasses import dataclass
from os import getenv
from typing import Any, Dict, List, Optional, Tuple

from agno.embedder.base import Embedder
from agno.utils.log import logger

try:
    from huggingface_hub import InferenceClient
except ImportError:
    logger.error("`huggingface-hub` not installed, please run `pip install huggingface-hub`")
    raise


@dataclass
class HuggingfaceCustomEmbedder(Embedder):
    """Huggingface Custom Embedder"""

    id: str = "intfloat/multilingual-e5-large"
    api_key: Optional[str] = getenv("HUGGINGFACE_API_KEY")
    client_params: Optional[Dict[str, Any]] = None
    huggingface_client: Optional[InferenceClient] = None

    @property
    def client(self) -> InferenceClient:
        if self.huggingface_client:
            return self.huggingface_client
        _client_params: Dict[str, Any] = {}
        if self.api_key:
            _client_params["api_key"] = self.api_key
        if self.client_params:
            _client_params.update(self.client_params)
        self.huggingface_client = InferenceClient(**_client_params)
        return self.huggingface_client

    def _response(self, text: str):
        return self.client.feature_extraction(text=text, model=self.id)

    def get_embedding(self, text: str) -> List[float]:
        response = self._response(text=text)
        try:
            # If already a list, return directly
            if isinstance(response, list):
                return response
            # If numpy array, convert to list
            elif hasattr(response, "tolist"):
                return response.tolist()
            else:
                return list(response)
        except Exception as e:
            logger.warning(f"Failed to process embeddings: {e}")
            return []

    def get_embedding_and_usage(self, text: str) -> Tuple[List[float], Optional[Dict]]:
        return self.get_embedding(text=text), None

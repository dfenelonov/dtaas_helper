import requests
import json
import time
from typing import Any, Dict, List, Optional


class GigaChatEmbeddings:
    def embeddings(self, texts, model):
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        payload = 'scope=GIGACHAT_API_CORP'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': '450ce936-9e4b-4e1c-aa70-a197e3890e8f',
            'Authorization': 'Basic YWRmYmQ4YWMtYTU1MC00MGI4LTkwNzEtNThkYjc2MmU2MzQ3OjQ0NDJlYzNhLTY3MzAtNDk3MC04ZjMzLTBhYTAxNTk2OGU2ZQ=='
        }

        response = requests.post(url, headers=headers, data=payload, verify=False)

        token = response.json()['access_token']
        url = "https://gigachat.devices.sberbank.ru/api/v1/embeddings"

        payload = json.dumps({
            "model": model,
            "input": texts
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response.json()['data']

    def embed_documents(
        self, texts: List[str], model="Embeddings"
    ) -> List[List[float]]:
        """Embed documents using a GigaChat embeddings models.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        result: List[List[float]] = []
        for text in texts:
            for embedding in self.embeddings(
                texts=[text], model=model
            ):
                result.append(embedding['embedding'])
        return result

    def embed_query(self, text: str, model="Embeddings") -> List[float]:
        """Embed a query using a GigaChat embeddings models.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        return self.embed_documents(texts=[text], model=model)[0]
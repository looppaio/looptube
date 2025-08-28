import chromadb
from chromadb import ClientAPI, Collection, GetResult
from functools import cached_property
from pathlib import Path

from looptube.core import LTModel


class LocalClient(LTModel):
    """Local Persistence client"""

    @cached_property
    def db_path(self) -> Path:
        return self.__env__.storage / ".db"

    @cached_property
    def client(self) -> ClientAPI:
        return chromadb.PersistentClient(path=self.db_path)

    def collection(self, collection: str) -> Collection:
        """Get or create a collection"""
        return self.client.get_or_create_collection(
            name=collection,
            metadata=dict(
                description=f"Looptube collection: {collection}",
                created_at=self.now().isoformat(),
            ),
            embedding_function=None,  # TODO: Add embedding function
        )

    def add(
        self,
        collection: str,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
        **kwargs,
    ) -> None:
        self.collection(collection).add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=[0.0, 0.0],
        )

    def exists(self, collection: str, keys: list[str]) -> GetResult:
        """Check if keys exist in collection"""
        return self.collection(collection).get(ids=keys)

    def heartbeat(self) -> int:
        return self.client.heartbeat()

    def reset(self) -> bool:
        return self.client.reset()

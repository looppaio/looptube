"""
Local Cache for Looptube

This class is used to manage the local cache for Looptube.

It is used to store the cache for the logs, storage, and HF.

It is also used to clear the cache for the logs, storage, and HF.

"""

from math import ceil
from pathlib import Path
from typing import Any
from .base import LTModel, LTSettings, LTQueue


class LTCache(LTModel):
    """Local Cache for Looptube"""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.settings = LTSettings()
        self.queue = LTQueue[Path]()
        self.enqueue()

    def capacity(self) -> int:
        """Get the cache capacity"""
        return LTSettings().cache_capacity

    def size(self, cache: Path | None = None, **kwargs: Any) -> int:
        """Get the cache size"""
        cache = cache or self.settings.cache
        bytes_sum = sum(map(lambda x: x[1].stat().st_size, self.get_tree(cache)))
        return ceil(bytes_sum / (2**30))

    def is_queueable(self, file: Path) -> bool:
        """Check if the file is queueable"""
        return ceil(self.size(file) + self.size(self.current)) <= self.capacity()

    def enqueue(self, file: Path | None = None, **kwargs: Any) -> None:
        """Enqueue the cache"""
        file = file or self.settings.cache

        for p, f in self.get_tree(file):
            while not self.is_queueable(f):
                self.dequeue()
            self.queue.add(p, f)

    def dequeue(self, **kwargs: Any) -> None:
        """Dequeue the cache"""
        deleted = self.queue.delete()
        if deleted:
            deleted[1].unlink(missing_ok=True)

    def get_tree(self, directory: Path | None = None) -> list[tuple[float, Path]]:
        """Get the tree of the cache"""
        directory = directory or self.settings.cache

        if not directory.exists():
            return []

        tree: list[tuple[float, Path]] = []

        def _get_tree(filepath: Path) -> tuple[float, Path]:
            files = list(filepath.glob("*"))

            is_files = list(filter(lambda x: x.is_file(), files))
            is_dirs = list(filter(lambda x: x.is_dir(), files))

            if is_files:
                tree.extend(
                    [
                        (round(file.stat().st_mtime), file.absolute())
                        for file in is_files
                    ]
                )

            if is_dirs:
                for _dir in is_dirs:
                    _get_tree(_dir)

        _get_tree(directory)
        return tree

    def logs_cache(self, **kwargs: Any) -> Path:
        """Log the cache"""
        return self.settings.logs

    def storage_cache(self, **kwargs: Any) -> Path:
        """Storage the cache"""
        return self.settings.storage

    def files_cache(self, **kwargs: Any) -> Path:
        """Files the cache"""
        return self.__files_store__

    def ml_cache(self, **kwargs: Any) -> Path:
        """HF the cache"""
        return self.settings.ml

    def clear_logs(self) -> bool:
        """Clear the logs"""
        return self.clear(self.logs_cache())

    def clear_storage(self) -> bool:
        """Clear the storage"""
        return self.clear(self.storage_cache())

    def clear_files(self) -> bool:
        """Clear the files"""
        return self.clear(self.files_cache())

    def clear_ml(self) -> bool:
        """Clear the HF"""
        return self.clear(self.ml_cache())

    def flush(self) -> bool:
        """Flush the cache"""
        self.queue.clear()
        return bool(self.queue.tree.empty())

    def clear(self, directory: Path | None = None) -> bool:
        """Clear the cache"""
        directory = directory or self.settings.cache

        for file in self.get_tree(directory):
            file[1].unlink(missing_ok=True)
        return len(self.get_tree(directory)) == 0

    def reset(self) -> bool:
        """Reset the cache"""
        return self.flush() and self.clear()

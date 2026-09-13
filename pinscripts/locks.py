"""Small process locks for coordinating parallel terminal workflows."""

from contextlib import contextmanager
import fcntl
from pathlib import Path

from .paths import OUTPUT


@contextmanager
def claim_lock(name, *, blocking=False, lock_directory=None):
    """Yield whether this process acquired a named filesystem lock."""
    directory = Path(lock_directory) if lock_directory is not None else OUTPUT / ".locks"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.lock"
    with path.open("a+") as lock:
        operation = fcntl.LOCK_EX
        if not blocking:
            operation |= fcntl.LOCK_NB
        try:
            fcntl.flock(lock.fileno(), operation)
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

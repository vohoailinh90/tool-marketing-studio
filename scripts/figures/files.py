"""Writing a file so that a failure leaves the previous one whole."""

from __future__ import annotations

import os
import uuid
from pathlib import Path


def write_atomic(path: Path, data: bytes) -> None:
    """Puts `data` in `path`: the bytes go to a temporary file beside it and replace it in one rename, so a full disk or an interrupted run
    leaves the previous file as it was (and no half-written file behind). A path that is a link is written through to its target."""
    path = Path(os.path.realpath(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp")
    try:
        temp.write_bytes(data)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)                       # what is left of a write that failed; nothing after a successful rename

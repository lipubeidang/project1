"""
Background task: periodically remove session directories older than 24 h.
"""

import asyncio
import shutil
import time
from pathlib import Path

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
SESSION_TTL_SECONDS = 24 * 60 * 60  # 24 hours


async def cleanup_expired_sessions():
    """Run forever, checking once per hour."""
    while True:
        await asyncio.sleep(3600)
        if not UPLOAD_DIR.exists():
            continue
        now = time.time()
        for session_dir in UPLOAD_DIR.iterdir():
            if not session_dir.is_dir():
                continue
            try:
                mtime = session_dir.stat().st_mtime
                if now - mtime > SESSION_TTL_SECONDS:
                    shutil.rmtree(session_dir, ignore_errors=True)
            except Exception:
                pass

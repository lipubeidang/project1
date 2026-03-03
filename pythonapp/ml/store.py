"""
Disk-based dataset storage (Parquet) + in-memory model/task caches.
"""

from pathlib import Path
import uuid
import pandas as pd

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory caches (no need to persist — models live only while the server runs)
model_store: dict = {}   # model_id -> {model, scaler, meta, test_data}
task_store: dict = {}     # task_id  -> {status, progress, result, error}


def save_dataset(session_id: str, df: pd.DataFrame) -> str:
    dataset_id = f"ds_{uuid.uuid4().hex[:12]}"
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(session_dir / f"{dataset_id}.parquet", index=False)
    return dataset_id


def load_dataset(session_id: str, dataset_id: str) -> pd.DataFrame:
    path = UPLOAD_DIR / session_id / f"{dataset_id}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Dataset {dataset_id} not found in session {session_id}")
    return pd.read_parquet(path)


def delete_dataset(session_id: str, dataset_id: str):
    path = UPLOAD_DIR / session_id / f"{dataset_id}.parquet"
    if path.exists():
        path.unlink()


def delete_session(session_id: str):
    import shutil
    session_dir = UPLOAD_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)


def list_datasets(session_id: str) -> list:
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        return []
    results = []
    for p in sorted(session_dir.glob("*.parquet")):
        try:
            df = pd.read_parquet(p)
            results.append({
                "dataset_id": p.stem,
                "row_count": len(df),
                "col_count": len(df.columns),
                "columns": [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns],
            })
        except Exception:
            pass
    return results

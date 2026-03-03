"""
Pydantic request / response schemas for the ML pipeline.
"""

from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class SelectFeaturesRequest(BaseModel):
    dataset_id: str
    feature_cols: List[str]
    target_col: str
    task_type: str = "classification"


class TrainRequest(BaseModel):
    dataset_id: str
    feature_cols: List[str]
    target_col: str
    task_type: str = "classification"
    model_type: str = "random_forest"
    hyperparams: Dict[str, Any] = {}


class PredictRequest(BaseModel):
    model_id: str
    data: Optional[List[Dict[str, Any]]] = None
    dataset_id: Optional[str] = None

"""
Pydantic request / response schemas for the ML pipeline.
"""

from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class PreprocessRequest(BaseModel):
    dataset_id: str
    preprocess_steps: List[Dict[str, Any]] = []
    target_col: Optional[str] = None  # 可选，分组/聚合等步骤若需要可传入

class SelectFeaturesRequest(BaseModel):
    dataset_id: str
    feature_cols: List[str]
    target_col: str
    task_type: str = "classification"
    preprocess_steps: List[Dict[str, Any]] = []


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

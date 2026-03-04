"""
All /ml/* API endpoints for the ML pipeline.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from typing import Optional
import uuid
import time
import numpy as np
import pandas as pd

from .store import (
    save_dataset,
    load_dataset,
    delete_dataset as remove_dataset,
    delete_session,
    list_datasets,
    model_store,
    task_store,
)
from .models import SelectFeaturesRequest, TrainRequest, PredictRequest

router = APIRouter(prefix="/ml", tags=["ML Pipeline"])


# ── Dataset Management ────────────────────────────────────────────────────────


@router.post("/upload-dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    x_session_id: str = Header(...),
):
    """Upload a file, parse it into a DataFrame, and save as Parquet."""
    from main import parse_file  # lazy import to avoid circular dependency

    content = await file.read()
    try:
        dfs = parse_file(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    if not dfs:
        raise HTTPException(status_code=400, detail="文件中未找到有效数据")

    df = pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]
    dataset_id = save_dataset(x_session_id, df)
    columns = [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns]

    return {
        "dataset_id": dataset_id,
        "row_count": len(df),
        "col_count": len(df.columns),
        "columns": columns,
        "preview": df.head(5).to_dict("records"),
    }


@router.get("/datasets")
async def get_datasets(x_session_id: str = Header(...)):
    """List all datasets in the current session."""
    return list_datasets(x_session_id)


@router.delete("/datasets/{dataset_id}")
async def delete_dataset_endpoint(
    dataset_id: str,
    x_session_id: str = Header(...),
):
    remove_dataset(x_session_id, dataset_id)
    return {"status": "deleted"}


@router.delete("/session/{session_id}")
async def delete_session_endpoint(session_id: str):
    delete_session(session_id)
    return {"status": "deleted"}


@router.post("/session/{session_id}/cleanup")
async def cleanup_session_endpoint(session_id: str):
    """POST variant for navigator.sendBeacon (only supports POST)."""
    delete_session(session_id)
    return {"status": "deleted"}


# ── Feature Selection ─────────────────────────────────────────────────────────


@router.post("/select-features")
async def select_features(
    req: SelectFeaturesRequest,
    x_session_id: str = Header(...),
):
    try:
        df = load_dataset(x_session_id, req.dataset_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="数据集不存在")

    all_cols = req.feature_cols + [req.target_col]
    missing = [c for c in all_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"列不存在: {missing}")

    subset = df[all_cols].copy()
    original_count = len(subset)
    subset = subset.dropna()
    dropped = original_count - len(subset)

    warnings = []
    if dropped > 0:
        warnings.append(f"移除了 {dropped} 行含空值的数据")

    # Save cleaned subset as a new dataset
    selection_id = save_dataset(x_session_id, subset)

    # Compute target statistics
    target_info = {}
    if req.task_type == "classification":
        dist = subset[req.target_col].value_counts().to_dict()
        target_info = {"distribution": {str(k): int(v) for k, v in dist.items()}}
    else:
        col = subset[req.target_col]
        target_info = {
            "mean": round(float(col.mean()), 4),
            "std": round(float(col.std()), 4),
            "min": round(float(col.min()), 4),
            "max": round(float(col.max()), 4),
        }

    return {
        "selection_id": selection_id,
        "row_count": len(subset),
        "col_count": len(all_cols),
        "target_info": target_info,
        "warnings": warnings,
        "preview": subset.head(5).to_dict("records"),
    }


# ── Model Training ────────────────────────────────────────────────────────────


def _get_model(task_type: str, model_type: str, hp: dict):
    """Instantiate a scikit-learn estimator."""
    from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
    from sklearn.ensemble import (
        RandomForestClassifier,
        RandomForestRegressor,
        GradientBoostingClassifier,
        GradientBoostingRegressor,
    )
    from sklearn.svm import SVC, SVR
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.neighbors import KNeighborsClassifier

    rs = hp.get("random_state", 42)

    if task_type == "classification":
        mapping = {
            "logistic_regression": lambda: LogisticRegression(max_iter=1000, random_state=rs),
            "random_forest": lambda: RandomForestClassifier(
                n_estimators=hp.get("n_estimators", 100),
                max_depth=hp.get("max_depth", 10),
                min_samples_leaf=hp.get("min_samples_leaf", 3),
                random_state=rs,
                class_weight=hp.get("class_weight"),
            ),
            "svm": lambda: SVC(C=hp.get("C", 1.0), probability=True, random_state=rs),
            "decision_tree": lambda: DecisionTreeClassifier(
                max_depth=hp.get("max_depth", 8),
                min_samples_leaf=hp.get("min_samples_leaf", 3),
                random_state=rs,
            ),
            "gradient_boosting": lambda: GradientBoostingClassifier(
                n_estimators=hp.get("n_estimators", 100),
                max_depth=hp.get("max_depth", 3),
                random_state=rs,
            ),
            "knn": lambda: KNeighborsClassifier(n_neighbors=hp.get("n_neighbors", 5)),
        }
    else:
        mapping = {
            "linear_regression": lambda: LinearRegression(),
            "ridge": lambda: Ridge(alpha=hp.get("alpha", 1.0)),
            "lasso": lambda: Lasso(alpha=hp.get("alpha", 1.0)),
            "random_forest": lambda: RandomForestRegressor(
                n_estimators=hp.get("n_estimators", 100),
                max_depth=hp.get("max_depth", 10),
                min_samples_leaf=hp.get("min_samples_leaf", 3),
                random_state=rs,
            ),
            "svr": lambda: SVR(C=hp.get("C", 1.0), kernel=hp.get("kernel", "rbf")),
            "svm": lambda: SVC(C=hp.get("C", 1.0), probability=True, random_state=rs, kernel=hp.get("kernel", "rbf")),

            "gradient_boosting": lambda: GradientBoostingRegressor(
                n_estimators=hp.get("n_estimators", 100),
                max_depth=hp.get("max_depth", 3),
                random_state=rs,
            ),
        }

    factory = mapping.get(model_type)
    if not factory:
        raise ValueError(f"不支持的模型: {model_type} (任务类型: {task_type})")
    return factory()


@router.post("/train")
async def train_model(
    req: TrainRequest,
    x_session_id: str = Header(...),
):
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        r2_score,
        mean_squared_error,
        mean_absolute_error,
    )

    try:
        df = load_dataset(x_session_id, req.dataset_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="数据集不存在")

    # Validate columns
    all_cols = req.feature_cols + [req.target_col]
    missing = [c for c in all_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"列不存在: {missing}")

    df = df[all_cols].dropna()
    if len(df) < 10:
        raise HTTPException(status_code=400, detail="有效数据少于 10 行，无法训练")

    X = df[req.feature_cols].values
    y = df[req.target_col].values

    hp = req.hyperparams
    test_size = hp.get("test_size", 0.2)
    random_state = hp.get("random_state", 42)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state,
        stratify=y if req.task_type == "classification" else None,
    )

    scaler = None
    if hp.get("scale_features", True):
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    try:
        model = _get_model(req.task_type, req.model_type, hp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    start = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    y_test_prob = None
    if req.task_type == "classification" and hasattr(model, "predict_proba"):
        y_test_prob = model.predict_proba(X_test)

    # Compute metrics
    if req.task_type == "classification":
        train_metrics = {
            "accuracy": round(float(accuracy_score(y_train, y_train_pred)), 4),
            "f1_weighted": round(
                float(f1_score(y_train, y_train_pred, average="weighted", zero_division=0)), 4
            ),
        }
        test_metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_test_pred)), 4),
            "f1_weighted": round(
                float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0)), 4
            ),
        }
    else:
        train_metrics = {
            "r2": round(float(r2_score(y_train, y_train_pred)), 4),
            "rmse": round(float(np.sqrt(mean_squared_error(y_train, y_train_pred))), 4),
            "mae": round(float(mean_absolute_error(y_train, y_train_pred)), 4),
        }
        test_metrics = {
            "r2": round(float(r2_score(y_test, y_test_pred)), 4),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_test_pred))), 4),
            "mae": round(float(mean_absolute_error(y_test, y_test_pred)), 4),
        }

    model_id = f"model_{uuid.uuid4().hex[:12]}"
    class_names = None
    if req.task_type == "classification":
        class_names = [str(c) for c in sorted(set(y))]

    # Detect potential overfitting / data issues
    warnings = []
    if req.task_type == "classification":
        train_acc = train_metrics["accuracy"]
        test_acc = test_metrics["accuracy"]
        if train_acc == 1.0 and test_acc == 1.0:
            warnings.append("训练集和测试集准确率均为 100%，可能存在数据泄漏或数据集过于简单")
        elif train_acc - test_acc > 0.15:
            warnings.append(f"训练集准确率 ({train_acc:.1%}) 远高于测试集 ({test_acc:.1%})，模型可能过拟合")
    else:
        train_r2 = train_metrics["r2"]
        test_r2 = test_metrics["r2"]
        if train_r2 > 0.99 and test_r2 > 0.99:
            warnings.append("训练集和测试集 R² 均接近 1.0，可能存在数据泄漏或数据集过于简单")
        elif train_r2 - test_r2 > 0.2:
            warnings.append(f"训练集 R² ({train_r2:.4f}) 远高于测试集 ({test_r2:.4f})，模型可能过拟合")

    if len(df) < 50:
        warnings.append(f"数据集仅有 {len(df)} 行，样本量较少，评估指标可能不可靠")

    model_store[model_id] = {
        "model": model,
        "scaler": scaler,
        "meta": {
            "task_type": req.task_type,
            "model_type": req.model_type,
            "feature_cols": req.feature_cols,
            "target_col": req.target_col,
            "class_names": class_names,
        },
        "test_data": {
            "X_test": X_test,
            "y_test": y_test,
            "y_pred": y_test_pred,
            "y_prob": y_test_prob,
        },
    }

    return {
        "model_id": model_id,
        "task_type": req.task_type,
        "model_type": req.model_type,
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "training_time_ms": round(training_time * 1000, 1),
        "warnings": warnings,
    }


# ── Async Task Query ──────────────────────────────────────────────────────────


@router.get("/task/{task_id}")
async def get_task(task_id: str):
    task = task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


# ── Prediction ────────────────────────────────────────────────────────────────


@router.post("/predict")
async def predict(
    req: PredictRequest,
    x_session_id: str = Header(default=""),
):
    if not req.model_id:
        raise HTTPException(status_code=400, detail="缺少 model_id")

    entry = model_store.get(req.model_id)
    if not entry:
        raise HTTPException(status_code=404, detail="模型不存在，可能已过期")

    model = entry["model"]
    scaler = entry["scaler"]
    feature_cols = entry["meta"]["feature_cols"]

    if req.dataset_id:
        try:
            df = load_dataset(x_session_id, req.dataset_id)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="数据集不存在")
        missing = [c for c in feature_cols if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"数据集缺少所需列: {missing}")
        X = df[feature_cols].values
    elif req.data:
        df = pd.DataFrame(req.data)
        missing = [c for c in feature_cols if c not in df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"输入数据缺少所需列: {missing}")
        X = df[feature_cols].values
    else:
        raise HTTPException(status_code=400, detail="请提供 data 或 dataset_id")

    if scaler:
        X = scaler.transform(X)

    predictions = model.predict(X).tolist()
    return {"predictions": predictions, "count": len(predictions)}


# ── Visualization ─────────────────────────────────────────────────────────────


@router.get("/model/{model_id}/visualization")
async def get_visualization(model_id: str, chart_type: str = "confusion_matrix"):
    entry = model_store.get(model_id)
    if not entry:
        raise HTTPException(status_code=404, detail="模型不存在，可能已过期")

    meta = entry["meta"]
    test_data = entry["test_data"]
    model = entry["model"]

    echarts_option = _build_chart(
        chart_type,
        meta["task_type"],
        model,
        meta,
        test_data["y_test"],
        test_data["y_pred"],
        test_data.get("y_prob"),
    )
    return {"chart_type": chart_type, "echarts_option": echarts_option}


def _build_chart(chart_type, task_type, model, meta, y_test, y_pred, y_prob):
    """Generate an ECharts option dict."""
    tc = "rgba(255,255,255,0.7)"  # text color for dark theme

    if chart_type == "confusion_matrix":
        if task_type != "classification":
            return _text_chart("混淆矩阵仅支持分类模型", tc)
        from sklearn.metrics import confusion_matrix

        labels = meta.get("class_names") or [str(c) for c in sorted(set(y_test))]
        cm = confusion_matrix(y_test, y_pred)
        data = []
        for i in range(len(labels)):
            for j in range(len(labels)):
                data.append([j, i, int(cm[i][j])])
        return {
            "backgroundColor": "transparent",
            "tooltip": {"position": "top"},
            "grid": {"top": "10%", "left": "20%", "right": "10%", "bottom": "15%"},
            "xAxis": {
                "type": "category", "data": labels, "name": "预测值",
                "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
                "splitArea": {"show": True},
            },
            "yAxis": {
                "type": "category", "data": labels, "name": "真实值",
                "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
                "splitArea": {"show": True},
            },
            "visualMap": {
                "min": 0, "max": int(cm.max()), "calculable": True,
                "orient": "horizontal", "left": "center", "bottom": "0%",
                "inRange": {"color": ["#1a1a2e", "#16213e", "#0f3460", "#e94560"]},
                "textStyle": {"color": tc},
            },
            "series": [{
                "type": "heatmap", "data": data,
                "label": {"show": True, "color": "#fff"},
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.5)"}},
            }],
        }

    elif chart_type == "roc":
        if task_type != "classification" or y_prob is None:
            return _text_chart("ROC 曲线仅支持分类模型（需要概率输出）", tc)
        from sklearn.metrics import roc_curve, auc

        if y_prob.shape[1] == 2:
            # Binary classification
            fpr, tpr, _ = roc_curve(y_test, y_prob[:, 1])
            roc_auc = auc(fpr, tpr)
            roc_data = [[round(float(f), 4), round(float(t), 4)] for f, t in zip(fpr, tpr)]
            return {
                "backgroundColor": "transparent",
                "tooltip": {"trigger": "item"},
                "legend": {
                    "data": [f"ROC (AUC={roc_auc:.3f})", "随机基线"],
                    "textStyle": {"color": tc},
                },
                "grid": {"top": "15%", "left": "12%", "right": "5%", "bottom": "12%"},
                "xAxis": {
                    "type": "value", "name": "False Positive Rate", "min": 0, "max": 1,
                    "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
                },
                "yAxis": {
                    "type": "value", "name": "True Positive Rate", "min": 0, "max": 1,
                    "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
                },
                "series": [
                    {
                        "type": "line", "name": f"ROC (AUC={roc_auc:.3f})",
                        "data": roc_data, "smooth": True,
                        "lineStyle": {"width": 2}, "showSymbol": False,
                        "areaStyle": {"opacity": 0.15},
                    },
                    {
                        "type": "line", "name": "随机基线",
                        "data": [[0, 0], [1, 1]],
                        "lineStyle": {"type": "dashed", "color": "rgba(255,255,255,0.3)"},
                        "showSymbol": False,
                    },
                ],
            }
        else:
            # Multi-class: one-vs-rest
            from sklearn.preprocessing import label_binarize

            classes = sorted(set(y_test))
            y_bin = label_binarize(y_test, classes=classes)
            series = []
            for i, cls in enumerate(classes):
                fpr, tpr, _ = roc_curve(y_bin[:, i], y_prob[:, i])
                roc_auc = auc(fpr, tpr)
                roc_data = [[round(float(f), 4), round(float(t), 4)] for f, t in zip(fpr, tpr)]
                series.append({
                    "type": "line", "name": f"类别 {cls} (AUC={roc_auc:.3f})",
                    "data": roc_data, "smooth": True, "showSymbol": False,
                })
            series.append({
                "type": "line", "name": "随机基线",
                "data": [[0, 0], [1, 1]],
                "lineStyle": {"type": "dashed", "color": "rgba(255,255,255,0.3)"},
                "showSymbol": False,
            })
            return {
                "backgroundColor": "transparent",
                "tooltip": {"trigger": "item"},
                "legend": {"textStyle": {"color": tc}},
                "grid": {"top": "15%", "left": "12%", "right": "5%", "bottom": "12%"},
                "xAxis": {
                    "type": "value", "name": "FPR", "min": 0, "max": 1,
                    "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
                },
                "yAxis": {
                    "type": "value", "name": "TPR", "min": 0, "max": 1,
                    "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
                },
                "series": series,
            }

    elif chart_type == "feature_importance":
        feature_cols = meta["feature_cols"]
        importances = None
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            coef = model.coef_
            importances = np.abs(coef).mean(axis=0) if coef.ndim > 1 else np.abs(coef)

        if importances is None:
            return _text_chart("该模型不支持特征重要性分析", tc)

        indices = np.argsort(importances)
        sorted_names = [feature_cols[i] for i in indices]
        sorted_values = [round(float(importances[i]), 4) for i in indices]

        return {
            "backgroundColor": "transparent",
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"top": "5%", "left": "30%", "right": "10%", "bottom": "5%"},
            "xAxis": {
                "type": "value", "name": "重要性",
                "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
            },
            "yAxis": {
                "type": "category", "data": sorted_names,
                "axisLabel": {"color": tc},
            },
            "series": [{
                "type": "bar", "data": sorted_values,
                "itemStyle": {
                    "color": {
                        "type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0,
                        "colorStops": [
                            {"offset": 0, "color": "#667eea"},
                            {"offset": 1, "color": "#14b8a6"},
                        ],
                    },
                },
                "barMaxWidth": 20,
                "label": {"show": True, "position": "right", "color": tc},
            }],
        }

    elif chart_type == "residuals":
        if task_type != "regression":
            return _text_chart("残差图仅支持回归模型", tc)

        residuals = (y_test - y_pred).tolist()
        data = [[round(float(p), 4), round(float(r), 4)] for p, r in zip(y_pred, residuals)]
        return {
            "backgroundColor": "transparent",
            "tooltip": {"trigger": "item"},
            "grid": {"top": "10%", "left": "12%", "right": "5%", "bottom": "12%"},
            "xAxis": {
                "type": "value", "name": "预测值",
                "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
            },
            "yAxis": {
                "type": "value", "name": "残差 (真实值 - 预测值)",
                "nameTextStyle": {"color": tc}, "axisLabel": {"color": tc},
            },
            "series": [
                {
                    "type": "scatter", "data": data,
                    "symbolSize": 6,
                    "itemStyle": {"color": "#667eea", "opacity": 0.7},
                },
                {
                    "type": "line", "data": [],
                    "markLine": {
                        "data": [{"yAxis": 0}],
                        "lineStyle": {"type": "dashed", "color": "rgba(255,255,255,0.3)"},
                        "label": {"show": False},
                    },
                },
            ],
        }

    else:
        return _text_chart(f"不支持的图表类型: {chart_type}", tc)


def _text_chart(msg: str, color: str) -> dict:
    """Return a minimal ECharts option that just displays a message."""
    return {
        "backgroundColor": "transparent",
        "title": {
            "text": msg,
            "left": "center", "top": "center",
            "textStyle": {"color": color, "fontSize": 14},
        },
    }

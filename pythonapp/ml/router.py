"""
All /ml/* API endpoints for the ML pipeline.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from typing import Optional
import uuid
import time
import logging

logger = logging.getLogger(__name__)
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
from .models import SelectFeaturesRequest, TrainRequest, PredictRequest, PreprocessRequest

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


@router.get("/datasets/{dataset_id}/preview")
async def get_dataset_preview(
    dataset_id: str,
    x_session_id: str = Header(...),
    limit: int = 500,
):
    """返回数据集的预览行，供表格浏览器使用。"""
    try:
        df = load_dataset(x_session_id, dataset_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="数据集不存在")
    rows = df.head(limit).to_dict("records")
    columns = [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns]
    return {
        "row_count": len(df),
        "columns": columns,
        "preview": rows,
    }


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



@router.post("/preprocess")
async def preprocess_data(
    req: PreprocessRequest,
    x_session_id: str = Header(...),
):
    try:
        df = load_dataset(x_session_id, req.dataset_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="数据集不存在")

    warnings = []
    target_col = getattr(req, "target_col", None)  # 可选，仅分组/聚合时用于保留目标列
    
    for step in req.preprocess_steps:
        if step["id"] == "group_by_column":
            config = step.get("config", {})
            group_columns = config.get("columns", [])
            aggregate_function = config.get("aggregateFunction", "sum")
            aggregate_columns = config.get("aggregateColumns", [])
            
            # 验证分组列和聚合列
            missing_group_cols = [c for c in group_columns if c not in df.columns]
            if missing_group_cols:
                raise HTTPException(status_code=400, detail=f"分组列不存在: {missing_group_cols}")
            
            missing_agg_cols = [c for c in aggregate_columns if c not in df.columns]
            if missing_agg_cols:
                raise HTTPException(status_code=400, detail=f"聚合列不存在: {missing_agg_cols}")
            
            # 执行分组和聚合
            try:
                # 构建聚合字典
                agg_dict = {col: aggregate_function for col in aggregate_columns}
                # 如果提供了目标列且不在分组/聚合列中，则保留目标列（用于预览）
                target_col_added = False
                if target_col and str(target_col) in df.columns and target_col not in group_columns and target_col not in aggregate_columns:
                    agg_dict[target_col] = "mean"
                    target_col_added = True
                # 确保至少有一个聚合列
                if not agg_dict:
                    raise HTTPException(status_code=400, detail="请至少选择一个聚合列")
                # 执行分组
                df = df.groupby(group_columns).agg(agg_dict).reset_index()
                # 展平多级列名（如果存在）
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns.values]
                # 如果自动添加了目标列，添加提醒
                if target_col_added:
                    warnings.append(f"目标列 '{target_col}' 已自动加入聚合（使用平均值）")
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=400, detail=f"按列分组失败: {str(e)}")
        
        elif step["id"] == "aggregate_stats":
            config = step.get("config", {})
            group_columns = config.get("groupColumns", [])
            stats_columns = config.get("statsColumns", [])
            stats_functions = config.get("statsFunctions", [])
            
            # 验证统计列
            missing_stats_cols = [c for c in stats_columns if c not in df.columns]
            if missing_stats_cols:
                raise HTTPException(status_code=400, detail=f"统计列不存在: {missing_stats_cols}")
            
            # 验证分组列（可选）
            if group_columns:
                missing_group_cols = [c for c in group_columns if c not in df.columns]
                if missing_group_cols:
                    raise HTTPException(status_code=400, detail=f"分组列不存在: {missing_group_cols}")
            
            # 执行聚合统计
            try:
                # 构建聚合字典，每个统计列可以有多个统计函数
                agg_dict = {}
                for col in stats_columns:
                    agg_dict[col] = stats_functions
                
                # 如果目标列不在统计列中，需要保留目标列
                target_col = req.target_col
                target_col_added = False
                if target_col and str(target_col) in df.columns and target_col not in stats_columns and target_col not in group_columns:
                    agg_dict[target_col] = ["mean"]
                    target_col_added = True
                
                # 确保至少有一个统计列
                if not agg_dict:
                    raise HTTPException(status_code=400, detail="请至少选择一个统计列")
                
                # 如果没有分组列，对整个数据集进行统计
                if group_columns:
                    # 按分组列分组后统计
                    df = df.groupby(group_columns).agg(agg_dict).reset_index()
                    # 展平多级列名
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns.values]
                else:
                    # 对整个数据集进行统计
                    result = {}
                    for col in stats_columns:
                        for func in stats_functions:
                            col_name = f"{col}_{func}"
                            if func == "count":
                                result[col_name] = [df[col].count()]
                            elif func == "sum":
                                result[col_name] = [df[col].sum()]
                            elif func == "mean":
                                result[col_name] = [df[col].mean()]
                            elif func == "median":
                                result[col_name] = [df[col].median()]
                            elif func == "std":
                                result[col_name] = [df[col].std()]
                            elif func == "min":
                                result[col_name] = [df[col].min()]
                            elif func == "max":
                                result[col_name] = [df[col].max()]
                    # 添加目标列的统计
                    if target_col_added:
                        result[f"{target_col}_mean"] = [df[target_col].mean()]
                    df = pd.DataFrame(result)
                
                # 如果自动添加了目标列，添加提醒
                if target_col_added:
                    warnings.append(f"目标列 '{target_col}' 已自动加入统计（使用平均值）")
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=400, detail=f"聚合统计失败: {str(e)}")
        
        elif step["id"] == "math_calc":
            config = step.get("config", {})
            new_column_name = config.get("newColumnName", "")
            calc_type = config.get("calcType", "binary")
            column1 = config.get("column1", "")
            column2 = config.get("column2", "")
            operator = config.get("operator", "+")
            constant_value = config.get("constantValue", 0)
            
            # 验证列存在
            if column1 not in df.columns:
                raise HTTPException(status_code=400, detail=f"列不存在: {column1}")
            if calc_type == "binary" and column2 not in df.columns:
                raise HTTPException(status_code=400, detail=f"列不存在: {column2}")
            
            # 执行数学计算
            try:
                if calc_type == "binary":
                    # 两列运算
                    if operator == "+":
                        df[new_column_name] = df[column1] + df[column2]
                    elif operator == "-":
                        df[new_column_name] = df[column1] - df[column2]
                    elif operator == "*":
                        df[new_column_name] = df[column1] * df[column2]
                    elif operator == "/":
                        df[new_column_name] = df[column1] / df[column2]
                    elif operator == "**":
                        df[new_column_name] = df[column1] ** df[column2]
                elif calc_type == "unary":
                    # 单列运算
                    if operator == "square":
                        df[new_column_name] = df[column1] ** 2
                    elif operator == "sqrt":
                        df[new_column_name] = np.sqrt(df[column1])
                    elif operator == "log":
                        df[new_column_name] = np.log(df[column1])
                    elif operator == "log10":
                        df[new_column_name] = np.log10(df[column1])
                    elif operator == "abs":
                        df[new_column_name] = np.abs(df[column1])
                    elif operator == "round":
                        df[new_column_name] = np.round(df[column1])
                elif calc_type == "constant":
                    # 常量运算
                    if operator == "+":
                        df[new_column_name] = df[column1] + constant_value
                    elif operator == "-":
                        df[new_column_name] = df[column1] - constant_value
                    elif operator == "*":
                        df[new_column_name] = df[column1] * constant_value
                    elif operator == "/":
                        df[new_column_name] = df[column1] / constant_value
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"数学计算失败: {str(e)}")
        
        elif step["id"] == "column_combine":
            config = step.get("config", {})
            new_column_name = config.get("newColumnName", "")
            columns = config.get("columns", [])
            combine_method = config.get("combineMethod", "concat")
            separator = config.get("separator", " ")
            
            # 验证列存在
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                raise HTTPException(status_code=400, detail=f"列不存在: {missing_cols}")
            
            # 执行列组合
            try:
                if combine_method == "concat":
                    # 字符串拼接
                    df[new_column_name] = df[columns].astype(str).agg(separator.join, axis=1)
                elif combine_method == "sum":
                    # 求和
                    df[new_column_name] = df[columns].sum(axis=1)
                elif combine_method == "mean":
                    # 平均值
                    df[new_column_name] = df[columns].mean(axis=1)
                elif combine_method == "product":
                    # 乘积
                    df[new_column_name] = df[columns].prod(axis=1)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列组合失败: {str(e)}")
        
        elif step["id"] in ["to_numeric", "to_string", "to_datetime"]:
            config = step.get("config", {})
            conversion_type = step["id"]
            columns = config.get("columns", [])
            
            # 验证列存在
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                raise HTTPException(status_code=400, detail=f"列不存在: {missing_cols}")
            
            # 执行列类型转换
            try:
                for col in columns:
                    if conversion_type == "to_numeric":
                        # 转数值型
                        error_handling = config.get("errorHandling", "coerce")
                        if error_handling == "ignore":
                            # 忽略错误，保持原值
                            df[col] = pd.to_numeric(df[col], errors="ignore")
                        elif error_handling == "coerce":
                            # 无效值设为NaN
                            df[col] = pd.to_numeric(df[col], errors="coerce")
                        elif error_handling == "default":
                            # 无效值设为默认值
                            default_value = config.get("defaultValue", 0)
                            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default_value)
                    elif conversion_type == "to_string":
                        # 转字符串
                        df[col] = df[col].astype(str)
                    elif conversion_type == "to_datetime":
                        # 转日期时间
                        date_format = config.get("dateFormat", "%Y-%m-%d %H:%M:%S")
                        df[col] = pd.to_datetime(df[col], format=date_format, errors="coerce")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列类型转换失败: {str(e)}")
        
        elif step["id"] in ["one_hot", "label_encode", "tfidf"]:
            config = step.get("config", {})
            encoding_type = step["id"]
            columns = config.get("columns", [])
            
            # 验证列存在
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                raise HTTPException(status_code=400, detail=f"列不存在: {missing_cols}")
            
            # 执行列转向量
            try:
                if encoding_type == "one_hot":
                    # One-Hot编码
                    prefix = config.get("prefix", "")
                    df_encoded = pd.get_dummies(df[columns], prefix=prefix)
                    # 删除原始列，添加编码后的列
                    df = pd.concat([df.drop(columns=columns), df_encoded], axis=1)
                elif encoding_type == "label_encode":
                    # Label编码
                    for col in columns:
                        df[col] = pd.factorize(df[col])[0]
                elif encoding_type == "tfidf":
                    # TF-IDF编码
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    
                    max_features = config.get("maxFeatures", 100)
                    for col in columns:
                        # 将列转换为字符串
                        text_data = df[col].astype(str)
                        # 创建TF-IDF向量化器
                        vectorizer = TfidfVectorizer(max_features=max_features)
                        # 拟合并转换文本数据
                        tfidf_matrix = vectorizer.fit_transform(text_data)
                        # 将稀疏矩阵转换为DataFrame
                        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), 
                                                   columns=[f"{col}_tfidf_{i}" for i in range(tfidf_matrix.shape[1])])
                        # 删除原始列，添加TF-IDF编码后的列
                        df = pd.concat([df.drop(columns=[col]), tfidf_df], axis=1)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列转向量失败: {str(e)}")
        
        elif step["id"] in ["sort_by_column", "move_column"]:
            config = step.get("config", {})
            reorder_type = step["id"]
            
            # 执行列重排
            try:
                if reorder_type == "sort_by_column":
                    # 按列排序
                    sort_columns = config.get("sortColumns", [])
                    sort_order = config.get("sortOrder", "asc")
                    ascending = sort_order == "asc"
                    df = df.sort_values(by=sort_columns, ascending=ascending)
                elif reorder_type == "move_column":
                    # 移动列
                    move_columns = config.get("moveColumns", [])
                    target_position = config.get("targetPosition", 0)
                    
                    # 获取所有列名
                    all_columns = list(df.columns)
                    
                    # 移除要移动的列
                    for col in move_columns:
                        if col in all_columns:
                            all_columns.remove(col)
                    
                    # 在目标位置插入移动的列
                    for i, col in enumerate(move_columns):
                        if col in df.columns:
                            insert_pos = min(target_position + i, len(all_columns))
                            all_columns.insert(insert_pos, col)
                    
                    # 重新排列DataFrame的列
                    df = df[all_columns]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列重排失败: {str(e)}")
        
        elif step["id"] in ["delete_rows", "delete_columns", "drop_na"]:
            config = step.get("config", {})
            delete_type = step["id"]
            
            # 执行删除操作
            try:
                if delete_type == "delete_rows":
                    # 删除行
                    condition_type = config.get("conditionType", "index_range")
                    if condition_type == "index_range":
                        # 按索引范围删除
                        start_index = config.get("startIndex", 0)
                        end_index = config.get("endIndex", len(df) - 1)
                        df = df.drop(df.index[start_index:end_index + 1])
                    elif condition_type == "condition":
                        # 按条件删除
                        condition_column = config.get("conditionColumn", "")
                        operator = config.get("operator", "eq")
                        compare_value = config.get("compareValue", "")
                        
                        # 构建条件
                        if operator == "eq":
                            condition = df[condition_column] == compare_value
                        elif operator == "ne":
                            condition = df[condition_column] != compare_value
                        elif operator == "gt":
                            condition = df[condition_column] > compare_value
                        elif operator == "lt":
                            condition = df[condition_column] < compare_value
                        elif operator == "ge":
                            condition = df[condition_column] >= compare_value
                        elif operator == "le":
                            condition = df[condition_column] <= compare_value
                        else:
                            condition = False
                        
                        df = df[~condition]
                elif delete_type == "delete_columns":
                    # 删除列
                    columns_to_delete = config.get("columns", [])
                    df = df.drop(columns=columns_to_delete)
                elif delete_type == "drop_na":
                    # 删除缺失值
                    drop_na_method = config.get("dropNaMethod", "any")
                    if drop_na_method == "any":
                        # 删除所有包含缺失值的行
                        df = df.dropna()
                    elif drop_na_method == "all":
                        # 删除全部为缺失值的行
                        df = df.dropna(how="all")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"删除操作失败: {str(e)}")

    # Save preprocessed dataset
    dataset_id = save_dataset(x_session_id, df)
    columns = [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns]
    preview_limit = 200

    return {
        "dataset_id": dataset_id,
        "row_count": len(df),
        "col_count": len(df.columns),
        "columns": columns,
        "preview": df.head(preview_limit).to_dict("records"),
        "warnings": warnings
    }

@router.post("/select-features")
async def select_features(
    req: SelectFeaturesRequest,
    x_session_id: str = Header(...),
):
    try:
        df = load_dataset(x_session_id, req.dataset_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="数据集不存在")

    # 初始化警告列表
    warnings = []

    # 应用预处理步骤
    for step in req.preprocess_steps:
        if step["id"] == "group_by_column":
            config = step.get("config", {})
            group_columns = config.get("columns", [])
            aggregate_function = config.get("aggregateFunction", "sum")
            aggregate_columns = config.get("aggregateColumns", [])
            
            # 验证分组列和聚合列
            missing_group_cols = [c for c in group_columns if c not in df.columns]
            if missing_group_cols:
                raise HTTPException(status_code=400, detail=f"分组列不存在: {missing_group_cols}")
            
            missing_agg_cols = [c for c in aggregate_columns if c not in df.columns]
            if missing_agg_cols:
                raise HTTPException(status_code=400, detail=f"聚合列不存在: {missing_agg_cols}")
            
            # 执行分组和聚合
            try:
                # 构建聚合字典
                agg_dict = {col: aggregate_function for col in aggregate_columns}
                # 如果目标列不在分组列或聚合列中，需要保留目标列
                target_col = req.target_col
                target_col_added = False
                if target_col not in group_columns and target_col not in aggregate_columns:
                    # 对目标列使用平均值聚合
                    agg_dict[target_col] = "mean"
                    target_col_added = True
                # 确保至少有一个聚合列
                if not agg_dict:
                    raise HTTPException(status_code=400, detail="请至少选择一个聚合列")
                # 执行分组
                df = df.groupby(group_columns).agg(agg_dict).reset_index()
                # 展平多级列名（如果存在）
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns.values]
                # 如果自动添加了目标列，添加提醒
                if target_col_added:
                    warnings.append(f"目标列 '{target_col}' 已自动加入聚合（使用平均值）")
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=400, detail=f"按列分组失败: {str(e)}")
        
        elif step["id"] == "aggregate_stats":
            config = step.get("config", {})
            group_columns = config.get("groupColumns", [])
            stats_columns = config.get("statsColumns", [])
            stats_functions = config.get("statsFunctions", [])
            
            # 验证统计列
            missing_stats_cols = [c for c in stats_columns if c not in df.columns]
            if missing_stats_cols:
                raise HTTPException(status_code=400, detail=f"统计列不存在: {missing_stats_cols}")
            
            # 验证分组列（可选）
            if group_columns:
                missing_group_cols = [c for c in group_columns if c not in df.columns]
                if missing_group_cols:
                    raise HTTPException(status_code=400, detail=f"分组列不存在: {missing_group_cols}")
            
            # 执行聚合统计
            try:
                # 构建聚合字典，每个统计列可以有多个统计函数
                agg_dict = {}
                for col in stats_columns:
                    agg_dict[col] = stats_functions
                
                # 如果目标列不在统计列中，需要保留目标列
                target_col = req.target_col
                target_col_added = False
                if target_col and str(target_col) in df.columns and target_col not in stats_columns and target_col not in group_columns:
                    agg_dict[target_col] = ["mean"]
                    target_col_added = True
                
                # 确保至少有一个统计列
                if not agg_dict:
                    raise HTTPException(status_code=400, detail="请至少选择一个统计列")
                
                # 如果没有分组列，对整个数据集进行统计
                if group_columns:
                    # 按分组列分组后统计
                    df = df.groupby(group_columns).agg(agg_dict).reset_index()
                    # 展平多级列名
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns.values]
                else:
                    # 对整个数据集进行统计
                    result = {}
                    for col in stats_columns:
                        for func in stats_functions:
                            col_name = f"{col}_{func}"
                            if func == "count":
                                result[col_name] = [df[col].count()]
                            elif func == "sum":
                                result[col_name] = [df[col].sum()]
                            elif func == "mean":
                                result[col_name] = [df[col].mean()]
                            elif func == "median":
                                result[col_name] = [df[col].median()]
                            elif func == "std":
                                result[col_name] = [df[col].std()]
                            elif func == "min":
                                result[col_name] = [df[col].min()]
                            elif func == "max":
                                result[col_name] = [df[col].max()]
                    # 添加目标列的统计
                    if target_col_added:
                        result[f"{target_col}_mean"] = [df[target_col].mean()]
                    df = pd.DataFrame(result)
                
                # 如果自动添加了目标列，添加提醒
                if target_col_added:
                    warnings.append(f"目标列 '{target_col}' 已自动加入统计（使用平均值）")
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=400, detail=f"聚合统计失败: {str(e)}")
        
        elif step["id"] == "math_calc":
            config = step.get("config", {})
            new_column_name = config.get("newColumnName", "")
            calc_type = config.get("calcType", "binary")
            column1 = config.get("column1", "")
            column2 = config.get("column2", "")
            operator = config.get("operator", "+")
            constant_value = config.get("constantValue", 0)
            
            # 验证列存在
            if column1 not in df.columns:
                raise HTTPException(status_code=400, detail=f"列不存在: {column1}")
            if calc_type == "binary" and column2 not in df.columns:
                raise HTTPException(status_code=400, detail=f"列不存在: {column2}")
            
            # 执行数学计算
            try:
                if calc_type == "binary":
                    # 两列运算
                    if operator == "+":
                        df[new_column_name] = df[column1] + df[column2]
                    elif operator == "-":
                        df[new_column_name] = df[column1] - df[column2]
                    elif operator == "*":
                        df[new_column_name] = df[column1] * df[column2]
                    elif operator == "/":
                        df[new_column_name] = df[column1] / df[column2]
                    elif operator == "**":
                        df[new_column_name] = df[column1] ** df[column2]
                elif calc_type == "unary":
                    # 单列运算
                    if operator == "square":
                        df[new_column_name] = df[column1] ** 2
                    elif operator == "sqrt":
                        df[new_column_name] = np.sqrt(df[column1])
                    elif operator == "log":
                        df[new_column_name] = np.log(df[column1])
                    elif operator == "log10":
                        df[new_column_name] = np.log10(df[column1])
                    elif operator == "abs":
                        df[new_column_name] = np.abs(df[column1])
                    elif operator == "round":
                        df[new_column_name] = np.round(df[column1])
                elif calc_type == "constant":
                    # 常量运算
                    if operator == "+":
                        df[new_column_name] = df[column1] + constant_value
                    elif operator == "-":
                        df[new_column_name] = df[column1] - constant_value
                    elif operator == "*":
                        df[new_column_name] = df[column1] * constant_value
                    elif operator == "/":
                        df[new_column_name] = df[column1] / constant_value
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"数学计算失败: {str(e)}")
        
        elif step["id"] == "column_combine":
            config = step.get("config", {})
            new_column_name = config.get("newColumnName", "")
            columns = config.get("columns", [])
            combine_method = config.get("combineMethod", "concat")
            separator = config.get("separator", " ")
            
            # 验证列存在
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                raise HTTPException(status_code=400, detail=f"列不存在: {missing_cols}")
            
            # 执行列组合
            try:
                if combine_method == "concat":
                    # 字符串拼接
                    df[new_column_name] = df[columns].astype(str).agg(separator.join, axis=1)
                elif combine_method == "sum":
                    # 求和
                    df[new_column_name] = df[columns].sum(axis=1)
                elif combine_method == "mean":
                    # 平均值
                    df[new_column_name] = df[columns].mean(axis=1)
                elif combine_method == "product":
                    # 乘积
                    df[new_column_name] = df[columns].prod(axis=1)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列组合失败: {str(e)}")
        
        elif step["id"] in ["to_numeric", "to_string", "to_datetime"]:
            config = step.get("config", {})
            conversion_type = step["id"]
            columns = config.get("columns", [])
            
            # 验证列存在
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                raise HTTPException(status_code=400, detail=f"列不存在: {missing_cols}")
            
            # 执行列类型转换
            try:
                for col in columns:
                    if conversion_type == "to_numeric":
                        # 转数值型
                        error_handling = config.get("errorHandling", "coerce")
                        if error_handling == "ignore":
                            # 忽略错误，保持原值
                            df[col] = pd.to_numeric(df[col], errors="ignore")
                        elif error_handling == "coerce":
                            # 无效值设为NaN
                            df[col] = pd.to_numeric(df[col], errors="coerce")
                        elif error_handling == "default":
                            # 无效值设为默认值
                            default_value = config.get("defaultValue", 0)
                            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default_value)
                    elif conversion_type == "to_string":
                        # 转字符串
                        df[col] = df[col].astype(str)
                    elif conversion_type == "to_datetime":
                        # 转日期时间
                        date_format = config.get("dateFormat", "%Y-%m-%d %H:%M:%S")
                        df[col] = pd.to_datetime(df[col], format=date_format, errors="coerce")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列类型转换失败: {str(e)}")
        
        elif step["id"] in ["one_hot", "label_encode", "tfidf"]:
            config = step.get("config", {})
            encoding_type = step["id"]
            columns = config.get("columns", [])
            
            # 验证列存在
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                raise HTTPException(status_code=400, detail=f"列不存在: {missing_cols}")
            
            # 执行列转向量
            try:
                if encoding_type == "one_hot":
                    # One-Hot编码
                    prefix = config.get("prefix", "")
                    df_encoded = pd.get_dummies(df[columns], prefix=prefix)
                    # 删除原始列，添加编码后的列
                    df = pd.concat([df.drop(columns=columns), df_encoded], axis=1)
                elif encoding_type == "label_encode":
                    # Label编码
                    for col in columns:
                        df[col] = pd.factorize(df[col])[0]
                elif encoding_type == "tfidf":
                    # TF-IDF编码
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    
                    max_features = config.get("maxFeatures", 100)
                    for col in columns:
                        # 将列转换为字符串
                        text_data = df[col].astype(str)
                        # 创建TF-IDF向量化器
                        vectorizer = TfidfVectorizer(max_features=max_features)
                        # 拟合并转换文本数据
                        tfidf_matrix = vectorizer.fit_transform(text_data)
                        # 将稀疏矩阵转换为DataFrame
                        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), 
                                                   columns=[f"{col}_tfidf_{i}" for i in range(tfidf_matrix.shape[1])])
                        # 删除原始列，添加TF-IDF编码后的列
                        df = pd.concat([df.drop(columns=[col]), tfidf_df], axis=1)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列转向量失败: {str(e)}")
        
        elif step["id"] in ["sort_by_column", "move_column"]:
            config = step.get("config", {})
            reorder_type = step["id"]
            
            # 执行列重排
            try:
                if reorder_type == "sort_by_column":
                    # 按列排序
                    sort_columns = config.get("sortColumns", [])
                    sort_order = config.get("sortOrder", "asc")
                    ascending = sort_order == "asc"
                    df = df.sort_values(by=sort_columns, ascending=ascending)
                elif reorder_type == "move_column":
                    # 移动列
                    move_columns = config.get("moveColumns", [])
                    target_position = config.get("targetPosition", 0)
                    
                    # 获取所有列名
                    all_columns = list(df.columns)
                    
                    # 移除要移动的列
                    for col in move_columns:
                        if col in all_columns:
                            all_columns.remove(col)
                    
                    # 在目标位置插入移动的列
                    for i, col in enumerate(move_columns):
                        if col in df.columns:
                            insert_pos = min(target_position + i, len(all_columns))
                            all_columns.insert(insert_pos, col)
                    
                    # 重新排列DataFrame的列
                    df = df[all_columns]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"列重排失败: {str(e)}")
        
        elif step["id"] in ["delete_rows", "delete_columns", "drop_na"]:
            config = step.get("config", {})
            delete_type = step["id"]
            
            # 执行删除操作
            try:
                if delete_type == "delete_rows":
                    # 删除行
                    condition_type = config.get("conditionType", "index_range")
                    if condition_type == "index_range":
                        # 按索引范围删除
                        start_index = config.get("startIndex", 0)
                        end_index = config.get("endIndex", len(df) - 1)
                        df = df.drop(df.index[start_index:end_index + 1])
                    elif condition_type == "condition":
                        # 按条件删除
                        condition_column = config.get("conditionColumn", "")
                        operator = config.get("operator", "eq")
                        compare_value = config.get("compareValue", "")
                        
                        # 构建条件
                        if operator == "eq":
                            condition = df[condition_column] == compare_value
                        elif operator == "ne":
                            condition = df[condition_column] != compare_value
                        elif operator == "gt":
                            condition = df[condition_column] > compare_value
                        elif operator == "lt":
                            condition = df[condition_column] < compare_value
                        elif operator == "ge":
                            condition = df[condition_column] >= compare_value
                        elif operator == "le":
                            condition = df[condition_column] <= compare_value
                        else:
                            condition = False
                        
                        df = df[~condition]
                elif delete_type == "delete_columns":
                    # 删除列
                    columns_to_delete = config.get("columns", [])
                    df = df.drop(columns=columns_to_delete)
                elif delete_type == "drop_na":
                    # 删除缺失值
                    drop_na_method = config.get("dropNaMethod", "any")
                    if drop_na_method == "any":
                        # 删除所有包含缺失值的行
                        df = df.dropna()
                    elif drop_na_method == "all":
                        # 删除全部为缺失值的行
                        df = df.dropna(how="all")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"删除操作失败: {str(e)}")

    all_cols = req.feature_cols + [req.target_col]
    missing = [c for c in all_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"列不存在: {missing}")

    subset = df[all_cols].copy()
    original_count = len(subset)
    subset = subset.dropna()
    dropped = original_count - len(subset)

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

    max_iter = hp.get("max_iter", 2000)

    if task_type == "classification":
        mapping = {
            "logistic_regression": lambda: LogisticRegression(
                max_iter=max_iter, random_state=rs,
            ),
            "random_forest": lambda: RandomForestClassifier(
                n_estimators=hp.get("n_estimators", 100),
                max_depth=hp.get("max_depth", 10),
                min_samples_leaf=hp.get("min_samples_leaf", 3),
                random_state=rs,
                class_weight=hp.get("class_weight"),
            ),
            "svm": lambda: SVC(
                C=hp.get("C", 1.0), kernel=hp.get("kernel", "rbf"),
                max_iter=max_iter, probability=True, random_state=rs,
            ),
            "decision_tree": lambda: DecisionTreeClassifier(
                max_depth=hp.get("max_depth", 8),
                min_samples_leaf=hp.get("min_samples_leaf", 3),
                random_state=rs,
            ),
            "gradient_boosting": lambda: GradientBoostingClassifier(
                n_estimators=hp.get("n_estimators", 100),
                learning_rate=hp.get("learning_rate", 0.1),
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
            "svr": lambda: SVR(
                C=hp.get("C", 1.0), kernel=hp.get("kernel", "rbf"),
                max_iter=max_iter,
            ),
            "gradient_boosting": lambda: GradientBoostingRegressor(
                n_estimators=hp.get("n_estimators", 100),
                learning_rate=hp.get("learning_rate", 0.1),
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
        precision_score,
        recall_score,
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
    # random_state 为 None 时每次划分不同，否则固定种子（如 42）导致相同数据得到相同准确率
    random_state = hp.get("random_state") if "random_state" in hp else 42

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

    n_samples, n_features = X_train.shape
    logger.info(
        "Training model: task=%s model=%s samples=%d features=%d hyperparams=%s",
        req.task_type, req.model_type, n_samples, n_features, hp,
    )
    start = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start
    logger.info("Training completed in %.3fs", training_time)

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
            "precision_weighted": round(
                float(precision_score(y_train, y_train_pred, average="weighted", zero_division=0)), 4
            ),
            "recall_weighted": round(
                float(recall_score(y_train, y_train_pred, average="weighted", zero_division=0)), 4
            ),
        }
        test_metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_test_pred)), 4),
            "f1_weighted": round(
                float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0)), 4
            ),
            "precision_weighted": round(
                float(precision_score(y_test, y_test_pred, average="weighted", zero_division=0)), 4
            ),
            "recall_weighted": round(
                float(recall_score(y_test, y_test_pred, average="weighted", zero_division=0)), 4
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

import pandas as pd
from typing import Union, List, Dict

def process_tables(tables: Union[pd.DataFrame, List[pd.DataFrame], Dict[str, pd.DataFrame]]) -> Dict:
    """
    处理一个或多个表格数据
    
    参数:
    tables: 可以是一个DataFrame，或DataFrame列表，或DataFrame字典
    
    返回:
    dict: 包含处理结果的字典
    """
    result = {
        'status': 'success',
        'message': '',
        'processed_count': 0,
        'table_info': []
    }
    
    try:
        # 判断输入类型并处理
        if isinstance(tables, pd.DataFrame):
            # 单个DataFrame
            table_list = [tables]
        elif isinstance(tables, list):
            # DataFrame列表
            if not all(isinstance(df, pd.DataFrame) for df in tables):
                return {
                    'status': 'failure',
                    'message': '列表中包含非DataFrame对象',
                    'processed_count': 0,
                    'table_info': []
                }
            table_list = tables
        elif isinstance(tables, dict):
            # DataFrame字典
            if not all(isinstance(df, pd.DataFrame) for df in tables.values()):
                return {
                    'status': 'failure',
                    'message': '字典中包含非DataFrame对象',
                    'processed_count': 0,
                    'table_info': []
                }
            table_list = list(tables.values())
        else:
            return {
                'status': 'failure',
                'message': f'不支持的数据类型: {type(tables)}',
                'processed_count': 0,
                'table_info': []
            }
        
        # 处理每个表格
        for i, df in enumerate(table_list):
            if df.empty:
                table_info = {
                    'index': i,
                    'shape': (0, 0),
                    'columns': [],
                    'sample_data': {},
                    'is_valid': True
                }
            else:
                table_info = {
                    'index': i,
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'sample_data': df.head(3).to_dict('records'),  # 前3行作为样本
                    'is_valid': True
                }
            
            result['table_info'].append(table_info)
        
        result['processed_count'] = len(table_list)
        result['message'] = f'成功处理 {len(table_list)} 个表格'
        
        return result
        
    except Exception as e:
        return {
            'status': 'failure',
            'message': f'处理表格时发生错误: {str(e)}',
            'processed_count': 0,
            'table_info': []
        }

def create_sample_tables():
    """创建示例表格用于测试"""
    # 创建第一个示例表格
    df1 = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'London', 'Tokyo']
    })
    
    # 创建第二个示例表格
    df2 = pd.DataFrame({
        'Product': ['Laptop', 'Phone', 'Tablet'],
        'Price': [1200, 800, 600],
        'Stock': [50, 100, 75]
    })
    
    return df1, df2

# 示例使用
if __name__ == "__main__":
    # 创建示例表格
    df1, df2 = create_sample_tables()
    
    print("=== 测试单个表格 ===")
    result = process_tables(df1)
    print(f"状态: {result['status']}")
    print(f"消息: {result['message']}")
    print(f"处理数量: {result['processed_count']}")
    print(f"表格信息: {result['table_info'][0]}")
    
    print("\n=== 测试多个表格列表 ===")
    table_list = [df1, df2]
    result = process_tables(table_list)
    print(f"状态: {result['status']}")
    print(f"消息: {result['message']}")
    print(f"处理数量: {result['processed_count']}")
    for info in result['table_info']:
        print(f"表格{info['index']}: {info['shape'][0]}行x{info['shape'][1]}列")
    
    print("\n=== 测试表格字典 ===")
    table_dict = {'users': df1, 'products': df2}
    result = process_tables(table_dict)
    print(f"状态: {result['status']}")
    print(f"消息: {result['message']}")
    print(f"处理数量: {result['processed_count']}")
    for info in result['table_info']:
        print(f"表格{info['index']}: {info['shape'][0]}行x{info['shape'][1]}列")

"""
数据验证工具
验证股票数据的格式和完整性
"""

from typing import List, Dict, Any, Optional

class DataValidator:
    """
    数据验证器
    """
    
    @staticmethod
    def validate_kline_data(data: List[Dict[str, Any]]) -> bool:
        """
        验证K线数据格式
        
        Args:
            data: K线数据列表
        
        Returns:
            是否验证通过
        """
        if not data:
            return False
        
        required_fields = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        for item in data:
            # 检查必填字段
            for field in required_fields:
                if field not in item:
                    return False
            
            # 检查数据类型
            if not isinstance(item['date'], str):
                return False
            
            # 检查价格字段是否为数字
            price_fields = ['open', 'high', 'low', 'close']
            for field in price_fields:
                if not isinstance(item[field], (int, float)):
                    return False
                if item[field] < 0:
                    return False
            
            # 检查成交量是否为非负整数
            if not isinstance(item['volume'], int):
                return False
            if item['volume'] < 0:
                return False
            
            # 检查价格合理性
            if item['low'] > item['high']:
                return False
            if item['open'] < item['low'] or item['open'] > item['high']:
                return False
            if item['close'] < item['low'] or item['close'] > item['high']:
                return False
        
        return True
    
    @staticmethod
    def validate_realtime_data(data: Dict[str, Any]) -> bool:
        """
        验证实时数据格式
        
        Args:
            data: 实时数据字典
        
        Returns:
            是否验证通过
        """
        required_fields = ['code', 'name', 'price', 'change', 'changePercent', 'time']
        
        # 检查必填字段
        for field in required_fields:
            if field not in data:
                return False
        
        # 检查数据类型
        if not isinstance(data['code'], str):
            return False
        if not isinstance(data['name'], str):
            return False
        if not isinstance(data['time'], str):
            return False
        
        # 检查价格字段是否为数字
        price_fields = ['price', 'change', 'changePercent']
        for field in price_fields:
            if not isinstance(data[field], (int, float)):
                return False
        
        # 检查价格合理性
        if data['price'] < 0:
            return False
        
        return True
    
    @staticmethod
    def validate_stock_list(data: List[Dict[str, str]]) -> bool:
        """
        验证股票列表格式
        
        Args:
            data: 股票列表
        
        Returns:
            是否验证通过
        """
        if not data:
            return False
        
        for item in data:
            if 'code' not in item or 'name' not in item:
                return False
            if not isinstance(item['code'], str) or not isinstance(item['name'], str):
                return False
        
        return True
    
    @staticmethod
    def check_data_consistency(data_sources: List[List[Dict[str, Any]]]) -> bool:
        """
        检查多个数据源的数据一致性
        
        Args:
            data_sources: 多个数据源的数据列表
        
        Returns:
            是否一致
        """
        if len(data_sources) < 2:
            return True
        
        # 检查数据长度是否一致
        base_length = len(data_sources[0])
        for data in data_sources[1:]:
            if len(data) != base_length:
                return False
        
        # 检查关键数据点是否一致（价格差异不超过5%）
        for i in range(min(5, base_length)):  # 只检查前5个数据点
            base_item = data_sources[0][i]
            for data in data_sources[1:]:
                item = data[i]
                # 检查收盘价差异
                if 'close' in base_item and 'close' in item:
                    price_diff = abs(base_item['close'] - item['close'])
                    if base_item['close'] > 0:
                        diff_percent = (price_diff / base_item['close']) * 100
                        if diff_percent > 5:
                            return False
        
        return True
    
    @staticmethod
    def validate_data_quality(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证数据质量并返回统计信息
        
        Args:
            data: 数据列表
        
        Returns:
            数据质量统计信息
        """
        if not data:
            return {
                'valid': False,
                'error': '数据为空'
            }
        
        stats = {
            'valid': True,
            'total_items': len(data),
            'missing_fields': [],
            'invalid_types': [],
            'data_anomalies': []
        }
        
        for i, item in enumerate(data):
            # 检查必填字段
            if 'close' not in item:
                stats['missing_fields'].append(f"第{i}条数据缺少close字段")
                stats['valid'] = False
            
            # 检查价格异常
            if 'close' in item:
                if item['close'] < 0:
                    stats['data_anomalies'].append(f"第{i}条数据价格为负")
                    stats['valid'] = False
                if item['close'] > 10000:  # 价格上限检查
                    stats['data_anomalies'].append(f"第{i}条数据价格异常高")
                    stats['valid'] = False
        
        return stats

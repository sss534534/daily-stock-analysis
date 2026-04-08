"""
数据源配置文件
定义系统支持的数据源及其优先级
"""

# 数据源优先级配置
DATA_SOURCE_PRIORITY = [
    "akshare",      # 优先级最高
    "eastmoney",    # 东方财富
    "tencent",      # 腾讯财经
    "sina",         # 新浪财经
    "mock"          # 模拟数据（最后的备份）
]

# 数据源配置
DATA_SOURCE_CONFIG = {
    "akshare": {
        "name": "akshare",
        "enabled": True,
        "timeout": 10,
        "retry_count": 3
    },
    "eastmoney": {
        "name": "eastmoney",
        "enabled": True,
        "timeout": 8,
        "retry_count": 3
    },
    "tencent": {
        "name": "tencent",
        "enabled": True,
        "timeout": 8,
        "retry_count": 3
    },
    "sina": {
        "name": "sina",
        "enabled": True,
        "timeout": 8,
        "retry_count": 3
    },
    "mock": {
        "name": "mock",
        "enabled": True,
        "timeout": 5,
        "retry_count": 1
    }
}

# API端点配置
API_ENDPOINTS = {
    "eastmoney": {
        "kline": "http://push2his.eastmoney.com/api/qt/stock/kline/get",
        "realtime": "http://push2.eastmoney.com/api/qt/stock/get"
    },
    "tencent": {
        "kline": "https://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={symbol},day,{days},1",
        "realtime": "https://qt.gtimg.cn/q={symbol}"
    },
    "sina": {
        "kline": "https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData",
        "realtime": "https://hq.sinajs.cn/list={symbol}"
    }
}

# 股票代码格式映射
STOCK_CODE_MAPPING = {
    "eastmoney": {
        "prefix": {
            "6": "1.",  # 沪市
            "0": "0.",  # 深市
            "3": "0."   # 创业板
        }
    },
    "tencent": {
        "prefix": {
            "6": "sh",  # 沪市
            "0": "sz",  # 深市
            "3": "sz"   # 创业板
        }
    },
    "sina": {
        "prefix": {
            "6": "sh",  # 沪市
            "0": "sz",  # 深市
            "3": "sz"   # 创业板
        }
    }
}

# 缓存配置
CACHE_CONFIG = {
    "realtime": {
        "expiry": 300,  # 5分钟
        "max_size": 1000
    },
    "kline": {
        "expiry": 600,  # 10分钟
        "max_size": 500
    },
    "stock_list": {
        "expiry": 3600,  # 1小时
        "max_size": 100
    }
}

# 数据源健康检查配置
HEALTH_CHECK_CONFIG = {
    "interval": 300,  # 5分钟检查一次
    "timeout": 5,
    "failure_threshold": 3  # 连续失败3次标记为不健康
}

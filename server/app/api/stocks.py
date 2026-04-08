from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.stocks import Stock, StockHistory, StockDB, StockHistoryDB
from app.database import get_db
from datetime import datetime, timedelta
import tushare as ts
import logging
import json
from functools import lru_cache

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Tushare Pro API
# 注意：这里使用了一个示例token，实际使用时需要替换为真实的token
# 可以在 https://tushare.pro/ 注册获取
PRO_API_TOKEN = '00000000000000000000000000000000000000000000000000'
pro = ts.pro_api(PRO_API_TOKEN)

router = APIRouter()

# 缓存字典，用于存储股票数据
cache: Dict[str, Dict[str, Any]] = {
    'stock_list': {'data': None, 'timestamp': None},
    'stock_realtime': {},
    'stock_kline': {}
}

# 缓存过期时间（秒）
STOCK_LIST_CACHE_EXPIRE = 3600  # 1小时
REALTIME_CACHE_EXPIRE = 60  # 1分钟
KLINE_CACHE_EXPIRE = 300  # 5分钟

# 初始化股票数据
def init_stocks(db: Session):
    # 检查是否已有股票数据
    if db.query(StockDB).count() == 0:
        try:
            # 从Tushare获取股票列表（沪深A股）
            df = pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,list_date'
            )
            
            # 筛选部分股票（前50只）
            top_stocks = df.head(50)
            
            # 插入初始股票数据
            for index, row in top_stocks.iterrows():
                stock = StockDB(
                    code=row['symbol'],
                    name=row['name'],
                    price=0.0,
                    change=0.0,
                    changePercent=0.0,
                    volume=0,
                    marketCap=0
                )
                db.add(stock)
            db.commit()
            logger.info(f"成功从Tushare获取并初始化{len(top_stocks)}只股票数据")
        except Exception as e:
            logger.error(f"初始化股票数据失败: {e}")
            # 如果API调用失败，使用备用数据
            fallback_stocks = [
                {
                    "code": "600036",
                    "name": "招商银行",
                    "price": 38.52,
                    "change": 0.85,
                    "changePercent": 2.26,
                    "volume": 45678900,
                    "marketCap": 980000000000
                },
                {
                    "code": "600519",
                    "name": "贵州茅台",
                    "price": 1685.00,
                    "change": -12.50,
                    "changePercent": -0.74,
                    "volume": 1234500,
                    "marketCap": 2100000000000
                },
                {
                    "code": "000858",
                    "name": "五粮液",
                    "price": 128.36,
                    "change": 2.15,
                    "changePercent": 1.70,
                    "volume": 23456700,
                    "marketCap": 490000000000
                },
                {
                    "code": "000333",
                    "name": "美的集团",
                    "price": 62.84,
                    "change": -0.95,
                    "changePercent": -1.49,
                    "volume": 34567800,
                    "marketCap": 440000000000
                },
                {
                    "code": "601318",
                    "name": "中国平安",
                    "price": 45.28,
                    "change": 1.23,
                    "changePercent": 2.79,
                    "volume": 56789000,
                    "marketCap": 820000000000
                },
                {
                    "code": "300750",
                    "name": "宁德时代",
                    "price": 168.50,
                    "change": -3.20,
                    "changePercent": -1.86,
                    "volume": 67890100,
                    "marketCap": 720000000000
                },
                {
                    "code": "002594",
                    "name": "比亚迪",
                    "price": 234.56,
                    "change": 5.68,
                    "changePercent": 2.48,
                    "volume": 45678900,
                    "marketCap": 680000000000
                },
                {
                    "code": "601398",
                    "name": "工商银行",
                    "price": 5.23,
                    "change": 0.08,
                    "changePercent": 1.55,
                    "volume": 123456700,
                    "marketCap": 1850000000000
                }
            ]
            
            for stock_data in fallback_stocks:
                stock = StockDB(**stock_data)
                db.add(stock)
            db.commit()
            logger.info("使用备用数据初始化股票数据")

# 获取股票列表
@router.get("", response_model=List[Stock])
async def get_stocks(db: Session = Depends(get_db)):
    # 初始化股票数据
    init_stocks(db)
    
    # 检查缓存是否有效
    current_time = datetime.now().timestamp()
    if (cache['stock_list']['data'] is not None and
        current_time - cache['stock_list']['timestamp'] < STOCK_LIST_CACHE_EXPIRE):
        return cache['stock_list']['data']
    
    # 从数据库获取股票列表
    stocks_db = db.query(StockDB).all()
    
    # 转换为API响应格式
    stocks = []
    for stock_db in stocks_db:
        stock = Stock(
            id=str(stock_db.id),
            code=stock_db.code,
            name=stock_db.name,
            price=stock_db.price,
            change=stock_db.change,
            changePercent=stock_db.changePercent,
            volume=stock_db.volume,
            marketCap=stock_db.marketCap
        )
        stocks.append(stock)
    
    # 更新缓存
    cache['stock_list']['data'] = stocks
    cache['stock_list']['timestamp'] = current_time
    
    return stocks

# 获取单个股票详情
@router.get("/{code}", response_model=Stock)
async def get_stock(code: str, db: Session = Depends(get_db)):
    # 初始化股票数据
    init_stocks(db)
    
    # 从数据库获取股票
    stock_db = db.query(StockDB).filter(StockDB.code == code).first()
    
    if stock_db:
        # 转换为API响应格式
        stock = Stock(
            id=str(stock_db.id),
            code=stock_db.code,
            name=stock_db.name,
            price=stock_db.price,
            change=stock_db.change,
            changePercent=stock_db.changePercent,
            volume=stock_db.volume,
            marketCap=stock_db.marketCap
        )
        return stock
    else:
        raise HTTPException(status_code=404, detail="Stock not found")

# 获取股票价格历史
@router.get("/{code}/history", response_model=List[StockHistory])
async def get_stock_history(
    code: str,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    # 初始化股票数据
    init_stocks(db)
    
    # 从数据库获取股票
    stock_db = db.query(StockDB).filter(StockDB.code == code).first()
    
    if stock_db:
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 转换为Tushare需要的格式
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            # 转换代码格式（Tushare需要的格式）
            if code.startswith('6'):
                ts_code = code + '.SH'  # 沪市
            else:
                ts_code = code + '.SZ'  # 深市
            
            # 调用Tushare API获取历史数据
            df = pro.daily(
                ts_code=ts_code,
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            # 转换数据格式
            history = []
            for index, row in df.iterrows():
                # 转换日期格式
                date_str = row['trade_date']
                date = datetime.strptime(date_str, "%Y%m%d")
                
                history.append(StockHistory(
                    date=date.strftime("%Y-%m-%d"),
                    price=row['close'],
                    volume=int(row['vol']),
                    high=row['high'],
                    low=row['low'],
                    open=row['open']
                ))
            
            # 按日期排序（从早到晚）
            history.sort(key=lambda x: x.date)
            
            return history
        except Exception as e:
            logger.error(f"获取股票历史数据失败: {e}")
            # 如果API调用失败，生成模拟数据
            history = []
            base_price = stock_db.price or 100.0
            price = base_price * 0.85
            
            for i in range(days):
                change = (random.random() - 0.48) * (price * 0.03)
                price = max(price + change, base_price * 0.7)
                
                date = datetime.now() - timedelta(days=(days - i))
                
                history.append(StockHistory(
                    date=date.strftime("%Y-%m-%d"),
                    price=round(price, 2),
                    volume=random.randint(5000000, 15000000),
                    high=round(price * 1.02, 2),
                    low=round(price * 0.98, 2),
                    open=round(price * (0.98 + random.random() * 0.04), 2)
                ))
            
            return history
    else:
        raise HTTPException(status_code=404, detail="Stock not found")

# 获取实时K线图数据
@router.get("/{code}/kline")
async def get_stock_kline(
    code: str,
    interval: str = Query(default="1d", regex="^(1m|5m|15m|30m|1h|4h|1d|1w|1M)$"),
    days: int = Query(default=120, ge=1, le=365),
    db: Session = Depends(get_db)
):
    # 初始化股票数据
    init_stocks(db)
    
    # 从数据库获取股票
    stock_db = db.query(StockDB).filter(StockDB.code == code).first()
    
    if not stock_db:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # 检查缓存是否有效
    cache_key = f"{code}_{interval}_{days}"
    current_time = datetime.now().timestamp()
    
    if (cache_key in cache['stock_kline'] and
        current_time - cache['stock_kline'][cache_key]['timestamp'] < KLINE_CACHE_EXPIRE):
        return cache['stock_kline'][cache_key]['data']
    
    try:
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 转换为Tushare需要的格式
        start_date_str = start_date.strftime("%Y%m%d")
        end_date_str = end_date.strftime("%Y%m%d")
        
        # 转换代码格式（Tushare需要的格式）
        if code.startswith('6'):
            ts_code = code + '.SH'  # 沪市
        else:
            ts_code = code + '.SZ'  # 深市
        
        # 根据interval选择不同的Tushare接口
        if interval == '1d':
            # 日线数据
            df = pro.daily(
                ts_code=ts_code,
                start_date=start_date_str,
                end_date=end_date_str
            )
        else:
            # 分钟线数据（需要根据interval选择不同接口）
            # 这里简化处理，使用日线数据
            df = pro.daily(
                ts_code=ts_code,
                start_date=start_date_str,
                end_date=end_date_str
            )
        
        # 转换数据格式
        kline_data = []
        for index, row in df.iterrows():
            # 转换日期格式
            date_str = row['trade_date']
            date = datetime.strptime(date_str, "%Y%m%d")
            
            kline_data.append({
                "timestamp": int(date.timestamp() * 1000),  # 毫秒时间戳
                "date": date.strftime("%Y-%m-%d"),
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close'],
                "volume": row['vol']  # Tushare的成交量字段是vol
            })
        
        # 按日期排序（从早到晚）
        kline_data.sort(key=lambda x: x['timestamp'])
        
        result = {
            "code": code,
            "name": stock_db.name,
            "interval": interval,
            "data": kline_data
        }
        
        # 更新缓存
        cache['stock_kline'][cache_key] = {
            'data': result,
            'timestamp': current_time
        }
        
        return result
    except Exception as e:
        # 如果Tushare API调用失败，回退到模拟数据
        logger.error(f"Tushare API error: {e}")
        # 生成模拟K线数据
        kline_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        base_price = stock_db.price or 100.0
        current_price = base_price * 0.85
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            # 生成随机价格波动
            change = (random.random() - 0.48) * (current_price * 0.03)
            current_price = max(current_price + change, base_price * 0.7)
            
            # 生成高低开收价格
            open_price = round(current_price * (0.98 + random.random() * 0.04), 2)
            high_price = round(max(current_price, open_price) * 1.02, 2)
            low_price = round(min(current_price, open_price) * 0.98, 2)
            close_price = round(current_price, 2)
            
            kline_data.append({
                "timestamp": int(date.timestamp() * 1000),  # 毫秒时间戳
                "date": date.strftime("%Y-%m-%d"),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": random.randint(5000000, 15000000)
            })
        
        result = {
            "code": code,
            "name": stock_db.name,
            "interval": interval,
            "data": kline_data
        }
        
        return result

# 获取实时股票价格
@router.get("/{code}/realtime")
async def get_stock_realtime(
    code: str,
    db: Session = Depends(get_db)
):
    # 初始化股票数据
    init_stocks(db)
    
    # 从数据库获取股票
    stock_db = db.query(StockDB).filter(StockDB.code == code).first()
    
    if not stock_db:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # 检查缓存是否有效
    current_time = datetime.now().timestamp()
    
    if (code in cache['stock_realtime'] and
        current_time - cache['stock_realtime'][code]['timestamp'] < REALTIME_CACHE_EXPIRE):
        return cache['stock_realtime'][code]['data']
    
    try:
        # 转换代码格式（Tushare需要的格式）
        if code.startswith('6'):
            ts_code = code + '.SH'  # 沪市
        else:
            ts_code = code + '.SZ'  # 深市
        
        # 调用Tushare API获取实时行情数据
        # 使用daily接口获取最新交易数据（实际实时行情需要使用trade接口，但需要更高权限）
        df = pro.daily(
            ts_code=ts_code,
            start_date=datetime.now().strftime("%Y%m%d"),
            end_date=datetime.now().strftime("%Y%m%d")
        )
        
        if not df.empty:
            row = df.iloc[0]
            
            # 获取前一天的收盘价用于计算涨跌幅
            prev_day = datetime.now() - timedelta(days=1)
            prev_df = pro.daily(
                ts_code=ts_code,
                start_date=prev_day.strftime("%Y%m%d"),
                end_date=prev_day.strftime("%Y%m%d")
            )
            
            pre_close = prev_df.iloc[0]['close'] if not prev_df.empty else row['open']
            change = row['close'] - pre_close
            change_percent = (change / pre_close) * 100
            
            result = {
                "code": code,
                "name": stock_db.name,
                "price": row['close'],
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "timestamp": int(datetime.now().timestamp() * 1000),
                "volume": row['vol']  # Tushare的成交量字段是vol
            }
            
            # 更新缓存
            cache['stock_realtime'][code] = {
                'data': result,
                'timestamp': current_time
            }
            
            return result
        else:
            # 如果没有当日数据，使用前一天的数据
            df = pro.daily(
                ts_code=ts_code,
                start_date=(datetime.now() - timedelta(days=1)).strftime("%Y%m%d"),
                end_date=(datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            )
            
            if not df.empty:
                row = df.iloc[0]
                
                result = {
                    "code": code,
                    "name": stock_db.name,
                    "price": row['close'],
                    "change": row['change'],
                    "changePercent": row['pct_chg'],
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "volume": row['vol']
                }
                
                # 更新缓存
                cache['stock_realtime'][code] = {
                    'data': result,
                    'timestamp': current_time
                }
                
                return result
            else:
                # 如果没有数据，使用数据库中的数据
                result = {
                    "code": code,
                    "name": stock_db.name,
                    "price": stock_db.price,
                    "change": stock_db.change,
                    "changePercent": stock_db.changePercent,
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "volume": stock_db.volume
                }
                
                return result
    except Exception as e:
        # 如果Tushare API调用失败，使用数据库中的数据
        logger.error(f"Tushare API error: {e}")
        result = {
            "code": code,
            "name": stock_db.name,
            "price": stock_db.price,
            "change": stock_db.change,
            "changePercent": stock_db.changePercent,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "volume": stock_db.volume
        }
        
        return result

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from app.models.portfolio import Position, PortfolioStats, PositionCreate, PositionUpdate, PositionDB
from app.database import get_db
from app.api.stocks import get_stock_realtime

router = APIRouter()

# 初始化投资组合数据
def init_positions(db: Session):
    # 检查是否已有投资组合数据
    if db.query(PositionDB).count() == 0:
        # 初始投资组合数据
        initial_positions = [
            {
                "stockCode": "600036",
                "stockName": "招商银行",
                "shares": 1000,
                "buyPrice": 35.20,
                "currentPrice": 38.52,
                "buyDate": "2023-10-15",
                "profit": 3320,
                "profitPercent": 9.43,
                "totalValue": 38520,
                "cost": 35200
            },
            {
                "stockCode": "600519",
                "stockName": "贵州茅台",
                "shares": 10,
                "buyPrice": 1750.00,
                "currentPrice": 1685.00,
                "buyDate": "2023-11-01",
                "profit": -650,
                "profitPercent": -3.71,
                "totalValue": 16850,
                "cost": 17500
            },
            {
                "stockCode": "002594",
                "stockName": "比亚迪",
                "shares": 200,
                "buyPrice": 210.00,
                "currentPrice": 234.56,
                "buyDate": "2023-12-10",
                "profit": 4912,
                "profitPercent": 11.69,
                "totalValue": 46912,
                "cost": 42000
            }
        ]
        
        # 插入初始投资组合数据
        for position_data in initial_positions:
            position = PositionDB(**position_data)
            db.add(position)
        db.commit()

# 获取投资组合列表
@router.get("", response_model=List[Position])
async def get_positions(db: Session = Depends(get_db)):
    # 初始化投资组合数据
    init_positions(db)
    
    # 从数据库获取投资组合列表
    positions_db = db.query(PositionDB).all()
    
    # 转换为API响应格式并更新最新价格
    positions = []
    for position_db in positions_db:
        # 获取最新股票价格
        try:
            realtime_data = await get_stock_realtime(position_db.stockCode, db)
            current_price = realtime_data["price"]
            
            # 更新当前价格和收益计算
            cost = position_db.shares * position_db.buyPrice
            total_value = position_db.shares * current_price
            profit = round(total_value - cost, 2)
            profit_percent = round((profit / cost) * 100, 2)
            
            # 更新数据库中的价格和收益
            position_db.currentPrice = current_price
            position_db.totalValue = round(total_value, 2)
            position_db.profit = profit
            position_db.profitPercent = profit_percent
            
            # 保存更新
            db.commit()
        except Exception as e:
            print(f"更新实时价格失败: {e}")
            current_price = position_db.currentPrice
            profit = position_db.profit
            profit_percent = position_db.profitPercent
            total_value = position_db.totalValue
        
        position = Position(
            id=str(position_db.id),
            stockCode=position_db.stockCode,
            stockName=position_db.stockName,
            shares=position_db.shares,
            buyPrice=position_db.buyPrice,
            currentPrice=current_price,
            buyDate=position_db.buyDate,
            profit=profit,
            profitPercent=profit_percent,
            totalValue=total_value,
            cost=position_db.cost
        )
        positions.append(position)
    
    return positions

# 添加新持仓
@router.post("", response_model=Position, status_code=201)
async def add_position(position: PositionCreate, db: Session = Depends(get_db)):
    try:
        # 获取真实股票价格
        realtime_data = await get_stock_realtime(position.stockCode, db)
        current_price = realtime_data["price"]
    except Exception as e:
        # 如果获取真实价格失败，使用买入价格作为当前价格
        print(f"获取实时价格失败: {e}")
        current_price = position.buyPrice
    
    cost = position.shares * position.buyPrice
    total_value = position.shares * current_price
    profit = round(total_value - cost, 2)
    profit_percent = round((profit / cost) * 100, 2)
    
    # 创建数据库模型实例
    position_db = PositionDB(
        stockCode=position.stockCode,
        stockName=position.stockName,
        shares=position.shares,
        buyPrice=position.buyPrice,
        currentPrice=current_price,
        buyDate=position.buyDate,
        profit=profit,
        profitPercent=profit_percent,
        totalValue=round(total_value, 2),
        cost=round(cost, 2)
    )
    
    # 保存到数据库
    db.add(position_db)
    db.commit()
    db.refresh(position_db)
    
    # 转换为API响应格式
    new_position = Position(
        id=str(position_db.id),
        stockCode=position_db.stockCode,
        stockName=position_db.stockName,
        shares=position_db.shares,
        buyPrice=position_db.buyPrice,
        currentPrice=position_db.currentPrice,
        buyDate=position_db.buyDate,
        profit=position_db.profit,
        profitPercent=position_db.profitPercent,
        totalValue=position_db.totalValue,
        cost=position_db.cost
    )
    
    return new_position

# 更新持仓
@router.put("/{id}", response_model=Position)
async def update_position(id: str, position_update: PositionUpdate, db: Session = Depends(get_db)):
    # 从数据库获取持仓
    position_db = db.query(PositionDB).filter(PositionDB.id == int(id)).first()
    
    if position_db:
        # 更新持仓信息
        if position_update.shares is not None:
            position_db.shares = position_update.shares
        if position_update.buyPrice is not None:
            position_db.buyPrice = position_update.buyPrice
        
        # 获取最新的股票价格
        try:
            realtime_data = await get_stock_realtime(position_db.stockCode, db)
            position_db.currentPrice = realtime_data["price"]
        except Exception as e:
            print(f"获取实时价格失败: {e}")
        
        # 重新计算相关字段
        cost = position_db.shares * position_db.buyPrice
        total_value = position_db.shares * position_db.currentPrice
        profit = round(total_value - cost, 2)
        profit_percent = round((profit / cost) * 100, 2)
        
        position_db.cost = round(cost, 2)
        position_db.totalValue = round(total_value, 2)
        position_db.profit = profit
        position_db.profitPercent = profit_percent
        
        # 保存到数据库
        db.commit()
        db.refresh(position_db)
        
        # 转换为API响应格式
        position = Position(
            id=str(position_db.id),
            stockCode=position_db.stockCode,
            stockName=position_db.stockName,
            shares=position_db.shares,
            buyPrice=position_db.buyPrice,
            currentPrice=position_db.currentPrice,
            buyDate=position_db.buyDate,
            profit=position_db.profit,
            profitPercent=position_db.profitPercent,
            totalValue=position_db.totalValue,
            cost=position_db.cost
        )
        
        return position
    else:
        raise HTTPException(status_code=404, detail="Position not found")

# 删除持仓
@router.delete("/{id}")
async def delete_position(id: str, db: Session = Depends(get_db)):
    # 从数据库获取持仓
    position_db = db.query(PositionDB).filter(PositionDB.id == int(id)).first()
    
    if position_db:
        # 从数据库删除
        db.delete(position_db)
        db.commit()
        return {"message": "Position deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Position not found")

# 获取投资组合统计信息
@router.get("/stats", response_model=PortfolioStats)
async def get_portfolio_stats(db: Session = Depends(get_db)):
    # 初始化投资组合数据
    init_positions(db)
    
    # 从数据库获取投资组合列表
    positions_db = db.query(PositionDB).all()
    
    # 更新所有持仓的最新价格并计算统计信息
    total_cost = 0
    total_value = 0
    total_profit = 0
    
    for position_db in positions_db:
        # 获取最新股票价格
        try:
            realtime_data = await get_stock_realtime(position_db.stockCode, db)
            current_price = realtime_data["price"]
            
            # 更新当前价格和收益计算
            cost = position_db.shares * position_db.buyPrice
            value = position_db.shares * current_price
            profit = round(value - cost, 2)
            
            # 更新数据库中的价格和收益
            position_db.currentPrice = current_price
            position_db.totalValue = round(value, 2)
            position_db.profit = profit
            position_db.profitPercent = round((profit / cost) * 100, 2)
            
            # 累加统计
            total_cost += cost
            total_value += value
            total_profit += profit
        except Exception as e:
            print(f"更新实时价格失败: {e}")
            total_cost += position_db.cost
            total_value += position_db.totalValue
            total_profit += position_db.profit
    
    # 保存所有更新
    db.commit()
    
    total_profit_percent = round((total_profit / total_cost) * 100, 2) if total_cost > 0 else 0
    position_count = len(positions_db)
    
    # 创建统计信息对象
    stats = PortfolioStats(
        totalCost=round(total_cost, 2),
        totalValue=round(total_value, 2),
        totalProfit=round(total_profit, 2),
        totalProfitPercent=total_profit_percent,
        positionCount=position_count
    )
    
    return stats

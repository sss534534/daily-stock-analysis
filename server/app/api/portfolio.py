from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from app.models.portfolio import Position, PortfolioStats, PositionCreate, PositionUpdate, PositionDB
from app.database import get_db
import random

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
    
    # 转换为API响应格式
    positions = []
    for position_db in positions_db:
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
        positions.append(position)
    
    return positions

# 添加新持仓
@router.post("", response_model=Position, status_code=201)
async def add_position(position: PositionCreate, db: Session = Depends(get_db)):
    # 模拟获取当前价格（实际项目中应该从股票数据中获取）
    current_price = round(position.buyPrice * (0.95 + random.random() * 0.1), 2)
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
    
    # 计算统计信息
    total_cost = sum(p.cost for p in positions_db)
    total_value = sum(p.totalValue for p in positions_db)
    total_profit = sum(p.profit for p in positions_db)
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

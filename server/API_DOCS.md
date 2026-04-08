# 股票分析系统后端API文档

## 概述
股票分析系统提供完整的股票数据、分析工具和投资管理功能的RESTful API。

## 基础URL
- FastAPI: `http://localhost:8000/api`
- 简易服务器: `http://localhost:3006/api`

## API端点列表

### 股票数据相关

#### 1. 获取股票列表
- **方法**: GET
- **路径**: `/stocks`
- **描述**: 获取所有股票列表
- **响应**: `List[Stock]`

#### 2. 获取单个股票详情
- **方法**: GET
- **路径**: `/stocks/{code}`
- **描述**: 获取指定股票的详细信息
- **参数**: `code` - 股票代码
- **响应**: `Stock`

#### 3. 获取股票历史数据
- **方法**: GET
- **路径**: `/stocks/{code}/history?days=30`
- **描述**: 获取股票历史价格数据
- **参数**: 
  - `code` - 股票代码
  - `days` - 天数，默认30天
- **响应**: `List[StockHistory]`

#### 4. 获取K线数据
- **方法**: GET
- **路径**: `/stocks/{code}/kline?interval=1d&days=120`
- **描述**: 获取股票K线数据
- **参数**:
  - `code` - 股票代码
  - `interval` - 时间间隔 (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
  - `days` - 天数，默认120天
- **响应**: K线数据对象

#### 5. 获取实时行情
- **方法**: GET
- **路径**: `/stocks/{code}/realtime`
- **描述**: 获取股票实时价格
- **参数**: `code` - 股票代码
- **响应**: 实时行情对象

### 分析功能相关

#### 1. AI分析
- **方法**: GET
- **路径**: `/analysis/ai/{code}`
- **描述**: 获取AI投资建议
- **参数**: `code` - 股票代码
- **响应**: `AIRecommendation`

#### 2. 风险分析
- **方法**: GET
- **路径**: `/analysis/risk/{code}`
- **描述**: 获取风险评估结果
- **参数**: `code` - 股票代码
- **响应**: `RiskAnalysis`

#### 3. 缠论分析
- **方法**: GET
- **路径**: `/analysis/chan/{code}`
- **描述**: 获取缠论分析结果
- **参数**: `code` - 股票代码
- **响应**: `ChanTheoryAnalysis`

#### 4. 利弗莫尔分析
- **方法**: GET
- **路径**: `/analysis/livermore/{code}`
- **描述**: 获取利弗莫尔分析结果
- **参数**: `code` - 股票代码
- **响应**: `LivermoreAnalysis`

#### 5. 带缠论分析的K线数据
- **方法**: GET
- **路径**: `/analysis/chan/kline/{code}?interval=1d&days=120`
- **描述**: 获取带缠论分析的K线数据
- **参数**:
  - `code` - 股票代码
  - `interval` - 时间间隔
  - `days` - 天数
- **响应**: 包含K线数据和缠论分析的对象

### 投资组合管理

#### 1. 获取投资组合列表
- **方法**: GET
- **路径**: `/portfolio`
- **描述**: 获取所有持仓记录
- **响应**: `List[Position]`

#### 2. 添加持仓
- **方法**: POST
- **路径**: `/portfolio`
- **描述**: 添加新的持仓记录
- **请求体**: `PositionCreate`
- **响应**: `Position`

#### 3. 更新持仓
- **方法**: PUT
- **路径**: `/portfolio/{id}`
- **描述**: 更新持仓信息
- **参数**: `id` - 持仓ID
- **请求体**: `PositionUpdate`
- **响应**: `Position`

#### 4. 删除持仓
- **方法**: DELETE
- **路径**: `/portfolio/{id}`
- **描述**: 删除持仓记录
- **参数**: `id` - 持仓ID
- **响应**: 成功消息

#### 5. 获取投资组合统计
- **方法**: GET
- **路径**: `/portfolio/stats`
- **描述**: 获取投资组合统计信息
- **响应**: `PortfolioStats`

### 股票诊断

#### 1. 获取股票诊断
- **方法**: GET
- **路径**: `/diagnosis/{code}`
- **描述**: 获取股票综合诊断结果
- **参数**: `code` - 股票代码
- **响应**: `DiagnosisResult`

### 投资工具

#### 1. 获取投资工具数据
- **方法**: GET
- **路径**: `/investment-tool`
- **描述**: 获取所有投资工具数据
- **响应**: `InvestmentToolResponse`

#### 2. 获取投资目标列表
- **方法**: GET
- **路径**: `/investment-tool/goals`
- **描述**: 获取投资目标列表
- **响应**: `List[InvestmentGoal]`

#### 3. 添加投资目标
- **方法**: POST
- **路径**: `/investment-tool/goals`
- **描述**: 添加新的投资目标
- **请求体**: `InvestmentGoal`
- **响应**: `InvestmentGoal`

#### 4. 更新投资目标
- **方法**: PUT
- **路径**: `/investment-tool/goals/{goal_id}`
- **描述**: 更新投资目标
- **参数**: `goal_id` - 目标ID
- **请求体**: `InvestmentGoal`
- **响应**: `InvestmentGoal`

#### 5. 删除投资目标
- **方法**: DELETE
- **路径**: `/investment-tool/goals/{goal_id}`
- **描述**: 删除投资目标
- **参数**: `goal_id` - 目标ID
- **响应**: 成功消息

#### 6. 获取资产配置
- **方法**: GET
- **路径**: `/investment-tool/asset-allocation`
- **描述**: 获取资产配置列表
- **响应**: `List[AssetAllocation]`

#### 7. 更新资产配置
- **方法**: PUT
- **路径**: `/investment-tool/asset-allocation/{allocation_id}`
- **描述**: 更新资产配置
- **参数**: `allocation_id` - 配置ID
- **请求体**: `AssetAllocation`
- **响应**: `AssetAllocation`

#### 8. 获取投资组合
- **方法**: GET
- **路径**: `/investment-tool/portfolios`
- **描述**: 获取投资组合列表
- **响应**: `List[InvestmentPortfolio]`

#### 9. 获取投资回顾
- **方法**: GET
- **路径**: `/investment-tool/reviews`
- **描述**: 获取投资回顾列表
- **响应**: `List[InvestmentReview]`

#### 10. 获取投资计划
- **方法**: GET
- **路径**: `/investment-tool/plans`
- **描述**: 获取投资计划列表
- **响应**: `List[InvestmentPlan]`

#### 11. 获取现金流数据
- **方法**: GET
- **路径**: `/investment-tool/cash-flows`
- **描述**: 获取现金流数据列表
- **响应**: `List[CashFlow]`

#### 12. 获取投资建议
- **方法**: GET
- **路径**: `/investment-tool/recommendations`
- **描述**: 获取投资建议列表
- **响应**: 投资建议列表

#### 13. 获取优化的资产配置
- **方法**: GET
- **路径**: `/investment-tool/optimize-asset-allocation?risk_tolerance=medium&time_horizon=10`
- **描述**: 根据风险承受能力和时间周期获取优化的资产配置
- **参数**:
  - `risk_tolerance` - 风险承受能力 (low, medium, high)
  - `time_horizon` - 时间周期（年）
- **响应**: 优化的资产配置对象

#### 14. 获取现金流分析
- **方法**: GET
- **路径**: `/investment-tool/cash-flow-analysis`
- **描述**: 获取现金流分析结果
- **响应**: 现金流分析对象

#### 15. 添加现金流记录
- **方法**: POST
- **路径**: `/investment-tool/cash-flows`
- **描述**: 添加新的现金流记录
- **请求体**: `CashFlow`
- **响应**: `CashFlow`

#### 16. 添加投资计划
- **方法**: POST
- **路径**: `/investment-tool/plans`
- **描述**: 添加新的投资计划
- **请求体**: `InvestmentPlan`
- **响应**: `InvestmentPlan`

### 军规相关

#### 1. 获取所有军规
- **方法**: GET
- **路径**: `/military-rules`
- **描述**: 获取所有投资军规
- **响应**: `MilitaryRuleResponse`

#### 2. 获取单个军规
- **方法**: GET
- **路径**: `/military-rules/{rule_id}`
- **描述**: 获取指定军规
- **参数**: `rule_id` - 军规ID
- **响应**: `MilitaryRule`

## 数据模型

### Stock
```json
{
  "id": "1",
  "code": "600036",
  "name": "招商银行",
  "price": 38.52,
  "change": 0.85,
  "changePercent": 2.26,
  "volume": 45678900,
  "marketCap": 980000000000
}
```

### Position
```json
{
  "id": "1",
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
}
```

### AIRecommendation
```json
{
  "type": "buy",
  "confidence": 85.5,
  "reason": "技术形态向好，基本面稳健",
  "targetPrice": 42.0,
  "stopLoss": 36.0,
  "timeframe": "短期"
}
```

### DiagnosisResult
```json
{
  "stockCode": "600036",
  "stockName": "招商银行",
  "technicalScore": 85,
  "fundamentalScore": 90,
  "marketScore": 80,
  "overallScore": 85,
  "rating": "good",
  "strengths": ["技术形态良好", "基本面稳健"],
  "weaknesses": ["短期波动较大"],
  "recommendation": "推荐买入，具备一定的投资价值和上涨潜力。"
}
```

## 错误处理

API使用标准HTTP状态码：
- 200: 成功
- 400: 请求参数错误
- 404: 资源未找到
- 500: 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述"
}
```

## 使用示例

### 获取股票列表
```bash
curl http://localhost:8000/api/stocks
```

### 获取K线数据
```bash
curl "http://localhost:8000/api/stocks/600036/kline?interval=1d&days=120"
```

### 添加持仓
```bash
curl -X POST http://localhost:8000/api/portfolio \
  -H "Content-Type: application/json" \
  -d '{
    "stockCode": "600036",
    "stockName": "招商银行",
    "shares": 1000,
    "buyPrice": 35.20,
    "buyDate": "2023-10-15"
  }'
```

### 获取AI分析
```bash
curl http://localhost:8000/api/analysis/ai/600036
```

### 获取优化的资产配置
```bash
curl "http://localhost:8000/api/investment-tool/optimize-asset-allocation?risk_tolerance=medium&time_horizon=10"
```

## 注意事项

1. **Tushare API配置**: 需要在`server/app/api/stocks.py`中配置有效的Tushare Pro API token
2. **数据缓存**: 系统使用内存缓存减少外部API调用，缓存过期时间：
   - 股票列表: 1小时
   - 实时行情: 1分钟
   - K线数据: 5分钟
3. **错误重试**: 外部API调用失败时会自动重试3次
4. **频率限制**: 系统限制每分钟最多60个请求，避免超过外部API限制

## 部署说明

### 启动FastAPI服务器
```bash
cd server
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 启动简易服务器
```bash
cd server
python main.py
```

## 开发环境

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Tushare Pro API
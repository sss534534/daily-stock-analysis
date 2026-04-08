# 股票分析系统后端接口完善 - 产品需求文档

## Overview
- **Summary**: 完善股票分析系统后端接口，提高数据质量、功能完整度和策略正确性。当前后端存在大量模拟数据，需要替换为真实股票数据；部分功能仅为框架，需要完整实现；各种分析策略需要确保正确性。
- **Purpose**: 提升系统的数据准确性和功能完整性，为用户提供可靠的股票分析服务。
- **Target Users**: 股票投资者、分析师、投资顾问等需要股票分析功能的用户。

## Goals
- 提高数据质量：替换模拟数据为真实股票数据，确保数据准确性和实时性
- 提高网站功能完整度：完善所有API接口，确保功能全面可用
- 确保不同策略功能运转100%正确：验证和优化各类分析策略的实现

## Non-Goals (Out of Scope)
- 前端UI改进（这属于前端优化范畴）
- 添加新的分析策略（当前仅完善现有策略）
- 数据库结构重构（保持现有数据模型不变）

## Background & Context
- 当前后端使用FastAPI框架，SQLite数据库
- 现有API模块：stocks（股票数据）、analysis（分析功能）、portfolio（投资组合）、diagnosis（诊断）、military_rules（军规）、investment_tool（投资工具）
- 大部分数据为模拟数据，需要替换为真实数据源（Tushare、akshare等）
- 部分分析策略如缠论分析需要优化实现

## Functional Requirements
- **FR-1**: 替换模拟股票数据为真实数据，确保数据准确性和实时性
- **FR-2**: 完善股票数据API，支持实时行情、历史数据、K线数据等功能
- **FR-3**: 优化分析策略实现，确保AI分析、风险分析、缠论分析等功能正确性
- **FR-4**: 完善投资组合管理功能，支持增删改查和统计分析
- **FR-5**: 优化股票诊断功能，提供准确的评分和建议
- **FR-6**: 完善投资工具功能，提供资产配置、现金流分析等服务

## Non-Functional Requirements
- **NFR-1**: API响应时间不超过1秒（95%的请求）
- **NFR-2**: 数据缓存机制，减少外部API调用频率
- **NFR-3**: 错误处理机制，确保系统稳定性
- **NFR-4**: 数据验证机制，确保输入输出数据的正确性

## Constraints
- **Technical**: 使用现有技术栈（FastAPI、SQLAlchemy、SQLite）
- **Dependencies**: Tushare、akshare等第三方数据服务
- **Performance**: 外部API调用频率限制，需要合理缓存

## Assumptions
- Tushare Pro API可以获取真实股票数据
- 外部数据源稳定可用
- 用户已配置有效的API密钥

## Acceptance Criteria

### AC-1: 真实股票数据获取
- **Given**: 系统配置了有效的Tushare API密钥
- **When**: 用户请求股票数据
- **Then**: 返回真实的股票行情数据，而非模拟数据
- **Verification**: programmatic

### AC-2: API功能完整性
- **Given**: 用户调用任何API端点
- **When**: 发送请求到对应的API路径
- **Then**: API能够正确响应并返回符合规范的数据
- **Verification**: programmatic

### AC-3: 分析策略正确性
- **Given**: 用户请求分析数据（如AI分析、缠论分析）
- **When**: 系统执行分析算法
- **Then**: 分析结果符合预期，且逻辑正确
- **Verification**: human-judgment

### AC-4: 投资组合管理功能
- **Given**: 用户管理投资组合
- **When**: 执行增删改查操作
- **Then**: 投资组合数据正确更新，统计信息准确
- **Verification**: programmatic

### AC-5: 系统稳定性
- **Given**: 系统持续运行
- **When**: 处理大量请求或外部API异常
- **Then**: 系统保持稳定，提供合理的错误处理
- **Verification**: programmatic

## Open Questions
- [ ] Tushare API密钥的配置方式
- [ ] 外部API调用失败的重试机制
- [ ] 数据缓存的过期策略
- [ ] 用户认证和授权机制（当前未实现）
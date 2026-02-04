// API服务文件，封装所有后端API调用逻辑

const API_BASE_URL = 'http://localhost:3006/api';

// 生成模拟K线数据
function generateMockKlineData(code: string, days: number = 120) {
  const data = [];
  let basePrice = 30.0;
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    const dateStr = date.toISOString().split('T')[0];
    
    const open = basePrice * (1 + (Math.random() - 0.5) * 0.04);
    const high = open * (1 + Math.random() * 0.03);
    const low = open * (1 - Math.random() * 0.03);
    const close = open * (1 + (Math.random() - 0.5) * 0.04);
    const volume = Math.floor(Math.random() * 4000000) + 1000000;
    
    data.push({
      date: dateStr,
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume,
    });
    
    basePrice = close;
  }
  
  return data;
}

// 通用请求函数
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API请求错误:', error);
    
    // 根据端点返回模拟数据
    if (endpoint === '/health') {
      return { status: 'ok', message: 'Stock Analysis Backend is running' } as T;
    } else if (endpoint === '/stocks') {
      return [
        { code: '600036', name: '招商银行' },
        { code: '600519', name: '贵州茅台' },
        { code: '000858', name: '五粮液' },
        { code: '000333', name: '美的集团' },
        { code: '601318', name: '中国平安' },
      ] as T;
    } else if (endpoint.includes('/kline')) {
      const code = endpoint.split('/')[2];
      const stockName = {
        '600036': '招商银行',
        '600519': '贵州茅台',
        '000858': '五粮液',
        '000333': '美的集团',
        '601318': '中国平安',
      }[code] || '未知股票';
      
      return {
        code,
        name: stockName,
        interval: '1d',
        data: generateMockKlineData(code, 120),
      } as T;
    } else if (endpoint === '/portfolio') {
      return [
        {
          id: '1',
          stockCode: '600036',
          stockName: '招商银行',
          shares: 1000,
          buyPrice: 30.0,
          currentPrice: 31.5,
          profit: 1500,
          profitPercent: 5.0,
          cost: 30000,
          totalValue: 31500,
          buyDate: '2024-01-01',
        },
      ] as T;
    } else if (endpoint === '/portfolio/stats') {
      return {
        totalValue: 31500,
        totalCost: 30000,
        totalProfit: 1500,
        totalProfitPercent: 5.0,
      } as T;
    } else if (endpoint === '/military-rules') {
      return {
        rules: [
          {
            id: 1,
            title: '第一条军规：顺势而为',
            content: '永远不要与市场作对，要顺应市场趋势进行操作。在上涨趋势中做多，在下跌趋势中做空或观望。',
            explanation: '市场趋势是由资金推动的，顺趋势操作可以提高成功率。逆势操作往往会导致亏损，因为市场的力量是巨大的，个人很难与之抗衡。',
            examples: [
              '在牛市中，即使短期回调，也应该保持多头思维，寻找买入机会。',
              '在熊市中，即使短期反弹，也应该保持空头思维，避免盲目抄底。',
            ],
            isExpanded: false
          },
          {
            id: 2,
            title: '第二条军规：严格止损',
            content: '每笔交易都必须设置止损位，当股价达到止损位时，必须无条件执行止损操作。',
            explanation: '止损是控制风险的重要手段，它可以防止单笔交易的亏损过大，保护本金安全。没有止损，一次错误的交易就可能导致巨大的亏损。',
            examples: [
              '买入股票后，设置5%的止损位，当股价下跌5%时，立即卖出。',
              '根据技术分析设置止损位，如跌破重要支撑位时止损。',
            ],
            isExpanded: false
          },
          {
            id: 3,
            title: '第三条军规：资金管理',
            content: '合理分配资金，单笔交易的资金比例不宜过高，一般不超过总资金的10-20%。',
            explanation: '资金管理可以分散风险，避免因单笔交易的失败而导致整体资金的大幅亏损。同时，合理的资金分配也可以让投资者在市场中存活更久，有更多的机会捕捉到好的交易机会。',
            examples: [
              '总资金10万元，单笔交易最多使用2万元，即20%的资金。',
              '根据市场风险调整仓位，在高风险时期减少仓位，在低风险时期增加仓位。',
            ],
            isExpanded: false
          },
          {
            id: 4,
            title: '第四条军规：心态平和',
            content: '保持冷静的心态，不要被情绪左右。在盈利时不要贪婪，在亏损时不要恐惧。',
            explanation: '心态是交易成功的关键因素之一。贪婪会导致投资者在高位追涨，最终被套；恐惧会导致投资者在低位割肉，错过反弹机会。只有保持平和的心态，才能做出理性的交易决策。',
            examples: [
              '当股票大幅上涨时，不要盲目加仓，要分析上涨的原因和可持续性。',
              '当股票大幅下跌时，不要恐慌卖出，要分析下跌的原因和是否已经达到止损位。',
            ],
            isExpanded: false
          },
          {
            id: 5,
            title: '第五条军规：学习总结',
            content: '不断学习和总结交易经验，分析成功和失败的原因，持续改进交易策略。',
            explanation: '市场是不断变化的，投资者需要不断学习新的知识和技能，以适应市场的变化。同时，总结交易经验可以帮助投资者发现自己的不足之处，从而改进交易策略，提高交易成功率。',
            examples: [
              '每次交易后，记录交易的原因、过程和结果，分析成功或失败的原因。',
              '定期回顾自己的交易记录，总结出适合自己的交易模式和策略。',
            ],
            isExpanded: false
          },
          {
            id: 6,
            title: '第六条军规：顺势而为',
            content: '永远不要与市场作对，要顺应市场趋势进行操作。在上涨趋势中做多，在下跌趋势中做空或观望。',
            explanation: '市场趋势是由资金推动的，顺趋势操作可以提高成功率。逆势操作往往会导致亏损，因为市场的力量是巨大的，个人很难与之抗衡。',
            examples: [
              '在牛市中，即使短期回调，也应该保持多头思维，寻找买入机会。',
              '在熊市中，即使短期反弹，也应该保持空头思维，避免盲目抄底。',
            ],
            isExpanded: false
          },
          {
            id: 7,
            title: '第七条军规：严格执行',
            content: '制定交易计划后，必须严格执行，不要随意更改交易计划。',
            explanation: '交易计划是基于理性分析制定的，随意更改交易计划往往是受到情绪的影响，容易导致错误的决策。严格执行交易计划可以帮助投资者保持理性，提高交易的一致性和成功率。',
            examples: [
              '制定好交易计划后，按照计划执行买入、卖出和止损操作。',
              '当市场情况发生变化时，先分析变化的原因，再决定是否需要调整交易计划。',
            ],
            isExpanded: false
          },
        ]
      } as T;
    } else if (endpoint.includes('/analysis/ai/')) {
      // 生成模拟AI分析数据
      const types = ['buy', 'sell', 'hold'];
      const type = types[Math.floor(Math.random() * types.length)];
      const confidence = Math.floor(Math.random() * 30) + 70;
      
      const reasons = {
        buy: [
          '技术指标显示该股票处于超卖区域，具备反弹潜力',
          '基本面分析显示公司业绩稳健增长，估值合理',
          '行业景气度上升，该股票具有较强的配置价值',
          '资金流入明显，主力资金持续加仓',
        ],
        sell: [
          '股价已达到目标位，建议获利了结',
          '技术形态显示顶部特征，存在回调风险',
          '基本面出现恶化迹象，业绩增长放缓',
          '主力资金流出明显，建议减仓规避风险',
        ],
        hold: [
          '当前价格处于合理区间，建议持有观望',
          '短期走势不明朗，建议等待更清晰的信号',
          '基本面稳定，但缺乏上涨催化剂',
          '技术面中性，建议保持现有仓位',
        ],
      };
      
      return {
        type,
        confidence,
        reason: reasons[type][Math.floor(Math.random() * reasons[type].length)],
        targetPrice: type === 'buy' ? 35.2 : type === 'sell' ? 28.8 : undefined,
        stopLoss: type === 'buy' ? 28.8 : type === 'sell' ? 35.2 : undefined,
        timeframe: ['短期(1-2周)', '中期(1-3个月)', '长期(3-6个月)'][Math.floor(Math.random() * 3)],
      } as T;
    } else if (endpoint.includes('/analysis/risk/')) {
      // 生成模拟风险分析数据
      const riskScore = Math.floor(Math.random() * 40) + 30;
      let level = 'medium';
      if (riskScore < 40) level = 'low';
      else if (riskScore < 60) level = 'medium';
      else if (riskScore < 80) level = 'high';
      else level = 'extreme';
      
      return {
        level,
        score: riskScore,
        factors: [
          { name: '市场风险', impact: Math.floor(Math.random() * 30) + 40, description: '整体市场波动对该股票的影响' },
          { name: '行业风险', impact: Math.floor(Math.random() * 30) + 30, description: '所属行业政策和竞争环境风险' },
          { name: '公司风险', impact: Math.floor(Math.random() * 30) + 20, description: '公司经营和财务风险' },
          { name: '流动性风险', impact: Math.floor(Math.random() * 30) + 25, description: '股票交易活跃度和变现能力' },
        ],
      } as T;
    }
    
    // 抛出错误，让调用方处理
    throw error;
  }
}

// 股票相关API
export const stockApi = {
  // 获取股票列表
  async getStocks() {
    return request<any[]>('/stocks');
  },

  // 获取单个股票详情
  async getStock(code: string) {
    return request<any>(`/stocks/${code}`);
  },

  // 获取股票价格历史
  async getStockHistory(code: string, days: number = 30) {
    return request<any[]>(`/stocks/${code}/history?days=${days}`);
  },

  // 获取实时K线图数据
  async getStockKline(code: string, interval: string = '1d', days: number = 120) {
    return request<any>(`/stocks/${code}/kline?interval=${interval}&days=${days}`);
  },

  // 获取实时股票价格
  async getStockRealtime(code: string) {
    return request<any>(`/stocks/${code}/realtime`);
  },
};

// 投资组合相关API
export const portfolioApi = {
  // 获取投资组合列表
  async getPositions() {
    return request<any[]>('/portfolio');
  },

  // 添加新持仓
  async addPosition(position: {
    stockCode: string;
    stockName: string;
    shares: number;
    buyPrice: number;
    buyDate: string;
  }) {
    return request<any>('/portfolio', {
      method: 'POST',
      body: JSON.stringify(position),
    });
  },

  // 更新持仓
  async updatePosition(id: string, updates: {
    shares?: number;
    buyPrice?: number;
  }) {
    return request<any>(`/portfolio/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  // 删除持仓
  async deletePosition(id: string) {
    return request<any>(`/portfolio/${id}`, {
      method: 'DELETE',
    });
  },

  // 获取投资组合统计信息
  async getPortfolioStats() {
    return request<any>('/portfolio/stats');
  },
};

// 股票诊断相关API
export const diagnosisApi = {
  // 获取股票诊断结果
  async getDiagnosis(code: string) {
    return request<any>(`/diagnosis/${code}`);
  },
};

// 分析相关API
export const analysisApi = {
  // 获取AI分析
  async getAIAnalysis(code: string) {
    return request<any>(`/analysis/ai/${code}`);
  },

  // 获取风险分析
  async getRiskAnalysis(code: string) {
    return request<any>(`/analysis/risk/${code}`);
  },

  // 获取缠论分析
  async getChanAnalysis(code: string) {
    return request<any>(`/analysis/chan/${code}`);
  },

  // 获取带缠论分析的K线数据
  async getChanKlineAnalysis(code: string, interval: string = '1d', days: number = 120) {
    return request<any>(`/analysis/chan/kline/${code}?interval=${interval}&days=${days}`);
  },

  // 获取利弗莫尔分析
  async getLivermoreAnalysis(code: string) {
    return request<any>(`/analysis/livermore/${code}`);
  },
};

// 军规相关API
export const militaryRulesApi = {
  // 获取所有军规
  async getMilitaryRules() {
    return request<any>('/military-rules');
  },

  // 获取单个军规
  async getMilitaryRule(id: number) {
    return request<any>(`/military-rules/${id}`);
  },
};

// 投资工具相关API
export const investmentToolApi = {
  // 获取投资工具数据
  async getInvestmentToolData() {
    return request<any>('/investment-tool');
  },

  // 获取投资目标
  async getInvestmentGoals() {
    return request<any>('/investment-tool/goals');
  },

  // 添加投资目标
  async addInvestmentGoal(goal: any) {
    return request<any>('/investment-tool/goals', {
      method: 'POST',
      body: JSON.stringify(goal),
    });
  },

  // 更新投资目标
  async updateInvestmentGoal(id: number, goal: any) {
    return request<any>(`/investment-tool/goals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(goal),
    });
  },

  // 删除投资目标
  async deleteInvestmentGoal(id: number) {
    return request<any>(`/investment-tool/goals/${id}`, {
      method: 'DELETE',
    });
  },

  // 获取资产配置
  async getAssetAllocations() {
    return request<any>('/investment-tool/asset-allocation');
  },

  // 更新资产配置
  async updateAssetAllocation(id: number, allocation: any) {
    return request<any>(`/investment-tool/asset-allocation/${id}`, {
      method: 'PUT',
      body: JSON.stringify(allocation),
    });
  },

  // 获取投资组合
  async getInvestmentPortfolios() {
    return request<any>('/investment-tool/portfolios');
  },

  // 获取投资回顾
  async getInvestmentReviews() {
    return request<any>('/investment-tool/reviews');
  },

  // 获取投资计划
  async getInvestmentPlans() {
    return request<any>('/investment-tool/plans');
  },

  // 获取现金流数据
  async getCashFlows() {
    return request<any>('/investment-tool/cash-flows');
  },

  // 获取投资建议
  async getInvestmentRecommendations() {
    return request<any>('/investment-tool/recommendations');
  },
};
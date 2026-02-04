// API服务文件，封装所有后端API调用逻辑

const API_BASE_URL = 'http://localhost:3004/api';

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
// API服务文件，封装所有后端API调用逻辑

const API_BASE_URL = 'http://localhost:3006/api';

// 缓存配置
const CACHE_CONFIG = {
  MAX_SIZE: 100,
  DEFAULT_TTL: 5 * 60 * 1000, // 默认5分钟
};

// 缓存项接口
interface CacheItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

// LRU缓存类
class LRUCache {
  private cache: Map<string, CacheItem<any>> = new Map();
  private maxSize: number;

  constructor(maxSize: number = CACHE_CONFIG.MAX_SIZE) {
    this.maxSize = maxSize;
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;

    // 检查是否过期
    if (Date.now() > item.timestamp + item.ttl) {
      this.cache.delete(key);
      return null;
    }

    // 更新访问顺序（LRU）
    this.cache.delete(key);
    this.cache.set(key, item);

    return item.data;
  }

  set<T>(key: string, data: T, ttl: number = CACHE_CONFIG.DEFAULT_TTL): void {
    // 如果缓存已满，删除最久未使用的项
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }

  has(key: string): boolean {
    return this.cache.has(key);
  }
}

// 创建全局缓存实例
const apiCache = new LRUCache();

// 移除模拟数据生成函数，使用真实后端API

// 日志记录函数
function log(level: 'info' | 'warn' | 'error' | 'debug', message: string, data?: any): void {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  
  switch (level) {
    case 'info':
      console.info(logMessage, data || '');
      break;
    case 'warn':
      console.warn(logMessage, data || '');
      break;
    case 'error':
      console.error(logMessage, data || '');
      break;
    case 'debug':
      console.debug(logMessage, data || '');
      break;
  }
}

// 请求频率限制器
class RateLimiter {
  private requests: Map<string, { count: number; resetTime: number }> = new Map();
  private windowMs: number;
  private maxRequests: number;

  constructor(maxRequests: number = 60, windowMs: number = 60 * 1000) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
  }

  isAllowed(key: string): boolean {
    const now = Date.now();
    const entry = this.requests.get(key);

    if (!entry) {
      this.requests.set(key, {
        count: 1,
        resetTime: now + this.windowMs,
      });
      return true;
    }

    if (now > entry.resetTime) {
      this.requests.set(key, {
        count: 1,
        resetTime: now + this.windowMs,
      });
      return true;
    }

    if (entry.count >= this.maxRequests) {
      return false;
    }

    this.requests.set(key, {
      count: entry.count + 1,
      resetTime: entry.resetTime,
    });
    return true;
  }
}

// 创建全局速率限制器实例
const rateLimiter = new RateLimiter(60, 60 * 1000); // 每分钟60个请求

// 请求选项接口
interface RequestOptions extends RequestInit {
  cache?: boolean;
  ttl?: number;
  retry?: boolean;
  maxRetries?: number;
  retryDelay?: number;
}

// 通用请求函数
async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const {
    cache = true,
    ttl = CACHE_CONFIG.DEFAULT_TTL,
    retry = true,
    maxRetries = 3,
    retryDelay = 1000,
    ...fetchOptions
  } = options;

  // 生成缓存键
  const cacheKey = `${endpoint}_${JSON.stringify(fetchOptions)}`;

  // 检查缓存
  if (cache) {
    const cachedData = apiCache.get<T>(cacheKey);
    if (cachedData) {
      log('debug', `缓存命中: ${endpoint}`);
      return cachedData;
    }
  }

  // 检查速率限制
  const rateLimitKey = endpoint.split('?')[0];
  if (!rateLimiter.isAllowed(rateLimitKey)) {
    log('warn', `请求频率超限: ${endpoint}`);
    throw new Error('请求频率过高，请稍后重试');
  }

  let retries = 0;

  while (true) {
    try {
      log('info', `发起请求: ${endpoint}`);
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...fetchOptions,
        headers: {
          'Content-Type': 'application/json',
          ...fetchOptions.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // 缓存响应数据
      if (cache) {
        apiCache.set(cacheKey, data, ttl);
        log('debug', `缓存数据: ${endpoint}`);
      }

      log('info', `请求成功: ${endpoint}`);
      return data;
    } catch (error: any) {
      retries++;
      log('error', `请求失败: ${endpoint}`, { error: error.message, retry: retries });

      if (!retry || retries >= maxRetries) {
        log('warn', `达到最大重试次数: ${endpoint}`);
        // 直接抛出错误，让调用方处理
        throw error;
      }

      // 指数退避策略
      const delay = retryDelay * Math.pow(2, retries - 1);
      log('info', `等待重试: ${endpoint}`, { delay });
      await new Promise(resolve => setTimeout(resolve, delay));
    }
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
// 收益跟踪工具

export interface ProfitRecord {
  date: string;
  totalValue: number;
  totalCost: number;
  profit: number;
  profitPercent: number;
}

const PROFIT_HISTORY_KEY = 'profit_history';

// 获取收益历史
export const getProfitHistory = (): ProfitRecord[] => {
  try {
    const data = localStorage.getItem(PROFIT_HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load profit history:', error);
    return [];
  }
};

// 保存收益历史
export const saveProfitHistory = (history: ProfitRecord[]): void => {
  try {
    localStorage.setItem(PROFIT_HISTORY_KEY, JSON.stringify(history));
  } catch (error) {
    console.error('Failed to save profit history:', error);
  }
};

// 添加今日收益记录
export const addTodayProfit = (totalValue: number, totalCost: number): void => {
  const history = getProfitHistory();
  const today = new Date().toISOString().split('T')[0];
  
  // 检查今天是否已有记录
  const existingIndex = history.findIndex(record => record.date === today);
  
  const profit = totalValue - totalCost;
  const profitPercent = totalCost > 0 ? (profit / totalCost) * 100 : 0;
  
  const newRecord: ProfitRecord = {
    date: today,
    totalValue,
    totalCost,
    profit,
    profitPercent,
  };
  
  if (existingIndex >= 0) {
    // 更新今天的记录
    history[existingIndex] = newRecord;
  } else {
    // 添加新记录
    history.push(newRecord);
  }
  
  // 只保留最近90天的数据
  const ninetyDaysAgo = new Date();
  ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
  const filtered = history.filter(record => new Date(record.date) >= ninetyDaysAgo);
  
  // 按日期排序
  filtered.sort((a, b) => a.date.localeCompare(b.date));
  
  saveProfitHistory(filtered);
};

// 生成模拟历史数据（用于演示）
export const generateMockProfitHistory = (totalValue: number, totalCost: number, days: number = 30): ProfitRecord[] => {
  const history: ProfitRecord[] = [];
  const today = new Date();
  
  let currentValue = totalCost * 0.95; // 从-5%开始
  const targetValue = totalValue;
  const dailyChange = (targetValue - currentValue) / days;
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // 添加一些随机波动
    const randomFactor = 1 + (Math.random() - 0.5) * 0.02; // ±1%的随机波动
    currentValue = currentValue + dailyChange * randomFactor;
    
    const profit = currentValue - totalCost;
    const profitPercent = totalCost > 0 ? (profit / totalCost) * 100 : 0;
    
    history.push({
      date: date.toISOString().split('T')[0],
      totalValue: parseFloat(currentValue.toFixed(2)),
      totalCost,
      profit: parseFloat(profit.toFixed(2)),
      profitPercent: parseFloat(profitPercent.toFixed(2)),
    });
  }
  
  return history;
};

// 计算日收益
export const calculateDailyProfit = (history: ProfitRecord[]): {
  value: number;
  percent: number;
} => {
  if (history.length < 2) {
    return { value: 0, percent: 0 };
  }
  
  const today = history[history.length - 1];
  const yesterday = history[history.length - 2];
  
  const value = today.profit - yesterday.profit;
  const percent = yesterday.totalValue > 0 
    ? ((today.totalValue - yesterday.totalValue) / yesterday.totalValue) * 100
    : 0;
  
  return {
    value: parseFloat(value.toFixed(2)),
    percent: parseFloat(percent.toFixed(2)),
  };
};

// 计算周收益
export const calculateWeeklyProfit = (history: ProfitRecord[]): {
  value: number;
  percent: number;
} => {
  if (history.length === 0) {
    return { value: 0, percent: 0 };
  }
  
  const today = history[history.length - 1];
  
  // 获取7天前的记录
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  const sevenDaysAgoStr = sevenDaysAgo.toISOString().split('T')[0];
  
  // 找到最接近7天前的记录
  let weekAgo = history[0];
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].date <= sevenDaysAgoStr) {
      weekAgo = history[i];
      break;
    }
  }
  
  const value = today.profit - weekAgo.profit;
  const percent = weekAgo.totalValue > 0 
    ? ((today.totalValue - weekAgo.totalValue) / weekAgo.totalValue) * 100
    : 0;
  
  return {
    value: parseFloat(value.toFixed(2)),
    percent: parseFloat(percent.toFixed(2)),
  };
};

// 计算月收益
export const calculateMonthlyProfit = (history: ProfitRecord[]): {
  value: number;
  percent: number;
} => {
  if (history.length === 0) {
    return { value: 0, percent: 0 };
  }
  
  const today = history[history.length - 1];
  
  // 获取30天前的记录
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const thirtyDaysAgoStr = thirtyDaysAgo.toISOString().split('T')[0];
  
  // 找到最接近30天前的记录
  let monthAgo = history[0];
  for (let i = history.length - 1; i >= 0; i--) {
    if (history[i].date <= thirtyDaysAgoStr) {
      monthAgo = history[i];
      break;
    }
  }
  
  const value = today.profit - monthAgo.profit;
  const percent = monthAgo.totalValue > 0 
    ? ((today.totalValue - monthAgo.totalValue) / monthAgo.totalValue) * 100
    : 0;
  
  return {
    value: parseFloat(value.toFixed(2)),
    percent: parseFloat(percent.toFixed(2)),
  };
};

// 获取近期收益趋势（用于图表）
export const getRecentProfitTrend = (history: ProfitRecord[], days: number = 30) => {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);
  const cutoffStr = cutoffDate.toISOString().split('T')[0];
  
  return history.filter(record => record.date >= cutoffStr);
};

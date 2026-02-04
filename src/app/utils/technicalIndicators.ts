// 技术指标计算工具

export interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  price: number;
  volume: number;
}

export interface MACDData {
  date: string;
  dif: number;
  dea: number;
  macd: number;
}

export interface KDJData {
  date: string;
  k: number;
  d: number;
  j: number;
}

export interface VolumeRatioData {
  date: string;
  volumeRatio: number;
  volume: number;
}

// 计算EMA（指数移动平均）
function calculateEMA(data: number[], period: number): number[] {
  const ema: number[] = [];
  const multiplier = 2 / (period + 1);
  
  // 第一个EMA值使用SMA
  let sum = 0;
  for (let i = 0; i < period; i++) {
    sum += data[i];
  }
  ema[period - 1] = sum / period;
  
  // 后续EMA值
  for (let i = period; i < data.length; i++) {
    ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1];
  }
  
  return ema;
}

// 计算MACD指标
export function calculateMACD(priceHistory: PriceData[]): MACDData[] {
  const prices = priceHistory.map(p => p.price);
  
  // 计算EMA12和EMA26
  const ema12 = calculateEMA(prices, 12);
  const ema26 = calculateEMA(prices, 26);
  
  // 计算DIF (差离值)
  const dif: number[] = [];
  for (let i = 0; i < prices.length; i++) {
    if (ema12[i] !== undefined && ema26[i] !== undefined) {
      dif[i] = ema12[i] - ema26[i];
    }
  }
  
  // 计算DEA (DIF的9日EMA)
  const validDif = dif.filter(d => d !== undefined);
  const dea = calculateEMA(validDif, 9);
  
  // 计算MACD柱
  const result: MACDData[] = [];
  let deaIndex = 0;
  
  for (let i = 0; i < priceHistory.length; i++) {
    if (dif[i] !== undefined) {
      const deaValue = dea[deaIndex] || 0;
      result.push({
        date: priceHistory[i].date,
        dif: parseFloat(dif[i].toFixed(3)),
        dea: parseFloat(deaValue.toFixed(3)),
        macd: parseFloat(((dif[i] - deaValue) * 2).toFixed(3)),
      });
      deaIndex++;
    }
  }
  
  return result;
}

// 计算KDJ指标
export function calculateKDJ(priceHistory: PriceData[], period: number = 9): KDJData[] {
  const result: KDJData[] = [];
  
  for (let i = period - 1; i < priceHistory.length; i++) {
    const slice = priceHistory.slice(i - period + 1, i + 1);
    
    const highestHigh = Math.max(...slice.map(p => p.high));
    const lowestLow = Math.min(...slice.map(p => p.low));
    const currentClose = priceHistory[i].price;
    
    // 计算RSV (未成熟随机值)
    const rsv = highestHigh === lowestLow 
      ? 50 
      : ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100;
    
    // 如果是第一个值，K和D都等于RSV
    if (i === period - 1) {
      const k = rsv;
      const d = rsv;
      const j = 3 * k - 2 * d;
      
      result.push({
        date: priceHistory[i].date,
        k: parseFloat(k.toFixed(2)),
        d: parseFloat(d.toFixed(2)),
        j: parseFloat(j.toFixed(2)),
      });
    } else {
      // K = 2/3 × 前一日K值 + 1/3 × 当日RSV
      const prevK = result[result.length - 1].k;
      const k = (2 / 3) * prevK + (1 / 3) * rsv;
      
      // D = 2/3 × 前一日D值 + 1/3 × 当日K值
      const prevD = result[result.length - 1].d;
      const d = (2 / 3) * prevD + (1 / 3) * k;
      
      // J = 3 × 当日K值 - 2 × 当日D值
      const j = 3 * k - 2 * d;
      
      result.push({
        date: priceHistory[i].date,
        k: parseFloat(k.toFixed(2)),
        d: parseFloat(d.toFixed(2)),
        j: parseFloat(j.toFixed(2)),
      });
    }
  }
  
  return result;
}

// 计算量比
export function calculateVolumeRatio(priceHistory: PriceData[]): VolumeRatioData[] {
  const result: VolumeRatioData[] = [];
  
  for (let i = 5; i < priceHistory.length; i++) {
    // 计算过去5日的平均成交量
    const past5Days = priceHistory.slice(i - 5, i);
    const avgVolume = past5Days.reduce((sum, p) => sum + p.volume, 0) / 5;
    
    // 量比 = 当日成交量 / 过去5日平均成交量
    const volumeRatio = avgVolume > 0 ? priceHistory[i].volume / avgVolume : 1;
    
    result.push({
      date: priceHistory[i].date,
      volumeRatio: parseFloat(volumeRatio.toFixed(2)),
      volume: priceHistory[i].volume,
    });
  }
  
  return result;
}

// MACD信号分析
export function analyzeMACDSignal(macdData: MACDData[]): {
  signal: 'buy' | 'sell' | 'neutral';
  strength: number;
  description: string;
} {
  if (macdData.length < 2) {
    return { signal: 'neutral', strength: 50, description: '数据不足' };
  }
  
  const latest = macdData[macdData.length - 1];
  const previous = macdData[macdData.length - 2];
  
  // 金叉：DIF上穿DEA
  if (previous.dif <= previous.dea && latest.dif > latest.dea) {
    const strength = Math.min(100, 70 + Math.abs(latest.macd) * 10);
    return {
      signal: 'buy',
      strength,
      description: 'MACD金叉，DIF上穿DEA，看涨信号',
    };
  }
  
  // 死叉：DIF下穿DEA
  if (previous.dif >= previous.dea && latest.dif < latest.dea) {
    const strength = Math.min(100, 70 + Math.abs(latest.macd) * 10);
    return {
      signal: 'sell',
      strength,
      description: 'MACD死叉，DIF下穿DEA，看跌信号',
    };
  }
  
  // MACD柱状图分析
  if (latest.macd > 0 && latest.dif > latest.dea) {
    return {
      signal: 'buy',
      strength: 60 + Math.abs(latest.macd) * 5,
      description: 'MACD多头排列，持续看涨',
    };
  }
  
  if (latest.macd < 0 && latest.dif < latest.dea) {
    return {
      signal: 'sell',
      strength: 60 + Math.abs(latest.macd) * 5,
      description: 'MACD空头排列，持续看跌',
    };
  }
  
  return {
    signal: 'neutral',
    strength: 50,
    description: 'MACD中性，观望为主',
  };
}

// KDJ信号分析
export function analyzeKDJSignal(kdjData: KDJData[]): {
  signal: 'buy' | 'sell' | 'neutral';
  strength: number;
  description: string;
} {
  if (kdjData.length < 2) {
    return { signal: 'neutral', strength: 50, description: '数据不足' };
  }
  
  const latest = kdjData[kdjData.length - 1];
  const previous = kdjData[kdjData.length - 2];
  
  // 超卖区金叉（K<20且K上穿D）
  if (latest.k < 20 && previous.k <= previous.d && latest.k > latest.d) {
    return {
      signal: 'buy',
      strength: 85,
      description: 'KDJ超卖区金叉，强烈买入信号',
    };
  }
  
  // 超买区死叉（K>80且K下穿D）
  if (latest.k > 80 && previous.k >= previous.d && latest.k < latest.d) {
    return {
      signal: 'sell',
      strength: 85,
      description: 'KDJ超买区死叉，强烈卖出信号',
    };
  }
  
  // 普通金叉
  if (previous.k <= previous.d && latest.k > latest.d) {
    return {
      signal: 'buy',
      strength: 65,
      description: 'KDJ金叉，买入信号',
    };
  }
  
  // 普通死叉
  if (previous.k >= previous.d && latest.k < latest.d) {
    return {
      signal: 'sell',
      strength: 65,
      description: 'KDJ死叉，卖出信号',
    };
  }
  
  // 超卖区
  if (latest.k < 20 && latest.d < 20) {
    return {
      signal: 'buy',
      strength: 70,
      description: 'KDJ处于超卖区，存在反弹机会',
    };
  }
  
  // 超买区
  if (latest.k > 80 && latest.d > 80) {
    return {
      signal: 'sell',
      strength: 70,
      description: 'KDJ处于超买区，存在回调风险',
    };
  }
  
  return {
    signal: 'neutral',
    strength: 50,
    description: 'KDJ中性，观望为主',
  };
}

// 量比分析
export function analyzeVolumeRatio(volumeRatioData: VolumeRatioData[]): {
  signal: 'buy' | 'sell' | 'neutral';
  strength: number;
  description: string;
} {
  if (volumeRatioData.length === 0) {
    return { signal: 'neutral', strength: 50, description: '数据不足' };
  }
  
  const latest = volumeRatioData[volumeRatioData.length - 1];
  
  // 量比大于2.5，放量明显
  if (latest.volumeRatio > 2.5) {
    return {
      signal: 'buy',
      strength: 75,
      description: `量比${latest.volumeRatio}，成交量显著放大，资金活跃`,
    };
  }
  
  // 量比在1.5-2.5之间，温和放量
  if (latest.volumeRatio >= 1.5) {
    return {
      signal: 'buy',
      strength: 65,
      description: `量比${latest.volumeRatio}，成交量温和放大，有资金关注`,
    };
  }
  
  // 量比在0.8-1.5之间，正常水平
  if (latest.volumeRatio >= 0.8) {
    return {
      signal: 'neutral',
      strength: 50,
      description: `量比${latest.volumeRatio}，成交量正常水平`,
    };
  }
  
  // 量比小于0.5，缩量严重
  if (latest.volumeRatio < 0.5) {
    return {
      signal: 'sell',
      strength: 65,
      description: `量比${latest.volumeRatio}，成交量严重萎缩，观望情绪浓厚`,
    };
  }
  
  // 量比在0.5-0.8之间，轻微缩量
  return {
    signal: 'neutral',
    strength: 45,
    description: `量比${latest.volumeRatio}，成交量略显不足`,
  };
}

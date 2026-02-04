import { Stock } from '../types/stock';

export const mockStocks: Stock[] = [
  {
    id: '1',
    code: '600036',
    name: '招商银行',
    price: 38.52,
    change: 0.85,
    changePercent: 2.26,
    volume: 45678900,
    marketCap: 980000000000,
  },
  {
    id: '2',
    code: '600519',
    name: '贵州茅台',
    price: 1685.00,
    change: -12.50,
    changePercent: -0.74,
    volume: 1234500,
    marketCap: 2100000000000,
  },
  {
    id: '3',
    code: '000858',
    name: '五粮液',
    price: 128.36,
    change: 2.15,
    changePercent: 1.70,
    volume: 23456700,
    marketCap: 490000000000,
  },
  {
    id: '4',
    code: '000333',
    name: '美的集团',
    price: 62.84,
    change: -0.95,
    changePercent: -1.49,
    volume: 34567800,
    marketCap: 440000000000,
  },
  {
    id: '5',
    code: '601318',
    name: '中国平安',
    price: 45.28,
    change: 1.23,
    changePercent: 2.79,
    volume: 56789000,
    marketCap: 820000000000,
  },
  {
    id: '6',
    code: '300750',
    name: '宁德时代',
    price: 168.50,
    change: -3.20,
    changePercent: -1.86,
    volume: 67890100,
    marketCap: 720000000000,
  },
  {
    id: '7',
    code: '002594',
    name: '比亚迪',
    price: 234.56,
    change: 5.68,
    changePercent: 2.48,
    volume: 45678900,
    marketCap: 680000000000,
  },
  {
    id: '8',
    code: '601398',
    name: '工商银行',
    price: 5.23,
    change: 0.08,
    changePercent: 1.55,
    volume: 123456700,
    marketCap: 1850000000000,
  },
];

export const generatePriceHistory = (basePrice: number, days: number = 30) => {
  const history = [];
  let price = basePrice * 0.85;
  
  for (let i = 0; i < days; i++) {
    const change = (Math.random() - 0.48) * (price * 0.03);
    price = Math.max(price + change, basePrice * 0.7);
    
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    
    history.push({
      date: date.toISOString().split('T')[0],
      price: parseFloat(price.toFixed(2)),
      volume: Math.floor(Math.random() * 10000000 + 5000000),
      high: parseFloat((price * 1.02).toFixed(2)),
      low: parseFloat((price * 0.98).toFixed(2)),
      open: parseFloat((price * (0.98 + Math.random() * 0.04)).toFixed(2)),
    });
  }
  
  return history;
};

export const formatNumber = (num: number | undefined | null): string => {
  if (num === undefined || num === null || typeof num !== 'number') {
    return '0.00';
  }
  if (num >= 1000000000000) {
    return (num / 1000000000000).toFixed(2) + '万亿';
  }
  if (num >= 100000000) {
    return (num / 100000000).toFixed(2) + '亿';
  }
  if (num >= 10000) {
    return (num / 10000).toFixed(2) + '万';
  }
  return num.toFixed(2);
};

export const formatCurrency = (num: number | undefined | null): string => {
  if (num === undefined || num === null || typeof num !== 'number') {
    return '¥0.00';
  }
  return '¥' + num.toFixed(2);
};

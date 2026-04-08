'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Dot,
  Line,
  Brush,
  Legend
} from 'recharts';
import { stockApi, analysisApi } from '../utils/api';
import { ChartContainer, ChartTooltipContent } from './ui/chart';

interface KLineData {
  timestamp: number;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface ChanAnalysis {
  trend: string;
  pivots: Array<{
    type: string;
    price: number;
    date: string;
  }>;
  centrals: Array<{
    start_date: string;
    end_date: string;
    high: number;
    low: number;
    mid: number;
    level: number;
  }>;
  buyPoints: Array<{
    price: number;
    date: string;
    confidence: number;
    type: string;
  }>;
  sellPoints: Array<{
    price: number;
    date: string;
    confidence: number;
    type: string;
  }>;
  segments: string[];
}

interface KlineChartProps {
  stockCode: string;
  interval?: string;
  days?: number;
}

const KlineChart: React.FC<KlineChartProps> = ({
  stockCode,
  interval = '1d',
  days = 120
}) => {
  const [klineData, setKlineData] = useState<KLineData[]>([]);
  const [chanAnalysis, setChanAnalysis] = useState<ChanAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedInterval, setSelectedInterval] = useState(interval);

  // 获取K线数据和缠论分析
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // 并行请求K线数据和缠论分析
      const [klineResult, analysisResult] = await Promise.all([
        stockApi.getStockKline(stockCode, selectedInterval, days),
        analysisApi.getChanKlineAnalysis(stockCode, selectedInterval, days)
      ]);
      
      setKlineData(klineResult.data);
      setChanAnalysis(analysisResult.chan_analysis);
    } catch (err) {
      console.error('获取K线数据失败:', err);
      setError('获取K线数据失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, [stockCode, selectedInterval, days]);

  // 初始加载数据
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 自动刷新数据（每5分钟）
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchData();
    }, 300000); // 5分钟

    return () => clearInterval(intervalId);
  }, [fetchData]);

  // 手动刷新数据
  const handleRefresh = () => {
    fetchData();
  };

  // 处理时间周期切换
  const handleIntervalChange = (newInterval: string) => {
    setSelectedInterval(newInterval);
  };

  // 自定义K线图提示框
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const change = (data.close - data.open) / data.open * 100;
      const changeColor = change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
      
      return (
        <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-xl transform transition-all duration-200 hover:shadow-2xl">
          <div className="flex items-center justify-between mb-2">
            <p className="font-semibold text-sm text-gray-900 dark:text-gray-100">{data.date}</p>
            <span className={`text-xs font-medium ${changeColor}`}>
              {change >= 0 ? '+' : ''}{change.toFixed(2)}%
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400">开盘</span>
              <span className="text-xs font-medium text-gray-900 dark:text-gray-100">{data.open.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400">收盘</span>
              <span className={`text-xs font-medium ${changeColor}`}>{data.close.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400">最高</span>
              <span className="text-xs font-medium text-green-600 dark:text-green-400">{data.high.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400">最低</span>
              <span className="text-xs font-medium text-red-600 dark:text-red-400">{data.low.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between col-span-2">
              <span className="text-xs text-gray-500 dark:text-gray-400">成交量</span>
              <span className="text-xs font-medium text-gray-900 dark:text-gray-100">{data.volume.toLocaleString()}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">加载K线数据...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <span className="text-red-600 dark:text-red-400">{error}</span>
      </div>
    );
  }

  if (klineData.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <span className="text-gray-600 dark:text-gray-400">暂无K线数据</span>
      </div>
    );
  }

  // 计算图表数据
  const chartData = klineData.map(item => ({
    date: item.date,
    value: item.close,
    high: item.high,
    low: item.low,
    volume: item.volume
  }));

  return (
    <div className="w-full space-y-4">
      {/* 时间周期选择 */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {stockCode} K线图
        </h3>
        <div className="flex space-x-2">
          {['1d', '1w', '1M'].map(interval => (
            <button
              key={interval}
              onClick={() => handleIntervalChange(interval)}
              className={`px-3 py-1 text-sm rounded-md ${selectedInterval === interval
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
            >
              {interval}
            </button>
          ))}
          <button
            onClick={handleRefresh}
            className="px-3 py-1 text-sm rounded-md bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 flex items-center gap-1"
            disabled={loading}
          >
            {loading ? (
              <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500"></span>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                刷新
              </>
            )}
          </button>
        </div>
      </div>

      {/* 缠论分析结果 */}
      {chanAnalysis && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md p-4">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">缠论分析</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">趋势</p>
              <p className={`text-sm font-medium ${chanAnalysis.trend === 'up'
                ? 'text-green-600 dark:text-green-400'
                : chanAnalysis.trend === 'down'
                ? 'text-red-600 dark:text-red-400'
                : 'text-gray-600 dark:text-gray-400'
                }`}>
                {chanAnalysis.trend === 'up' ? '上涨' : chanAnalysis.trend === 'down' ? '下跌' : '横盘'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">买点</p>
              <p className="text-sm font-medium text-green-600 dark:text-green-400">
                {chanAnalysis.buyPoints.length}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">卖点</p>
              <p className="text-sm font-medium text-red-600 dark:text-red-400">
                {chanAnalysis.sellPoints.length}
              </p>
            </div>
          </div>
          {chanAnalysis.segments.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">线段分析</p>
              <div className="flex flex-wrap gap-2">
                {chanAnalysis.segments.map((segment, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded-full text-gray-800 dark:text-gray-200"
                  >
                    {segment}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* K线图 */}
      <div className="space-y-2">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4 shadow-sm">
          <div className="h-[320px] md:h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={chartData}
                margin={{
                  top: 15,
                  right: 20,
                  left: 0,
                  bottom: 15,
                }}
              >
            <defs>
              {/* 现代渐变色 */}
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="50%" stopColor="#60a5fa" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#93c5fd" stopOpacity={0} />
              </linearGradient>
              {/* 上升趋势渐变 */}
              <linearGradient id="colorUp" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              {/* 下降趋势渐变 */}
              <linearGradient id="colorDown" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="#f3f4f6" 
              strokeOpacity={0.6}
              vertical={false}
            />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb', strokeWidth: 1 }}
              interval={Math.ceil(chartData.length / 15)}
              tickMargin={8}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#6b7280' }}
              tickLine={false}
              axisLine={{ stroke: '#e5e7eb', strokeWidth: 1 }}
              domain={['dataMin - (dataMax - dataMin) * 0.05', 'dataMax + (dataMax - dataMin) * 0.05']}
              tickMargin={12}
              tickFormatter={(value) => value.toFixed(2)}
            />
            <Tooltip 
              content={<CustomTooltip />}
              cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '3 3' }}
            />
            
            {/* 中枢区域 */}
            {chanAnalysis?.centrals.map((central, index) => (
              <React.Fragment key={index}>
                <ReferenceLine
                  y={central.high}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  label={{
                    value: `中枢上沿: ${central.high.toFixed(2)}`,
                    position: 'right',
                    fill: '#d97706',
                    fontSize: 11,
                    fontWeight: '500',
                    background: '#fffbeb',
                    borderRadius: '4px',
                    padding: '2px 6px'
                  }}
                />
                <ReferenceLine
                  y={central.low}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  label={{
                    value: `中枢下沿: ${central.low.toFixed(2)}`,
                    position: 'right',
                    fill: '#d97706',
                    fontSize: 11,
                    fontWeight: '500',
                    background: '#fffbeb',
                    borderRadius: '4px',
                    padding: '2px 6px'
                  }}
                />
                <ReferenceLine
                  y={central.mid}
                  stroke="#f59e0b"
                  strokeDasharray="2 2"
                  strokeWidth={1}
                />
              </React.Fragment>
            ))}
            
            {/* 买点标注 */}
            {chanAnalysis?.buyPoints.map((point, index) => {
              const dataPoint = chartData.find(d => d.date === point.date);
              if (dataPoint) {
                return (
                  <Dot
                    key={`buy-${index}`}
                    cx={chartData.indexOf(dataPoint)}
                    cy={chartData.indexOf(dataPoint)}
                    r={5}
                    fill="#10b981"
                    stroke="white"
                    strokeWidth={2}
                    animationDuration={500}
                    label={{
                      value: `${point.type === 'first' ? '一买' : point.type === 'second' ? '二买' : '三买'}: ${point.price.toFixed(2)}`,
                      position: 'top',
                      fill: '#059669',
                      fontSize: 11,
                      fontWeight: '500',
                      background: '#ecfdf5',
                      borderRadius: '4px',
                      padding: '2px 6px',
                      offset: 10
                    }}
                  />
                );
              }
              return null;
            })}
            
            {/* 卖点标注 */}
            {chanAnalysis?.sellPoints.map((point, index) => {
              const dataPoint = chartData.find(d => d.date === point.date);
              if (dataPoint) {
                return (
                  <Dot
                    key={`sell-${index}`}
                    cx={chartData.indexOf(dataPoint)}
                    cy={chartData.indexOf(dataPoint)}
                    r={5}
                    fill="#ef4444"
                    stroke="white"
                    strokeWidth={2}
                    animationDuration={500}
                    label={{
                      value: `${point.type === 'first' ? '一卖' : point.type === 'second' ? '二卖' : '三卖'}: ${point.price.toFixed(2)}`,
                      position: 'bottom',
                      fill: '#dc2626',
                      fontSize: 11,
                      fontWeight: '500',
                      background: '#fef2f2',
                      borderRadius: '4px',
                      padding: '2px 6px',
                      offset: 10
                    }}
                  />
                );
              }
              return null;
            })}
            
            {/* K线图线 */}
            <Area
              type="monotone"
              dataKey="value"
              stroke="#3b82f6"
              strokeWidth={2.5}
              fill="url(#colorValue)"
              animationDuration={1000}
              animationBegin={200}
              isAnimationActive={true}
            />
            
            {/* 添加成交量区域图 */}
            {/* <Area
              type="monotone"
              dataKey="volume"
              stroke="transparent"
              fill="#93c5fd"
              fillOpacity={0.3}
              yAxisId="volume"
              animationDuration={800}
            /> */}
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* 缩放控制 */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-2">
          <div className="h-[80px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={chartData}
                margin={{
                  top: 0,
                  right: 0,
                  left: 0,
                  bottom: 0,
                }}
              >
                <defs>
                  <linearGradient id="brushGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.6} />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  strokeWidth={1}
                  fill="url(#brushGradient)"
                />
                <Brush
                  dataKey="date"
                  height={40}
                  stroke="#3b82f6"
                  fill="#dbeafe"
                  strokeWidth={1}
                  handle={{
                    fill: '#3b82f6',
                    stroke: '#3b82f6',
                    strokeWidth: 1,
                    r: 5,
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 缠论分析详情 */}
      {chanAnalysis && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md p-4">
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">缠论分析详情</h4>
          
          {/* 买卖点详情 */}
          <div className="space-y-4">
            {/* 买点 */}
            {chanAnalysis.buyPoints.length > 0 && (
              <div>
                <h5 className="text-xs font-medium text-green-600 dark:text-green-400 mb-2">买点</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {chanAnalysis.buyPoints.map((point, index) => (
                    <div key={index} className="bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800 rounded-md p-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-green-800 dark:text-green-300">
                          {point.type === 'first' ? '第一类买点' : point.type === 'second' ? '第二类买点' : '第三类买点'}
                        </span>
                        <span className="text-xs text-green-600 dark:text-green-400">
                          {point.confidence.toFixed(0)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-600 dark:text-gray-400">{point.date}</span>
                        <span className="text-xs font-medium text-green-800 dark:text-green-300">
                          {point.price.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* 卖点 */}
            {chanAnalysis.sellPoints.length > 0 && (
              <div>
                <h5 className="text-xs font-medium text-red-600 dark:text-red-400 mb-2">卖点</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {chanAnalysis.sellPoints.map((point, index) => (
                    <div key={index} className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800 rounded-md p-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-red-800 dark:text-red-300">
                          {point.type === 'first' ? '第一类卖点' : point.type === 'second' ? '第二类卖点' : '第三类卖点'}
                        </span>
                        <span className="text-xs text-red-600 dark:text-red-400">
                          {point.confidence.toFixed(0)}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-600 dark:text-gray-400">{point.date}</span>
                        <span className="text-xs font-medium text-red-800 dark:text-red-300">
                          {point.price.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default KlineChart;

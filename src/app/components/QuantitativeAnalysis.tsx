import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { mockStocks, generatePriceHistory } from '../utils/mockData';
import { ChanTheoryAnalysis, LivermoreAnalysis } from '../types/stock';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Scatter, ScatterChart, ZAxis } from 'recharts';
import { TrendingUp, TrendingDown, Activity, Target, ChevronUp, ChevronDown, AlertCircle } from 'lucide-react';

export function QuantitativeAnalysis() {
  const [selectedStock, setSelectedStock] = useState('');
  const [chanAnalysis, setChanAnalysis] = useState<ChanTheoryAnalysis | null>(null);
  const [livermoreAnalysis, setLivermoreAnalysis] = useState<LivermoreAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeChan = () => {
    if (!selectedStock) return;
    setIsAnalyzing(true);

    setTimeout(() => {
      const stock = mockStocks.find(s => s.code === selectedStock);
      if (!stock) return;

      const trends: ChanTheoryAnalysis['trend'][] = ['up', 'down', 'sideways'];
      const trend = trends[Math.floor(Math.random() * trends.length)];
      
      // Generate pivots
      const priceHistory = generatePriceHistory(stock.price, 30);
      const pivots: ChanTheoryAnalysis['pivots'] = [];
      
      for (let i = 5; i < priceHistory.length - 5; i += 5) {
        const isHigh = Math.random() > 0.5;
        pivots.push({
          type: isHigh ? 'high' : 'low',
          price: isHigh ? priceHistory[i].high : priceHistory[i].low,
          date: priceHistory[i].date,
        });
      }

      // Generate buy/sell points
      const buyPoints = pivots
        .filter(p => p.type === 'low')
        .slice(0, 2)
        .map(p => ({
          price: p.price,
          date: p.date,
          confidence: Math.floor(Math.random() * 30) + 70,
        }));

      const sellPoints = pivots
        .filter(p => p.type === 'high')
        .slice(0, 2)
        .map(p => ({
          price: p.price,
          date: p.date,
          confidence: Math.floor(Math.random() * 30) + 70,
        }));

      const analysis: ChanTheoryAnalysis = {
        trend,
        level: Math.floor(Math.random() * 3) + 1,
        pivots,
        segments: [
          '线段1：上涨趋势，形成3个向上笔',
          '线段2：盘整区间，多空力量均衡',
          '线段3：下跌趋势开始形成',
        ],
        buyPoints,
        sellPoints,
      };

      setChanAnalysis(analysis);
      setIsAnalyzing(false);
    }, 1500);
  };

  const analyzeLivermore = () => {
    if (!selectedStock) return;
    setIsAnalyzing(true);

    setTimeout(() => {
      const stock = mockStocks.find(s => s.code === selectedStock);
      if (!stock) return;

      const phases: LivermoreAnalysis['marketPhase'][] = ['accumulation', 'markup', 'distribution', 'markdown'];
      const phase = phases[Math.floor(Math.random() * phases.length)];

      const priceHistory = generatePriceHistory(stock.price, 30);
      const pivotalPoints = [
        { price: Math.min(...priceHistory.map(p => p.low)), type: '关键支撑位' },
        { price: Math.max(...priceHistory.map(p => p.high)), type: '关键阻力位' },
        { price: stock.price, type: '当前价格' },
      ];

      const recommendations = {
        accumulation: '市场处于吸筹阶段，主力资金在低位积累筹码。建议耐心等待突破信号，逢低分批建仓。',
        markup: '市场进入拉升阶段，趋势明确向上。建议持有现有仓位，可在回调时适当加仓。',
        distribution: '市场进入派发阶段，主力开始出货。建议逐步减仓，锁定利润。',
        markdown: '市场进入下跌阶段，趋势已经转弱。建议观望为主，等待新的买点出现。',
      };

      const volumeAnalyses = {
        accumulation: '成交量温和，显示主力在悄悄吸筹',
        markup: '成交量放大，显示多头力量强劲',
        distribution: '成交量高位放大，显示主力在派发筹码',
        markdown: '成交量萎缩，显示空头力量主导',
      };

      const analysis: LivermoreAnalysis = {
        marketPhase: phase,
        pivotalPoints,
        trendStrength: Math.floor(Math.random() * 40) + 60,
        volumeAnalysis: volumeAnalyses[phase],
        recommendation: recommendations[phase],
      };

      setLivermoreAnalysis(analysis);
      setIsAnalyzing(false);
    }, 1500);
  };

  const stock = mockStocks.find(s => s.code === selectedStock);
  const priceHistory = stock ? generatePriceHistory(stock.price, 30) : [];

  const getTrendColor = (trend: ChanTheoryAnalysis['trend']) => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      case 'sideways': return 'text-yellow-600';
    }
  };

  const getTrendText = (trend: ChanTheoryAnalysis['trend']) => {
    switch (trend) {
      case 'up': return '上涨趋势';
      case 'down': return '下跌趋势';
      case 'sideways': return '横盘整理';
    }
  };

  const getPhaseColor = (phase: LivermoreAnalysis['marketPhase']) => {
    switch (phase) {
      case 'accumulation': return 'text-blue-600';
      case 'markup': return 'text-green-600';
      case 'distribution': return 'text-orange-600';
      case 'markdown': return 'text-red-600';
    }
  };

  const getPhaseText = (phase: LivermoreAnalysis['marketPhase']) => {
    switch (phase) {
      case 'accumulation': return '吸筹阶段';
      case 'markup': return '拉升阶段';
      case 'distribution': return '派发阶段';
      case 'markdown': return '下跌阶段';
    }
  };

  return (
    <div className="space-y-6">
      {/* Stock Selection */}
      <Card>
        <CardHeader>
          <CardTitle>量化分析</CardTitle>
          <CardDescription>基于缠论和利弗莫尔交易法则的专业分析</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Select value={selectedStock} onValueChange={setSelectedStock}>
                <SelectTrigger>
                  <SelectValue placeholder="选择要分析的股票" />
                </SelectTrigger>
                <SelectContent>
                  {mockStocks.map(stock => (
                    <SelectItem key={stock.code} value={stock.code}>
                      {stock.code} - {stock.name} - ¥{stock.price}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedStock && (
        <Tabs defaultValue="chan" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="chan">缠论分析</TabsTrigger>
            <TabsTrigger value="livermore">利弗莫尔分析</TabsTrigger>
          </TabsList>

          <TabsContent value="chan" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>缠论技术分析</CardTitle>
                    <CardDescription>基于缠中说禅理论的笔、线段、中枢分析</CardDescription>
                  </div>
                  <Button onClick={analyzeChan} disabled={isAnalyzing}>
                    {isAnalyzing ? (
                      <>
                        <Activity className="w-4 h-4 mr-2 animate-spin" />
                        分析中...
                      </>
                    ) : (
                      '开始分析'
                    )}
                  </Button>
                </div>
              </CardHeader>
            </Card>

            {chanAnalysis && stock && !isAnalyzing && (
              <div className="space-y-6">
                {/* Trend Overview */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>趋势判断</span>
                      <Badge className={`${getTrendColor(chanAnalysis.trend)} text-lg px-4 py-2`} variant="outline">
                        {chanAnalysis.trend === 'up' && <TrendingUp className="w-4 h-4 mr-2" />}
                        {chanAnalysis.trend === 'down' && <TrendingDown className="w-4 h-4 mr-2" />}
                        {getTrendText(chanAnalysis.trend)}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600 mb-1">级别</div>
                        <div className="text-2xl">{chanAnalysis.level}级别趋势</div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600 mb-1">转折点数量</div>
                        <div className="text-2xl">{chanAnalysis.pivots.length}个</div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600 mb-1">买卖点</div>
                        <div className="text-2xl">
                          {chanAnalysis.buyPoints.length}买 / {chanAnalysis.sellPoints.length}卖
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Price Chart with Pivots */}
                <Card>
                  <CardHeader>
                    <CardTitle>价格走势与关键点位</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={priceHistory}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} domain={['dataMin - 5', 'dataMax + 5']} />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="price" 
                          stroke="#3b82f6" 
                          strokeWidth={2}
                          dot={false}
                        />
                        {chanAnalysis.buyPoints.map((point, i) => (
                          <ReferenceLine
                            key={`buy-${i}`}
                            y={point.price}
                            stroke="#22c55e"
                            strokeDasharray="5 5"
                            label={{ value: `买点 ${point.confidence}%`, position: 'right', fill: '#22c55e' }}
                          />
                        ))}
                        {chanAnalysis.sellPoints.map((point, i) => (
                          <ReferenceLine
                            key={`sell-${i}`}
                            y={point.price}
                            stroke="#ef4444"
                            strokeDasharray="5 5"
                            label={{ value: `卖点 ${point.confidence}%`, position: 'right', fill: '#ef4444' }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Buy/Sell Points */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-green-600">
                        <ChevronUp className="w-5 h-5" />
                        买入点位
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {chanAnalysis.buyPoints.length === 0 ? (
                        <p className="text-slate-500 text-sm">暂无买入信号</p>
                      ) : (
                        <div className="space-y-3">
                          {chanAnalysis.buyPoints.map((point, index) => (
                            <div key={index} className="p-3 bg-green-50 rounded-lg">
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-semibold">买点 {index + 1}</span>
                                <Badge variant="outline" className="text-green-600">
                                  置信度 {point.confidence}%
                                </Badge>
                              </div>
                              <div className="text-sm text-slate-600">
                                价格: ¥{point.price.toFixed(2)} | 日期: {point.date}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-red-600">
                        <ChevronDown className="w-5 h-5" />
                        卖出点位
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {chanAnalysis.sellPoints.length === 0 ? (
                        <p className="text-slate-500 text-sm">暂无卖出信号</p>
                      ) : (
                        <div className="space-y-3">
                          {chanAnalysis.sellPoints.map((point, index) => (
                            <div key={index} className="p-3 bg-red-50 rounded-lg">
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-semibold">卖点 {index + 1}</span>
                                <Badge variant="outline" className="text-red-600">
                                  置信度 {point.confidence}%
                                </Badge>
                              </div>
                              <div className="text-sm text-slate-600">
                                价格: ¥{point.price.toFixed(2)} | 日期: {point.date}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Segments Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle>线段划分</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {chanAnalysis.segments.map((segment, index) => (
                        <div key={index} className="p-3 bg-slate-50 rounded-lg text-sm">
                          {segment}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="livermore" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>利弗莫尔交易法则</CardTitle>
                    <CardDescription>基于Jesse Livermore的关键点交易理论</CardDescription>
                  </div>
                  <Button onClick={analyzeLivermore} disabled={isAnalyzing}>
                    {isAnalyzing ? (
                      <>
                        <Activity className="w-4 h-4 mr-2 animate-spin" />
                        分析中...
                      </>
                    ) : (
                      '开始分析'
                    )}
                  </Button>
                </div>
              </CardHeader>
            </Card>

            {livermoreAnalysis && stock && !isAnalyzing && (
              <div className="space-y-6">
                {/* Market Phase */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>市场阶段判断</span>
                      <Badge className={`${getPhaseColor(livermoreAnalysis.marketPhase)} text-lg px-4 py-2`} variant="outline">
                        {getPhaseText(livermoreAnalysis.marketPhase)}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600 mb-1">趋势强度</div>
                        <div className="text-2xl mb-2">{livermoreAnalysis.trendStrength}%</div>
                        <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 rounded-full transition-all"
                            style={{ width: `${livermoreAnalysis.trendStrength}%` }}
                          />
                        </div>
                      </div>
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600 mb-1">成交量分析</div>
                        <div className="text-sm mt-2">{livermoreAnalysis.volumeAnalysis}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Pivotal Points */}
                <Card>
                  <CardHeader>
                    <CardTitle>关键点位（Pivotal Points）</CardTitle>
                    <CardDescription>利弗莫尔理论的核心：关键价格点位</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={priceHistory}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} domain={['dataMin - 10', 'dataMax + 10']} />
                        <Tooltip />
                        <Line 
                          type="monotone" 
                          dataKey="price" 
                          stroke="#3b82f6" 
                          strokeWidth={2}
                          dot={false}
                        />
                        {livermoreAnalysis.pivotalPoints.map((point, i) => (
                          <ReferenceLine
                            key={i}
                            y={point.price}
                            stroke={point.type === '关键支撑位' ? '#22c55e' : point.type === '关键阻力位' ? '#ef4444' : '#f59e0b'}
                            strokeDasharray="5 5"
                            strokeWidth={2}
                            label={{ 
                              value: `${point.type}: ¥${point.price.toFixed(2)}`, 
                              position: 'right', 
                              fill: point.type === '关键支撑位' ? '#22c55e' : point.type === '关键阻力位' ? '#ef4444' : '#f59e0b'
                            }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                      {livermoreAnalysis.pivotalPoints.map((point, index) => (
                        <div key={index} className="p-4 bg-slate-50 rounded-lg">
                          <div className="flex items-center gap-2 mb-2">
                            <Target className="w-4 h-4 text-blue-600" />
                            <span className="font-semibold text-sm">{point.type}</span>
                          </div>
                          <div className="text-2xl">¥{point.price.toFixed(2)}</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Trading Recommendation */}
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>交易建议：</strong> {livermoreAnalysis.recommendation}
                  </AlertDescription>
                </Alert>

                {/* Livermore Principles */}
                <Card>
                  <CardHeader>
                    <CardTitle>利弗莫尔核心原则</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-semibold mb-1 text-blue-900">1. 跟随趋势</h4>
                        <p className="text-sm text-blue-700">
                          "趋势是你的朋友" - 在明确的趋势中交易，不要试图抄底或逃顶
                        </p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-semibold mb-1 text-blue-900">2. 关键点交易</h4>
                        <p className="text-sm text-blue-700">
                          在关键的支撑位和阻力位进行操作，这些是市场的转折点
                        </p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-semibold mb-1 text-blue-900">3. 资金管理</h4>
                        <p className="text-sm text-blue-700">
                          严格控制仓位，设置止损，保护资本是第一要务
                        </p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-semibold mb-1 text-blue-900">4. 市场阶段识别</h4>
                        <p className="text-sm text-blue-700">
                          识别市场处于吸筹、拉升、派发还是下跌阶段，采取相应策略
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}

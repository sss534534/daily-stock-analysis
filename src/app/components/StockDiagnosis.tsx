import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { mockStocks, generatePriceHistory } from '../utils/mockData';
import { DiagnosisResult } from '../types/stock';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, BarChart, Bar, ComposedChart, Legend } from 'recharts';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Activity, BarChart3 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  calculateMACD, 
  calculateKDJ, 
  calculateVolumeRatio,
  analyzeMACDSignal,
  analyzeKDJSignal,
  analyzeVolumeRatio,
  MACDData,
  KDJData,
  VolumeRatioData
} from '../utils/technicalIndicators';
import { diagnosisApi, stockApi } from '../utils/api';

export function StockDiagnosis() {
  const [selectedStock, setSelectedStock] = useState('');
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [macdData, setMacdData] = useState<MACDData[]>([]);
  const [kdjData, setKdjData] = useState<KDJData[]>([]);
  const [volumeRatioData, setVolumeRatioData] = useState<VolumeRatioData[]>([]);
  const [macdSignal, setMacdSignal] = useState<any>(null);
  const [kdjSignal, setKdjSignal] = useState<any>(null);
  const [volumeSignal, setVolumeSignal] = useState<any>(null);

  const runDiagnosis = async () => {
    if (!selectedStock) return;

    setIsAnalyzing(true);
    
    try {
      // 尝试从API获取诊断结果
      const apiDiagnosis = await diagnosisApi.getDiagnosis(selectedStock);
      
      // 获取价格历史数据用于技术指标计算
      const priceHistory = generatePriceHistory(apiDiagnosis.currentPrice || 100, 60);
      
      // Calculate technical indicators
      const macd = calculateMACD(priceHistory);
      const kdj = calculateKDJ(priceHistory);
      const volumeRatio = calculateVolumeRatio(priceHistory);
      
      // Analyze signals
      const macdAnalysis = analyzeMACDSignal(macd);
      const kdjAnalysis = analyzeKDJSignal(kdj);
      const volumeAnalysis = analyzeVolumeRatio(volumeRatio);
      
      setMacdData(macd);
      setKdjData(kdj);
      setVolumeRatioData(volumeRatio);
      setMacdSignal(macdAnalysis);
      setKdjSignal(kdjAnalysis);
      setVolumeSignal(volumeAnalysis);
      
      // 使用API返回的诊断结果
      setDiagnosis(apiDiagnosis);
    } catch (error) {
      console.error('API诊断失败，使用本地计算:', error);
      // 失败时使用本地计算
      setTimeout(() => {
        const stock = mockStocks.find(s => s.code === selectedStock);
        if (!stock) return;

        const priceHistory = generatePriceHistory(stock.price, 60);
        
        // Calculate technical indicators
        const macd = calculateMACD(priceHistory);
        const kdj = calculateKDJ(priceHistory);
        const volumeRatio = calculateVolumeRatio(priceHistory);
        
        // Analyze signals
        const macdAnalysis = analyzeMACDSignal(macd);
        const kdjAnalysis = analyzeKDJSignal(kdj);
        const volumeAnalysis = analyzeVolumeRatio(volumeRatio);
        
        setMacdData(macd);
        setKdjData(kdj);
        setVolumeRatioData(volumeRatio);
        setMacdSignal(macdAnalysis);
        setKdjSignal(kdjAnalysis);
        setVolumeSignal(volumeAnalysis);

        // Calculate technical score based on indicators
        const macdScore = macdAnalysis.signal === 'buy' ? macdAnalysis.strength : 
                          macdAnalysis.signal === 'sell' ? 100 - macdAnalysis.strength : 50;
        const kdjScore = kdjAnalysis.signal === 'buy' ? kdjAnalysis.strength : 
                         kdjAnalysis.signal === 'sell' ? 100 - kdjAnalysis.strength : 50;
        const volumeScore = volumeAnalysis.strength;
        
        const technicalScore = Math.floor((macdScore + kdjScore + volumeScore) / 3);
        const fundamentalScore = Math.floor(Math.random() * 40) + 50;
        const marketScore = Math.floor(Math.random() * 40) + 55;
        const overallScore = Math.floor((technicalScore + fundamentalScore + marketScore) / 3);

        let rating: DiagnosisResult['rating'] = 'neutral';
        if (overallScore >= 85) rating = 'excellent';
        else if (overallScore >= 70) rating = 'good';
        else if (overallScore >= 50) rating = 'neutral';
        else if (overallScore >= 35) rating = 'poor';
        else rating = 'risk';

        const strengths = [];
        const weaknesses = [];
        
        // Build strengths and weaknesses based on indicators
        if (macdAnalysis.signal === 'buy') {
          strengths.push(macdAnalysis.description);
        } else if (macdAnalysis.signal === 'sell') {
          weaknesses.push(macdAnalysis.description);
        }
        
        if (kdjAnalysis.signal === 'buy') {
          strengths.push(kdjAnalysis.description);
        } else if (kdjAnalysis.signal === 'sell') {
          weaknesses.push(kdjAnalysis.description);
        }
        
        if (volumeAnalysis.signal === 'buy') {
          strengths.push(volumeAnalysis.description);
        } else if (volumeAnalysis.signal === 'sell' || volumeAnalysis.strength < 50) {
          weaknesses.push(volumeAnalysis.description);
        }
        
        // Add additional analysis points
        if (technicalScore > 70) {
          strengths.push('技术形态良好，多个指标显示买入信号');
        } else if (technicalScore < 40) {
          weaknesses.push('技术形态转弱，多个指标显示卖出信号');
        }

        const result: DiagnosisResult = {
          stockCode: stock.code,
          stockName: stock.name,
          technicalScore,
          fundamentalScore,
          marketScore,
          overallScore,
          rating,
          strengths: strengths.length > 0 ? strengths : ['技术面中性，暂无明显优势'],
          weaknesses: weaknesses.length > 0 ? weaknesses : ['暂无明显风险'],
          recommendation: overallScore >= 70 
            ? '综合评分较高，技术指标支持，建议持有或适当加仓，注意控制仓位'
            : overallScore >= 50
            ? '综合评分中等，技术指标中性，建议观望，等待更清晰的信号'
            : '综合评分偏低，技术指标偏弱，建议谨慎操作，或考虑减仓',
        };

        setDiagnosis(result);
        setIsAnalyzing(false);
      }, 1500);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getRatingColor = (rating: DiagnosisResult['rating']) => {
    switch (rating) {
      case 'excellent': return 'bg-green-500';
      case 'good': return 'bg-blue-500';
      case 'neutral': return 'bg-yellow-500';
      case 'poor': return 'bg-orange-500';
      case 'risk': return 'bg-red-500';
    }
  };

  const getRatingText = (rating: DiagnosisResult['rating']) => {
    switch (rating) {
      case 'excellent': return '优秀';
      case 'good': return '良好';
      case 'neutral': return '中性';
      case 'poor': return '较差';
      case 'risk': return '风险';
    }
  };

  const stock = mockStocks.find(s => s.code === selectedStock);
  const priceHistory = stock ? generatePriceHistory(stock.price) : [];

  return (
    <div className="space-y-6">
      {/* Stock Selection */}
      <Card>
        <CardHeader>
          <CardTitle>股票诊断</CardTitle>
          <CardDescription>选择股票进行全面技术和基本面诊断</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Select value={selectedStock} onValueChange={setSelectedStock}>
                <SelectTrigger>
                  <SelectValue placeholder="选择要诊断的股票" />
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
            <Button onClick={runDiagnosis} disabled={!selectedStock || isAnalyzing}>
              {isAnalyzing ? (
                <>
                  <Activity className="w-4 h-4 mr-2 animate-spin" />
                  诊断中...
                </>
              ) : (
                '开始诊断'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Diagnosis Results */}
      {diagnosis && stock && (
        <div className="space-y-6">
          {/* Overall Rating */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{diagnosis.stockName} ({diagnosis.stockCode})</CardTitle>
                  <CardDescription>综合诊断评分</CardDescription>
                </div>
                <Badge className={`${getRatingColor(diagnosis.rating)} text-white text-lg px-4 py-2`}>
                  {getRatingText(diagnosis.rating)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center mb-6">
                <div className="text-6xl mb-2">{diagnosis.overallScore}</div>
                <div className="text-slate-600">综合评分</div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">技术面</span>
                    <span className="font-semibold">{diagnosis.technicalScore}</span>
                  </div>
                  <Progress value={diagnosis.technicalScore} className="h-2" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">基本面</span>
                    <span className="font-semibold">{diagnosis.fundamentalScore}</span>
                  </div>
                  <Progress value={diagnosis.fundamentalScore} className="h-2" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">市场面</span>
                    <span className="font-semibold">{diagnosis.marketScore}</span>
                  </div>
                  <Progress value={diagnosis.marketScore} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Price Chart */}
          <Card>
            <CardHeader>
              <CardTitle>价格走势</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={priceHistory}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                  <YAxis stroke="#64748b" fontSize={12} domain={['dataMin - 5', 'dataMax + 5']} />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorPrice)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Technical Indicators */}
          <Tabs defaultValue="macd" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="macd">MACD</TabsTrigger>
              <TabsTrigger value="kdj">KDJ</TabsTrigger>
              <TabsTrigger value="volume">量比</TabsTrigger>
            </TabsList>

            {/* MACD Tab */}
            <TabsContent value="macd" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>MACD指标分析</CardTitle>
                      <CardDescription>平滑异同移动平均线 - 趋势跟踪指标</CardDescription>
                    </div>
                    {macdSignal && (
                      <Badge 
                        variant={macdSignal.signal === 'buy' ? 'default' : macdSignal.signal === 'sell' ? 'destructive' : 'outline'}
                        className="text-base px-4 py-2"
                      >
                        {macdSignal.signal === 'buy' ? '看涨' : macdSignal.signal === 'sell' ? '看跌' : '中性'}
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* MACD Chart */}
                  <ResponsiveContainer width="100%" height={300}>
                    <ComposedChart data={macdData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="dif" stroke="#3b82f6" strokeWidth={2} name="DIF" dot={false} />
                      <Line type="monotone" dataKey="dea" stroke="#f59e0b" strokeWidth={2} name="DEA" dot={false} />
                      <Bar dataKey="macd" fill="#22c55e" name="MACD柱" />
                    </ComposedChart>
                  </ResponsiveContainer>

                  {/* MACD Signal Analysis */}
                  {macdSignal && (
                    <div className="space-y-3">
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold">信号强度</span>
                          <span className="text-lg">{macdSignal.strength}%</span>
                        </div>
                        <Progress value={macdSignal.strength} className="h-2" />
                      </div>
                      <Alert>
                        <BarChart3 className="h-4 w-4" />
                        <AlertDescription>
                          <strong>MACD分析：</strong> {macdSignal.description}
                        </AlertDescription>
                      </Alert>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <div className="text-slate-600 mb-1">DIF值</div>
                          <div className="text-lg font-semibold text-blue-600">
                            {macdData[macdData.length - 1]?.dif.toFixed(3)}
                          </div>
                        </div>
                        <div className="p-3 bg-orange-50 rounded-lg">
                          <div className="text-slate-600 mb-1">DEA值</div>
                          <div className="text-lg font-semibold text-orange-600">
                            {macdData[macdData.length - 1]?.dea.toFixed(3)}
                          </div>
                        </div>
                        <div className="p-3 bg-green-50 rounded-lg">
                          <div className="text-slate-600 mb-1">MACD柱</div>
                          <div className="text-lg font-semibold text-green-600">
                            {macdData[macdData.length - 1]?.macd.toFixed(3)}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* KDJ Tab */}
            <TabsContent value="kdj" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>KDJ指标分析</CardTitle>
                      <CardDescription>随机指标 - 超买超卖判断</CardDescription>
                    </div>
                    {kdjSignal && (
                      <Badge 
                        variant={kdjSignal.signal === 'buy' ? 'default' : kdjSignal.signal === 'sell' ? 'destructive' : 'outline'}
                        className="text-base px-4 py-2"
                      >
                        {kdjSignal.signal === 'buy' ? '看涨' : kdjSignal.signal === 'sell' ? '看跌' : '中性'}
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* KDJ Chart */}
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={kdjData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} domain={[0, 100]} />
                      <Tooltip />
                      <Legend />
                      {/* Reference lines for overbought/oversold */}
                      <Line y={80} stroke="#ef4444" strokeDasharray="5 5" />
                      <Line y={20} stroke="#22c55e" strokeDasharray="5 5" />
                      <Line type="monotone" dataKey="k" stroke="#3b82f6" strokeWidth={2} name="K值" dot={false} />
                      <Line type="monotone" dataKey="d" stroke="#f59e0b" strokeWidth={2} name="D值" dot={false} />
                      <Line type="monotone" dataKey="j" stroke="#8b5cf6" strokeWidth={2} name="J值" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>

                  {/* KDJ Signal Analysis */}
                  {kdjSignal && (
                    <div className="space-y-3">
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold">信号强度</span>
                          <span className="text-lg">{kdjSignal.strength}%</span>
                        </div>
                        <Progress value={kdjSignal.strength} className="h-2" />
                      </div>
                      <Alert>
                        <BarChart3 className="h-4 w-4" />
                        <AlertDescription>
                          <strong>KDJ分析：</strong> {kdjSignal.description}
                        </AlertDescription>
                      </Alert>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <div className="text-slate-600 mb-1">K值</div>
                          <div className="text-lg font-semibold text-blue-600">
                            {kdjData[kdjData.length - 1]?.k.toFixed(2)}
                          </div>
                          <div className="text-xs text-slate-500 mt-1">
                            {kdjData[kdjData.length - 1]?.k > 80 ? '超买区' : kdjData[kdjData.length - 1]?.k < 20 ? '超卖区' : '正常区'}
                          </div>
                        </div>
                        <div className="p-3 bg-orange-50 rounded-lg">
                          <div className="text-slate-600 mb-1">D值</div>
                          <div className="text-lg font-semibold text-orange-600">
                            {kdjData[kdjData.length - 1]?.d.toFixed(2)}
                          </div>
                          <div className="text-xs text-slate-500 mt-1">
                            {kdjData[kdjData.length - 1]?.d > 80 ? '超买区' : kdjData[kdjData.length - 1]?.d < 20 ? '超卖区' : '正常区'}
                          </div>
                        </div>
                        <div className="p-3 bg-purple-50 rounded-lg">
                          <div className="text-slate-600 mb-1">J值</div>
                          <div className="text-lg font-semibold text-purple-600">
                            {kdjData[kdjData.length - 1]?.j.toFixed(2)}
                          </div>
                          <div className="text-xs text-slate-500 mt-1">
                            {kdjData[kdjData.length - 1]?.j > 100 ? '严重超买' : kdjData[kdjData.length - 1]?.j < 0 ? '严重超卖' : '正常'}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Volume Ratio Tab */}
            <TabsContent value="volume" className="space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>量比分析</CardTitle>
                      <CardDescription>成交量相对强度指标</CardDescription>
                    </div>
                    {volumeSignal && (
                      <Badge 
                        variant={volumeSignal.signal === 'buy' ? 'default' : volumeSignal.signal === 'sell' ? 'destructive' : 'outline'}
                        className="text-base px-4 py-2"
                      >
                        {volumeSignal.signal === 'buy' ? '放量' : volumeSignal.signal === 'sell' ? '缩量' : '正常'}
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Volume Ratio Chart */}
                  <ResponsiveContainer width="100%" height={300}>
                    <ComposedChart data={volumeRatioData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                      <YAxis yAxisId="left" stroke="#64748b" fontSize={12} />
                      <YAxis yAxisId="right" orientation="right" stroke="#64748b" fontSize={12} />
                      <Tooltip />
                      <Legend />
                      <Bar yAxisId="right" dataKey="volume" fill="#94a3b8" name="成交量" opacity={0.3} />
                      <Line yAxisId="left" type="monotone" dataKey="volumeRatio" stroke="#3b82f6" strokeWidth={2} name="量比" dot={false} />
                    </ComposedChart>
                  </ResponsiveContainer>

                  {/* Volume Signal Analysis */}
                  {volumeSignal && (
                    <div className="space-y-3">
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold">当前量比</span>
                          <span className="text-2xl font-bold text-blue-600">
                            {volumeRatioData[volumeRatioData.length - 1]?.volumeRatio.toFixed(2)}
                          </span>
                        </div>
                        <div className="text-sm text-slate-600 mt-2">
                          量比 = 当日成交量 / 过去5日平均成交量
                        </div>
                      </div>
                      <Alert>
                        <BarChart3 className="h-4 w-4" />
                        <AlertDescription>
                          <strong>量比分析：</strong> {volumeSignal.description}
                        </AlertDescription>
                      </Alert>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <h4 className="font-semibold mb-2 text-blue-900">量比参考标准</h4>
                          <ul className="text-sm space-y-1 text-blue-700">
                            <li>• 量比 {'>'} 2.5：显著放量，资金活跃</li>
                            <li>• 量比 1.5-2.5：温和放量</li>
                            <li>• 量比 0.8-1.5：正常水平</li>
                            <li>• 量比 {'<'} 0.5：严重缩量</li>
                          </ul>
                        </div>
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold mb-2">成交量数据</h4>
                          <div className="text-sm space-y-2">
                            <div className="flex justify-between">
                              <span className="text-slate-600">当日成交量</span>
                              <span className="font-semibold">
                                {(volumeRatioData[volumeRatioData.length - 1]?.volume / 10000).toFixed(0)}万
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-600">5日均量</span>
                              <span className="font-semibold">
                                {(volumeRatioData[volumeRatioData.length - 1]?.volume / volumeRatioData[volumeRatioData.length - 1]?.volumeRatio / 10000).toFixed(0)}万
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  优势分析
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {diagnosis.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 text-green-600 mt-1 flex-shrink-0" />
                      <span className="text-sm">{strength}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-orange-600">
                  <AlertTriangle className="w-5 h-5" />
                  风险提示
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {diagnosis.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <TrendingDown className="w-4 h-4 text-orange-600 mt-1 flex-shrink-0" />
                      <span className="text-sm">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Recommendation */}
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>操作建议：</strong> {diagnosis.recommendation}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
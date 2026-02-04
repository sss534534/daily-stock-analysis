import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { getPositions } from '../utils/storage';
import { mockStocks, formatCurrency } from '../utils/mockData';
import { Position, AIRecommendation, RiskAnalysis } from '../types/stock';
import { Brain, TrendingUp, TrendingDown, Minus, AlertTriangle, ShieldAlert, Activity, Target } from 'lucide-react';
import { analysisApi, portfolioApi } from '../utils/api';

export function AIAnalysis() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);
  const [recommendation, setRecommendation] = useState<AIRecommendation | null>(null);
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null);
  const [portfolioRisk, setPortfolioRisk] = useState<RiskAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    loadPositions();
    analyzePortfolioRisk();
  }, []);

  const loadPositions = async () => {
    try {
      // 尝试从API获取持仓数据
      const apiPositions = await portfolioApi.getPositions();
      
      // 验证并处理API返回的数据
      const validPositions = (apiPositions || []).filter(pos => {
        return pos && typeof pos === 'object' && 
               typeof pos.id === 'string' && 
               typeof pos.stockCode === 'string' && 
               typeof pos.stockName === 'string' && 
               typeof pos.shares === 'number' && 
               typeof pos.buyPrice === 'number' && 
               typeof pos.currentPrice === 'number' && 
               typeof pos.cost === 'number' && 
               typeof pos.totalValue === 'number' && 
               typeof pos.profit === 'number' && 
               typeof pos.profitPercent === 'number' && 
               typeof pos.buyDate === 'string';
      });
      
      setPositions(validPositions);
    } catch (error) {
      console.error('API获取持仓失败，使用本地存储:', error);
      try {
        // 失败时使用本地存储
        const stored = getPositions();
        // 验证并处理本地存储的数据
        const validPositions = (stored || []).filter(pos => {
          return pos && typeof pos === 'object' && 
                 typeof pos.id === 'string' && 
                 typeof pos.stockCode === 'string' && 
                 typeof pos.stockName === 'string' && 
                 typeof pos.shares === 'number' && 
                 typeof pos.buyPrice === 'number' && 
                 typeof pos.currentPrice === 'number' && 
                 typeof pos.cost === 'number' && 
                 typeof pos.totalValue === 'number' && 
                 typeof pos.profit === 'number' && 
                 typeof pos.profitPercent === 'number' && 
                 typeof pos.buyDate === 'string';
        });
        setPositions(validPositions);
      } catch (localError) {
        console.error('本地存储获取失败:', localError);
        setPositions([]);
      }
    }
  };

  const analyzeStock = async (position: Position) => {
    // 验证position参数
    if (!position || typeof position !== 'object' || 
        typeof position.stockCode !== 'string' || 
        typeof position.stockName !== 'string') {
      console.error('无效的position参数:', position);
      return;
    }
    
    setSelectedPosition(position);
    setIsAnalyzing(true);

    try {
      // 尝试从API获取AI分析和风险分析
      const [aiRec, risk] = await Promise.all([
        analysisApi.getAIAnalysis(position.stockCode),
        analysisApi.getRiskAnalysis(position.stockCode)
      ]);
      
      // 验证API返回的数据
      if (aiRec && typeof aiRec === 'object') {
        setRecommendation(aiRec);
      }
      
      if (risk && typeof risk === 'object') {
        setRiskAnalysis(risk);
      }
    } catch (error) {
      console.error('API分析失败，使用本地计算:', error);
      // 失败时使用本地计算
      setTimeout(() => {
        try {
          // Generate AI recommendation
          const types: AIRecommendation['type'][] = ['buy', 'sell', 'hold'];
          const type = types[Math.floor(Math.random() * types.length)];
          const confidence = Math.floor(Math.random() * 30) + 70;
          
          const stock = mockStocks.find(s => s.code === position.stockCode);
          const currentPrice = stock?.price || position.currentPrice || 0;

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

          const aiRec: AIRecommendation = {
            type,
            confidence,
            reason: reasons[type][Math.floor(Math.random() * reasons[type].length)],
            targetPrice: type === 'buy' ? currentPrice * 1.15 : type === 'sell' ? currentPrice * 0.92 : undefined,
            stopLoss: type === 'buy' ? currentPrice * 0.92 : type === 'sell' ? currentPrice * 1.08 : undefined,
            timeframe: ['短期(1-2周)', '中期(1-3个月)', '长期(3-6个月)'][Math.floor(Math.random() * 3)],
          };

          // Generate risk analysis
          const riskScore = Math.floor(Math.random() * 40) + 30;
          let level: RiskAnalysis['level'] = 'medium';
          if (riskScore < 40) level = 'low';
          else if (riskScore < 60) level = 'medium';
          else if (riskScore < 80) level = 'high';
          else level = 'extreme';

          const risk: RiskAnalysis = {
            level,
            score: riskScore,
            factors: [
              { name: '市场风险', impact: Math.floor(Math.random() * 30) + 40, description: '整体市场波动对该股票的影响' },
              { name: '行业风险', impact: Math.floor(Math.random() * 30) + 30, description: '所属行业政策和竞争环境风险' },
              { name: '公司风险', impact: Math.floor(Math.random() * 30) + 20, description: '公司经营和财务风险' },
              { name: '流动性风险', impact: Math.floor(Math.random() * 30) + 25, description: '股票交易活跃度和变现能力' },
            ],
          };

          setRecommendation(aiRec);
          setRiskAnalysis(risk);
        } catch (localError) {
          console.error('本地计算失败:', localError);
          // 如果本地计算也失败，设置默认值
          const defaultRecommendation: AIRecommendation = {
            type: 'hold',
            confidence: 50,
            reason: '数据不足，无法提供具体建议',
            timeframe: '短期(1-2周)',
          };
          
          const defaultRisk: RiskAnalysis = {
            level: 'medium',
            score: 50,
            factors: [
              { name: '市场风险', impact: 50, description: '整体市场波动对该股票的影响' },
              { name: '行业风险', impact: 50, description: '所属行业政策和竞争环境风险' },
              { name: '公司风险', impact: 50, description: '公司经营和财务风险' },
              { name: '流动性风险', impact: 50, description: '股票交易活跃度和变现能力' },
            ],
          };
          
          setRecommendation(defaultRecommendation);
          setRiskAnalysis(defaultRisk);
        }
      }, 1500);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const analyzePortfolioRisk = () => {
    setTimeout(() => {
      try {
        // 尝试从本地存储获取持仓数据
        const storedPositions = getPositions();
        
        // 验证并处理本地存储的数据
        const validPositions = (storedPositions || []).filter(pos => {
          return pos && typeof pos === 'object' && 
                 typeof pos.totalValue === 'number';
        });
        
        // 计算总市值
        const totalValue = validPositions.reduce((sum, pos) => sum + (pos.totalValue || 0), 0);
        
        // Calculate portfolio concentration risk
        const concentrationRisk = validPositions.length > 0 && totalValue > 0 
          ? Math.max(...validPositions.map(p => ((p.totalValue || 0) / totalValue) * 100))
          : 0;

        const riskScore = Math.min(
          Math.floor(concentrationRisk * 0.8 + Math.random() * 20),
          90
        );

        let level: RiskAnalysis['level'] = 'medium';
        if (riskScore < 40) level = 'low';
        else if (riskScore < 60) level = 'medium';
        else if (riskScore < 80) level = 'high';
        else level = 'extreme';

        const risk: RiskAnalysis = {
          level,
          score: riskScore,
          factors: [
            { name: '集中度风险', impact: Math.floor(concentrationRisk), description: '单一股票占比过高可能导致风险集中' },
            { name: '行业分散度', impact: Math.floor(Math.random() * 40) + 30, description: '行业配置分散程度影响整体风险' },
            { name: '市场相关性', impact: Math.floor(Math.random() * 40) + 35, description: '持仓股票与大盘的关联程度' },
            { name: '波动率风险', impact: Math.floor(Math.random() * 40) + 40, description: '投资组合整体价格波动水平' },
          ],
        };

        setPortfolioRisk(risk);
      } catch (error) {
        console.error('分析组合风险失败:', error);
        // 如果出错，设置默认的风险分析数据
        const defaultRisk: RiskAnalysis = {
          level: 'medium',
          score: 50,
          factors: [
            { name: '集中度风险', impact: 30, description: '单一股票占比过高可能导致风险集中' },
            { name: '行业分散度', impact: 40, description: '行业配置分散程度影响整体风险' },
            { name: '市场相关性', impact: 50, description: '持仓股票与大盘的关联程度' },
            { name: '波动率风险', impact: 45, description: '投资组合整体价格波动水平' },
          ],
        };
        setPortfolioRisk(defaultRisk);
      }
    }, 500);
  };

  const getRecommendationIcon = (type: AIRecommendation['type']) => {
    switch (type) {
      case 'buy': return <TrendingUp className="w-5 h-5" />;
      case 'sell': return <TrendingDown className="w-5 h-5" />;
      case 'hold': return <Minus className="w-5 h-5" />;
    }
  };

  const getRecommendationColor = (type: AIRecommendation['type']) => {
    switch (type) {
      case 'buy': return 'bg-green-500';
      case 'sell': return 'bg-red-500';
      case 'hold': return 'bg-yellow-500';
    }
  };

  const getRecommendationText = (type: AIRecommendation['type']) => {
    switch (type) {
      case 'buy': return '建议买入';
      case 'sell': return '建议卖出';
      case 'hold': return '建议持有';
    }
  };

  const getRiskColor = (level: RiskAnalysis['level']) => {
    switch (level) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-orange-600';
      case 'extreme': return 'text-red-600';
    }
  };

  const getRiskText = (level: RiskAnalysis['level']) => {
    switch (level) {
      case 'low': return '低风险';
      case 'medium': return '中等风险';
      case 'high': return '高风险';
      case 'extreme': return '极高风险';
    }
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="individual" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="individual">个股分析</TabsTrigger>
          <TabsTrigger value="portfolio">组合分析</TabsTrigger>
        </TabsList>

        <TabsContent value="individual" className="space-y-6">
          {/* Position Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                AI智能分析
              </CardTitle>
              <CardDescription>使用大模型分析您的持仓，提供个性化投资建议</CardDescription>
            </CardHeader>
            <CardContent>
              {positions.length === 0 ? (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    暂无持仓数据，请先在"仓位管理"中添加持仓
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {positions.map(position => (
                    <Card 
                      key={position.id} 
                      className="cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => analyzeStock(position)}
                    >
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg">{position.stockName}</CardTitle>
                        <CardDescription>{position.stockCode}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-slate-600">持仓市值</span>
                            <span>{formatCurrency(position.totalValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-600">盈亏</span>
                            <span className={position.profit >= 0 ? 'text-green-600' : 'text-red-600'}>
                              {position.profit >= 0 ? '+' : ''}{position.profitPercent.toFixed(2)}%
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {isAnalyzing && (
            <Card>
              <CardContent className="py-12">
                <div className="flex flex-col items-center gap-4">
                  <Activity className="w-12 h-12 animate-spin text-blue-500" />
                  <p className="text-slate-600">AI正在分析中，请稍候...</p>
                </div>
              </CardContent>
            </Card>
          )}

          {recommendation && selectedPosition && !isAnalyzing && (
            <div className="space-y-6">
              {/* Recommendation Card */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>{selectedPosition.stockName} ({selectedPosition.stockCode})</CardTitle>
                      <CardDescription>AI投资建议</CardDescription>
                    </div>
                    <Badge className={`${getRecommendationColor(recommendation.type)} text-white text-lg px-4 py-2 flex items-center gap-2`}>
                      {getRecommendationIcon(recommendation.type)}
                      {getRecommendationText(recommendation.type)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm">推荐置信度</span>
                      <span className="font-semibold">{recommendation.confidence}%</span>
                    </div>
                    <Progress value={recommendation.confidence} className="h-2" />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-slate-50 rounded-lg">
                      <div className="text-sm text-slate-600 mb-1">投资时间框架</div>
                      <div className="font-semibold">{recommendation.timeframe}</div>
                    </div>
                    {recommendation.targetPrice && (
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600 mb-1">目标价位</div>
                        <div className="font-semibold text-green-600">
                          <Target className="w-4 h-4 inline mr-1" />
                          {formatCurrency(recommendation.targetPrice)}
                        </div>
                      </div>
                    )}
                    {recommendation.stopLoss && (
                      <div className="p-4 bg-slate-50 rounded-lg">
                        <div className="text-sm text-slate-600 mb-1">止损价位</div>
                        <div className="font-semibold text-red-600">
                          <ShieldAlert className="w-4 h-4 inline mr-1" />
                          {formatCurrency(recommendation.stopLoss)}
                        </div>
                      </div>
                    )}
                  </div>

                  <Alert>
                    <Brain className="h-4 w-4" />
                    <AlertDescription>
                      <strong>AI分析：</strong> {recommendation.reason}
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>

              {/* Risk Analysis */}
              {riskAnalysis && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      风险评估
                    </CardTitle>
                    <CardDescription>该持仓的风险分析</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="text-center">
                      <div className={`text-4xl mb-2 ${getRiskColor(riskAnalysis.level)}`}>
                        {riskAnalysis.score}
                      </div>
                      <Badge variant="outline" className={getRiskColor(riskAnalysis.level)}>
                        {getRiskText(riskAnalysis.level)}
                      </Badge>
                    </div>

                    <div className="space-y-4">
                      {riskAnalysis.factors.map((factor, index) => (
                        <div key={index}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm">{factor.name}</span>
                            <span className="text-sm font-semibold">{factor.impact}%</span>
                          </div>
                          <Progress value={factor.impact} className="h-2 mb-1" />
                          <p className="text-xs text-slate-600">{factor.description}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-6">
          {/* Portfolio Risk Analysis */}
          {portfolioRisk && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5" />
                  投资组合风险评估
                </CardTitle>
                <CardDescription>整体持仓的风险分析与建议</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center">
                  <div className={`text-5xl mb-3 ${getRiskColor(portfolioRisk.level)}`}>
                    {portfolioRisk.score}
                  </div>
                  <Badge variant="outline" className={`${getRiskColor(portfolioRisk.level)} text-lg px-4 py-2`}>
                    {getRiskText(portfolioRisk.level)}
                  </Badge>
                </div>

                <div className="space-y-4">
                  {portfolioRisk.factors.map((factor, index) => (
                    <div key={index}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">{factor.name}</span>
                        <span className="text-sm font-semibold">{factor.impact}%</span>
                      </div>
                      <Progress value={factor.impact} className="h-2 mb-1" />
                      <p className="text-xs text-slate-600">{factor.description}</p>
                    </div>
                  ))}
                </div>

                <Alert>
                  <Brain className="h-4 w-4" />
                  <AlertDescription>
                    <strong>AI建议：</strong>
                    {portfolioRisk.score < 40 
                      ? '您的投资组合风险控制较好，建议保持当前配置策略，适度关注市场变化。'
                      : portfolioRisk.score < 60
                      ? '您的投资组合存在一定风险，建议适当分散投资，降低单一股票或行业的集中度。'
                      : portfolioRisk.score < 80
                      ? '您的投资组合风险偏高，强烈建议进行风险调整，考虑减仓高风险资产，增加防御性配置。'
                      : '您的投资组合风险极高，建议立即采取风险管理措施，大幅降低仓位或调整持仓结构。'
                    }
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

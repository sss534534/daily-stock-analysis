'use client';

import React, { useState, useEffect } from 'react';
import { investmentToolApi } from '../utils/api';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from './ui/card';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from './ui/tabs';
import {
  Button,
  ButtonGroup,
  IconButton
} from './ui/button';
import {
  Input,
  InputGroup,
  InputLeftAddon,
  InputRightAddon
} from './ui/input';
import {
  Slider
} from './ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from './ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from './ui/table';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import {
  Plus,
  Edit,
  Trash2,
  Target,
  PieChart as PieChartIcon,
  BarChart3,
  Calendar,
  DollarSign,
  FileText,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { Badge } from './ui/badge';
import { Label } from './ui/label';
import { Separator } from './ui/separator';

interface InvestmentGoal {
  id: number;
  title: string;
  target_amount: number;
  time_horizon: number;
  risk_tolerance: string;
  current_amount: number;
  monthly_contribution: number;
  start_date: string;
  description: string;
}

interface AssetAllocation {
  id: number;
  goal_id: number;
  cash: number;
  stocks: number;
  bonds: number;
  real_estate: number;
  commodities: number;
  alternative: number;
  risk_score: number;
}

interface InvestmentPortfolio {
  id: number;
  goal_id: number;
  name: string;
  assets: Array<{
    name: string;
    type: string;
    weight: number;
    return: number;
  }>;
  risk_level: string;
  expected_return: number;
}

interface InvestmentReview {
  id: number;
  portfolio_id: number;
  review_date: string;
  performance: number;
  notes: string;
  recommended_actions: string[];
}

interface InvestmentPlan {
  id: number;
  goal_id: number;
  frequency: string;
  amount: number;
  start_date: string;
  next_investment_date: string;
}

interface CashFlow {
  id: number;
  month: string;
  income: number;
  expenses: number;
  investment: number;
  savings: number;
}

interface InvestmentRecommendation {
  title: string;
  content: string;
  action: string;
}

const InvestmentTool: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [goals, setGoals] = useState<InvestmentGoal[]>([]);
  const [allocations, setAllocations] = useState<AssetAllocation[]>([]);
  const [portfolios, setPortfolios] = useState<InvestmentPortfolio[]>([]);
  const [reviews, setReviews] = useState<InvestmentReview[]>([]);
  const [plans, setPlans] = useState<InvestmentPlan[]>([]);
  const [cashFlows, setCashFlows] = useState<CashFlow[]>([]);
  const [recommendations, setRecommendations] = useState<InvestmentRecommendation[]>([]);
  const [activeGoal, setActiveGoal] = useState<InvestmentGoal | null>(null);

  useEffect(() => {
    fetchInvestmentToolData();
  }, []);

  const fetchInvestmentToolData = async () => {
    try {
      setLoading(true);
      const [goalsData, allocationsData, portfoliosData, reviewsData, plansData, cashFlowsData, recommendationsData] = await Promise.all([
        investmentToolApi.getInvestmentGoals(),
        investmentToolApi.getAssetAllocations(),
        investmentToolApi.getInvestmentPortfolios(),
        investmentToolApi.getInvestmentReviews(),
        investmentToolApi.getInvestmentPlans(),
        investmentToolApi.getCashFlows(),
        investmentToolApi.getInvestmentRecommendations()
      ]);
      
      setGoals(goalsData);
      setAllocations(allocationsData);
      setPortfolios(portfoliosData);
      setReviews(reviewsData);
      setPlans(plansData);
      setCashFlows(cashFlowsData);
      setRecommendations(recommendationsData);
      
      if (goalsData.length > 0) {
        setActiveGoal(goalsData[0]);
      }
      
      setError(null);
    } catch (err) {
      console.error('获取投资工具数据失败:', err);
      setError('获取数据失败，请稍后重试');
      // 使用模拟数据
      setGoals(getMockGoals());
      setAllocations(getMockAllocations());
      setPortfolios(getMockPortfolios());
      setReviews(getMockReviews());
      setPlans(getMockPlans());
      setCashFlows(getMockCashFlows());
      setRecommendations(getMockRecommendations());
    } finally {
      setLoading(false);
    }
  };

  // 模拟数据
  const getMockGoals = (): InvestmentGoal[] => [
    {
      id: 1,
      title: "退休储蓄",
      target_amount: 1000000,
      time_horizon: 20,
      risk_tolerance: "medium",
      current_amount: 100000,
      monthly_contribution: 3000,
      start_date: "2024-01-01",
      description: "为20年后的退休生活储蓄"
    },
    {
      id: 2,
      title: "子女教育",
      target_amount: 500000,
      time_horizon: 15,
      risk_tolerance: "medium",
      current_amount: 50000,
      monthly_contribution: 1500,
      start_date: "2024-01-01",
      description: "为子女的大学教育储蓄"
    }
  ];

  const getMockAllocations = (): AssetAllocation[] => [
    {
      id: 1,
      goal_id: 1,
      cash: 10,
      stocks: 60,
      bonds: 20,
      real_estate: 5,
      commodities: 3,
      alternative: 2,
      risk_score: 65
    },
    {
      id: 2,
      goal_id: 2,
      cash: 15,
      stocks: 50,
      bonds: 30,
      real_estate: 3,
      commodities: 1,
      alternative: 1,
      risk_score: 55
    }
  ];

  const getMockPortfolios = (): InvestmentPortfolio[] => [
    {
      id: 1,
      goal_id: 1,
      name: "退休投资组合",
      assets: [
        { name: "沪深300ETF", type: "stock", weight: 30, return: 0.08 },
        { name: "中证500ETF", type: "stock", weight: 20, return: 0.10 },
        { name: "国债ETF", type: "bond", weight: 20, return: 0.03 },
        { name: "企业债ETF", type: "bond", weight: 10, return: 0.05 },
        { name: "货币基金", type: "cash", weight: 10, return: 0.02 },
        { name: "黄金ETF", type: "commodity", weight: 5, return: 0.04 },
        { name: "房地产REITs", type: "real_estate", weight: 5, return: 0.06 }
      ],
      risk_level: "medium",
      expected_return: 0.065
    },
    {
      id: 2,
      goal_id: 2,
      name: "教育投资组合",
      assets: [
        { name: "沪深300ETF", type: "stock", weight: 25, return: 0.08 },
        { name: "中证500ETF", type: "stock", weight: 15, return: 0.10 },
        { name: "国债ETF", type: "bond", weight: 30, return: 0.03 },
        { name: "企业债ETF", type: "bond", weight: 10, return: 0.05 },
        { name: "货币基金", type: "cash", weight: 15, return: 0.02 },
        { name: "黄金ETF", type: "commodity", weight: 3, return: 0.04 },
        { name: "房地产REITs", type: "real_estate", weight: 2, return: 0.06 }
      ],
      risk_level: "low-medium",
      expected_return: 0.05
    }
  ];

  const getMockReviews = (): InvestmentReview[] => [
    {
      id: 1,
      portfolio_id: 1,
      review_date: "2024-12-31",
      performance: 0.085,
      notes: "2024年投资组合表现良好，超过预期收益",
      recommended_actions: [
        "保持当前资产配置",
        "考虑增加国际市场 exposure",
        "定期再平衡"
      ]
    },
    {
      id: 2,
      portfolio_id: 2,
      review_date: "2024-12-31",
      performance: 0.062,
      notes: "教育投资组合表现符合预期",
      recommended_actions: [
        "保持保守配置",
        "增加每月定投金额"
      ]
    }
  ];

  const getMockPlans = (): InvestmentPlan[] => [
    {
      id: 1,
      goal_id: 1,
      frequency: "monthly",
      amount: 3000,
      start_date: "2024-01-01",
      next_investment_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    },
    {
      id: 2,
      goal_id: 2,
      frequency: "monthly",
      amount: 1500,
      start_date: "2024-01-01",
      next_investment_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    }
  ];

  const getMockCashFlows = (): CashFlow[] => {
    const flows = [];
    const today = new Date();
    
    for (let i = 0; i < 12; i++) {
      const monthDate = new Date(today.getFullYear(), today.getMonth() - i, 1);
      const income = Math.random() * 4000 + 8000;
      const expenses = Math.random() * 3000 + 5000;
      const investment = Math.random() * 2000 + 1000;
      const savings = income - expenses - investment;
      
      flows.push({
        id: i + 1,
        month: monthDate.toISOString().split('T')[0],
        income: Math.round(income * 100) / 100,
        expenses: Math.round(expenses * 100) / 100,
        investment: Math.round(investment * 100) / 100,
        savings: Math.round(savings * 100) / 100
      });
    }
    
    return flows;
  };

  const getMockRecommendations = (): InvestmentRecommendation[] => [
    {
      title: "军规1: 设定长期目标",
      content: "基于您的风险承受能力和时间 horizon，建议设定合理的长期投资目标。",
      action: "使用投资目标工具创建详细的投资计划。"
    },
    {
      title: "军规2: 永不满仓",
      content: "建议保持10-20%的现金储备，以应对市场波动和把握投资机会。",
      action: "调整资产配置，确保适当的现金比例。"
    },
    {
      title: "军规3: 均衡配置",
      content: "构建多元化的投资组合，降低单一资产风险。",
      action: "检查并优化您的资产配置比例。"
    },
    {
      title: "军规4: 定期复盘",
      content: "建议每季度对投资组合进行一次全面回顾和再平衡。",
      action: "使用投资回顾工具记录和分析投资表现。"
    },
    {
      title: "军规5: 稳定心态",
      content: "避免市场情绪影响，坚持长期投资策略。",
      action: "设置止损和止盈点，减少情绪化决策。"
    },
    {
      title: "军规6: 定期投入",
      content: "采用定期定额投资策略，平滑市场波动风险。",
      action: "设置每月自动投资计划。"
    },
    {
      title: "军规7: 保持现金流",
      content: "确保有足够的应急资金，避免因流动性问题被迫卖出资产。",
      action: "使用现金流工具分析和管理个人财务状况。"
    }
  ];

  // 颜色配置
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

  // 格式化金额
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2
    }).format(amount);
  };

  // 格式化百分比
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">加载投资工具数据...</span>
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

  return (
    <div className="w-full space-y-6">
      {/* 投资工具标题 */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          军规落实工具
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          帮助您实际应用炒股7条军规的综合投资管理工具
        </p>
      </div>

      {/* 工具标签页 */}
      <Tabs defaultValue="goals" className="w-full">
        <TabsList className="grid w-full grid-cols-7 mb-6">
          <TabsTrigger value="goals" className="flex items-center gap-2">
            <Target className="w-4 h-4" />
            <span>投资目标</span>
          </TabsTrigger>
          <TabsTrigger value="allocation" className="flex items-center gap-2">
            <PieChartIcon className="w-4 h-4" />
            <span>资产配置</span>
          </TabsTrigger>
          <TabsTrigger value="portfolio" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            <span>投资组合</span>
          </TabsTrigger>
          <TabsTrigger value="reviews" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            <span>投资回顾</span>
          </TabsTrigger>
          <TabsTrigger value="plans" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <span>投资计划</span>
          </TabsTrigger>
          <TabsTrigger value="cashflow" className="flex items-center gap-2">
            <DollarSign className="w-4 h-4" />
            <span>现金流</span>
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            <span>投资建议</span>
          </TabsTrigger>
        </TabsList>

        {/* 投资目标 */}
        <TabsContent value="goals" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              投资目标管理
            </h3>
            <Button variant="default" size="sm" className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              添加目标
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {goals.map((goal) => (
              <Card key={goal.id} className="border-gray-200 dark:border-gray-700">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{goal.title}</CardTitle>
                    <div className="flex items-center gap-2">
                      <IconButton size="sm">
                        <Edit className="w-4 h-4" />
                      </IconButton>
                      <IconButton size="sm" variant="destructive">
                        <Trash2 className="w-4 h-4" />
                      </IconButton>
                    </div>
                  </div>
                  <CardDescription>{goal.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">目标金额</Label>
                      <p className="text-lg font-bold">{formatCurrency(goal.target_amount)}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">当前金额</Label>
                      <p className="text-lg font-bold">{formatCurrency(goal.current_amount)}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">时间跨度</Label>
                      <p className="text-lg font-bold">{goal.time_horizon} 年</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">月投入</Label>
                      <p className="text-lg font-bold">{formatCurrency(goal.monthly_contribution)}</p>
                    </div>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">风险承受能力</Label>
                    <Badge variant={
                      goal.risk_tolerance === 'low' ? 'outline' :
                      goal.risk_tolerance === 'medium' ? 'secondary' : 'default'
                    }>
                      {goal.risk_tolerance === 'low' ? '低风险' :
                       goal.risk_tolerance === 'medium' ? '中风险' : '高风险'}
                    </Badge>
                  </div>
                  <div>
                    <Label className="text-sm font-medium">进度</Label>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                      <div
                        className="bg-blue-600 h-2.5 rounded-full"
                        style={{ width: `${(goal.current_amount / goal.target_amount) * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {((goal.current_amount / goal.target_amount) * 100).toFixed(1)}% 完成
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 资产配置 */}
        <TabsContent value="allocation" className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            资产配置管理
          </h3>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {allocations.map((allocation) => {
              const goal = goals.find(g => g.id === allocation.goal_id);
              const data = [
                { name: '现金', value: allocation.cash, color: COLORS[0] },
                { name: '股票', value: allocation.stocks, color: COLORS[1] },
                { name: '债券', value: allocation.bonds, color: COLORS[2] },
                { name: '房地产', value: allocation.real_estate, color: COLORS[3] },
                { name: '大宗商品', value: allocation.commodities, color: COLORS[4] },
                { name: '另类投资', value: allocation.alternative, color: COLORS[5] }
              ];

              return (
                <Card key={allocation.id} className="border-gray-200 dark:border-gray-700">
                  <CardHeader>
                    <CardTitle>{goal?.title || '未关联目标'}</CardTitle>
                    <CardDescription>资产配置比例</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {data.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => `${value}%`} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">风险评分</Label>
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                          <div
                            className={`h-2.5 rounded-full ${
                              allocation.risk_score < 40 ? 'bg-green-500' :
                              allocation.risk_score < 70 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${allocation.risk_score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{allocation.risk_score}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* 投资组合 */}
        <TabsContent value="portfolio" className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            投资组合分析
          </h3>

          <div className="space-y-6">
            {portfolios.map((portfolio) => {
              const goal = goals.find(g => g.id === portfolio.goal_id);
              const data = portfolio.assets.map(asset => ({
                name: asset.name,
                weight: asset.weight,
                return: asset.return * 100
              }));

              return (
                <Card key={portfolio.id} className="border-gray-200 dark:border-gray-700">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>{portfolio.name}</CardTitle>
                        <CardDescription>{goal?.title || '未关联目标'}</CardDescription>
                      </div>
                      <Badge variant="secondary">
                        {portfolio.risk_level === 'low' ? '低风险' :
                         portfolio.risk_level === 'low-medium' ? '中低风险' :
                         portfolio.risk_level === 'medium' ? '中风险' :
                         portfolio.risk_level === 'medium-high' ? '中高风险' : '高风险'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-sm font-medium mb-4">资产权重</h4>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis />
                              <Tooltip formatter={(value) => `${value}%`} />
                              <Bar dataKey="weight" fill="#8884d8" />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium mb-4">预期收益</h4>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis />
                              <Tooltip formatter={(value) => `${value}%`} />
                              <Bar dataKey="return" fill="#82ca9d" />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-2">组合预期收益</h4>
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {formatPercent(portfolio.expected_return)}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* 投资回顾 */}
        <TabsContent value="reviews" className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            投资回顾与分析
          </h3>

          <div className="space-y-6">
            {reviews.map((review) => {
              const portfolio = portfolios.find(p => p.id === review.portfolio_id);

              return (
                <Card key={review.id} className="border-gray-200 dark:border-gray-700">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>投资回顾</CardTitle>
                        <CardDescription>
                          {portfolio?.name} - {new Date(review.review_date).toLocaleDateString()}
                        </CardDescription>
                      </div>
                      <Badge variant={
                        review.performance > 0.08 ? 'default' :
                        review.performance > 0.04 ? 'secondary' : 'outline'
                      }>
                        {formatPercent(review.performance)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-2">回顾笔记</h4>
                      <p className="text-gray-700 dark:text-gray-300">{review.notes}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-2">建议行动</h4>
                      <ul className="list-disc pl-5 space-y-1">
                        {review.recommended_actions.map((action, index) => (
                          <li key={index} className="text-gray-700 dark:text-gray-300">
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* 投资计划 */}
        <TabsContent value="plans" className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            投资计划管理
          </h3>

          <div className="space-y-6">
            {plans.map((plan) => {
              const goal = goals.find(g => g.id === plan.goal_id);

              return (
                <Card key={plan.id} className="border-gray-200 dark:border-gray-700">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>定期投资计划</CardTitle>
                        <CardDescription>{goal?.title || '未关联目标'}</CardDescription>
                      </div>
                      <Badge variant="secondary">
                        {plan.frequency === 'monthly' ? '每月' :
                         plan.frequency === 'quarterly' ? '每季度' : '每年'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium">投资金额</Label>
                        <p className="text-lg font-bold">{formatCurrency(plan.amount)}</p>
                      </div>
                      <div>
                        <Label className="text-sm font-medium">下次投资日期</Label>
                        <p className="text-lg font-bold">
                          {new Date(plan.next_investment_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">开始日期</Label>
                      <p className="text-gray-700 dark:text-gray-300">
                        {new Date(plan.start_date).toLocaleDateString()}
                      </p>
                    </div>
                  </CardContent>
                  <CardFooter className="border-t pt-4">
                    <Button variant="secondary" className="w-full">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      更新投资计划
                    </Button>
                  </CardFooter>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* 现金流 */}
        <TabsContent value="cashflow" className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            现金流分析
          </h3>

          <Card className="border-gray-200 dark:border-gray-700">
            <CardHeader>
              <CardTitle>月度现金流</CardTitle>
              <CardDescription>过去12个月的收支情况</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={cashFlows}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Legend />
                    <Bar dataKey="income" name="收入" fill="#82ca9d" />
                    <Bar dataKey="expenses" name="支出" fill="#ff8042" />
                    <Bar dataKey="investment" name="投资" fill="#8884d8" />
                    <Bar dataKey="savings" name="储蓄" fill="#0088fe" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">总收入</h4>
                  <p className="text-lg font-bold">
                    {formatCurrency(cashFlows.reduce((sum, flow) => sum + flow.income, 0))}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">总支出</h4>
                  <p className="text-lg font-bold">
                    {formatCurrency(cashFlows.reduce((sum, flow) => sum + flow.expenses, 0))}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">总投资</h4>
                  <p className="text-lg font-bold">
                    {formatCurrency(cashFlows.reduce((sum, flow) => sum + flow.investment, 0))}
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400">总储蓄</h4>
                  <p className="text-lg font-bold">
                    {formatCurrency(cashFlows.reduce((sum, flow) => sum + flow.savings, 0))}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 投资建议 */}
        <TabsContent value="recommendations" className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            军规落实建议
          </h3>

          <div className="space-y-4">
            {recommendations.map((recommendation, index) => (
              <Card key={index} className="border-gray-200 dark:border-gray-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">{recommendation.title}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-gray-700 dark:text-gray-300">
                    {recommendation.content}
                  </p>
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-md p-3">
                    <h4 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-1">建议行动</h4>
                    <p className="text-sm text-blue-700 dark:text-blue-200">
                      {recommendation.action}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default InvestmentTool;

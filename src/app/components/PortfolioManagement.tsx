import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Plus, Trash2, TrendingUp, TrendingDown, DollarSign, Calendar, BarChart2 } from 'lucide-react';
import { Position } from '../types/stock';
import { getPositions, addPosition, deletePosition, calculatePositionMetrics } from '../utils/storage';
import { mockStocks, formatCurrency, formatNumber } from '../utils/mockData';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import {
  generateMockProfitHistory,
  calculateDailyProfit,
  calculateWeeklyProfit,
  calculateMonthlyProfit,
  getRecentProfitTrend,
  ProfitRecord,
} from '../utils/profitTracking';
import { portfolioApi, stockApi } from '../utils/api';

export function PortfolioManagement() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [profitHistory, setProfitHistory] = useState<ProfitRecord[]>([]);
  const [dailyProfit, setDailyProfit] = useState({ value: 0, percent: 0 });
  const [weeklyProfit, setWeeklyProfit] = useState({ value: 0, percent: 0 });
  const [monthlyProfit, setMonthlyProfit] = useState({ value: 0, percent: 0 });
  const [formData, setFormData] = useState({
    stockCode: '',
    shares: '',
    buyPrice: '',
  });

  useEffect(() => {
    loadPositions();
  }, []);

  const loadPositions = async () => {
    try {
      // 尝试从API获取数据
      const apiPositions = await portfolioApi.getPositions();
      const stats = await portfolioApi.getPortfolioStats();
      
      setPositions(apiPositions);
      
      // 使用API返回的统计数据生成收益历史
      const history = generateMockProfitHistory(stats.totalValue, stats.totalCost, 30);
      setProfitHistory(history);
      
      // Calculate daily, weekly, monthly profits
      setDailyProfit(calculateDailyProfit(history));
      setWeeklyProfit(calculateWeeklyProfit(history));
      setMonthlyProfit(calculateMonthlyProfit(history));
    } catch (error) {
      console.error('API请求失败，使用本地数据:', error);
      // 失败时使用本地存储的数据
      const stored = getPositions();
      const updated = stored.map(pos => {
        const stock = mockStocks.find(s => s.code === pos.stockCode);
        if (stock) {
          return calculatePositionMetrics(pos, stock.price);
        }
        return pos;
      });
      setPositions(updated);
      
      // Calculate profit statistics
      const totalValue = updated.reduce((sum, pos) => sum + pos.totalValue, 0);
      const totalCost = updated.reduce((sum, pos) => sum + pos.cost, 0);
      
      // Generate mock history for demonstration
      const history = generateMockProfitHistory(totalValue, totalCost, 30);
      setProfitHistory(history);
      
      // Calculate daily, weekly, monthly profits
      setDailyProfit(calculateDailyProfit(history));
      setWeeklyProfit(calculateWeeklyProfit(history));
      setMonthlyProfit(calculateMonthlyProfit(history));
    }
  };

  const handleAddPosition = async () => {
    if (!formData.stockCode || !formData.shares || !formData.buyPrice) {
      return;
    }

    const stock = mockStocks.find(s => s.code === formData.stockCode);
    if (!stock) return;

    const shares = parseFloat(formData.shares);
    const buyPrice = parseFloat(formData.buyPrice);
    const buyDate = new Date().toISOString().split('T')[0];

    try {
      // 尝试通过API添加持仓
      await portfolioApi.addPosition({
        stockCode: stock.code,
        stockName: stock.name,
        shares,
        buyPrice,
        buyDate,
      });
    } catch (error) {
      console.error('API添加持仓失败，使用本地存储:', error);
      // 失败时使用本地存储
      const cost = shares * buyPrice;
      const totalValue = shares * stock.price;
      const profit = totalValue - cost;
      const profitPercent = (profit / cost) * 100;

      addPosition({
        stockCode: stock.code,
        stockName: stock.name,
        shares,
        buyPrice,
        currentPrice: stock.price,
        buyDate,
        cost,
        totalValue,
        profit,
        profitPercent,
      });
    }

    setFormData({ stockCode: '', shares: '', buyPrice: '' });
    setIsDialogOpen(false);
    loadPositions();
  };

  const handleDeletePosition = async (id: string) => {
    try {
      // 尝试通过API删除持仓
      await portfolioApi.deletePosition(id);
    } catch (error) {
      console.error('API删除持仓失败，使用本地存储:', error);
      // 失败时使用本地存储
      deletePosition(id);
    }
    loadPositions();
  };

  const totalValue = positions.reduce((sum, pos) => sum + pos.totalValue, 0);
  const totalCost = positions.reduce((sum, pos) => sum + pos.cost, 0);
  const totalProfit = totalValue - totalCost;
  const totalProfitPercent = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>总市值</CardDescription>
            <CardTitle className="text-2xl">{formatCurrency(totalValue)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>总成本</CardDescription>
            <CardTitle className="text-2xl">{formatCurrency(totalCost)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>总盈亏</CardDescription>
            <CardTitle className={`text-2xl flex items-center gap-2 ${totalProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalProfit >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
              {formatCurrency(Math.abs(totalProfit))}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>收益率</CardDescription>
            <CardTitle className={`text-2xl ${totalProfitPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalProfitPercent >= 0 ? '+' : ''}{totalProfitPercent.toFixed(2)}%
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Positions Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>持仓列表</CardTitle>
              <CardDescription>管理您的股票持仓</CardDescription>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  添加持仓
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>添加新持仓</DialogTitle>
                  <DialogDescription>输入您的股票持仓信息</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label>选择股票</Label>
                    <Select value={formData.stockCode} onValueChange={(value) => setFormData({ ...formData, stockCode: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择股票" />
                      </SelectTrigger>
                      <SelectContent>
                        {mockStocks.map(stock => (
                          <SelectItem key={stock.code} value={stock.code}>
                            {stock.code} - {stock.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>持有股数</Label>
                    <Input
                      type="number"
                      placeholder="输入股数"
                      value={formData.shares}
                      onChange={(e) => setFormData({ ...formData, shares: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>买入价格</Label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="输入买入价格"
                      value={formData.buyPrice}
                      onChange={(e) => setFormData({ ...formData, buyPrice: e.target.value })}
                    />
                  </div>
                  <Button className="w-full" onClick={handleAddPosition}>
                    确认添加
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {positions.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <DollarSign className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>暂无持仓，点击"添加持仓"开始管理您的股票</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>股票代码</TableHead>
                  <TableHead>股票名称</TableHead>
                  <TableHead className="text-right">持股数量</TableHead>
                  <TableHead className="text-right">买入价</TableHead>
                  <TableHead className="text-right">现价</TableHead>
                  <TableHead className="text-right">成本</TableHead>
                  <TableHead className="text-right">市值</TableHead>
                  <TableHead className="text-right">盈亏</TableHead>
                  <TableHead className="text-right">收益率</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {positions.map(position => (
                  <TableRow key={position.id}>
                    <TableCell>{position.stockCode}</TableCell>
                    <TableCell>{position.stockName}</TableCell>
                    <TableCell className="text-right">{formatNumber(position.shares)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(position.buyPrice)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(position.currentPrice)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(position.cost)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(position.totalValue)}</TableCell>
                    <TableCell className={`text-right ${position.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {position.profit >= 0 ? '+' : ''}{formatCurrency(position.profit)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge variant={position.profitPercent >= 0 ? 'default' : 'destructive'}>
                        {position.profitPercent >= 0 ? '+' : ''}{position.profitPercent.toFixed(2)}%
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeletePosition(position.id)}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Profit Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5" />
            收益统计
          </CardTitle>
          <CardDescription>查看日、周、月收益表现</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Profit Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card className="border-2">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardDescription className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    日收益
                  </CardDescription>
                  {dailyProfit.percent >= 0 ? (
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-600" />
                  )}
                </div>
                <CardTitle className={`text-2xl ${dailyProfit.value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {dailyProfit.value >= 0 ? '+' : ''}{formatCurrency(dailyProfit.value)}
                </CardTitle>
                <div className={`text-sm ${dailyProfit.percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {dailyProfit.percent >= 0 ? '+' : ''}{dailyProfit.percent.toFixed(2)}%
                </div>
              </CardHeader>
            </Card>

            <Card className="border-2">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardDescription className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    周收益
                  </CardDescription>
                  {weeklyProfit.percent >= 0 ? (
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-600" />
                  )}
                </div>
                <CardTitle className={`text-2xl ${weeklyProfit.value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {weeklyProfit.value >= 0 ? '+' : ''}{formatCurrency(weeklyProfit.value)}
                </CardTitle>
                <div className={`text-sm ${weeklyProfit.percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {weeklyProfit.percent >= 0 ? '+' : ''}{weeklyProfit.percent.toFixed(2)}%
                </div>
              </CardHeader>
            </Card>

            <Card className="border-2">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardDescription className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    月收益
                  </CardDescription>
                  {monthlyProfit.percent >= 0 ? (
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-600" />
                  )}
                </div>
                <CardTitle className={`text-2xl ${monthlyProfit.value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {monthlyProfit.value >= 0 ? '+' : ''}{formatCurrency(monthlyProfit.value)}
                </CardTitle>
                <div className={`text-sm ${monthlyProfit.percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {monthlyProfit.percent >= 0 ? '+' : ''}{monthlyProfit.percent.toFixed(2)}%
                </div>
              </CardHeader>
            </Card>
          </div>

          {/* Profit Trend Tabs */}
          <Tabs defaultValue="profit" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="profit">盈亏趋势</TabsTrigger>
              <TabsTrigger value="value">市值趋势</TabsTrigger>
            </TabsList>

            <TabsContent value="profit" className="mt-4">
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={profitHistory}>
                  <defs>
                    <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#64748b" 
                    fontSize={12}
                    tickFormatter={(value) => {
                      const date = new Date(value);
                      return `${date.getMonth() + 1}/${date.getDate()}`;
                    }}
                  />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value)}
                    labelFormatter={(label) => `日期: ${label}`}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="profit" 
                    stroke="#22c55e" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorProfit)" 
                    name="盈亏"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </TabsContent>

            <TabsContent value="value" className="mt-4">
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={profitHistory}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#64748b" 
                    fontSize={12}
                    tickFormatter={(value) => {
                      const date = new Date(value);
                      return `${date.getMonth() + 1}/${date.getDate()}`;
                    }}
                  />
                  <YAxis stroke="#64748b" fontSize={12} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value)}
                    labelFormatter={(label) => `日期: ${label}`}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="totalValue" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorValue)" 
                    name="总市值"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
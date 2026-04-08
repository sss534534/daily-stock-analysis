import { useState, lazy, Suspense } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Card } from './components/ui/card';
import { BarChart3, Brain, LineChart, Wallet, TrendingUp, Shield, Target } from 'lucide-react';

const PortfolioManagement = lazy(() => import('./components/PortfolioManagement'));
const StockDiagnosis = lazy(() => import('./components/StockDiagnosis'));
const AIAnalysis = lazy(() => import('./components/AIAnalysis'));
const QuantitativeAnalysis = lazy(() => import('./components/QuantitativeAnalysis'));
const KlineChart = lazy(() => import('./components/KlineChart'));
const MilitaryRules = lazy(() => import('./components/MilitaryRules'));
const InvestmentTool = lazy(() => import('./components/InvestmentTool'));

export default function App() {
  const [activeTab, setActiveTab] = useState('portfolio');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200">
      <div className="container mx-auto py-8 px-4 max-w-7xl">
        {/* Header Section */}
        <div className="mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  智能股票分析系统
                </h1>
                <p className="text-slate-600 mt-2 text-lg">专业级股票分析与量化交易平台</p>
              </div>
              <div className="hidden md:flex items-center gap-4">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-2 rounded-lg border border-blue-100">
                  <span className="text-sm text-blue-700 font-medium">实时市场数据</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Container */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          {/* Main Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            {/* Enhanced Tabs List with Mobile Support */}
            <div className="border-b border-slate-200">
              <div className="overflow-x-auto scrollbar-hide">
                <TabsList className="inline-flex h-14 bg-transparent gap-1 px-2">
                  <TabsTrigger 
                    value="portfolio" 
                    className="flex items-center gap-2 text-sm font-medium hover:bg-slate-50 data-[state=active]:bg-slate-50 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 min-w-[100px] sm:min-w-[120px]"
                  >
                    <Wallet className="w-4 h-4" />
                    <span className="hidden sm:inline">仓位管理</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="diagnosis" 
                    className="flex items-center gap-2 text-sm font-medium hover:bg-slate-50 data-[state=active]:bg-slate-50 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 min-w-[100px] sm:min-w-[120px]"
                  >
                    <BarChart3 className="w-4 h-4" />
                    <span className="hidden sm:inline">股票诊断</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="ai" 
                    className="flex items-center gap-2 text-sm font-medium hover:bg-slate-50 data-[state=active]:bg-slate-50 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 min-w-[100px] sm:min-w-[120px]"
                  >
                    <Brain className="w-4 h-4" />
                    <span className="hidden sm:inline">AI建议</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="quantitative" 
                    className="flex items-center gap-2 text-sm font-medium hover:bg-slate-50 data-[state=active]:bg-slate-50 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 min-w-[100px] sm:min-w-[120px]"
                  >
                    <LineChart className="w-4 h-4" />
                    <span className="hidden sm:inline">量化分析</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="kline" 
                    className="flex items-center gap-2 text-sm font-medium hover:bg-slate-50 data-[state=active]:bg-slate-50 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 min-w-[100px] sm:min-w-[120px]"
                  >
                    <TrendingUp className="w-4 h-4" />
                    <span className="hidden sm:inline">K线分析</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="military-rules" 
                    className="flex items-center gap-2 text-sm font-medium hover:bg-slate-50 data-[state=active]:bg-slate-50 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 min-w-[100px] sm:min-w-[120px]"
                  >
                    <Shield className="w-4 h-4" />
                    <span className="hidden sm:inline">炒股军规</span>
                  </TabsTrigger>
                  <TabsTrigger 
                    value="investment-tool" 
                    className="flex items-center gap-2 text-sm font-medium hover:bg-slate-50 data-[state=active]:bg-slate-50 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600 min-w-[100px] sm:min-w-[120px]"
                  >
                    <Target className="w-4 h-4" />
                    <span className="hidden sm:inline">军规落实</span>
                  </TabsTrigger>
                </TabsList>
              </div>
            </div>

            {/* Content Area with Enhanced Spacing */}
            <div className="p-6 bg-slate-50">
              <TabsContent value="portfolio" className="mt-0">
                <Suspense fallback={<div className="flex items-center justify-center h-64">加载中...</div>}>
                  <PortfolioManagement />
                </Suspense>
              </TabsContent>

              <TabsContent value="diagnosis" className="mt-0">
                <Suspense fallback={<div className="flex items-center justify-center h-64">加载中...</div>}>
                  <StockDiagnosis />
                </Suspense>
              </TabsContent>

              <TabsContent value="ai" className="mt-0">
                <Suspense fallback={<div className="flex items-center justify-center h-64">加载中...</div>}>
                  <AIAnalysis />
                </Suspense>
              </TabsContent>

              <TabsContent value="quantitative" className="mt-0">
                <Suspense fallback={<div className="flex items-center justify-center h-64">加载中...</div>}>
                  <QuantitativeAnalysis />
                </Suspense>
              </TabsContent>

              <TabsContent value="kline" className="mt-0">
                <Card className="p-6 border border-slate-200 shadow-sm">
                  <Suspense fallback={<div className="flex items-center justify-center h-64">加载中...</div>}>
                    <KlineChart stockCode="600036" interval="1d" days={120} />
                  </Suspense>
                </Card>
              </TabsContent>

              <TabsContent value="military-rules" className="mt-0">
                <Card className="p-6 border border-slate-200 shadow-sm">
                  <Suspense fallback={<div className="flex items-center justify-center h-64">加载中...</div>}>
                    <MilitaryRules />
                  </Suspense>
                </Card>
              </TabsContent>

              <TabsContent value="investment-tool" className="mt-0">
                <Card className="p-6 border border-slate-200 shadow-sm">
                  <Suspense fallback={<div className="flex items-center justify-center h-64">加载中...</div>}>
                    <InvestmentTool />
                  </Suspense>
                </Card>
              </TabsContent>
            </div>
          </Tabs>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-slate-500">
          <p>© 2026 智能股票分析系统 | 专业金融分析工具</p>
        </div>
      </div>
    </div>
  );
}

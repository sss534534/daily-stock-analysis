import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Card } from './components/ui/card';
import { PortfolioManagement } from './components/PortfolioManagement';
import { StockDiagnosis } from './components/StockDiagnosis';
import { AIAnalysis } from './components/AIAnalysis';
import { QuantitativeAnalysis } from './components/QuantitativeAnalysis';
import KlineChart from './components/KlineChart';
import MilitaryRules from './components/MilitaryRules';
import InvestmentTool from './components/InvestmentTool';
import { BarChart3, Brain, LineChart, Wallet, TrendingUp, Shield, Target } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('portfolio');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-slate-800">智能股票分析系统</h1>
          <p className="text-slate-600">专业级股票分析与量化交易平台</p>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-7 mb-6 h-auto">
            <TabsTrigger value="portfolio" className="flex items-center gap-2 py-3">
              <Wallet className="w-4 h-4" />
              <span>仓位管理</span>
            </TabsTrigger>
            <TabsTrigger value="diagnosis" className="flex items-center gap-2 py-3">
              <BarChart3 className="w-4 h-4" />
              <span>股票诊断</span>
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center gap-2 py-3">
              <Brain className="w-4 h-4" />
              <span>AI建议</span>
            </TabsTrigger>
            <TabsTrigger value="quantitative" className="flex items-center gap-2 py-3">
              <LineChart className="w-4 h-4" />
              <span>量化分析</span>
            </TabsTrigger>
            <TabsTrigger value="kline" className="flex items-center gap-2 py-3">
              <TrendingUp className="w-4 h-4" />
              <span>K线分析</span>
            </TabsTrigger>
            <TabsTrigger value="military-rules" className="flex items-center gap-2 py-3">
              <Shield className="w-4 h-4" />
              <span>炒股军规</span>
            </TabsTrigger>
            <TabsTrigger value="investment-tool" className="flex items-center gap-2 py-3">
              <Target className="w-4 h-4" />
              <span>军规落实</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="portfolio" className="mt-0">
            <PortfolioManagement />
          </TabsContent>

          <TabsContent value="diagnosis" className="mt-0">
            <StockDiagnosis />
          </TabsContent>

          <TabsContent value="ai" className="mt-0">
            <AIAnalysis />
          </TabsContent>

          <TabsContent value="quantitative" className="mt-0">
            <QuantitativeAnalysis />
          </TabsContent>

          <TabsContent value="kline" className="mt-0">
            <Card className="p-4">
              <KlineChart stockCode="600036" interval="1d" days={120} />
            </Card>
          </TabsContent>

          <TabsContent value="military-rules" className="mt-0">
            <Card className="p-6">
              <MilitaryRules />
            </Card>
          </TabsContent>

          <TabsContent value="investment-tool" className="mt-0">
            <Card className="p-6">
              <InvestmentTool />
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

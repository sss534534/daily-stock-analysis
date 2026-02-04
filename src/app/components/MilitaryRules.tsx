'use client';

import React, { useState, useEffect } from 'react';
import { militaryRulesApi } from '../utils/api';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ChevronDown, ChevronRight, Target, Wallet, PieChart, RefreshCw, Brain, DollarSign, Briefcase } from 'lucide-react';

interface MilitaryRule {
  id: number;
  title: string;
  content: string;
  category: string;
  description: string;
}

interface MilitaryRulesResponse {
  rules: MilitaryRule[];
  total: number;
}

const MilitaryRules: React.FC = () => {
  const [rules, setRules] = useState<MilitaryRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRules, setExpandedRules] = useState<number[]>([]);

  useEffect(() => {
    fetchMilitaryRules();
  }, []);

  const fetchMilitaryRules = async () => {
    try {
      setLoading(true);
      const response = await militaryRulesApi.getMilitaryRules();
      setRules(response.rules);
      setError(null);
    } catch (err) {
      console.error('获取军规失败:', err);
      setError('获取军规失败，请稍后重试');
      // 使用本地模拟数据作为备用
      setRules(getMockMilitaryRules());
    } finally {
      setLoading(false);
    }
  };

  const getMockMilitaryRules = (): MilitaryRule[] => {
    return [
      {
        id: 1,
        title: "军规 1",
        content: "莫求暴富，为自己设定一个长期目标",
        category: "目标设定",
        description: "投资是一场马拉松，不是短跑。设定合理的长期目标，避免追求短期暴富的心态。"
      },
      {
        id: 2,
        title: "军规 2",
        content: "永不满仓，找到自己的资产配置中枢",
        category: "资金管理",
        description: "保持合理的仓位，永远不要满仓操作，建立适合自己风险承受能力的资产配置方案。"
      },
      {
        id: 3,
        title: "军规 3",
        content: "均衡为王，构建基金经理1/2水平的投资组合",
        category: "投资组合",
        description: "Diversification is the only free lunch in investing. 构建均衡的投资组合，降低单一资产风险。"
      },
      {
        id: 4,
        title: "军规 4",
        content: "定期复盘，优胜劣汰再平衡",
        category: "投资管理",
        description: "定期回顾投资表现，淘汰表现不佳的资产，重新平衡投资组合。"
      },
      {
        id: 5,
        title: "军规 5",
        content: "稳定心态，克服贪婪与恐惧",
        category: "心态管理",
        description: "在市场上涨时避免贪婪，在市场下跌时避免恐惧，保持理性的投资心态。"
      },
      {
        id: 6,
        title: "军规 6",
        content: "定期投入，必要时加倍",
        category: "投资策略",
        description: "采用定期投资策略，在市场低迷时可以适当增加投入，降低平均成本。"
      },
      {
        id: 7,
        title: "军规 7",
        content: "做好主业，保持现金流",
        category: "基础保障",
        description: "投资不是生活的全部，做好自己的主业，保持稳定的现金流，为投资提供持续的资金支持。"
      }
    ];
  };

  const toggleRule = (ruleId: number) => {
    setExpandedRules(prev =>
      prev.includes(ruleId) ? prev.filter(id => id !== ruleId) : [...prev, ruleId]
    );
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case '目标设定':
        return <Target className="w-5 h-5" />;
      case '资金管理':
        return <Wallet className="w-5 h-5" />;
      case '投资组合':
        return <PieChart className="w-5 h-5" />;
      case '投资管理':
        return <RefreshCw className="w-5 h-5" />;
      case '心态管理':
        return <Brain className="w-5 h-5" />;
      case '投资策略':
        return <DollarSign className="w-5 h-5" />;
      case '基础保障':
        return <Briefcase className="w-5 h-5" />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">加载军规数据...</span>
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
      {/* 军规标题 */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          炒股7条军规
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          投资的基本原则和行为准则
        </p>
      </div>

      {/* 军规层次结构 */}
      <div className="relative">
        {/* 顶层：我是谁 */}
        <div className="flex justify-center mb-8">
          <Card className="w-full max-w-md border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20">
            <CardHeader className="pb-2">
              <CardTitle className="text-center text-blue-800 dark:text-blue-300">我是谁</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* 军规1 */}
        <div className="flex justify-center mb-8">
          <Card className="w-full max-w-2xl">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{rules[0]?.title}</CardTitle>
                <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                  {rules[0]?.category}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-gray-800 dark:text-gray-200 font-medium">
                  {rules[0]?.content}
                </p>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {rules[0]?.description}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 连接线 */}
        <div className="absolute top-[120px] left-1/2 transform -translate-x-1/2 w-1 h-16 bg-gray-300 dark:bg-gray-700"></div>
        <div className="flex justify-center mb-8">
          <div className="flex space-x-12">
            {/* 怎么买 */}
            <div>
              <Card className="w-full max-w-md border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20">
                <CardHeader className="pb-2">
                  <CardTitle className="text-center text-green-800 dark:text-green-300">怎么买</CardTitle>
                </CardHeader>
              </Card>
              <div className="mt-4">
                <Card className="w-full">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{rules[1]?.title}</CardTitle>
                      <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                        {rules[1]?.category}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <p className="text-gray-800 dark:text-gray-200 font-medium">
                        {rules[1]?.content}
                      </p>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">
                        {rules[1]?.description}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* 买什么 */}
            <div>
              <Card className="w-full max-w-md border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900/20">
                <CardHeader className="pb-2">
                  <CardTitle className="text-center text-purple-800 dark:text-purple-300">买什么</CardTitle>
                </CardHeader>
              </Card>
              <div className="mt-4">
                <Card className="w-full">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{rules[2]?.title}</CardTitle>
                      <Badge variant="secondary" className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">
                        {rules[2]?.category}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <p className="text-gray-800 dark:text-gray-200 font-medium">
                        {rules[2]?.content}
                      </p>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">
                        {rules[2]?.description}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>

        {/* 连接线 */}
        <div className="absolute top-[320px] left-1/2 transform -translate-x-1/2 w-1 h-16 bg-gray-300 dark:bg-gray-700"></div>

        {/* 技术支持、心态支持、资金支持 */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-8">
            {/* 技术支持 */}
            <div className="flex flex-col items-center">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">技术支持</div>
              <Card className="w-full max-w-xs">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{rules[3]?.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-800 dark:text-gray-200 text-sm">
                    {rules[3]?.content}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* 心态支持 */}
            <div className="flex flex-col items-center">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">心态支持</div>
              <Card className="w-full max-w-xs">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{rules[4]?.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-800 dark:text-gray-200 text-sm">
                    {rules[4]?.content}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* 资金支持 */}
            <div className="flex flex-col items-center">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">资金支持</div>
              <Card className="w-full max-w-xs">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{rules[5]?.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-800 dark:text-gray-200 text-sm">
                    {rules[5]?.content}
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* 连接线 */}
        <div className="absolute top-[520px] left-1/2 transform -translate-x-1/2 w-1 h-16 bg-gray-300 dark:bg-gray-700"></div>

        {/* 底层基石：军规7 */}
        <div className="flex justify-center">
          <Card className="w-full max-w-2xl border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{rules[6]?.title}</CardTitle>
                <Badge variant="secondary" className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300">
                  {rules[6]?.category}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-gray-800 dark:text-gray-200 font-medium">
                  {rules[6]?.content}
                </p>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  {rules[6]?.description}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 军规详情列表 */}
      <div className="mt-12">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          军规详情
        </h3>
        <div className="space-y-4">
          {rules.map((rule) => (
            <Card key={rule.id} className="border-gray-200 dark:border-gray-700">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getCategoryIcon(rule.category)}
                    <CardTitle className="text-lg">{rule.title}</CardTitle>
                  </div>
                  <button
                    onClick={() => toggleRule(rule.id)}
                    className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    {expandedRules.includes(rule.id) ? (
                      <ChevronDown className="w-5 h-5" />
                    ) : (
                      <ChevronRight className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-800 dark:text-gray-200 mb-2">
                  {rule.content}
                </p>
                {expandedRules.includes(rule.id) && (
                  <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                    <p className="text-gray-600 dark:text-gray-400">
                      {rule.description}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MilitaryRules;

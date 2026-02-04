from fastapi import APIRouter
from app.models.military_rules import MilitaryRule, MilitaryRuleResponse

router = APIRouter()

# 炒股7条军规数据
military_rules = [
    MilitaryRule(
        id=1,
        title="军规 1",
        content="莫求暴富，为自己设定一个长期目标",
        category="目标设定",
        description="投资是一场马拉松，不是短跑。设定合理的长期目标，避免追求短期暴富的心态。"
    ),
    MilitaryRule(
        id=2,
        title="军规 2",
        content="永不满仓，找到自己的资产配置中枢",
        category="资金管理",
        description="保持合理的仓位，永远不要满仓操作，建立适合自己风险承受能力的资产配置方案。"
    ),
    MilitaryRule(
        id=3,
        title="军规 3",
        content="均衡为王，构建基金经理1/2水平的投资组合",
        category="投资组合",
        description=" diversification is the only free lunch in investing. 构建均衡的投资组合，降低单一资产风险。"
    ),
    MilitaryRule(
        id=4,
        title="军规 4",
        content="定期复盘，优胜劣汰再平衡",
        category="投资管理",
        description="定期回顾投资表现，淘汰表现不佳的资产，重新平衡投资组合。"
    ),
    MilitaryRule(
        id=5,
        title="军规 5",
        content="稳定心态，克服贪婪与恐惧",
        category="心态管理",
        description="在市场上涨时避免贪婪，在市场下跌时避免恐惧，保持理性的投资心态。"
    ),
    MilitaryRule(
        id=6,
        title="军规 6",
        content="定期投入，必要时加倍",
        category="投资策略",
        description="采用定期投资策略，在市场低迷时可以适当增加投入，降低平均成本。"
    ),
    MilitaryRule(
        id=7,
        title="军规 7",
        content="做好主业，保持现金流",
        category="基础保障",
        description="投资不是生活的全部，做好自己的主业，保持稳定的现金流，为投资提供持续的资金支持。"
    )
]

# 获取所有军规
@router.get("", response_model=MilitaryRuleResponse)
async def get_military_rules():
    return MilitaryRuleResponse(
        rules=military_rules,
        total=len(military_rules)
    )

# 获取单个军规
@router.get("/{rule_id}", response_model=MilitaryRule)
async def get_military_rule(rule_id: int):
    for rule in military_rules:
        if rule.id == rule_id:
            return rule
    # 如果没有找到，返回第一条军规
    return military_rules[0]

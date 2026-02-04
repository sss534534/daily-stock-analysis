# 缠论技术分析核心算法
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class KLine:
    def __init__(self, timestamp: int, date: str, open: float, high: float, low: float, close: float, volume: int):
        self.timestamp = timestamp
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

class ChanPivot:
    def __init__(self, type: str, price: float, date: str):
        self.type = type  # "high" or "low"
        self.price = price
        self.date = date

class ChanCentral:
    def __init__(self, start_date: str, end_date: str, high: float, low: float, level: int):
        self.start_date = start_date
        self.end_date = end_date
        self.high = high
        self.low = low
        self.level = level
        self.mid = (high + low) / 2

class ChanBuyPoint:
    def __init__(self, price: float, date: str, confidence: float, type: str):
        self.price = price
        self.date = date
        self.confidence = confidence
        self.type = type  # "first", "second", "third"

class ChanSellPoint:
    def __init__(self, price: float, date: str, confidence: float, type: str):
        self.price = price
        self.date = date
        self.confidence = confidence
        self.type = type  # "first", "second", "third"

class ChanTheoryAnalyzer:
    def __init__(self):
        self.min_central_bars = 5  # 中枢最小K线数量
        self.central_threshold = 0.03  # 中枢阈值，用于判断中枢区间

    def parse_kline_data(self, kline_data: List[Dict]) -> List[KLine]:
        """解析K线数据"""
        return [
            KLine(
                timestamp=item["timestamp"],
                date=item["date"],
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                volume=item["volume"]
            )
            for item in kline_data
        ]

    def identify_pivots(self, klines: List[KLine]) -> List[ChanPivot]:
        """识别转折点"""
        if len(klines) < 3:
            return []

        pivots = []

        # 识别第一个可能的转折点
        if klines[0].high > klines[1].high and klines[1].high < klines[2].high:
            pivots.append(ChanPivot("low", klines[1].low, klines[1].date))
        elif klines[0].low < klines[1].low and klines[1].low > klines[2].low:
            pivots.append(ChanPivot("high", klines[1].high, klines[1].date))

        # 识别中间的转折点
        for i in range(1, len(klines) - 1):
            current = klines[i]
            prev = klines[i - 1]
            next_k = klines[i + 1]

            # 低点转折点
            if current.low < prev.low and current.low < next_k.low:
                pivots.append(ChanPivot("low", current.low, current.date))
            # 高点转折点
            elif current.high > prev.high and current.high > next_k.high:
                pivots.append(ChanPivot("high", current.high, current.date))

        # 识别最后一个可能的转折点
        if len(klines) >= 3:
            last_idx = len(klines) - 1
            if klines[last_idx].high > klines[last_idx - 1].high and klines[last_idx - 1].high < klines[last_idx - 2].high:
                pivots.append(ChanPivot("low", klines[last_idx - 1].low, klines[last_idx - 1].date))
            elif klines[last_idx].low < klines[last_idx - 1].low and klines[last_idx - 1].low > klines[last_idx - 2].low:
                pivots.append(ChanPivot("high", klines[last_idx - 1].high, klines[last_idx - 1].date))

        return pivots

    def identify_centrals(self, klines: List[KLine]) -> List[ChanCentral]:
        """识别中枢"""
        if len(klines) < self.min_central_bars:
            return []

        centrals = []
        i = 0

        while i + self.min_central_bars <= len(klines):
            window = klines[i:i + self.min_central_bars]
            high = max(k.high for k in window)
            low = min(k.low for k in window)
            
            # 检查是否形成中枢
            if (high - low) / low < self.central_threshold:
                central = ChanCentral(
                    start_date=window[0].date,
                    end_date=window[-1].date,
                    high=high,
                    low=low,
                    level=1  # 暂时设置为1级中枢
                )
                centrals.append(central)
                i += self.min_central_bars
            else:
                i += 1

        return centrals

    def identify_buy_sell_points(self, klines: List[KLine], centrals: List[ChanCentral]) -> Tuple[List[ChanBuyPoint], List[ChanSellPoint]]:
        """识别买卖点"""
        buy_points = []
        sell_points = []

        if not centrals or len(klines) < 10:
            return buy_points, sell_points

        # 分析最近的中枢
        latest_central = centrals[-1]
        latest_klines = klines[-20:]  # 分析最近20根K线

        # 识别买点
        for i, kline in enumerate(latest_klines):
            # 第一类买点：中枢下方的背驰
            if kline.low < latest_central.low:
                # 检查是否有背驰迹象（简化判断）
                if i > 5:
                    prev_low = min(k.low for k in latest_klines[i-5:i])
                    if kline.low < prev_low and kline.volume < latest_klines[i-1].volume:
                        buy_points.append(ChanBuyPoint(
                            price=kline.low,
                            date=kline.date,
                            confidence=85.0,
                            type="first"
                        ))

            # 第二类买点：中枢下方的回调不创新低
            elif kline.low >= latest_central.low and kline.low < latest_central.mid:
                if i > 2:
                    if kline.low > latest_klines[i-1].low and kline.low > latest_klines[i-2].low:
                        buy_points.append(ChanBuyPoint(
                            price=kline.low,
                            date=kline.date,
                            confidence=80.0,
                            type="second"
                        ))

            # 第三类买点：中枢上方的回调不回中枢
            elif kline.low > latest_central.high:
                if i > 2:
                    if kline.low > latest_central.high and kline.close > kline.open:
                        buy_points.append(ChanBuyPoint(
                            price=kline.low,
                            date=kline.date,
                            confidence=75.0,
                            type="third"
                        ))

        # 识别卖点
        for i, kline in enumerate(latest_klines):
            # 第一类卖点：中枢上方的背驰
            if kline.high > latest_central.high:
                if i > 5:
                    prev_high = max(k.high for k in latest_klines[i-5:i])
                    if kline.high > prev_high and kline.volume < latest_klines[i-1].volume:
                        sell_points.append(ChanSellPoint(
                            price=kline.high,
                            date=kline.date,
                            confidence=85.0,
                            type="first"
                        ))

            # 第二类卖点：中枢上方的反弹不创新高
            elif kline.high <= latest_central.high and kline.high > latest_central.mid:
                if i > 2:
                    if kline.high < latest_klines[i-1].high and kline.high < latest_klines[i-2].high:
                        sell_points.append(ChanSellPoint(
                            price=kline.high,
                            date=kline.date,
                            confidence=80.0,
                            type="second"
                        ))

            # 第三类卖点：中枢下方的反弹不回中枢
            elif kline.high < latest_central.low:
                if i > 2:
                    if kline.high < latest_central.low and kline.close < kline.open:
                        sell_points.append(ChanSellPoint(
                            price=kline.high,
                            date=kline.date,
                            confidence=75.0,
                            type="third"
                        ))

        return buy_points, sell_points

    def analyze(self, kline_data: List[Dict]) -> Dict:
        """执行完整的缠论分析"""
        # 解析K线数据
        klines = self.parse_kline_data(kline_data)
        
        # 识别转折点
        pivots = self.identify_pivots(klines)
        
        # 识别中枢
        centrals = self.identify_centrals(klines)
        
        # 识别买卖点
        buy_points, sell_points = self.identify_buy_sell_points(klines, centrals)
        
        # 分析趋势
        trend = self.analyze_trend(klines, centrals)
        
        # 生成线段分析
        segments = self.analyze_segments(klines, pivots)
        
        return {
            "trend": trend,
            "pivots": [{
                "type": p.type,
                "price": p.price,
                "date": p.date
            } for p in pivots],
            "centrals": [{
                "start_date": c.start_date,
                "end_date": c.end_date,
                "high": c.high,
                "low": c.low,
                "mid": c.mid,
                "level": c.level
            } for c in centrals],
            "buyPoints": [{
                "price": b.price,
                "date": b.date,
                "confidence": b.confidence,
                "type": b.type
            } for b in buy_points],
            "sellPoints": [{
                "price": s.price,
                "date": s.date,
                "confidence": s.confidence,
                "type": s.type
            } for s in sell_points],
            "segments": segments
        }

    def analyze_trend(self, klines: List[KLine], centrals: List[ChanCentral]) -> str:
        """分析趋势"""
        if not centrals:
            # 基于最近价格走势判断
            if len(klines) >= 10:
                recent = klines[-10:]
                start_price = recent[0].close
                end_price = recent[-1].close
                if end_price > start_price * 1.05:
                    return "up"
                elif end_price < start_price * 0.95:
                    return "down"
            return "sideways"

        # 基于中枢位置判断趋势
        latest_central = centrals[-1]
        latest_price = klines[-1].close

        if latest_price > latest_central.high:
            return "up"
        elif latest_price < latest_central.low:
            return "down"
        else:
            return "sideways"

    def analyze_segments(self, klines: List[KLine], pivots: List[ChanPivot]) -> List[str]:
        """分析线段"""
        segments = []

        if len(pivots) >= 2:
            # 分析最近的转折点
            latest_pivot = pivots[-1]
            second_latest_pivot = pivots[-2]

            if latest_pivot.type == "high" and second_latest_pivot.type == "low":
                segments.append("当前处于上涨线段中")
            elif latest_pivot.type == "low" and second_latest_pivot.type == "high":
                segments.append("当前处于下跌线段中")

        if len(klines) >= 5:
            # 分析最近的K线形态
            recent = klines[-5:]
            high = max(k.high for k in recent)
            low = min(k.low for k in recent)
            if high == recent[-1].high:
                segments.append("线段可能即将向上突破")
            elif low == recent[-1].low:
                segments.append("线段可能即将向下突破")

        return segments

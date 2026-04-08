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
        """识别转折点（优化版）"""
        if len(klines) < 5:
            return []

        pivots = []
        
        # 使用K线包含关系处理（缠论中的包含关系处理）
        processed_klines = self._process_included_klines(klines)
        
        if len(processed_klines) < 3:
            return []

        # 识别中间的转折点
        for i in range(1, len(processed_klines) - 1):
            current = processed_klines[i]
            prev = processed_klines[i - 1]
            next_k = processed_klines[i + 1]

            # 低点转折点（底分型）
            if current.low < prev.low and current.low < next_k.low:
                # 确认是有效底分型
                if i > 1 and i < len(processed_klines) - 2:
                    prev_prev = processed_klines[i - 2]
                    next_next = processed_klines[i + 2]
                    if current.low <= prev_prev.low and current.low <= next_next.low:
                        pivots.append(ChanPivot("low", current.low, current.date))
                else:
                    pivots.append(ChanPivot("low", current.low, current.date))
                    
            # 高点转折点（顶分型）
            elif current.high > prev.high and current.high > next_k.high:
                # 确认是有效顶分型
                if i > 1 and i < len(processed_klines) - 2:
                    prev_prev = processed_klines[i - 2]
                    next_next = processed_klines[i + 2]
                    if current.high >= prev_prev.high and current.high >= next_next.high:
                        pivots.append(ChanPivot("high", current.high, current.date))
                else:
                    pivots.append(ChanPivot("high", current.high, current.date))

        # 过滤重复和相邻的转折点
        filtered_pivots = []
        for i, pivot in enumerate(pivots):
            if i == 0:
                filtered_pivots.append(pivot)
            else:
                prev_pivot = filtered_pivots[-1]
                # 确保转折点类型交替出现
                if pivot.type != prev_pivot.type:
                    filtered_pivots.append(pivot)

        return filtered_pivots
    
    def _process_included_klines(self, klines: List[KLine]) -> List[KLine]:
        """处理K线包含关系"""
        if len(klines) < 2:
            return klines
            
        processed = [klines[0]]
        
        for i in range(1, len(klines)):
            current = klines[i]
            last = processed[-1]
            
            # 判断是否存在包含关系
            if (current.low >= last.low and current.high <= last.high) or \
               (last.low >= current.low and last.high <= current.high):
                # 存在包含关系，合并K线
                new_high = max(last.high, current.high)
                new_low = min(last.low, current.low)
                new_open = last.open  # 保留第一个K线的开盘价
                new_close = current.close  # 保留最后一个K线的收盘价
                
                merged_kline = KLine(
                    timestamp=current.timestamp,
                    date=current.date,
                    open=new_open,
                    high=new_high,
                    low=new_low,
                    close=new_close,
                    volume=last.volume + current.volume
                )
                processed[-1] = merged_kline
            else:
                processed.append(current)
                
        return processed

    def identify_centrals(self, klines: List[KLine]) -> List[ChanCentral]:
        """识别中枢（优化版）"""
        if len(klines) < 10:  # 中枢需要至少5根K线，加上前后的线段
            return []

        centrals = []
        
        # 先识别转折点
        pivots = self.identify_pivots(klines)
        
        if len(pivots) < 4:  # 至少需要4个转折点才能形成中枢（3个线段）
            return []
        
        # 基于转折点识别中枢
        for i in range(2, len(pivots) - 1):
            # 检查是否有3个连续的线段重叠
            if i >= 2 and i + 1 < len(pivots):
                # 获取三个连续的转折点
                p1 = pivots[i-2]
                p2 = pivots[i-1]
                p3 = pivots[i]
                p4 = pivots[i+1]
                
                # 计算三个线段的价格区间
                if p1.type == "low" and p2.type == "high" and p3.type == "low" and p4.type == "high":
                    # 上涨-下跌-上涨结构
                    seg1_high = p2.price
                    seg1_low = p1.price
                    seg2_high = p2.price
                    seg2_low = p3.price
                    seg3_high = p4.price
                    seg3_low = p3.price
                    
                    # 计算重叠区间
                    overlap_high = min(seg1_high, seg2_high, seg3_high)
                    overlap_low = max(seg1_low, seg2_low, seg3_low)
                    
                    if overlap_high > overlap_low:
                        # 找到对应的K线区间
                        start_idx = self._find_kline_index_by_date(klines, p1.date)
                        end_idx = self._find_kline_index_by_date(klines, p4.date)
                        
                        if start_idx >= 0 and end_idx >= 0 and end_idx - start_idx >= 4:
                            central = ChanCentral(
                                start_date=klines[start_idx].date,
                                end_date=klines[end_idx].date,
                                high=overlap_high,
                                low=overlap_low,
                                level=self._determine_central_level(overlap_high, overlap_low, klines)
                            )
                            centrals.append(central)
                
                elif p1.type == "high" and p2.type == "low" and p3.type == "high" and p4.type == "low":
                    # 下跌-上涨-下跌结构
                    seg1_high = p1.price
                    seg1_low = p2.price
                    seg2_high = p3.price
                    seg2_low = p2.price
                    seg3_high = p3.price
                    seg3_low = p4.price
                    
                    # 计算重叠区间
                    overlap_high = min(seg1_high, seg2_high, seg3_high)
                    overlap_low = max(seg1_low, seg2_low, seg3_low)
                    
                    if overlap_high > overlap_low:
                        # 找到对应的K线区间
                        start_idx = self._find_kline_index_by_date(klines, p1.date)
                        end_idx = self._find_kline_index_by_date(klines, p4.date)
                        
                        if start_idx >= 0 and end_idx >= 0 and end_idx - start_idx >= 4:
                            central = ChanCentral(
                                start_date=klines[start_idx].date,
                                end_date=klines[end_idx].date,
                                high=overlap_high,
                                low=overlap_low,
                                level=self._determine_central_level(overlap_high, overlap_low, klines)
                            )
                            centrals.append(central)
        
        # 过滤重叠的中枢，保留级别更高的
        filtered_centrals = self._filter_overlapping_centrals(centrals)
        
        return filtered_centrals
    
    def _find_kline_index_by_date(self, klines: List[KLine], date: str) -> int:
        """根据日期查找K线索引"""
        for i, kline in enumerate(klines):
            if kline.date == date:
                return i
        return -1
    
    def _determine_central_level(self, high: float, low: float, klines: List[KLine]) -> int:
        """确定中枢级别"""
        # 计算中枢高度
        central_height = high - low
        
        # 计算整体价格区间
        overall_high = max(k.high for k in klines)
        overall_low = min(k.low for k in klines)
        overall_range = overall_high - overall_low
        
        if overall_range == 0:
            return 1
        
        # 根据中枢高度占整体区间的比例确定级别
        ratio = central_height / overall_range
        
        if ratio > 0.3:
            return 3  # 高级别中枢
        elif ratio > 0.15:
            return 2  # 中级别中枢
        else:
            return 1  # 低级别中枢
    
    def _filter_overlapping_centrals(self, centrals: List[ChanCentral]) -> List[ChanCentral]:
        """过滤重叠的中枢"""
        if len(centrals) <= 1:
            return centrals
        
        # 按级别降序排序
        sorted_centrals = sorted(centrals, key=lambda c: c.level, reverse=True)
        
        filtered = []
        for central in sorted_centrals:
            is_overlapping = False
            for existing in filtered:
                # 检查是否重叠
                if not (central.high < existing.low or central.low > existing.high):
                    is_overlapping = True
                    break
            if not is_overlapping:
                filtered.append(central)
        
        return filtered

    def identify_buy_sell_points(self, klines: List[KLine], centrals: List[ChanCentral]) -> Tuple[List[ChanBuyPoint], List[ChanSellPoint]]:
        """识别买卖点（优化版）"""
        buy_points = []
        sell_points = []

        if not centrals or len(klines) < 15:
            return buy_points, sell_points

        # 识别转折点
        pivots = self.identify_pivots(klines)
        
        if len(pivots) < 3:
            return buy_points, sell_points

        # 分析最近的中枢
        latest_central = centrals[-1]
        latest_price = klines[-1].close

        # 计算背驰（简化版：通过比较力度）
        def calculate_force(prices, start_idx, end_idx):
            """计算价格变动力度"""
            if end_idx <= start_idx:
                return 0
            return abs(prices[end_idx] - prices[start_idx]) / (end_idx - start_idx)

        # 识别第一类买点：中枢下方的背驰
        if latest_price < latest_central.low:
            # 查找最近的两个低点
            recent_lows = []
            for i in range(len(klines)-1, max(0, len(klines)-30), -1):
                if klines[i].low < latest_central.low:
                    recent_lows.append((i, klines[i].low))
                if len(recent_lows) >= 2:
                    break
            
            if len(recent_lows) >= 2:
                # 计算两段下跌的力度
                prices = [k.close for k in klines]
                force1 = calculate_force(prices, recent_lows[1][0], recent_lows[0][0])
                
                # 如果当前下跌力度小于前一段，可能发生背驰
                if force1 < 0.02:  # 力度阈值
                    buy_points.append(ChanBuyPoint(
                        price=recent_lows[0][1],
                        date=klines[recent_lows[0][0]].date,
                        confidence=85.0,
                        type="first"
                    ))

        # 识别第二类买点：中枢下方的回调不创新低
        elif latest_price >= latest_central.low and latest_price < latest_central.high:
            # 查找最近的回调低点
            for i in range(len(klines)-1, max(0, len(klines)-20), -1):
                if klines[i].low < latest_central.high and klines[i].low > latest_central.low:
                    # 检查是否形成底分型
                    if i >= 2:
                        if klines[i].low < klines[i-1].low and klines[i].low < klines[i+1].low:
                            buy_points.append(ChanBuyPoint(
                                price=klines[i].low,
                                date=klines[i].date,
                                confidence=80.0,
                                type="second"
                            ))
                            break

        # 识别第三类买点：中枢上方的回调不回中枢
        elif latest_price > latest_central.high:
            # 查找最近的回调低点
            for i in range(len(klines)-1, max(0, len(klines)-20), -1):
                if klines[i].low > latest_central.high:
                    # 检查是否形成底分型
                    if i >= 2:
                        if klines[i].low < klines[i-1].low and klines[i].low < klines[i+1].low:
                            buy_points.append(ChanBuyPoint(
                                price=klines[i].low,
                                date=klines[i].date,
                                confidence=75.0,
                                type="third"
                            ))
                            break

        # 识别第一类卖点：中枢上方的背驰
        if latest_price > latest_central.high:
            # 查找最近的两个高点
            recent_highs = []
            for i in range(len(klines)-1, max(0, len(klines)-30), -1):
                if klines[i].high > latest_central.high:
                    recent_highs.append((i, klines[i].high))
                if len(recent_highs) >= 2:
                    break
            
            if len(recent_highs) >= 2:
                # 计算两段上涨的力度
                prices = [k.close for k in klines]
                force1 = calculate_force(prices, recent_highs[1][0], recent_highs[0][0])
                
                # 如果当前上涨力度小于前一段，可能发生背驰
                if force1 < 0.02:  # 力度阈值
                    sell_points.append(ChanSellPoint(
                        price=recent_highs[0][1],
                        date=klines[recent_highs[0][0]].date,
                        confidence=85.0,
                        type="first"
                    ))

        # 识别第二类卖点：中枢上方的反弹不创新高
        elif latest_price <= latest_central.high and latest_price > latest_central.low:
            # 查找最近的反弹高点
            for i in range(len(klines)-1, max(0, len(klines)-20), -1):
                if klines[i].high > latest_central.low and klines[i].high < latest_central.high:
                    # 检查是否形成顶分型
                    if i >= 2:
                        if klines[i].high > klines[i-1].high and klines[i].high > klines[i+1].high:
                            sell_points.append(ChanSellPoint(
                                price=klines[i].high,
                                date=klines[i].date,
                                confidence=80.0,
                                type="second"
                            ))
                            break

        # 识别第三类卖点：中枢下方的反弹不回中枢
        elif latest_price < latest_central.low:
            # 查找最近的反弹高点
            for i in range(len(klines)-1, max(0, len(klines)-20), -1):
                if klines[i].high < latest_central.low:
                    # 检查是否形成顶分型
                    if i >= 2:
                        if klines[i].high > klines[i-1].high and klines[i].high > klines[i+1].high:
                            sell_points.append(ChanSellPoint(
                                price=klines[i].high,
                                date=klines[i].date,
                                confidence=75.0,
                                type="third"
                            ))
                            break

        # 去重并按日期排序
        buy_points.sort(key=lambda x: x.date)
        sell_points.sort(key=lambda x: x.date)
        
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

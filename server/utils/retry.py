"""
重试机制工具
实现指数退避重试算法
"""

import time
import functools
from typing import Callable, Any, Optional

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 延迟增长因子
        exceptions: 需要捕获的异常类型
    
    Returns:
        装饰后的函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempts = 0
            current_delay = delay
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    
                    # 指数退避
                    wait_time = current_delay * (backoff_factor ** (attempts - 1))
                    print(f"尝试 {attempts}/{max_attempts} 失败: {e}，等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

class RetryManager:
    """
    重试管理器
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 30.0
    ):
        """
        初始化重试管理器
        
        Args:
            max_attempts: 最大重试次数
            initial_delay: 初始延迟时间（秒）
            backoff_factor: 延迟增长因子
            max_delay: 最大延迟时间（秒）
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行带重试的函数
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
        
        Returns:
            函数执行结果
        """
        attempts = 0
        
        while attempts < self.max_attempts:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempts += 1
                if attempts >= self.max_attempts:
                    raise
                
                # 计算延迟时间
                delay = min(
                    self.initial_delay * (self.backoff_factor ** (attempts - 1)),
                    self.max_delay
                )
                
                print(f"尝试 {attempts}/{self.max_attempts} 失败: {e}，等待 {delay:.2f} 秒后重试...")
                time.sleep(delay)
        
        return func(*args, **kwargs)

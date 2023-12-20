"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 15/12/2023
@Description  :
"""
from functools import wraps
from types import FunctionType
from typing import Callable

import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from timeit import default_timer as timer
from pathlib import Path
from contextlib import contextmanager

from src.app.config import qt_logger

# TODO: add decorator func
# TODO: add fixed time test
# TODO: add resource monitor as single multi tests


class TimeTracker:
    _instance = None

    def __init__(self, base_path):
        pass

    def __new__(cls, base_path):
        if cls._instance is None:
            cls._instance = super(TimeTracker, cls).__new__(cls)
            cls._instance.__init_once(base_path)
        return cls._instance

    def __init_once(self, base_path):
        self.records = {}
        self.base_path = Path(base_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Call this method to clean up and save the plots."""
        self.save_plots()

    @contextmanager
    def track(self, name):
        """Context manager to track the execution time of a block of code."""
        start = timer()
        try:
            yield
        except Exception as e:
            qt_logger.error(f"TimeTracker.track Error at  {name} with {e}")
            raise e
        finally:
            end = timer()
            self.records.setdefault(name, []).append(end - start)

    def track_func(self, func: Callable):
        """self.track decorator for functions"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 根据被装饰函数的类型确定如何获取跟踪名称
            if isinstance(func, FunctionType):
                name = func.__qualname__  # 对于类方法和静态方法
            else:
                # 对于实例方法
                name = f"{args[0].__class__.__name__}.{func.__name__}"

            with self.track(name):
                return func(*args, **kwargs)

        return wrapper

    def save_plots(self):
        output_directory = self.base_path / \
            f"timetracker_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_directory.mkdir(parents=True, exist_ok=True)

        for name, durations in self.records.items():
            plt.figure()
            x = np.arange(1, len(durations) + 1)
            y = np.array(durations)
            plt.plot(x, y, label='Execution Time')

            # Calculating and plotting the average line
            avg = np.mean(y)
            plt.axhline(
                y=avg,
                color='r',
                linestyle='--',
                label=f'Average: {avg:.4f}s')

            # Plotting a fitting curve
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x, p(x), "r--", label=f'Fit: {z[0]:.2f}x + {z[1]:.2f}')

            plt.title(f"Execution Time for '{name}'")
            plt.xlabel('Runs')
            plt.ylabel('Time (seconds)')
            plt.legend()
            plt.savefig(output_directory / f"{name}.png")
            plt.close()


# Example usage with specified path
output_path = r'C:\Users\18317\python\BoostFace_pyqt6\tests\performance'
time_tracker = TimeTracker(output_path)

if __name__ == '__main__':
    with time_tracker.track("task1"):
        time.sleep(1)  # Simulate a task taking 1 second
    with time_tracker.track("task1"):
        time.sleep(2)  # Simulate the same task taking 2 seconds
    with time_tracker.track("task2"):
        time.sleep(0.5)  # Simulate a different task taking 0.5 seconds
    time_tracker.close()

"""
test on socket or async by sending image data or message
"""
import threading

import time

import numpy as np


# 调整数组大小以减少内存使用
def cpu_intensive_numpy_operation_smaller():
    arr = np.random.rand(1000, 1000)
    result = np.linalg.inv(arr)
    return result


# 单线程测试
start_time = time.time()
cpu_intensive_numpy_operation_smaller()
single_thread_time = time.time() - start_time

# 多线程测试
threads = []
thread_count = 5
start_time = time.time()
for _ in range(thread_count):
    thread = threading.Thread(target=cpu_intensive_numpy_operation_smaller)
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
multi_thread_time = time.time() - start_time

print(single_thread_time, multi_thread_time, single_thread_time / multi_thread_time)

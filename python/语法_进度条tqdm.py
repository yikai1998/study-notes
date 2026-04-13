# coding=gbk 

from tqdm import tqdm 
import time 
from multiprocessing import Pool 

# Introduction
"""
tqdm is a fast, extensible progress bar for Python and CLI (Command Line Interface).  
It's an open-source project that can be used to add a visual progress meter to loops and other iterative processes.  
It's particularly useful for long-running tasks where you want to give users feedback on the progress of the operation. 
""" 


# Sample1
for i in tqdm(range(20), desc='processing'):
    time.sleep(1)


# Sample2 - cowork with Pools
def do_work(x):
    time.sleep(1)
    return x**x

if __name__ == '__main__':
    with Pool(4) as p:
        list(tqdm(p.imap(do_work, range(20)), total=len(range(20))))
"""
While some scripts might work fine without the guard, it's considered best practice to include `if __name__ == "__main__": ` when:
 Defining or Creating Multiprocessing Pools: Always include this guard when your script uses the multiprocessing module, especially when defining pools or processing data in parallel, to ensure cross-platform compatibility and prevent execution issues.
 Writing Reusable Code or Libraries: Use it to prevent code from being executed unintentionally when your script is imported as a module in other scripts.
 Ensuring Clarity and Safety: Adding this guard helps clarify the execution entry point and ensure resource-intensive initialization only occurs when intended.

Here's a comparison of map, imap, and imap_unordered: 
map 
Synchronous Execution: map applies the given function to all items in the input iterable and returns a list of results. It waits for all tasks to complete before returning any results. 
Use Case: Best used when you need all results and don't need them in real-time. It's simple and straightforward for cases where you can afford to wait for all tasks to finish. 
Performance: May be slightly faster than imap because it can optimize the distribution of tasks since it knows the total number of tasks upfront. 

imap 
Asynchronous Execution: imap also applies the function to all items in the input iterable but returns an iterator. It yields results as soon as they are available, which allows for real-time processing. 
Use Case: Ideal for tasks where you want to process results as they come in, or when you want to display a progress bar (like with tqdm), or when you're dealing with a large number of tasks and don't want to wait for all of them to complete before starting to process the results. 
Memory Usage: Can be more memory-efficient than map because it doesn't need to store all results at once. 

imap_unordered 
Asynchronous Execution: Similar to imap, but it does not guarantee the order of results. It yields results as soon as they are available, but the order may not match the input order. 
Use Case: Best used when the order of results does not matter, and you want the benefits of asynchronous execution without the overhead of maintaining order. 
Performance: Often faster than imap because it doesn't need to manage the order of results, which can reduce synchronization overhead. 
""" 


# Basic Parameters of tqdm
""" 
desc: A string to label the progress bar. 

total: The total number of iterations. If the loop is not known in advance, you can set it to None and update it later. 

unit: The unit of each iteration (e.g., 'it', 'batch', 'epoch'). 

unit_scale: Automatically determine the scale of total (e.g., adding 'k' for thousands). 

dynamic_ncols: Adjust the width of the bar based on the terminal window size. 

mininterval: The minimum update interval in seconds (e.e., 0.1 means the bar will update at least every 0.1 seconds). 

maxinterval: The maximum update interval in seconds. 

ncols: The width of the entire bar in columns. 

nrows: The height of the entire bar (for multi-line bars). 

ascii: The character set used to draw the bar (e.g., "#", "█"). 

bar_format: A custom format for the bar string (e.g., {l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]). 
""" 


""" 
pbar.update(n): This method is used to manually advance the progress bar by n steps. If you call pbar.update(2), it means you're indicating that 2 units of progress have been made since the last update.  

This is typically used in scenarios where the amount of work done in each iteration isn't uniform or when you want to manually control the progress bar's advancement. 

No Impact on Actual Work 
""" 

# how to make the description in tqdm be auto updated dynamically
# Sample1
with tqdm(total=20, desc='processing') as pb:
    for i in range(20):
        pb.set_description(f'updating {i}')
        time.sleep(1)
        pb.update(1)

# Sample2
def do_work(x): 
    time.sleep(1)  # Simulate some work 
    return x * x 

if __name__ == '__main__': 
    with tqdm(total=20, desc="Processing") as pbar: 
        for i, result in enumerate(map(do_work, range(20))): 
            pbar.update(1)  # Update the progress bar by 1 step 
            pbar.set_description(f"Processing {i+1} {result}")  # Update the description to reflect the current item 

    # Sample3 - cowork with Pools
    with Pool(4) as p: 
        with tqdm(total=20, desc="Processing") as pbar: 
            for i, result in enumerate(p.imap(do_work, range(20))): 
                pbar.update(1)  # Update the progress bar by 1 step 
                pbar.set_description(f"Processing {i+1} {result}")  # Update the description to reflect the current item 


# 用 tqdm.contrib.concurrent 最省事，一行代码就能让 concurrent.futures 的并发任务带进度条，且不需要自己维护 pbar.update()
```py
from tqdm.contrib.concurrent import thread_map, process_map
# 在内部就是一次性 executor.map，它天生没有 imap 的“边算边 yield”能力。只是在内部把 tqdm 包在一次性 map 上，进度条会动，但最终结果仍是整包返回，并不具备 imap 的“流式消费”能力。

# 线程池示例
results = thread_map(
    your_func,          # 要并发的函数
    iterable,           # 可迭代对象
    max_workers=8,      # 等价于 ThreadPoolExecutor(max_workers=8)
    desc="Processing"   # 进度条描述
)

# 进程池示例（CPU 密集）
results = process_map(
    your_func,
    iterable,
    max_workers=4,
    desc="Processing"
)

# 例子
def activity(fruit):
    time.sleep(0.2)          # 每个小块 0.2 秒
    return fruit

big_list = ['apple', 'banana', 'peach'] * 1000

results = thread_map(activity, big_list, max_workers=8, desc="Processing")

```

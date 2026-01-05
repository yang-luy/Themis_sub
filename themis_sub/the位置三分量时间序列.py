#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 15:20:38 2025

@author: yang
"""
import pyspedas
from pytplot import get_data
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates

# 下载并加载数据
trange = ['2017-03-27', '2017-03-28']
probe = 'e'

# 下载状态数据（包含位置信息）
pyspedas.themis.state(trange=trange, probe=probe, level='l2')

# 获取位置数据
pos_data = get_data('the_pos_gsm')

if pos_data is not None:
    times, positions = pos_data[0], pos_data[1]
    
    # 地球半径（单位：km）
    earth_radius_km = 6371.0
    
    # 将位置数据从km转换为Re（除以地球半径）
    positions_re = positions / earth_radius_km
    
    # 提取三个坐标分量（单位：Re）
    x = positions_re[:, 0]  # X 坐标
    y = positions_re[:, 1]  # Y 坐标
    z = positions_re[:, 2]  # Z 坐标
    
    # 创建图形
    plt.figure(figsize=(16, 8))
    
    # 将时间戳转换为datetime对象（UTC）
    utc_times = [datetime.utcfromtimestamp(t) for t in times]
    
    # 绘制三个坐标分量的时间序列图
    plt.plot(utc_times, x, 'r-', label='X (Re)', linewidth=2, alpha=0.8)
    plt.plot(utc_times, y, 'g-', label='Y (Re)', linewidth=2, alpha=0.8)
    plt.plot(utc_times, z, 'b-', label='Z (Re)', linewidth=2, alpha=0.8)
    
    # 设置坐标轴标签
    plt.xlabel('Time (UTC)', fontsize=14)
    plt.ylabel('Position (Re)', fontsize=14)
    plt.title('THEMIS-E Position (GSM Coordinates)\n' + 
              f'{trange[0]} to {trange[1]}', fontsize=16, fontweight='bold', pad=20)
    
    # 设置时间轴格式为世界时（UTC）
    ax = plt.gca()
    
    # 设置10分钟分辨率的时间轴刻度
    major_locator = mdates.HourLocator(interval=1)
    major_formatter = mdates.DateFormatter('%H:%M')
    minor_locator = mdates.MinuteLocator(byminute=range(0, 60, 10))
    
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_major_formatter(major_formatter)
    ax.xaxis.set_minor_locator(minor_locator)
    
    # 设置刻度标签样式，使其不倾斜
    ax.tick_params(axis='x', which='major', labelsize=10, rotation=0, pad=10)
    ax.tick_params(axis='x', which='minor', labelsize=0)
    
    # 调整布局
    plt.subplots_adjust(bottom=0.15)
    
    # 添加网格
    ax.grid(True, which='major', alpha=0.3, linestyle='-')
    ax.grid(True, which='minor', alpha=0.1, linestyle=':')
    
    # 添加图例
    plt.legend(fontsize=12, loc='upper right')
    
    # 显示图形
    plt.tight_layout()
    plt.show()
    
    # 显示基本统计信息
    print("=" * 60)
    print("THEMIS-E POSITION COMPONENTS TIME SERIES ANALYSIS")
    print("=" * 60)
    
    start_utc = utc_times[0].strftime('%Y-%m-%d %H:%M:%S')
    end_utc = utc_times[-1].strftime('%Y-%m-%d %H:%M:%S')
    print(f"Time Range: {start_utc} to {end_utc} (UTC)")
    print(f"Number of Data Points: {len(times)}")
    
    print(f"\nPosition Statistics (in Earth Radii, Re):")
    print(f"X Range: [{x.min():.2f}, {x.max():.2f}] Re")
    print(f"Y Range: [{y.min():.2f}, {y.max():.2f}] Re")
    print(f"Z Range: [{z.min():.2f}, {z.max():.2f}] Re")
    
    radial_dist = np.sqrt(x**2 + y**2 + z**2)
    print(f"\nRadial Distance from Earth Center:")
    print(f"Range: [{radial_dist.min():.2f}, {radial_dist.max():.2f}] Re")
    
    print(f"\nNote: All positions are in Earth Radii (Re)")
    print(f"Earth Radius used for conversion: {earth_radius_km} km")
    
else:
    print("错误: 无法获取 the_pos_gsm 数据")
    print("请确保卫星代号是 'e'，且数据下载成功")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 21:17:41 2025

@author: yang
"""
import cdflib
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import matplotlib.dates as mdates

# 打开CDF文件
cdf_file = cdflib.CDF('/Users/yang/Desktop/data/THEMIS/the/l2/esa/2017/the_l2_esa_20170327_v01.cdf')

# 读取时间数据
time_data = cdf_file.varget('the_peir_time')
print(f"原始时间数据范围: {time_data.min()} 到 {time_data.max()}")

# 手动将Unix时间戳转换为datetime
def unix_to_datetime(unix_timestamp):
    """将Unix时间戳转换为datetime对象"""
    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)

# 转换所有时间点
datetime_array = [unix_to_datetime(ts) for ts in time_data]

print("时间转换完成:")
print(f"第一个时间点: {datetime_array[0]}")
print(f"最后一个时间点: {datetime_array[-1]}")
print(f"总时间跨度: {datetime_array[-1] - datetime_array[0]}")

# 读取离子速度数据
gsm_data = cdf_file.varget('the_peir_velocity_gsm')

v_x = gsm_data[:, 0]  # Vx分量
v_y = gsm_data[:, 1]  # Vy分量  
v_z = gsm_data[:, 2]  # Vz分量

# 设置目标时间范围：2017-03-27 5:00--6:00 UTC
start_time = datetime(2017, 3, 27, 5, 0, 0, tzinfo=timezone.utc)
end_time = datetime(2017, 3, 27, 6, 0, 0, tzinfo=timezone.utc)

print(f"\n目标筛选范围: {start_time} 到 {end_time}")

# 筛选在时间范围内的数据点
time_mask = (np.array(datetime_array) >= start_time) & (np.array(datetime_array) <= end_time)
filtered_time = np.array(datetime_array)[time_mask]
filtered_v_x = v_x[time_mask]  # 筛选Vx分量
filtered_v_y = v_y[time_mask]  # 筛选Vy分量
filtered_v_z = v_z[time_mask]  # 筛选Vz分量

print(f"筛选后的数据点数: {len(filtered_v_x)}")

if len(filtered_time) > 0:
    print(f"实际筛选到的时间范围: {filtered_time[0]} 到 {filtered_time[-1]}")
    
    # 创建三个子图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # 设置时间轴格式
    major_locator = mdates.MinuteLocator(byminute=range(0, 60, 10))
    major_formatter = mdates.DateFormatter('%H:%M')
    
    # 绘制Vx分量
    axes[0].plot(filtered_time, filtered_v_x, 'r-', linewidth=1)
    axes[0].set_ylabel('Vx (km/s)', fontsize=12)
    axes[0].grid(True, which='both', alpha=0.3)
    axes[0].set_title('THEMIS (e) - Ion Velocity Components (GSM) 2017-03-27 05:00-06:00 UTC', fontsize=14, pad=20)
    
    # 绘制Vy分量
    axes[1].plot(filtered_time, filtered_v_y, 'g-', linewidth=1)
    axes[1].set_ylabel('Vy (km/s)', fontsize=12)
    axes[1].grid(True, which='both', alpha=0.3)
    
    # 绘制Vz分量
    axes[2].plot(filtered_time, filtered_v_z, 'b-', linewidth=1)
    axes[2].set_ylabel('Vz (km/s)', fontsize=12)
    axes[2].set_xlabel('UTC Time', fontsize=12)
    axes[2].grid(True, which='both', alpha=0.3)
    
    # 设置时间轴格式
    for ax in axes:
        ax.xaxis.set_major_locator(major_locator)
        ax.xaxis.set_major_formatter(major_formatter)
        ax.tick_params(axis='x', rotation=0)
    
    # 设置次要刻度为每分钟
    minor_locator = mdates.MinuteLocator(interval=1)
    for ax in axes:
        ax.xaxis.set_minor_locator(minor_locator)
    
    # 调整布局
    plt.tight_layout()
    plt.show()
    
    # 打印一些统计信息 - 三分量的统计
    print(f"\nVx范围: {filtered_v_x.min():.2f} - {filtered_v_x.max():.2f} Km/s, 平均值: {filtered_v_x.mean():.2f} Km/s")
    print(f"Vy范围: {filtered_v_y.min():.2f} - {filtered_v_y.max():.2f} Km/s, 平均值: {filtered_v_y.mean():.2f} Km/s") 
    print(f"Vz范围: {filtered_v_z.min():.2f} - {filtered_v_z.max():.2f} Km/s, 平均值: {filtered_v_z.mean():.2f} Km/s")
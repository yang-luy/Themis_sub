#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 16:26:58 2025

@author: yang
"""
import pyspedas
from pytplot import get_data
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone
import matplotlib.dates as mdates

# 设置目标时间范围
target_start = datetime(2017, 3, 27, 5, 20, 0, tzinfo=timezone.utc)
target_end = datetime(2017, 3, 27, 6, 0, 0, tzinfo=timezone.utc)
trange = [target_start.strftime('%Y-%m-%d/%H:%M'), target_end.strftime('%Y-%m-%d/%H:%M')]
probe = 'e'

print(f"处理 THEMIS-{probe.upper()} 数据")
print(f"时间范围: {target_start.strftime('%H:%M')} - {target_end.strftime('%H:%M')} UTC")

# 下载数据
pyspedas.themis.fgm(trange=trange, probe=probe, level='l2', coord='gsm')

# 使用正确的变量名
fgm_var = f'th{probe}_fgl_gsm'

# 获取数据
fgm_data = get_data(fgm_var)

if fgm_data is None:
    print("错误: 无法获取磁场数据")
else:
    # 获取时间和数据
    times_b, b_vals, _ = fgm_data if len(fgm_data) == 3 else (fgm_data[0], fgm_data[1], None)
    
    # 筛选时间范围
    filtered_times = []
    filtered_values = []
    for i, t in enumerate(times_b):
        current_time = datetime.fromtimestamp(t, tz=timezone.utc)
        if target_start <= current_time <= target_end:
            filtered_times.append(current_time)
            filtered_values.append(b_vals[i])
    
    filtered_values = np.array(filtered_values)
    
    print(f"磁场数据点: {len(filtered_times)}")
    
    # 计算磁场俯仰角
    Bz = filtered_values[:, 2]
    B_total = np.sqrt(filtered_values[:, 0]**2 + filtered_values[:, 1]**2 + filtered_values[:, 2]**2)
    
    # 计算 arcsin(Bz/Bt)
    elevation_angles = []
    for i in range(len(B_total)):
        Bt = B_total[i]
        Bz_val = Bz[i]
        
        if Bt == 0:
            elevation_angles.append(np.nan)
        else:
            ratio = Bz_val / Bt
            ratio = np.clip(ratio, -1.0, 1.0)
            elevation_rad = np.arcsin(ratio)
            elevation_deg = np.degrees(elevation_rad)
            elevation_angles.append(elevation_deg)
    
    elevation_angles = np.array(elevation_angles)
    
    # 统计信息
    if len(elevation_angles) > 0:
        print(f"磁场俯仰角范围: {np.nanmin(elevation_angles):.1f}° - {np.nanmax(elevation_angles):.1f}°")
        print(f"磁场俯仰角平均值: {np.nanmean(elevation_angles):.1f}°")
    
    # 创建图形
    plt.figure(figsize=(12, 5))
    
    # 绘制磁场俯仰角
    plt.plot(filtered_times, elevation_angles, 'g-', linewidth=0.8, alpha=0.7)
    plt.ylabel('Magnetic Elevation Angle\nθ = arcsin(Bz/Bt) (°)', fontsize=12)
    plt.xlabel('UTC Time', fontsize=12)
    plt.title(f'THEMIS-{probe.upper()}: Magnetic Elevation Angle (2017-03-27 05:20-06:00 UTC)', fontsize=14)
    plt.grid(True, alpha=0.3, linestyle=':')
    plt.ylim(-90, 90)
    
    # 添加参考线
    plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5, linewidth=0.8)
    plt.axhline(y=45, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    plt.axhline(y=-45, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    
    # 设置x轴格式
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(20, 60, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    ax.set_xlim(target_start, target_end)
    
    # 调整布局
    plt.tight_layout()
    plt.show()
    print("绘图完成")
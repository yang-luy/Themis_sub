#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 21 22:56:54 2025

@author: yang
"""

import pyspedas
from pytplot import get_data
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# 下载并加载数据
trange = ['2017-03-27', '2017-03-28']
probe = 'd'

# 下载状态数据（包含位置信息）
pyspedas.themis.state(trange=trange, probe=probe, level='l1')

# 获取位置数据
pos_data = get_data('thd_pos_gsm')

if pos_data is not None:
    times, positions = pos_data[0], pos_data[1]
    
    # 地球半径（单位：km）
    earth_radius_km = 6371.0
    
    # 将位置数据从km转换为Re（除以地球半径）
    positions_re = positions / earth_radius_km
    
    # 提取X和Y坐标分量（单位：Re）
    x = positions_re[:, 0]  # X 坐标
    y = positions_re[:, 1]  # Y 坐标
    
    # 将时间戳转换为datetime对象（UTC）
    utc_times = [datetime.utcfromtimestamp(t) for t in times]
    
    # 定义要标记的时间段（2017-03-27 05:00--06:00 UTC）
    target_start = datetime(2017, 3, 27, 5, 0, 0)
    target_end = datetime(2017, 3, 27, 6, 0, 0)
    
    # 筛选出目标时间段内的数据点
    target_indices = []
    for i, t in enumerate(utc_times):
        if target_start <= t <= target_end:
            target_indices.append(i)
    
    # 创建图形
    plt.figure(figsize=(14, 12))
    
    # 绘制完整的XY平面轨迹图
    # 用颜色表示时间变化（完整轨迹）
    scatter = plt.scatter(x, y, c=times, cmap='viridis', s=10, alpha=0.5, label='Full Trajectory')
    
    # 连接完整轨迹线
    plt.plot(x, y, 'gray', linewidth=0.5, alpha=0.3)
    
    # 标记目标时间段的轨迹
    if target_indices:
        target_x = x[target_indices]
        target_y = y[target_indices]
        target_times = [utc_times[i] for i in target_indices]
        
        # 用红色突出显示目标时间段轨迹
        plt.scatter(target_x, target_y, c='red', s=25, alpha=0.8, 
                   edgecolors='darkred', linewidth=1, label=f'05:00-06:00 UTC')
        
        # 连接目标时间段轨迹线
        plt.plot(target_x, target_y, 'r-', linewidth=2, alpha=0.8)
        
        # 标记目标时间段的起点和终点
        plt.plot(target_x[0], target_y[0], 'go', markersize=15, 
                markeredgecolor='white', markeredgewidth=2, label='05:00 UTC Start')
        plt.plot(target_x[-1], target_y[-1], 'bo', markersize=15, 
                markeredgecolor='white', markeredgewidth=2, label='06:00 UTC End')
        
        # 添加时间标签
        if len(target_x) > 0:
            # 在轨迹上标注几个时间点
            sample_indices = np.linspace(0, len(target_x)-1, min(5, len(target_x)), dtype=int)
            for idx in sample_indices:
                time_label = target_times[idx].strftime('%H:%M')
                plt.annotate(time_label, 
                            xy=(target_x[idx], target_y[idx]),
                            xytext=(5, 5), textcoords='offset points',
                            fontsize=9, fontweight='bold',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2"))
    
    # 标记完整轨迹的起点和终点
    plt.plot(x[0], y[0], 'k^', markersize=15, label='Full Trajectory Start', 
            markeredgecolor='white', markeredgewidth=2)
    plt.plot(x[-1], y[-1], 'kv', markersize=15, label='Full Trajectory End',
            markeredgecolor='white', markeredgewidth=2)
    
    # 添加地球（半径为1 Re）
    earth_circle = plt.Circle((0, 0), 1, color='blue', alpha=0.2, label='Earth (1 Re)')
    plt.gca().add_patch(earth_circle)
    
    # 添加坐标轴
    plt.xlabel('X (Re)', fontsize=14)
    plt.ylabel('Y (Re)', fontsize=14)
    plt.title('THEMIS-D Trajectory in XY Plane (GSM Coordinates)\n' + 
              f'{trange[0]} to {trange[1]} - Highlighted: 05:00-06:00 UTC', 
              fontsize=16, fontweight='bold', pad=20)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, orientation='vertical', pad=0.02)
    cbar.set_label('Time (UTC)', fontsize=12)
    
    # 设置颜色条刻度为UTC时间
    time_min = times.min()
    time_max = times.max()
    cbar_ticks = np.linspace(time_min, time_max, 5)
    cbar_tick_labels = []
    for tick in cbar_ticks:
        dt = datetime.utcfromtimestamp(tick)
        if (time_max - time_min) <= 86400:  # 如果时间跨度小于等于1天
            cbar_tick_labels.append(dt.strftime('%H:%M'))
        else:
            cbar_tick_labels.append(dt.strftime('%m-%d\n%H:%M'))
    
    cbar.set_ticks(cbar_ticks)
    cbar.set_ticklabels(cbar_tick_labels)
    
    # 添加网格
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # 设置坐标轴比例相等
    plt.gca().set_aspect('equal', adjustable='box')
    
    # 添加图例
    plt.legend(fontsize=11, loc='upper right', framealpha=0.9)
    
    # 设置坐标轴范围
    x_margin = (x.max() - x.min()) * 0.1
    y_margin = (y.max() - y.min()) * 0.1
    plt.xlim(x.min() - x_margin, x.max() + x_margin)
    plt.ylim(y.min() - y_margin, y.max() + y_margin)
    
    # 添加原点标记
    plt.plot(0, 0, 'k+', markersize=15, markeredgewidth=2)
    
    # 添加文本说明框
    if target_indices:
        text_str = f"05:00-06:00 UTC:\n{len(target_indices)} data points\n"
        text_str += f"Start: X={target_x[0]:.2f} Re, Y={target_y[0]:.2f} Re\n"
        text_str += f"End: X={target_x[-1]:.2f} Re, Y={target_y[-1]:.2f} Re\n"
        text_str += f"Displacement: {np.sqrt((target_x[-1]-target_x[0])**2 + (target_y[-1]-target_y[0])**2):.2f} Re"
        
        plt.annotate(text_str, xy=(0.02, 0.02), xycoords='axes fraction',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
                    verticalalignment='bottom')
    
    # 调整布局
    plt.tight_layout()
    
    # 显示图形
    plt.show()
    
    # 显示基本统计信息
    print("=" * 60)
    print("THEMIS-E TRAJECTORY ANALYSIS (XY Plane)")
    print("=" * 60)
    
    print(f"\nData Range: {trange[0]} to {trange[1]}")
    
    # 将第一个和最后一个时间戳转换UTC时间
    start_utc = datetime.utcfromtimestamp(times[0]).strftime('%Y-%m-%d %H:%M:%S')
    end_utc = datetime.utcfromtimestamp(times[-1]).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Full Time Range: {start_utc} to {end_utc} (UTC)")
    print(f"Number of Data Points (Total): {len(times)}")
    
    # 目标时间段统计
    if target_indices:
        target_start_utc = target_times[0].strftime('%Y-%m-%d %H:%M:%S')
        target_end_utc = target_times[-1].strftime('%Y-%m-%d %H:%M:%S')
        print(f"\nTarget Time Range: {target_start_utc} to {target_end_utc} (UTC)")
        print(f"Number of Data Points (05:00-06:00 UTC): {len(target_indices)}")
        
        print(f"\nTarget Period Statistics (in Earth Radii, Re):")
        print(f"X Range: [{target_x.min():.2f}, {target_x.max():.2f}] Re")
        print(f"Y Range: [{target_y.min():.2f}, {target_y.max():.2f}] Re")
        print(f"Average Position: X={target_x.mean():.2f}, Y={target_y.mean():.2f} Re")
        
        # 计算到地球中心的距离
        target_distances = np.sqrt(target_x**2 + target_y**2)
        print(f"Distance from Earth Center:")
        print(f"  Min: {target_distances.min():.2f} Re")
        print(f"  Max: {target_distances.max():.2f} Re")
        print(f"  Average: {target_distances.mean():.2f} Re")
        
        # 计算位移
        target_displacement = np.sqrt((target_x[-1] - target_x[0])**2 + (target_y[-1] - target_y[0])**2)
        print(f"Displacement during target period: {target_displacement:.2f} Re")
        
        # 计算平均速度 (Re/hour)
        time_duration_hours = (target_end - target_start).total_seconds() / 3600
        avg_speed = target_displacement / time_duration_hours
        print(f"Average speed during target period: {avg_speed:.2f} Re/hour")
    
    print(f"\nNote: All positions are in Earth Radii (Re)")
    print(f"Earth Radius used for conversion: {earth_radius_km} km")
    
else:
    print("错误: 无法获取 the_pos_gsm 数据")
    print("请确保卫星代号是 'e'，且数据下载成功")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 21 23:39:04 2025

@author: yang
"""

import pyspedas
from pytplot import get_data
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from mpl_toolkits.mplot3d import Axes3D

# 下载并加载数据
trange = ['2017-03-27', '2017-03-28']
probes = ['e', 'd']  # 两颗卫星

print("下载两颗卫星的状态数据...")
for probe in probes:
    pyspedas.themis.state(trange=trange, probe=probe, level='l1')
    print(f"  THEMIS-{probe.upper()} 数据下载完成")

# 创建3D图形
fig = plt.figure(figsize=(16, 12))
ax = fig.add_subplot(111, projection='3d')

# 定义颜色和标记
colors = {'e': 'blue', 'd': 'red'}
markers = {'e': 'o', 'd': 's'}
labels = {'e': 'THEMIS-E', 'd': 'THEMIS-D'}

# 存储所有卫星的轨迹数据
all_satellites_data = []

for probe in probes:
    # 获取位置数据
    if probe == 'e':
        pos_var_name = 'the_pos_gsm'
    else:
        pos_var_name = f'th{probe}_pos_gsm'
    
    pos_data = get_data(pos_var_name)
    
    if pos_data is not None:
        times, positions = pos_data[0], pos_data[1]
        
        # 地球半径（单位：km）
        earth_radius_km = 6371.0
        
        # 将位置数据从km转换为Re（除以地球半径）
        positions_re = positions / earth_radius_km
        
        # 提取X、Y、Z三个坐标分量（单位：Re）
        x = positions_re[:, 0]  # X 坐标
        y = positions_re[:, 1]  # Y 坐标
        z = positions_re[:, 2]  # Z 坐标
        
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
        
        # 绘制完整的3D轨迹图
        color = colors[probe]
        label = labels[probe]
        
        # 用颜色表示时间变化（完整轨迹）
        scatter = ax.scatter(x, y, z, c=times, cmap='viridis', s=8, alpha=0.5, 
                            label=f'{label} - Full Trajectory')
        
        # 连接完整轨迹线
        ax.plot(x, y, z, color=color, linewidth=0.8, alpha=0.4)
        
        # 标记目标时间段的轨迹
        if target_indices:
            target_x = x[target_indices]
            target_y = y[target_indices]
            target_z = z[target_indices]
            
            # 用较深的颜色突出显示目标时间段轨迹
            highlight_color = 'darkred' if probe == 'd' else 'darkblue'
            ax.scatter(target_x, target_y, target_z, c=highlight_color, s=25, alpha=0.9, 
                      edgecolors='black', linewidth=1, 
                      label=f'{label} - 05:00-06:00 UTC ({len(target_indices)} points)')
            
            # 连接目标时间段轨迹线
            ax.plot(target_x, target_y, target_z, color=highlight_color, linewidth=2.5, alpha=0.9)
            
            # 标记目标时间段的起点和终点
            marker = markers[probe]
            ax.plot([target_x[0]], [target_y[0]], [target_z[0]], 
                   marker=marker, color=highlight_color, markersize=8, 
                   markeredgecolor='white', markeredgewidth=1, 
                   label=f'{label} - 05:00 UTC Start')
            ax.plot([target_x[-1]], [target_y[-1]], [target_z[-1]], 
                   marker=marker, color=highlight_color, markersize=8, 
                   markeredgecolor='white', markeredgewidth=1, 
                   label=f'{label} - 06:00 UTC End')
        
        # 存储卫星数据供后续分析
        all_satellites_data.append({
            'probe': probe,
            'label': label,
            'x': x,
            'y': y,
            'z': z,
            'times': times,
            'utc_times': utc_times,
            'target_indices': target_indices if target_indices else []
        })
        
        print(f"THEMIS-{probe.upper()}: 获取到 {len(times)} 个数据点")
        if target_indices:
            print(f"  目标时间段 (05:00-06:00 UTC): {len(target_indices)} 个数据点")
    else:
        print(f"错误: 无法获取 THEMIS-{probe.upper()} 的位置数据")

# 添加地球球体（半径为1 Re）
u = np.linspace(0, 2 * np.pi, 25)
v = np.linspace(0, np.pi, 25)

earth_x = np.outer(np.cos(u), np.sin(v))
earth_y = np.outer(np.sin(u), np.sin(v))
earth_z = np.outer(np.ones(np.size(u)), np.cos(v))

# 绘制地球球体
ax.plot_surface(earth_x, earth_y, earth_z, color='green', alpha=0.15, label='Earth (1 Re)')

# 添加坐标轴标签
ax.set_xlabel('X (Re)', fontsize=12, labelpad=10)
ax.set_ylabel('Y (Re)', fontsize=12, labelpad=10)
ax.set_zlabel('Z (Re)', fontsize=12, labelpad=10)

# 设置图形标题
ax.set_title('THEMIS-E and THEMIS-D 3D Trajectories (GSM Coordinates)\n' + 
             f'{trange[0]} to {trange[1]} - 05:00-06:00 UTC Highlighted', 
             fontsize=14, pad=20)

# 添加网格
ax.grid(True, alpha=0.2, linestyle='--')

# 计算所有卫星数据的整体范围，设置统一的坐标轴比例
all_x = []
all_y = []
all_z = []

for sat_data in all_satellites_data:
    all_x.extend(sat_data['x'])
    all_y.extend(sat_data['y'])
    all_z.extend(sat_data['z'])

if all_x and all_y and all_z:
    max_range = max([max(all_x)-min(all_x), max(all_y)-min(all_y), max(all_z)-min(all_z)])
    mid_x = (max(all_x)+min(all_x)) * 0.5
    mid_y = (max(all_y)+min(all_y)) * 0.5
    mid_z = (max(all_z)+min(all_z)) * 0.5
    
    ax.set_xlim(mid_x - max_range*0.5, mid_x + max_range*0.5)
    ax.set_ylim(mid_y - max_range*0.5, mid_y + max_range*0.5)
    ax.set_zlim(mid_z - max_range*0.5, mid_z + max_range*0.5)

# 添加图例（简化图例，避免重复）
from matplotlib.lines import Line2D
legend_elements = []
for probe in probes:
    color = colors[probe]
    label = labels[probe]
    legend_elements.append(Line2D([0], [0], color=color, lw=2, label=label))
legend_elements.append(Line2D([0], [0], color='darkblue', lw=2, label='05:00-06:00 UTC (E)'))
legend_elements.append(Line2D([0], [0], color='darkred', lw=2, label='05:00-06:00 UTC (D)'))
legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
                              markersize=10, label='Earth (1 Re)'))

ax.legend(handles=legend_elements, fontsize=9, loc='upper left', framealpha=0.9)

# 设置初始视角（可以旋转查看）
ax.view_init(elev=25, azim=45)  # 俯仰角25度，方位角45度

# 添加原点标记
ax.plot([0], [0], [0], 'k+', markersize=8, markeredgewidth=1)

# 调整布局
plt.tight_layout()

# 显示图形
plt.show()

# 显示基本统计信息
print("\n" + "=" * 60)
print("THEMIS-E AND THEMIS-D 3D TRAJECTORY SUMMARY")
print("=" * 60)

print(f"\nTime Range: {trange[0]} to {trange[1]}")

for sat_data in all_satellites_data:
    probe = sat_data['probe']
    label = sat_data['label']
    
    print(f"\n{label}:")
    print(f"  Total Data Points: {len(sat_data['x'])}")
    
    if sat_data['target_indices']:
        target_x = sat_data['x'][sat_data['target_indices']]
        target_y = sat_data['y'][sat_data['target_indices']]
        target_z = sat_data['z'][sat_data['target_indices']]
        
        print(f"  05:00-06:00 UTC Period:")
        print(f"    Data Points: {len(sat_data['target_indices'])}")
        print(f"    Position Range: X:[{target_x.min():.2f}, {target_x.max():.2f}] Re")
        print(f"                    Y:[{target_y.min():.2f}, {target_y.max():.2f}] Re")
        print(f"                    Z:[{target_z.min():.2f}, {target_z.max():.2f}] Re")
        
        # 计算3D位移
        target_displacement = np.sqrt((target_x[-1] - target_x[0])**2 + 
                                     (target_y[-1] - target_y[0])**2 + 
                                     (target_z[-1] - target_z[0])**2)
        print(f"    3D Displacement: {target_displacement:.2f} Re")
        
        # 计算平均速度 (Re/hour)
        time_duration_hours = 1.0  # 05:00-06:00 UTC 是1小时
        avg_speed = target_displacement / time_duration_hours
        print(f"    Average Speed: {avg_speed:.2f} Re/hour")

# 计算两颗卫星在目标时间段的最小距离
if len(all_satellites_data) == 2 and all_satellites_data[0]['target_indices'] and all_satellites_data[1]['target_indices']:
    print("\n" + "=" * 60)
    print("RELATIVE POSITION ANALYSIS")
    print("=" * 60)
    
    # 获取两颗卫星在目标时间段的数据
    sat_e = all_satellites_data[0]
    sat_d = all_satellites_data[1]
    
    target_x_e = sat_e['x'][sat_e['target_indices']]
    target_y_e = sat_e['y'][sat_e['target_indices']]
    target_z_e = sat_e['z'][sat_e['target_indices']]
    
    target_x_d = sat_d['x'][sat_d['target_indices']]
    target_y_d = sat_d['y'][sat_d['target_indices']]
    target_z_d = sat_d['z'][sat_d['target_indices']]
    
    # 确保两个数组长度相同（取较短的长度）
    min_len = min(len(target_x_e), len(target_x_d))
    
    if min_len > 0:
        # 计算每个时间点的距离
        distances = []
        for i in range(min_len):
            dist = np.sqrt((target_x_e[i] - target_x_d[i])**2 + 
                          (target_y_e[i] - target_y_d[i])**2 + 
                          (target_z_e[i] - target_z_d[i])**2)
            distances.append(dist)
        
        distances = np.array(distances)
        
        print(f"\nRelative Distance between THEMIS-E and THEMIS-D (05:00-06:00 UTC):")
        print(f"  Minimum Distance: {distances.min():.2f} Re")
        print(f"  Maximum Distance: {distances.max():.2f} Re")
        print(f"  Average Distance: {distances.mean():.2f} Re")
        print(f"  Standard Deviation: {distances.std():.2f} Re")
        
        # 找到最小距离发生的时间
        min_dist_idx = np.argmin(distances)
        min_dist_time = sat_e['utc_times'][sat_e['target_indices'][min_dist_idx]]
        print(f"  Time of Minimum Distance: {min_dist_time.strftime('%H:%M:%S')} UTC")

print(f"\nNote: Use mouse to rotate and zoom the 3D plot")
print(f"      THEMIS-E: Blue, THEMIS-D: Red")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 21 16:09:57 2025

@author: yang
"""

import pyspedas
from pytplot import get_data
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone
import matplotlib.dates as mdates

# 设置目标时间范围：2017-03-27 5:20--6:00 UTC
target_start = datetime(2017, 3, 27, 5, 20, 0, tzinfo=timezone.utc)
target_end = datetime(2017, 3, 27, 6, 0, 0, tzinfo=timezone.utc)
trange = [target_start.strftime('%Y-%m-%d/%H:%M'), target_end.strftime('%Y-%m-%d/%H:%M')]
probe = 'd'

print(f"处理 THEMIS-{probe.upper()} 卫星数据")
print(f"时间范围: {target_start.strftime('%Y-%m-%d %H:%M:%S')} 到 {target_end.strftime('%Y-%m-%d %H:%M:%S')} UTC")

# 下载数据
print("\n下载FGM磁场数据...")
pyspedas.themis.fgm(trange=trange, probe=probe, level='l2', coord='gsm')

print("下载ESA等离子体数据...")
pyspedas.themis.esa(trange=trange, probe=probe, level='l2')

# 定义变量名
fgm_var_name = f'th{probe}_fgs_gsm'  # 磁场GSM分量
density_var_name = f'th{probe}_peir_density'     # 密度
temperature_var_name = f'th{probe}_peir_avgtemp' # 平均温度

# 获取数据
print("\n获取数据...")
fgm_data = get_data(fgm_var_name)
density_data = get_data(density_var_name)
temperature_data = get_data(temperature_var_name)

# 检查数据是否成功获取
if fgm_data is None:
    print(f"错误: 无法获取磁场数据 '{fgm_var_name}'")
if density_data is None:
    print(f"错误: 无法获取密度数据 '{density_var_name}'")
if temperature_data is None:
    print(f"错误: 无法获取温度数据 '{temperature_var_name}'")

# 定义筛选函数
def filter_data_by_time(times, values, start_dt, end_dt):
    """根据datetime时间范围筛选数据"""
    filtered_times = []
    filtered_values = []
    for i, t in enumerate(times):
        current_time = datetime.fromtimestamp(t, tz=timezone.utc)
        if start_dt <= current_time <= end_dt:
            filtered_times.append(current_time)
            # 处理不同维度的数据
            if values.ndim == 1:
                filtered_values.append(values[i])
            else:  # 多维数据，如磁场有多个分量
                filtered_values.append(values[i])
    return filtered_times, np.array(filtered_values)

# 物理常数
k_B = 1.380649e-23  # 玻尔兹曼常数，单位 J/K
eV_to_K = 11604.525  # 1 eV 对应的开尔文温度

# 初始化变量
filtered_times_bz, bz_values = [], []
filtered_times_dens, dens_values = [], []
filtered_times_press, press_values = [], []

# 处理磁场数据 (Bz分量)
if fgm_data is not None:
    times_fgm, fgm_vals = fgm_data[0], fgm_data[1]
    if len(fgm_vals.shape) > 1 and fgm_vals.shape[1] >= 3:
        # 提取Bz分量 (第三个分量，索引2)
        bz_vals = fgm_vals[:, 2]
        filtered_times_bz, bz_values = filter_data_by_time(times_fgm, bz_vals, target_start, target_end)
        print(f"磁场Bz分量: 筛选到 {len(filtered_times_bz)} 个数据点")
        if len(filtered_times_bz) > 0:
            print(f"  Bz范围: {np.nanmin(bz_values):.2f} -- {np.nanmax(bz_values):.2f} nT")
    else:
        print("警告: 磁场数据维度不符合预期")

# 处理密度和温度数据，计算热压
if density_data is not None and temperature_data is not None:
    times_dens, dens_vals = density_data[0], density_data[1]
    times_temp, temp_vals = temperature_data[0], temperature_data[1]
    
    # 筛选密度数据
    filtered_times_dens, dens_values = filter_data_by_time(times_dens, dens_vals, target_start, target_end)
    
    # 筛选温度数据
    filtered_times_temp, temp_values = filter_data_by_time(times_temp, temp_vals, target_start, target_end)
    
    print(f"密度数据: 筛选到 {len(filtered_times_dens)} 个数据点")
    print(f"温度数据: 筛选到 {len(filtered_times_temp)} 个数据点")
    
    # 计算热压 (需要密度和温度时间对齐)
    if len(filtered_times_dens) > 0 and len(filtered_times_temp) > 0:
        # 简化处理：假设时间点相同，取相同数量的点
        min_len = min(len(filtered_times_dens), len(filtered_times_temp))
        if min_len > 0:
            filtered_times_press = filtered_times_dens[:min_len]
            dens_short = dens_values[:min_len]
            temp_short = temp_values[:min_len]
            
            # 单位转换与热压计算
            # 密度: cm^{-3} -> m^{-3}
            n_m3 = dens_short * 1e6
            
            # 温度: eV -> K
            T_K = temp_short * eV_to_K
            
            # 计算热压: P = n * k * T
            P_Pa = n_m3 * k_B * T_K
            
            # 压力: Pa -> nPa
            press_values = P_Pa * 1e9
            
            print(f"热压计算: 使用 {min_len} 个对齐的数据点")
            print(f"  密度范围: {np.nanmin(dens_short):.2e} -- {np.nanmax(dens_short):.2e} cm⁻³")
            print(f"  温度范围: {np.nanmin(temp_short):.2f} -- {np.nanmax(temp_short):.2f} eV")
            print(f"  热压范围: {np.nanmin(press_values):.2e} -- {np.nanmax(press_values):.2e} nPa")

# 创建图形 - 三个子图
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

plot_title_suffix = f"THEMIS-{probe.upper()} 2017-03-27 05:20-06:00 UTC"

# 子图1: 磁场Bz分量
ax1 = axes[0]
if len(filtered_times_bz) > 0 and len(bz_values) > 0:
    # 绘制Bz分量 (蓝色实线)
    ax1.plot(filtered_times_bz, bz_values, 'b-', linewidth=1)
    ax1.set_ylabel('Bz (nT)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--', which='both')
    ax1.axhline(y=0, color='gray', linestyle=':', linewidth=0.8, alpha=0.7)
    
    # 添加统计信息
    if np.any(~np.isnan(bz_values)):
        mean_bz = np.nanmean(bz_values)
        std_bz = np.nanstd(bz_values)
        min_bz = np.nanmin(bz_values)
        max_bz = np.nanmax(bz_values)
        
        stats_text = f'Mean: {mean_bz:.2f} nT\nStd: {std_bz:.2f} nT\nMin: {min_bz:.2f} nT\nMax: {max_bz:.2f} nT'
        ax1.text(0.02, 0.95, stats_text, transform=ax1.transAxes,
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    ax1.set_title(f'Magnetic Field Bz Component (GSM)', fontsize=12, loc='left')
else:
    ax1.text(0.5, 0.5, 'Bz Data Not Available', 
             ha='center', va='center', transform=ax1.transAxes, fontsize=12)
    ax1.set_ylabel('Bz (nT)', fontsize=12)

# 子图2: 粒子密度
ax2 = axes[1]
if len(filtered_times_dens) > 0 and len(dens_values) > 0:
    # 绘制密度 (绿色实线)
    ax2.plot(filtered_times_dens, dens_values, 'g-', linewidth=1)
    ax2.set_ylabel('Density (cm⁻³)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', which='both')
    
    # 添加统计信息
    if np.any(~np.isnan(dens_values)):
        mean_dens = np.nanmean(dens_values)
        std_dens = np.nanstd(dens_values)
        min_dens = np.nanmin(dens_values)
        max_dens = np.nanmax(dens_values)
        
        stats_text = f'Mean: {mean_dens:.2e}\nStd: {std_dens:.2e}\nMin: {min_dens:.2e}\nMax: {max_dens:.2e}'
        ax2.text(0.02, 0.95, stats_text, transform=ax2.transAxes,
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    ax2.set_title(f'Plasma Ion Density', fontsize=12, loc='left')
else:
    ax2.text(0.5, 0.5, 'Density Data Not Available', 
             ha='center', va='center', transform=ax2.transAxes, fontsize=12)
    ax2.set_ylabel('Density (cm⁻³)', fontsize=12)

# 子图3: 热压
ax3 = axes[2]
if len(filtered_times_press) > 0 and len(press_values) > 0:
    # 绘制热压 (红色实线)
    ax3.plot(filtered_times_press, press_values, 'r-', linewidth=1)
    ax3.set_ylabel('Thermal Pressure (nPa)', fontsize=12, fontweight='bold')
    ax3.set_xlabel('UTC Time', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--', which='both')
    
    # 添加统计信息
    if np.any(~np.isnan(press_values)):
        mean_press = np.nanmean(press_values)
        std_press = np.nanstd(press_values)
        min_press = np.nanmin(press_values)
        max_press = np.nanmax(press_values)
        
        stats_text = f'Mean: {mean_press:.2e}\nStd: {std_press:.2e}\nMin: {min_press:.2e}\nMax: {max_press:.2e}'
        ax3.text(0.02, 0.95, stats_text, transform=ax3.transAxes,
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
    
    ax3.set_title(f'Thermal Pressure (P = nkT)', fontsize=12, loc='left')
else:
    ax3.text(0.5, 0.5, 'Pressure Data Not Available', 
             ha='center', va='center', transform=ax3.transAxes, fontsize=12)
    ax3.set_ylabel('Pressure (nPa)', fontsize=12)
    ax3.set_xlabel('UTC Time', fontsize=12)

# 设置共享的x轴格式
for ax in axes:
    # 主刻度：每10分钟
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # 次刻度：每分钟（最小分辨率），不显示标签
    ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))
    # 横坐标标签不倾斜，居中显示
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    # 严格设置x轴范围，消除留白
    ax.set_xlim(target_start, target_end)

# 设置整个图的标题
fig.suptitle(f'THEMIS-{probe.upper()}: Magnetic Field, Density and Thermal Pressure\n{plot_title_suffix}', 
             fontsize=14, y=1.02, fontweight='bold')

# 自动调整子图布局
plt.tight_layout()
plt.subplots_adjust(top=0.90, hspace=0.15)  # 调整顶部空间和子图间距

plt.show()
print("\n绘图完成。")
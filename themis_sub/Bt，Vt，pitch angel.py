#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 15:39:05 2025

@author: yang
"""
import pyspedas
from pytplot import get_data
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone
import matplotlib.dates as mdates
from scipy.interpolate import interp1d

# 设置目标时间范围
target_start = datetime(2017, 3, 27, 5, 20, 0, tzinfo=timezone.utc)
target_end = datetime(2017, 3, 27, 6, 0, 0, tzinfo=timezone.utc)
trange = [target_start.strftime('%Y-%m-%d/%H:%M'), target_end.strftime('%Y-%m-%d/%H:%M')]
probe = 'e'

print(f"处理 THEMIS-{probe.upper()} 数据")
print(f"时间范围: {target_start.strftime('%H:%M')} - {target_end.strftime('%H:%M')} UTC")

# 下载数据
pyspedas.themis.fgm(trange=trange, probe=probe, level='l2', coord='gsm')
pyspedas.themis.esa(trange=trange, probe=probe, level='l2')

# 使用正确的变量名
fgm_var = f'th{probe}_fgl_gsm'  # 磁场
vel_var = f'th{probe}_peir_velocity_gsm'  # 离子速度

# 获取数据
fgm_data = get_data(fgm_var)
vel_data = get_data(vel_var)

if fgm_data is None or vel_data is None:
    print("错误: 无法获取数据")
else:
    # get_data返回元组：(时间, 数据, 元数据)
    # 我们只需要时间和数据
    times_b, b_vals, _ = fgm_data if len(fgm_data) == 3 else (fgm_data[0], fgm_data[1], None)
    times_v, v_vals, _ = vel_data if len(vel_data) == 3 else (vel_data[0], vel_data[1], None)
    
    # 筛选时间范围的函数
    def filter_by_time(times, values, start_dt, end_dt):
        """筛选指定时间范围内的数据"""
        filtered_times = []
        filtered_values = []
        for i, t in enumerate(times):
            current_time = datetime.fromtimestamp(t, tz=timezone.utc)
            if start_dt <= current_time <= end_dt:
                filtered_times.append(current_time)
                filtered_values.append(values[i])
        return filtered_times, np.array(filtered_values)
    
    # 处理磁场数据
    filtered_times_b, b_values = filter_by_time(times_b, b_vals, target_start, target_end)
    
    # 处理速度数据
    filtered_times_v, v_values = filter_by_time(times_v, v_vals, target_start, target_end)
    
    print(f"磁场数据点: {len(filtered_times_b)} (高采样率)")
    print(f"速度数据点: {len(filtered_times_v)} (低采样率)")
    
    # 将datetime转换为秒数以便插值
    def datetime_to_seconds(dt_array, reference_time):
        return np.array([(dt - reference_time).total_seconds() for dt in dt_array])
    
    seconds_b = datetime_to_seconds(filtered_times_b, target_start)
    seconds_v = datetime_to_seconds(filtered_times_v, target_start)
    
    # 将速度数据插值到磁场数据的时间点上（线性插值）
    print("将速度数据插值到磁场数据时间网格上...")
    
    # 对速度的三个分量分别进行插值
    vx_interp = interp1d(seconds_v, v_values[:, 0], kind='linear', 
                        bounds_error=False, fill_value='extrapolate')
    vy_interp = interp1d(seconds_v, v_values[:, 1], kind='linear',
                        bounds_error=False, fill_value='extrapolate')
    vz_interp = interp1d(seconds_v, v_values[:, 2], kind='linear',
                        bounds_error=False, fill_value='extrapolate')
    
    # 在磁场时间点上插值速度
    v_interpolated = np.column_stack([
        vx_interp(seconds_b),
        vy_interp(seconds_b),
        vz_interp(seconds_b)
    ])
    
    # 计算插值后的总速度
    v_total_interp = np.sqrt(v_interpolated[:, 0]**2 + 
                             v_interpolated[:, 1]**2 + 
                             v_interpolated[:, 2]**2)
    
    # 计算总磁场
    b_total = np.sqrt(b_values[:, 0]**2 + b_values[:, 1]**2 + b_values[:, 2]**2)
    
    print(f"插值后数据点数: {len(seconds_b)}")
    
    # 计算夹角
    angles = []
    for i in range(len(seconds_b)):
        b_vec = b_values[i]
        v_vec = v_interpolated[i]
        
        b_mag = np.linalg.norm(b_vec)
        v_mag = np.linalg.norm(v_vec)
        
        if b_mag == 0 or v_mag == 0:
            angles.append(np.nan)
        else:
            dot_product = np.dot(b_vec, v_vec)
            cos_angle = np.clip(dot_product / (b_mag * v_mag), -1.0, 1.0)
            angle_rad = np.arccos(cos_angle)
            angles.append(np.degrees(angle_rad))
    
    angles = np.array(angles)
    
    # 统计信息
    valid_angles = angles[~np.isnan(angles)]
    if len(valid_angles) > 0:
        print(f"夹角范围: {np.nanmin(angles):.1f}° - {np.nanmax(angles):.1f}°")
        print(f"夹角平均值: {np.nanmean(angles):.1f}°")
        print(f"夹角中位数: {np.median(valid_angles):.1f}°")
        
        # 角度分布统计
        parallel = np.sum((angles >= 0) & (angles < 30))
        oblique = np.sum((angles >= 30) & (angles < 60))
        quasi_perp = np.sum((angles >= 60) & (angles < 120))
        oblique2 = np.sum((angles >= 120) & (angles < 150))
        anti_parallel = np.sum((angles >= 150) & (angles <= 180))
        
        print(f"\n角度分布:")
        print(f"  平行(0-30°): {parallel} 点 ({parallel/len(valid_angles)*100:.1f}%)")
        print(f"  倾斜(30-60°): {oblique} 点 ({oblique/len(valid_angles)*100:.1f}%)")
        print(f"  准垂直(60-120°): {quasi_perp} 点 ({quasi_perp/len(valid_angles)*100:.1f}%)")
        print(f"  倾斜(120-150°): {oblique2} 点 ({oblique2/len(valid_angles)*100:.1f}%)")
        print(f"  反平行(150-180°): {anti_parallel} 点 ({anti_parallel/len(valid_angles)*100:.1f}%)")
    
    # 创建图形
    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
    
    # 子图1: 离子总流速
    ax1 = axes[0]
    ax1.plot(filtered_times_b, v_total_interp, 'b-', linewidth=0.5, alpha=0.7)
    ax1.set_ylabel('Ion Velocity\n(km/s)', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle=':')
    ax1.set_title(f'THEMIS-{probe.upper()}: Ion Velocity, Magnetic Field, and Pitch Angle', 
                  fontsize=12, loc='left')
    
    # 添加统计信息
    stats_v = f'Mean: {np.nanmean(v_total_interp):.1f} km/s\nMax: {np.nanmax(v_total_interp):.1f} km/s'
    ax1.text(0.02, 0.95, stats_v, transform=ax1.transAxes,
             verticalalignment='top', fontsize=8,
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    # 子图2: 总磁场强度
    ax2 = axes[1]
    ax2.plot(filtered_times_b, b_total, 'r-', linewidth=0.5, alpha=0.7)
    ax2.set_ylabel('Magnetic Field\n(nT)', fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle=':')
    
    # 添加统计信息
    stats_b = f'Mean: {np.nanmean(b_total):.1f} nT\nMax: {np.nanmax(b_total):.1f} nT'
    ax2.text(0.02, 0.95, stats_b, transform=ax2.transAxes,
             verticalalignment='top', fontsize=8,
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.7))
    
    # 子图3: 夹角
    ax3 = axes[2]
    ax3.plot(filtered_times_b, angles, 'g-', linewidth=0.5, alpha=0.7)
    ax3.set_ylabel('Pitch Angle\n(°)', fontsize=11)
    ax3.set_xlabel('UTC Time', fontsize=11)
    ax3.grid(True, alpha=0.3, linestyle=':')
    ax3.set_ylim(0, 180)
    
    # 添加水平参考线
    ax3.axhline(y=90, color='gray', linestyle='--', alpha=0.5, linewidth=1, label='90°')
    ax3.axhline(y=45, color='gray', linestyle=':', alpha=0.3, linewidth=0.5)
    ax3.axhline(y=135, color='gray', linestyle=':', alpha=0.3, linewidth=0.5)
    
    # 添加统计信息
    stats_angle = f'Mean: {np.nanmean(angles):.1f}°\nMedian: {np.median(valid_angles):.1f}°'
    ax3.text(0.02, 0.95, stats_angle, transform=ax3.transAxes,
             verticalalignment='top', fontsize=8,
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    ax3.legend(loc='upper right', fontsize=9)
    
    # 设置x轴格式
    for ax in axes:
        # 主刻度标签：每十分钟一个
        ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(20, 60, 10)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        # 网格线：每分钟一条（使用次刻度）
        ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
        ax.set_xlim(target_start, target_end)
        
        # 确保次刻度网格线显示
        ax.grid(True, which='major', alpha=0.3, linestyle=':')
        ax.grid(True, which='minor', alpha=0.1, linestyle=':')
    
    # 自动调整布局
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.1)
    
    plt.show()
    print("绘图完成")
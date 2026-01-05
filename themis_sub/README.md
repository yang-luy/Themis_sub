# THEMIS卫星数据分析工具

## 项目简介

本项目是一套用于分析THEMIS（Time History of Events and Macroscale Interactions during Substorms）卫星数据的Python脚本集合。THEMIS是NASA的一项任务，旨在研究磁层亚暴现象。这些脚本使用[pyspedas](https://github.com/spedas/pyspedas)库来下载和处理THEMIS卫星的磁场、等离子体和粒子数据。

## 功能特点

这个项目包含以下功能脚本：

- [Bt，Vt，pitch angel.py](Bt，Vt，pitch angel.py): 分析磁场和离子速度的俯仰角
- [Bz，N，热压.py](Bz，N，热压.py): 分析磁场分量、粒子密度和热压力
- [thd yz平面轨迹.py](thd yz平面轨迹.py): 绘制卫星在YZ平面的轨迹
- [thd_xy平面轨迹图.py](thd_xy平面轨迹图.py): 绘制卫星在XY平面的轨迹
- [thd_xz平面轨迹图.py](thd_xz平面轨迹图.py): 绘制卫星在XZ平面的轨迹
- [the位置三分量时间序列.py](the位置三分量时间序列.py): 显示卫星位置的三分量时间序列
- [the，thd3D.py](the，thd3D.py): 三维可视化卫星轨迹和相关数据
- [磁场俯仰角.py](磁场俯仰角.py): 分析磁场的俯仰角
- [离子速度三分量.py](离子速度三分量.py): 分析离子速度的三个分量

## 环境要求

- Python 3.7+
- pip

## 安装步骤

1. 克隆或下载本项目到本地:

```bash
git clone <your_repository_url>
cd Substorm
```

2. 创建虚拟环境（推荐）:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖包:

```bash
pip install -r requirements.txt
```

## 使用方法

每个脚本都可以直接运行，例如:

```bash
python "Bt，Vt，pitch angel.py"
```

注意：部分脚本可能需要互联网连接以下载THEMIS卫星数据。

## 数据说明

本项目分析的数据主要包括：
- THEMIS卫星的磁场数据（FGM）
- 等离子体数据（ESA）
- 粒子速度和密度数据

默认分析时间范围为2017年3月27日，具体为05:20到06:00 UTC。

## 依赖库说明

- [pyspedas](https://github.com/spedas/pyspedas): SPEDAS软件的Python版本，用于下载和处理空间物理数据
- [pytplot](https://github.com/spedas/pytplot): 用于绘制空间物理数据的绘图工具
- [matplotlib](https://matplotlib.org/): 用于数据可视化
- [numpy](https://numpy.org/): 用于数值计算
- [scipy](https://scipy.org/): 用于科学计算

## 贡献

欢迎提交Issue和Pull Request来改进本项目。

## 许可证

[MIT License](LICENSE)
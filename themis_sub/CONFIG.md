# 项目配置说明

## Python环境配置

### 1. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# 在Linux/Mac:
source venv/bin/activate
# 在Windows:
venv\Scripts\activate

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 2. 直接安装（不推荐）

```bash
pip install -r requirements.txt
```

## 依赖库说明

本项目使用了以下主要库：

- `pyspedas`: 用于下载和处理空间物理数据
- `pytplot`: 用于空间物理数据的可视化
- `matplotlib`: 用于数据绘图
- `numpy`: 用于数值计算
- `scipy`: 用于科学计算

## 运行脚本

### 运行单个脚本

```bash
python "Bt，Vt，pitch angel.py"
```

### 批量运行脚本

创建一个批处理脚本来运行所有分析脚本：

```bash
#!/bin/bash

# 运行所有分析脚本
for script in *.py; do
  if [ "$script" != "CONFIG.md" ] && [ "$script" != "setup.py" ]; then
    echo "Running $script..."
    python "$script"
  fi
done
```

## 数据源配置

所有脚本默认使用以下参数：

- 时间范围：2017-03-27 05:20 - 06:00 UTC
- 卫星：THEMIS-D（部分脚本可能使用其他卫星）
- 数据级别：Level 2
- 坐标系：GSM坐标系

如果需要修改这些参数，可以在脚本中调整以下变量：

```python
target_start = datetime(2017, 3, 27, 5, 20, 0, tzinfo=timezone.utc)
target_end = datetime(2017, 3, 27, 6, 0, 0, tzinfo=timezone.utc)
probe = 'd'  # 卫星编号
```

## 常见问题

### 1. 网络连接问题

由于脚本需要从远程服务器下载数据，确保网络连接正常。如果网络较慢，可能需要等待较长时间。

### 2. 依赖安装问题

如果安装pyspedas或pytplot时遇到问题，可以尝试：

```bash
pip install --upgrade setuptools
pip install pyspedas pytplot
```

### 3. 内存不足

处理大量数据时可能会遇到内存不足问题，可以尝试减少时间范围或增加系统虚拟内存。
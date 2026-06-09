# 🎬 动画制作工具 (Animation Creator)

> AI 驱动的自动化动画制作平台，支持关键帧动画、骨骼动画、粒子特效和 AI 辅助生成。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ 核心功能

### 1. 🎨 AI 关键帧动画生成
- 文本描述 → 自动生成关键帧序列
- 支持补间动画自动插值
- 多种缓动函数（ease-in, ease-out, bounce, elastic）

### 2. 🦴 骨骼动画系统
- 2D 骨骼绑定与蒙皮
- 动作库预设（走路、跑步、跳跃、挥手）
- 动作混合与过渡

### 3. 💥 粒子特效引擎
- 火焰、烟雾、雨雪、爆炸特效
- 粒子系统实时预览
- JSON 配置文件导入导出

### 4. 📹 视频合成导出
- 导出为 MP4 / GIF / WebM / APNG
- 可调帧率（12/24/30/60 FPS）
- 透明度通道支持
- 音频轨道叠加

### 5. 🤖 Claude AI 辅助创作
- 自然语言描述场景 → 自动生成动画脚本
- 角色设计建议
- 分镜头脚本生成

---

## 🚀 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 运行
```bash
python main.py
```

### 示例：文字生成动画
```python
from animation_creator import AnimationEngine

engine = AnimationEngine()

# 用自然语言描述创建动画
engine.create_animation(
    prompt="一个橙色小球从左上角弹跳到右下角，带弹性效果",
    duration=3.0,  # 秒
    fps=30,
    output="bouncing_ball.mp4"
)
```

---

## 📂 项目结构
```
animation-creator/
├── main.py                  # 主入口
├── animation_creator/
│   ├── __init__.py
│   ├── engine.py           # 动画引擎核心
│   ├── keyframe.py         # 关键帧系统
│   ├── skeleton.py         # 骨骼动画
│   ├── particles.py        # 粒子系统
│   ├── interpolation.py    # 补间插值
│   ├── exporter.py         # 导出模块
│   └── ai_assistant.py     # AI 辅助创作
├── presets/                 # 预设动画模板
│   ├── characters/         # 角色骨骼预设
│   ├── particles/          # 粒子效果预设
│   └── scenes/             # 场景模板
├── examples/               # 示例动画
├── tests/                  # 测试
└── requirements.txt
```

## 🛠️ 技术栈
- **核心引擎**: Python + NumPy + SciPy
- **渲染后端**: Pillow / OpenCV / Cairo
- **AI 集成**: Claude API (Anthropic SDK)
- **导出**: FFmpeg + imageio

## 📝 License
MIT © Phoenix-YT666

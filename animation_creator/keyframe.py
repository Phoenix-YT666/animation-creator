"""
关键帧系统 (Keyframe System)
管理和生成动画关键帧，支持 AI 辅助生成。
"""

from typing import List, Dict, Any, Optional
import json
import os


class Keyframe:
    """单个关键帧"""

    def __init__(self, time: float, elements: List[Dict],
                 easing: str = "linear", label: str = ""):
        self.time = time
        self.elements = elements
        self.easing = easing
        self.label = label

    def to_dict(self) -> Dict:
        return {
            "time": self.time,
            "elements": self.elements,
            "easing": self.easing,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Keyframe":
        return cls(
            time=data.get("time", 0),
            elements=data.get("elements", []),
            easing=data.get("easing", "linear"),
            label=data.get("label", ""),
        )


class KeyframeSystem:
    """关键帧管理系统"""

    def __init__(self):
        self.keyframes: List[Keyframe] = []

    def add_keyframe(self, time: float, elements: List[Dict],
                    easing: str = "linear", label: str = "") -> Keyframe:
        """添加一个关键帧"""
        kf = Keyframe(time, elements, easing, label)
        self.keyframes.append(kf)
        self.keyframes.sort(key=lambda k: k.time)
        return kf

    def remove_keyframe(self, index: int):
        """删除关键帧"""
        if 0 <= index < len(self.keyframes):
            self.keyframes.pop(index)

    def get_keyframes(self) -> List[Dict]:
        """获取所有关键帧的数据列表"""
        return [kf.to_dict() for kf in self.keyframes]

    def clear(self):
        """清空所有关键帧"""
        self.keyframes = []

    def generate_from_description(self, description: str,
                                 width: int = 800, height: int = 600,
                                 duration: float = 3.0) -> List[Dict]:
        """
        根据文字描述用 AI 生成关键帧序列

        这构建了一个结构化的 prompt，可以发送给 Claude API 来解析。
        在没有 API 的情况下，使用基于关键词的启发式生成。

        Args:
            description: 动画描述文本
            width/height: 画布尺寸
            duration: 动画时长(秒)

        Returns:
            关键帧数据列表
        """
        # 构建 AI prompt（发送给 Claude）
        prompt = self._build_ai_prompt(description, width, height, duration)

        # 尝试使用 AI
        ai_result = self._try_ai_generation(prompt)
        if ai_result:
            return ai_result

        # 降级：启发式生成
        return self._heuristic_generation(description, width, height, duration)

    def _build_ai_prompt(self, description: str, width: int, height: int,
                        duration: float) -> str:
        """构建发送给 AI 的 prompt"""
        return f"""你是一个动画师。请根据以下描述生成关键帧序列。

画布尺寸: {width}x{height}
动画时长: {duration} 秒
描述: "{description}"

请返回 JSON 格式的关键帧序列。每个关键帧包含:
- time: 时间点(秒)
- easing: 缓动函数 (linear/ease_in/ease_out/ease_in_out/bounce_out/elastic_out)
- elements: 元素数组，每个元素包含:
  - id: 唯一标识
  - type: circle/rect/line/text/star/heart
  - x, y: 位置坐标
  - size: 大小
  - color: 颜色(hex)
  - opacity: 透明度(0-1)

要求:
1. 至少 3-5 个关键帧
2. 元素在各帧之间有连贯运动
3. 合理使用缓动函数
4. 元素颜色和大小有变化

只返回 JSON 数组，不要其他文字。"""

    def _try_ai_generation(self, prompt: str) -> Optional[List[Dict]]:
        """尝试通过 AI API 生成关键帧"""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return None

        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text

            # 提取 JSON
            import re
            json_match = re.search(r'\[[\s\S]*\]', text)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass

        return None

    def _heuristic_generation(self, description: str, width: int, height: int,
                             duration: float) -> List[Dict]:
        """基于关键词的启发式关键帧生成"""
        desc_lower = description.lower()

        # 检测模式
        has_bounce = any(w in desc_lower for w in ["弹跳", "弹", "bounce", "跳"])
        has_rotate = any(w in desc_lower for w in ["旋转", "转", "rotate", "spin"])
        has_fade = any(w in desc_lower for w in ["淡入", "淡出", "fade", "渐"])
        has_scale = any(w in desc_lower for w in ["变大", "缩小", "放大", "scale", "zoom", "大"])
        has_explosion = any(w in desc_lower for w in ["爆炸", "explode", "burst", "炸"])

        # 提取颜色
        colors_found = []
        for cn in ["红", "橙", "黄", "绿", "蓝", "紫", "粉", "白", "黑",
                    "red", "orange", "yellow", "green", "blue", "purple", "pink"]:
            if cn in desc_lower:
                colors_found.append(cn)

        color_hex = self._get_hex_for_color(colors_found[0] if colors_found else "橙")
        alt_color = self._get_hex_for_color(colors_found[1] if len(colors_found) > 1 else "蓝")

        keyframes = []
        num_keyframes = 5
        easing = "bounce_out" if has_bounce else "ease_out"

        for i in range(num_keyframes):
            t = i / (num_keyframes - 1) * duration

            elements = []
            el_id = "main_element"

            if has_bounce:
                # 弹跳路径
                bounce_t = i / (num_keyframes - 1)
                y_pos = height * 0.8 - abs(math.sin(bounce_t * math.pi * 3) * height * 0.5)
                x_pos = width * 0.1 + bounce_t * width * 0.8
            elif has_rotate:
                angle = i * math.pi * 2 / (num_keyframes - 1)
                radius = min(width, height) * 0.3
                x_pos = width / 2 + math.cos(angle) * radius
                y_pos = height / 2 + math.sin(angle) * radius
            else:
                x_pos = width * 0.1 + (i / (num_keyframes - 1)) * width * 0.8
                y_pos = height / 2

            size = 50
            if has_scale:
                size = 20 + (i / (num_keyframes - 1)) * 80

            opacity = 1.0
            if has_fade:
                opacity = i / (num_keyframes - 1)

            rotation = 0
            if has_rotate:
                rotation = i * 360 / (num_keyframes - 1)

            elements.append({
                "id": el_id,
                "type": "circle",
                "x": x_pos,
                "y": y_pos,
                "size": size,
                "color": color_hex,
                "opacity": opacity,
                "rotation": rotation,
            })

            if has_explosion and i == num_keyframes - 1:
                # 最后一帧爆炸：多个小圆分散
                elements = [{
                    "id": f"fragment_{j}",
                    "type": "circle",
                    "x": x_pos + random.uniform(-100, 100),
                    "y": y_pos + random.uniform(-100, 100),
                    "size": random.uniform(5, 20),
                    "color": random.choice([color_hex, alt_color, "#ffdd00"]),
                } for j in range(10)]

            keyframes.append({
                "time": t,
                "elements": elements,
                "easing": easing if i < num_keyframes - 1 else "linear",
                "label": f"关键帧{i+1}",
            })

        return keyframes

    def _get_hex_for_color(self, color_name: str) -> str:
        """颜色名 → hex"""
        color_map = {
            "红": "#ff3333", "red": "#ff3333",
            "橙": "#ff8800", "orange": "#ff8800",
            "黄": "#ffdd00", "yellow": "#ffdd00",
            "绿": "#33cc33", "green": "#33cc33",
            "蓝": "#3388ff", "blue": "#3388ff",
            "紫": "#9933ff", "purple": "#9933ff",
            "粉": "#ff66aa", "pink": "#ff66aa",
            "白": "#ffffff", "white": "#ffffff",
            "黑": "#222222", "black": "#222222",
        }
        return color_map.get(color_name, "#ff8800")


import math
import random

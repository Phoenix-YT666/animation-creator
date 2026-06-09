"""
补间插值系统 (Interpolation System)
提供多种缓动函数和关键帧之间的帧插值计算。
纯本地数学计算，无外部依赖。
"""

import math
from typing import List, Dict, Any, Callable, Optional


# ====== 缓动函数 (Easing Functions) ======

def linear(t: float) -> float:
    """线性插值"""
    return max(0.0, min(1.0, t))


def ease_in_quad(t: float) -> float:
    """二次缓入"""
    t = max(0.0, min(1.0, t))
    return t * t


def ease_out_quad(t: float) -> float:
    """二次缓出"""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t: float) -> float:
    """二次缓入缓出"""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 2 * t * t
    return 1 - pow(-2 * t + 2, 2) / 2


def ease_in_cubic(t: float) -> float:
    """三次缓入"""
    t = max(0.0, min(1.0, t))
    return t * t * t


def ease_out_cubic(t: float) -> float:
    """三次缓出"""
    t = max(0.0, min(1.0, t))
    return 1 - pow(1 - t, 3)


def ease_in_out_cubic(t: float) -> float:
    """三次缓入缓出"""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def ease_in_quart(t: float) -> float:
    """四次缓入"""
    t = max(0.0, min(1.0, t))
    return t * t * t * t


def ease_out_quart(t: float) -> float:
    """四次缓出"""
    t = max(0.0, min(1.0, t))
    return 1 - pow(1 - t, 4)


def ease_in_out_quart(t: float) -> float:
    """四次缓入缓出"""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 8 * t * t * t * t
    return 1 - pow(-2 * t + 2, 4) / 2


def ease_in_quint(t: float) -> float:
    """五次缓入 — 更明显加速"""
    t = max(0.0, min(1.0, t))
    return t * t * t * t * t


def ease_out_quint(t: float) -> float:
    """五次缓出 — 更明显减速"""
    t = max(0.0, min(1.0, t))
    return 1 - pow(1 - t, 5)


def ease_in_out_quint(t: float) -> float:
    """五次缓入缓出"""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 16 * t * t * t * t * t
    return 1 - pow(-2 * t + 2, 5) / 2


def ease_in_sine(t: float) -> float:
    """正弦缓入"""
    t = max(0.0, min(1.0, t))
    return 1 - math.cos((t * math.pi) / 2)


def ease_out_sine(t: float) -> float:
    """正弦缓出"""
    t = max(0.0, min(1.0, t))
    return math.sin((t * math.pi) / 2)


def ease_in_out_sine(t: float) -> float:
    """正弦缓入缓出"""
    t = max(0.0, min(1.0, t))
    return -(math.cos(math.pi * t) - 1) / 2


def ease_out_bounce(t: float) -> float:
    """弹跳缓出 — 落地弹跳效果"""
    t = max(0.0, min(1.0, t))
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_in_bounce(t: float) -> float:
    """弹跳缓入"""
    return 1 - ease_out_bounce(1 - max(0.0, min(1.0, t)))


def ease_in_out_bounce(t: float) -> float:
    """弹跳缓入缓出"""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    return (1 + ease_out_bounce(2 * t - 1)) / 2


def ease_out_elastic(t: float) -> float:
    """弹性缓出"""
    t = max(0.0, min(1.0, t))
    if t == 0 or t == 1:
        return t
    c4 = (2 * math.pi) / 3
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_in_elastic(t: float) -> float:
    """弹性缓入"""
    t = max(0.0, min(1.0, t))
    if t == 0 or t == 1:
        return t
    c4 = (2 * math.pi) / 3
    return -(pow(2, 10 * (t - 1)) * math.sin((t * 10 - 10.75) * c4))


def ease_in_out_elastic(t: float) -> float:
    """弹性缓入缓出"""
    t = max(0.0, min(1.0, t))
    if t == 0 or t == 1:
        return t
    c5 = (2 * math.pi) / 4.5
    if t < 0.5:
        return -(pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    return (pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1


def ease_out_back(t: float) -> float:
    """超出后回退"""
    t = max(0.0, min(1.0, t))
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def ease_in_back(t: float) -> float:
    """超出后回退缓入"""
    t = max(0.0, min(1.0, t))
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t


# 缓动函数注册表
EASING_FUNCTIONS: Dict[str, Callable[[float], float]] = {
    "linear": linear,
    "ease_in": ease_in_quad,
    "ease_out": ease_out_quad,
    "ease_in_out": ease_in_out_quad,
    "ease_in_quad": ease_in_quad,
    "ease_out_quad": ease_out_quad,
    "ease_in_out_quad": ease_in_out_quad,
    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,
    "ease_in_quart": ease_in_quart,
    "ease_out_quart": ease_out_quart,
    "ease_in_out_quart": ease_in_out_quart,
    "ease_in_quint": ease_in_quint,
    "ease_out_quint": ease_out_quint,
    "ease_in_out_quint": ease_in_out_quint,
    "ease_in_sine": ease_in_sine,
    "ease_out_sine": ease_out_sine,
    "ease_in_out_sine": ease_in_out_sine,
    "bounce_in": ease_in_bounce,
    "bounce_out": ease_out_bounce,
    "bounce_in_out": ease_in_out_bounce,
    "elastic_in": ease_in_elastic,
    "elastic_out": ease_out_elastic,
    "elastic_in_out": ease_in_out_elastic,
    "back_in": ease_in_back,
    "back_out": ease_out_back,
}


# ====== 值插值函数 ======

def interpolate_value(start: float, end: float, t: float,
                     easing: str = "linear") -> float:
    """在两个值之间按缓动函数插值

    Args:
        start: 起始值
        end: 结束值
        t: 0~1 之间的进度
        easing: 缓动函数名称

    Returns:
        插值结果
    """
    ease_fn = EASING_FUNCTIONS.get(easing, linear)
    eased_t = ease_fn(t)
    return start + (end - start) * eased_t


def interpolate_color(start_color: str, end_color: str, t: float,
                     easing: str = "linear") -> str:
    """在两个颜色之间插值

    Args:
        start_color: 起始颜色 (hex 如 '#ff0000')
        end_color: 结束颜色 (hex 如 '#0000ff')
        t: 进度 0~1
        easing: 缓动函数

    Returns:
        插值后的 hex 颜色
    """
    start_rgb = _hex_to_rgb(start_color)
    end_rgb = _hex_to_rgb(end_color)

    ease_fn = EASING_FUNCTIONS.get(easing, linear)
    eased_t = ease_fn(t)

    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * eased_t)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * eased_t)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * eased_t)

    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def interpolate_position(start_pos: tuple, end_pos: tuple, t: float,
                        easing: str = "linear") -> tuple:
    """在两个坐标之间插值"""
    x = interpolate_value(start_pos[0], end_pos[0], t, easing)
    y = interpolate_value(start_pos[1], end_pos[1], t, easing)
    return (x, y)


# ====== 关键帧插值 ======

def interpolate_keyframes(keyframes: List[Dict[str, Any]],
                         fps: int, duration: float) -> List[Dict[str, Any]]:
    """将稀疏的关键帧序列插值为完整帧序列

    Args:
        keyframes: 关键帧列表，每帧包含:
            {
                "index": int,        # 关键帧在总帧序列中的位置
                "time": float,       # 时间点(秒)
                "elements": [...]    # 该帧的元素列表
            }
        fps: 帧率
        duration: 总时长(秒)

    Returns:
        完整帧序列，每个帧是 {index, time, elements} dict
    """
    total_frames = int(fps * duration)
    if len(keyframes) < 2:
        # 不足两个关键帧，返回空帧序列
        return [{"index": i, "time": i / fps, "elements": []}
                for i in range(total_frames)]

    frames = []
    sorted_kf = sorted(keyframes, key=lambda k: k.get("time", k.get("index", 0) / fps))

    for frame_idx in range(total_frames):
        frame_time = frame_idx / fps

        # 找到前后两个关键帧
        prev_kf = sorted_kf[0]
        next_kf = sorted_kf[-1]

        for i, kf in enumerate(sorted_kf):
            kf_time = kf.get("time", kf.get("index", 0) / fps)
            if kf_time <= frame_time:
                prev_kf = kf
            if kf_time >= frame_time:
                next_kf = kf
                break

        prev_time = prev_kf.get("time", prev_kf.get("index", 0) / fps)
        next_time = next_kf.get("time", next_kf.get("index", 0) / fps)

        # 计算时间进度 (0~1)
        if next_time > prev_time:
            t = (frame_time - prev_time) / (next_time - prev_time)
        else:
            t = 0.0

        # 获取缓动函数
        easing = next_kf.get("easing", "linear")

        # 插值所有元素
        interpolated_elements = _interpolate_elements(
            prev_kf.get("elements", []),
            next_kf.get("elements", []),
            t, easing
        )

        frames.append({
            "index": frame_idx,
            "time": frame_time,
            "elements": interpolated_elements,
        })

    return frames


def _interpolate_elements(prev_elements: List[Dict],
                         next_elements: List[Dict],
                         t: float, easing: str) -> List[Dict]:
    """在两个帧的元素列表之间插值"""
    result = []

    # 匹配元素（按 id 或索引）
    prev_by_id = {}
    for i, el in enumerate(prev_elements):
        eid = el.get("id", f"el_{i}")
        prev_by_id[eid] = el

    for i, next_el in enumerate(next_elements):
        eid = next_el.get("id", f"el_{i}")
        prev_el = prev_by_id.get(eid)

        if prev_el is None:
            # 新元素直接出现
            result.append(next_el.copy())
            continue

        # 插值
        interpolated = {
            "id": eid,
            "type": next_el.get("type", prev_el.get("type", "circle")),
        }

        # 插值位置
        if "x" in prev_el and "x" in next_el:
            interpolated["x"] = interpolate_value(prev_el["x"], next_el["x"], t, easing)
        if "y" in prev_el and "y" in next_el:
            interpolated["y"] = interpolate_value(prev_el["y"], next_el["y"], t, easing)

        # 插值大小
        if "size" in prev_el and "size" in next_el:
            interpolated["size"] = interpolate_value(prev_el["size"], next_el["size"], t, easing)

        # 插值颜色
        if "color" in prev_el and "color" in next_el:
            interpolated["color"] = interpolate_color(prev_el["color"], next_el["color"], t, easing)

        # 插值透明度
        if "opacity" in prev_el and "opacity" in next_el:
            interpolated["opacity"] = interpolate_value(prev_el["opacity"], next_el["opacity"], t, easing)

        # 插值旋转角度
        if "rotation" in prev_el and "rotation" in next_el:
            interpolated["rotation"] = interpolate_value(prev_el["rotation"], next_el["rotation"], t, easing)

        # 保留不变的属性
        for key in ["text", "font", "shape", "width", "height", "stroke_color", "stroke_width"]:
            if key in next_el:
                interpolated[key] = next_el[key]
            elif key in prev_el:
                interpolated[key] = prev_el[key]

        result.append(interpolated)

    return result


# ====== 辅助函数 ======

def _hex_to_rgb(hex_color: str) -> tuple:
    """将 hex 颜色转为 (r, g, b)"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_position_path(start: tuple, end: tuple, steps: int,
                        easing: str = "linear") -> List[tuple]:
    """生成位置路径上的所有中间点

    用于批量预计算运动轨迹。

    Args:
        start: 起始坐标 (x, y)
        end: 结束坐标 (x, y)
        steps: 中间步数
        easing: 缓动函数

    Returns:
        包含 start 和 end 的 steps+1 个坐标点列表
    """
    positions = []
    for i in range(steps + 1):
        t = i / steps if steps > 0 else 1.0
        pos = interpolate_position(start, end, t, easing)
        positions.append(pos)
    return positions

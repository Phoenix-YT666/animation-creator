"""
帧渲染引擎 (Frame Renderer)
使用 Pillow 将帧元素渲染为真实图片。
纯本地处理，不依赖 AI API。
"""

from typing import List, Dict, Any, Optional, Tuple
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


class FrameRenderer:
    """将帧数据渲染为 PIL Image 的渲染器"""

    def __init__(self, width: int = 800, height: int = 600,
                 bg_color: str = "#1a1a2e"):
        """
        Args:
            width: 画布宽度(像素)
            height: 画布高度(像素)
            bg_color: 背景色 (hex)
        """
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self._font_cache = {}

    def render_frame(self, elements: List[Dict[str, Any]],
                    bg_color: Optional[str] = None) -> Image.Image:
        """渲染一帧

        Args:
            elements: 元素列表，每个元素包含:
                type: "circle"|"rect"|"line"|"text"|"polygon"|"ellipse"|"star"
                x, y: 位置
                size, color, opacity, rotation 等属性
            bg_color: 背景色(覆盖默认)

        Returns:
            PIL Image 对象
        """
        bg = bg_color or self.bg_color
        image = Image.new("RGBA", (self.width, self.height), bg)
        draw = ImageDraw.Draw(image)

        # 按 z_index 排序
        sorted_elements = sorted(elements, key=lambda e: e.get("z_index", 0))

        for element in sorted_elements:
            el_type = element.get("type", "circle")
            opacity = element.get("opacity", 1.0)

            # 对每个元素创建临时图层以支持透明度
            el_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            el_draw = ImageDraw.Draw(el_layer)

            if el_type == "circle":
                self._draw_circle(el_draw, element)
            elif el_type == "rect" or el_type == "rectangle":
                self._draw_rect(el_draw, element)
            elif el_type == "line":
                self._draw_line(el_draw, element)
            elif el_type == "text":
                self._draw_text(el_draw, element)
            elif el_type == "ellipse":
                self._draw_ellipse(el_draw, element)
            elif el_type == "polygon":
                self._draw_polygon(el_draw, element)
            elif el_type == "star":
                self._draw_star(el_draw, element)
            elif el_type == "heart":
                self._draw_heart(el_draw, element)

            # 应用旋转
            if element.get("rotation", 0) != 0:
                el_layer = el_layer.rotate(
                    element["rotation"],
                    resample=Image.BICUBIC,
                    expand=False
                )

            # 应用透明度
            if opacity < 1.0:
                alpha = el_layer.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                el_layer.putalpha(alpha)

            # 合并到主图层
            image = Image.alpha_composite(image, el_layer)

        # 移除 alpha 通道转为 RGB
        rgb_image = Image.new("RGB", (self.width, self.height), bg)
        rgb_image.paste(image, (0, 0), image)
        return rgb_image

    def apply_effects(self, image: Image.Image,
                     effects: List[str]) -> Image.Image:
        """应用特效

        支持: shadow, glow, blur, sharpen, grayscale, sepia,
              vignette, noise, contrast, brightness
        """
        for effect in effects:
            if effect == "blur":
                image = image.filter(ImageFilter.GaussianBlur(radius=2))
            elif effect == "sharpen":
                image = image.filter(ImageFilter.SHARPEN)
            elif effect == "grayscale":
                image = ImageEnhance.Color(image).enhance(0)
            elif effect == "sepia":
                gray = ImageEnhance.Color(image).enhance(0)
                sepia = Image.new("RGB", image.size, (112, 66, 20))
                image = Image.blend(image, sepia, 0.3)
            elif effect == "vignette":
                image = self._add_vignette(image)
            elif effect == "contrast":
                image = ImageEnhance.Contrast(image).enhance(1.5)
            elif effect == "brightness":
                image = ImageEnhance.Brightness(image).enhance(1.3)
            elif effect == "noise":
                image = self._add_noise(image)
        return image

    # ====== 元素绘制方法 ======

    def _draw_circle(self, draw: ImageDraw.Draw, el: Dict):
        x = el.get("x", 0)
        y = el.get("y", 0)
        size = el.get("size", 50)
        color = el.get("color", "#ff6600")
        stroke_color = el.get("stroke_color")
        stroke_width = el.get("stroke_width", 0)

        bbox = [x - size, y - size, x + size, y + size]
        if stroke_color and stroke_width > 0:
            draw.ellipse(bbox, fill=color, outline=stroke_color, width=int(stroke_width))
        else:
            draw.ellipse(bbox, fill=color)

    def _draw_rect(self, draw: ImageDraw.Draw, el: Dict):
        x = el.get("x", 0)
        y = el.get("y", 0)
        w = el.get("width", el.get("size", 100))
        h = el.get("height", el.get("size", 80))
        color = el.get("color", "#4488ff")
        stroke_color = el.get("stroke_color")
        stroke_width = el.get("stroke_width", 0)
        corner_radius = el.get("corner_radius", 0)

        bbox = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
        if corner_radius > 0:
            draw.rounded_rectangle(bbox, radius=int(corner_radius), fill=color)
        elif stroke_color and stroke_width > 0:
            draw.rectangle(bbox, fill=color, outline=stroke_color, width=int(stroke_width))
        else:
            draw.rectangle(bbox, fill=color)

    def _draw_line(self, draw: ImageDraw.Draw, el: Dict):
        x1 = el.get("x1", el.get("x", 0))
        y1 = el.get("y1", el.get("y", 0))
        x2 = el.get("x2", x1 + 100)
        y2 = el.get("y2", y1)
        color = el.get("color", "#ffffff")
        width = el.get("width", 2)

        draw.line([(x1, y1), (x2, y2)], fill=color, width=int(width))

    def _draw_text(self, draw: ImageDraw.Draw, el: Dict):
        text = el.get("text", "")
        x = el.get("x", 0)
        y = el.get("y", 0)
        color = el.get("color", "#ffffff")
        font_size = el.get("font_size", el.get("size", 24))
        font_name = el.get("font", "arial")

        font = self._get_font(font_name, int(font_size))
        anchor = el.get("anchor", "mm")  # 默认居中

        draw.text((x, y), text, fill=color, font=font, anchor=anchor)

    def _draw_ellipse(self, draw: ImageDraw.Draw, el: Dict):
        x = el.get("x", 0)
        y = el.get("y", 0)
        rx = el.get("rx", el.get("width", 60))
        ry = el.get("ry", el.get("height", 40))
        color = el.get("color", "#ff4488")

        bbox = [x - rx, y - ry, x + rx, y + ry]
        draw.ellipse(bbox, fill=color)

    def _draw_polygon(self, draw: ImageDraw.Draw, el: Dict):
        points = el.get("points", [])
        color = el.get("color", "#44ff88")

        if len(points) >= 3:
            draw.polygon(points, fill=color)

    def _draw_star(self, draw: ImageDraw.Draw, el: Dict):
        """绘制五角星"""
        cx = el.get("x", 0)
        cy = el.get("y", 0)
        outer_r = el.get("size", 50)
        inner_r = outer_r * 0.38
        color = el.get("color", "#ffdd00")
        points_count = el.get("points_count", 5)

        points = []
        for i in range(points_count * 2):
            angle = math.pi / 2 + (math.pi * i / points_count)
            r = outer_r if i % 2 == 0 else inner_r
            px = cx + r * math.cos(angle)
            py = cy - r * math.sin(angle)
            points.append((px, py))

        draw.polygon(points, fill=color)

    def _draw_heart(self, draw: ImageDraw.Draw, el: Dict):
        """用两个圆 + 一个三角形近似心形，然后叠加"""
        x = el.get("x", 0)
        y = el.get("y", 0)
        size = el.get("size", 50)
        color = el.get("color", "#ff2244")

        # 心形：两个上半圆 + 下半三角
        radius = size * 0.35
        left_circle = [x - radius * 1.1, y - radius * 0.8,
                      x - radius * 0.1, y + radius * 0.6]
        right_circle = [x + radius * 0.1, y - radius * 0.8,
                       x + radius * 1.1, y + radius * 0.6]

        draw.ellipse(left_circle, fill=color)
        draw.ellipse(right_circle, fill=color)

        # 下半三角
        triangle = [
            (x - radius * 1.15, y - radius * 0.1),
            (x + radius * 1.15, y - radius * 0.1),
            (x, y + radius * 1.3),
        ]
        draw.polygon(triangle, fill=color)

    # ====== 特效方法 ======

    def _add_vignette(self, image: Image.Image) -> Image.Image:
        """添加暗角效果"""
        w, h = image.size
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        cx, cy = w / 2, h / 2
        max_r = math.sqrt(cx * cx + cy * cy)

        # 从中心向外画同心圆，越来越暗
        for i in range(10, 0, -1):
            r = max_r * i / 10
            alpha = int(40 * (1 - i / 10))
            bbox = [cx - r, cy - r, cx + r, cy + r]
            draw.ellipse(bbox, fill=(0, 0, 0, alpha))

        # 合成
        result = image.convert("RGBA")
        result = Image.alpha_composite(result, overlay)
        return result.convert("RGB")

    def _add_noise(self, image: Image.Image) -> Image.Image:
        """添加噪点"""
        w, h = image.size
        pixels = image.load()
        for x in range(w):
            for y in range(h):
                r, g, b = pixels[x, y][:3]
                noise = random.randint(-20, 20)
                pixels[x, y] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise)),
                )
        return image

    # ====== 辅助方法 ======

    def _get_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        """获取字体（带缓存）"""
        cache_key = f"{font_name}_{size}"
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # 尝试系统字体路径
        font_paths = [
            # Windows
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",    # 宋体
            "C:/Windows/Fonts/arial.ttf",     # Arial
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]

        for path in font_paths:
            try:
                font = ImageFont.truetype(path, size)
                self._font_cache[cache_key] = font
                return font
            except (IOError, OSError):
                continue

        # 回退到默认字体
        try:
            font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
        self._font_cache[cache_key] = font
        return font


# ====== 便捷工具函数 ======

def render_frame_simple(elements: List[Dict], width: int = 800,
                       height: int = 600, bg_color: str = "#1a1a2e") -> Image.Image:
    """快速渲染一帧的便捷函数"""
    renderer = FrameRenderer(width, height, bg_color)
    return renderer.render_frame(elements)


def create_test_frame() -> Image.Image:
    """创建测试帧（验证渲染器正常工作）"""
    elements = [
        {"type": "circle", "x": 400, "y": 300, "size": 100, "color": "#ff6600"},
        {"type": "rect", "x": 200, "y": 150, "width": 80, "height": 60,
         "color": "#4488ff", "corner_radius": 8},
        {"type": "star", "x": 600, "y": 200, "size": 50, "color": "#ffdd00"},
        {"type": "text", "x": 400, "y": 500, "text": "Animation Creator",
         "font_size": 36, "color": "#ffffff", "anchor": "mm"},
    ]
    return render_frame_simple(elements, 800, 600, "#1a1a2e")

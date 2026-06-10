"""
肉夹馍历史 AI 动画视频生成脚本
1分钟动画，展示肉夹馍从秦朝到现代的演变
"""

import sys
sys.path.insert(0, '.')

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw

from animation_creator.renderer import FrameRenderer
from animation_creator.exporter import export_video, export_gif
from animation_creator.interpolation import interpolate_value, EASING_FUNCTIONS
from animation_creator.particles import ParticleSystem, simulate_particles_frames

# ====== 配置 ======
FPS = 30
WIDTH, HEIGHT = 1280, 720
DURATION = 60  # 1分钟
TOTAL_FRAMES = FPS * DURATION

# ====== 场景定义 ======
SCENES = [
    {
        "name": "片头标题",
        "start": 0, "end": 8,
        "title": "肉夹馍的千年传奇",
        "subtitle": "从秦军干粮到世界美食",
        "bg_color": "#1a0a00",
        "accent": "#ff6600",
    },
    {
        "name": "秦朝起源",
        "start": 8, "end": 18,
        "title": "公元前 221 年 · 秦朝",
        "subtitle": "腊汁肉的前身——寒肉诞生",
        "bg_color": "#2d1f0e",
        "accent": "#cc4400",
    },
    {
        "name": "战国军粮",
        "start": 18, "end": 28,
        "title": "战国 · 军中干粮",
        "subtitle": "白吉馍——行军途中的便携面饼",
        "bg_color": "#3d2b14",
        "accent": "#dd8800",
    },
    {
        "name": "唐朝发展",
        "start": 28, "end": 38,
        "title": "唐朝 · 长安街头",
        "subtitle": "腊汁肉夹白吉馍，风行长安城",
        "bg_color": "#4a1a0a",
        "accent": "#ee4400",
    },
    {
        "name": "陕西名小吃",
        "start": 38, "end": 48,
        "title": "陕西 · 中华名小吃",
        "subtitle": "馍酥肉烂，肥而不腻，瘦而不柴",
        "bg_color": "#5a2a10",
        "accent": "#ff5500",
    },
    {
        "name": "走向世界",
        "start": 48, "end": 56,
        "title": "从西安到世界",
        "subtitle": "Chinese Hamburger —— 全球美食",
        "bg_color": "#6a3a18",
        "accent": "#ff8822",
    },
    {
        "name": "结尾",
        "start": 56, "end": 60,
        "title": "咬一口 · 千年历史",
        "subtitle": "肉夹馍 — 最中国的汉堡",
        "bg_color": "#1a0a00",
        "accent": "#ff6600",
    },
]

# ====== 辅助函数 ======
renderer = FrameRenderer(WIDTH, HEIGHT, "#1a0a00")

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_mo(x, y, size, color, draw, t=0):
    """画肉夹馍（白吉馍的外形）"""
    c = hex_to_rgb(color)
    # 馍 — 椭圆形扁饼
    rx, ry = size, size * 0.6
    draw.ellipse([x - rx, y - ry, x + rx, y + ry], fill=color)
    # 上层面皮的光泽
    lighter = f"#{min(255, c[0]+40):02x}{min(255, c[1]+30):02x}{min(255, c[2]+20):02x}"
    draw.ellipse([x - rx*0.7, y - ry*0.8, x + rx*0.7, y - ry*0.1], fill=lighter)
    # 中间开口线
    draw.line([(x - rx*0.5, y), (x + rx*0.5, y)], fill="#3d1f0a", width=2)

def draw_meat(x, y, size, color, draw):
    """画腊汁肉块"""
    c = hex_to_rgb(color)
    # 不规则的肉块
    points = []
    for i in range(8):
        angle = i * math.pi * 2 / 8
        r = size * (0.7 + 0.3 * math.sin(i * 3.7))
        points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
    draw.polygon(points, fill=color)
    # 纹理
    darker = f"#{max(0, c[0]-40):02x}{max(0, c[1]-20):02x}{max(0, c[2]-10):02x}"
    draw.line([(x - size*0.3, y - size*0.1), (x + size*0.3, y)], fill=darker, width=1)
    draw.line([(x - size*0.2, y + size*0.2), (x + size*0.4, y + size*0.1)], fill=darker, width=1)

def draw_soldier(x, y, scale, draw, facing_right=True):
    """画秦军士兵的简化剪影"""
    direction = 1 if facing_right else -1
    # 头盔
    draw.ellipse([x-12*scale, y-30*scale, x+12*scale, y-12*scale], fill="#333333")
    draw.rectangle([x-14*scale, y-32*scale, x+14*scale, y-28*scale], fill="#444444")
    # 身体
    draw.rectangle([x-10*scale, y-12*scale, x+10*scale, y+15*scale], fill="#2a2a2a")
    # 腿
    draw.line([(x-5*scale, y+15*scale), (x-8*scale, y+30*scale)], fill="#222222", width=4)
    draw.line([(x+5*scale, y+15*scale), (x+8*scale, y+30*scale)], fill="#222222", width=4)
    # 手臂拿馍
    draw.line([(x+direction*10*scale, y-5*scale), (x+direction*20*scale, y+2*scale)], fill="#2a2a2a", width=3)

def draw_tang_person(x, y, scale, draw):
    """画唐代长安街头人物"""
    # 圆头
    draw.ellipse([x-8*scale, y-28*scale, x+8*scale, y-14*scale], fill="#e8c89e")
    # 唐装身体
    draw.rectangle([x-12*scale, y-14*scale, x+12*scale, y+12*scale], fill="#cc2233")
    # 领口
    draw.rectangle([x-6*scale, y-14*scale, x+6*scale, y-6*scale], fill="#ffdd88")
    # 下裙
    draw.polygon([(x-14*scale, y+12*scale), (x+14*scale, y+12*scale),
                  (x+10*scale, y+30*scale), (x-10*scale, y+30*scale)], fill="#aa1122")

def draw_building(x, y, w, h, color, draw):
    """画古代建筑简化版"""
    draw.rectangle([x, y, x+w, y+h], fill=color)
    # 屋檐
    draw.polygon([(x-15, y), (x+w//2, y-25), (x+w+15, y)], fill="#8B4513")
    # 窗户
    win_w, win_h = w//4, h//5
    for i in range(3):
        wx = x + w//6 + i * w//3 - win_w//2
        wy = y + h//4
        draw.rectangle([wx, wy, wx+win_w, wy+win_h], fill="#ffdd88")

def draw_chopsticks_and_bowl(x, y, draw):
    """画碗和筷子"""
    draw.ellipse([x-15, y+5, x+15, y+25], fill="#ddddcc")
    draw.ellipse([x-12, y+8, x+12, y+22], fill="#886622")
    draw.line([(x-5, y-20), (x+8, y+8)], fill="#8B4513", width=2)
    draw.line([(x+3, y-20), (x+15, y+8)], fill="#8B4513", width=2)

# ====== 主渲染循环 ======

def render_all_frames():
    frames = []
    all_elements = []

    # 用简单的逐帧循环
    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        img = Image.new("RGB", (WIDTH, HEIGHT), "#1a0a00")
        draw = ImageDraw.Draw(img)

        # 找到当前场景
        current_scene = None
        for sc in SCENES:
            if sc["start"] <= t < sc["end"]:
                current_scene = sc
                break
        if current_scene is None:
            current_scene = SCENES[-1]

        bg = current_scene["bg_color"]
        accent = current_scene["accent"]
        scene_t = t - current_scene["start"]
        scene_dur = current_scene["end"] - current_scene["start"]
        progress = min(1.0, max(0.0, scene_t / scene_dur))

        # 背景渐变
        bg_rgb = hex_to_rgb(bg)
        for y in range(HEIGHT):
            gradient = y / HEIGHT
            r = int(bg_rgb[0] * (1 - gradient * 0.3))
            g = int(bg_rgb[1] * (1 - gradient * 0.2))
            b = int(bg_rgb[2] * (1 - gradient * 0.4))
            draw.line([(0, y), (WIDTH, y)], fill=f"#{r:02x}{g:02x}{b:02x}")

        # 场景专属绘制
        scene_idx = SCENES.index(current_scene)

        if scene_idx == 0:  # 片头标题
            # 粒子背景（火花）
            for i in range(40):
                px = (WIDTH * 0.5 + math.sin(t * 3 + i * 0.8) * WIDTH * 0.4) % WIDTH
                py = (HEIGHT * 0.5 + math.cos(t * 2.7 + i * 0.6) * HEIGHT * 0.4) % HEIGHT
                spark_size = 1 + abs(math.sin(t * 5 + i)) * 3
                alpha = int(100 + 155 * math.sin(t * 4 + i * 0.5))
                draw.ellipse([px-spark_size, py-spark_size, px+spark_size, py+spark_size],
                            fill=accent)

            # 肉夹馍 logo 动画
            mo_size = 60 + math.sin(t * 1.5) * 15
            fade = min(1.0, scene_t / 2.0)
            mo_color = accent
            draw_mo(WIDTH//2, HEIGHT//2 - 40, mo_size, mo_color, draw, t)

            # 标题文字淡入
            if progress > 0.1:
                title_alpha = min(1.0, (progress - 0.1) / 0.4)
                txt_color = "#ffffff"
                # 文字阴影
                draw.text((WIDTH//2 + 2, HEIGHT//2 + 62), current_scene["title"],
                         fill="#000000", anchor="mm",
                         font=renderer._get_font("msyh", 52))
                draw.text((WIDTH//2, HEIGHT//2 + 60), current_scene["title"],
                         fill=txt_color, anchor="mm",
                         font=renderer._get_font("msyh", 52))

            if progress > 0.3:
                sub_color = accent
                draw.text((WIDTH//2, HEIGHT//2 + 120), current_scene["subtitle"],
                         fill=sub_color, anchor="mm",
                         font=renderer._get_font("msyh", 26))

        elif scene_idx == 1:  # 秦朝起源
            # 古代建筑背景
            for i in range(5):
                bx = 100 + i * 240
                draw_building(bx, HEIGHT - 350 + random.randint(-10, 10),
                            180, 320, "#5a3a1a", draw)

            # 山顶的太阳
            sun_y = HEIGHT - 250 + math.sin(t * 0.5) * 20
            draw.ellipse([WIDTH - 150, sun_y - 60, WIDTH - 30, sun_y + 60],
                        fill="#ff8844")

            # 腊汁肉罐子
            pot_x = WIDTH//2 + int(math.sin(t * 0.3) * 40)
            pot_y = HEIGHT//2 + 50
            draw.ellipse([pot_x-40, pot_y-30, pot_x+40, pot_y+60], fill="#663300")
            draw.ellipse([pot_x-30, pot_y-20, pot_x+30, pot_y], fill="#884400")
            # 蒸汽
            for i in range(3):
                sx = pot_x - 10 + i * 10
                sy = pot_y - 40 - math.sin(t * 2 + i) * 25
                steam_s = 3 + math.sin(t * 3 + i) * 2
                draw.ellipse([sx-steam_s, sy-steam_s, sx+steam_s, sy+steam_s],
                            fill="#ffffff", outline=None)

            # 标题
            draw.text((WIDTH//2, 60), current_scene["title"],
                     fill="#ffcc88", anchor="mm",
                     font=renderer._get_font("msyh", 36))
            draw.text((WIDTH//2, 110), current_scene["subtitle"],
                     fill="#dd8844", anchor="mm",
                     font=renderer._get_font("msyh", 22))

        elif scene_idx == 2:  # 战国军粮
            # 行军背景
            for i in range(10):
                mt_x = i * 140 - (t * 30) % 140
                mt_h = 80 + math.sin(i * 1.5) * 30
                draw.polygon([(mt_x-20, HEIGHT-100), (mt_x+70, HEIGHT-100-mt_h),
                             (mt_x+160, HEIGHT-100)], fill="#554433")

            # 士兵们
            for i in range(5):
                sx = 150 + i * 200 + int(t * 20) % 200
                draw_soldier(sx, HEIGHT - 160, 2.5, draw, facing_right=(i % 2 == 0))
                # 士兵手里的馍
                draw_mo(sx + 45, HEIGHT - 170, 15, "#dd9944", draw, t)

            # 篝火
            fire_x = WIDTH - 200
            fire_base_y = HEIGHT - 100
            for i in range(30):
                fy = fire_base_y - random.randint(0, 60) * math.sin(t * 6 + i * 0.3)
                fx = fire_x + random.randint(-25, 25)
                fs = 2 + random.random() * 4
                fcolor = random.choice(["#ff4400", "#ff8800", "#ffcc00", "#ff2200"])
                draw.ellipse([fx-fs, fy-fs, fx+fs, fy+fs], fill=fcolor)

            draw.text((WIDTH//2, 50), current_scene["title"],
                     fill="#ffcc88", anchor="mm",
                     font=renderer._get_font("msyh", 36))
            draw.text((WIDTH//2, 100), current_scene["subtitle"],
                     fill="#dd8844", anchor="mm",
                     font=renderer._get_font("msyh", 22))

        elif scene_idx == 3:  # 唐朝发展
            # 长安城街道
            for i in range(12):
                lx = i * 115
                ly = HEIGHT - 200
                # 唐式建筑
                draw.rectangle([lx, ly-120, lx+100, ly], fill="#cc6633")
                draw.polygon([(lx-10, ly-120), (lx+50, ly-160), (lx+110, ly-120)],
                            fill="#884422")
                # 灯笼
                lantern_y = ly - 180 + math.sin(t * 2 + i) * 8
                draw.ellipse([lx+35, lantern_y, lx+65, lantern_y+25], fill="#ff4444")

            # 长安人物
            for i in range(4):
                px = 200 + i * 250
                py = HEIGHT - 140
                draw_tang_person(px + int(math.sin(t + i) * 30), py, 1.8, draw)

            # 街边小摊 — 肉夹馍
            stall_x = WIDTH//2
            stall_y = HEIGHT - 160
            draw.rectangle([stall_x-80, stall_y-30, stall_x+80, stall_y+20], fill="#8B6914")
            # 蒸笼冒气
            for i in range(8):
                sx = stall_x - 50 + i * 14
                sy = stall_y - 50 - math.sin(t * 3 + i) * 18
                draw.ellipse([sx-4, sy-4, sx+4, sy+4], fill="#eeeeee")
            # 摊位上的馍
            for i in range(3):
                draw_mo(stall_x - 30 + i * 30, stall_y - 15, 18, "#dd9944", draw, t)

            draw.text((WIDTH//2, 40), current_scene["title"],
                     fill="#ffcc88", anchor="mm",
                     font=renderer._get_font("msyh", 36))
            draw.text((WIDTH//2, 90), current_scene["subtitle"],
                     fill="#dd8844", anchor="mm",
                     font=renderer._get_font("msyh", 22))

        elif scene_idx == 4:  # 陕西名小吃
            # 温暖色调渐变
            for y in range(HEIGHT):
                g = y / HEIGHT
                r = min(255, int(60 + g * 80))
                gc = min(255, int(20 + g * 50))
                b = min(255, int(5 + g * 20))
                draw.line([(0, y), (WIDTH, y)], fill=f"#{r:02x}{gc:02x}{b:02x}")

            # 大肉夹馍展示
            center_mo_size = 80 + math.sin(t * 0.8) * 10
            draw_mo(WIDTH//2 - 100, HEIGHT//2, center_mo_size, "#dd8844", draw, t)
            draw_meat(WIDTH//2 - 100, HEIGHT//2 - 10, 35, "#cc4411", draw)

            # 另一侧 — 碗+筷子
            draw_chopsticks_and_bowl(WIDTH//2 + 150, HEIGHT//2 - 60, draw)

            # 香料飞散粒子
            spice_colors = ["#ff6644", "#cc8844", "#dd9933", "#ff4422", "#ffaa66"]
            for i in range(20):
                sx = WIDTH//2 - 100 + math.sin(t * 4 + i * 0.7) * 180
                sy = HEIGHT//2 - 20 + math.cos(t * 3.5 + i * 0.6) * 120
                ss = 2 + abs(math.sin(t * 3 + i)) * 4
                draw.ellipse([sx-ss, sy-ss, sx+ss, sy+ss],
                            fill=random.choice(spice_colors))

            draw.text((WIDTH//2, 50), current_scene["title"],
                     fill="#ffcc88", anchor="mm",
                     font=renderer._get_font("msyh", 38))
            # 分两行显示 subtitle
            parts = current_scene["subtitle"].split("，")
            for pi, part in enumerate(parts):
                draw.text((WIDTH//2, 110 + pi * 35), part,
                         fill="#ffbb77", anchor="mm",
                         font=renderer._get_font("msyh", 24))

        elif scene_idx == 5:  # 走向世界
            # 世界地图简略背景
            continents = [
                (100, 200, 120, 280),    # 北美
                (150, 380, 100, 180),    # 南美
                (400, 150, 180, 200),    # 欧洲
                (500, 300, 120, 280),    # 非洲
                (800, 200, 250, 300),    # 亚洲
                (850, 520, 180, 120),    # 澳洲
            ]
            for cx, cy, cw, ch in continents:
                draw.ellipse([cx, cy, cx+cw, cy+ch], fill="#334455", outline="#667788")

            # 从西安出发的光点
            start_x, start_y = 930, 280
            for i in range(6):
                angle = t * 0.8 + i * math.pi / 3
                dist = (t * 60) % 500
                ex = start_x + math.cos(angle) * dist
                ey = start_y + math.sin(angle) * dist * 0.6
                es = 3 + abs(math.sin(t * 3 + i)) * 3
                draw.ellipse([ex-es, ey-es, ex+es, ey+es], fill="#ff6600")
                # 尾迹
                for trail in range(5):
                    tx = ex - math.cos(angle) * trail * 8
                    ty = ey - math.sin(angle) * trail * 8 * 0.6
                    ts = es * (1 - trail/5)
                    draw.ellipse([tx-ts, ty-ts, tx+ts, ty+ts],
                                fill=f"#ff6600")

            # 西安标记
            draw.ellipse([start_x-12, start_y-12, start_x+12, start_y+12],
                        fill="#ff2200")
            draw.text((start_x+20, start_y-15), "西安", fill="#ffffff",
                     font=renderer._get_font("msyh", 16))

            # 各处的小肉夹馍图标
            target_positions = [(250, 330), (180, 470), (500, 280), (620, 480)]
            for idx, (tx, ty) in enumerate(target_positions):
                appear_t = idx * 0.3
                if progress > appear_t:
                    local_p = min(1.0, (progress - appear_t) / 0.3)
                    mo_s = 10 + local_p * 15
                    draw_mo(tx, ty, mo_s, "#ff9944", draw, t)

            draw.text((WIDTH//2, 45), current_scene["title"],
                     fill="#ffcc88", anchor="mm",
                     font=renderer._get_font("msyh", 38))
            draw.text((WIDTH//2, 100), current_scene["subtitle"],
                     fill="#ffbb66", anchor="mm",
                     font=renderer._get_font("msyh", 24))

        elif scene_idx == 6:  # 结尾
            # 全屏渐变
            for y in range(HEIGHT):
                g = y / HEIGHT
                r = int(15 + g * 20)
                gc = int(5 + g * 10)
                b = int(2 + g * 2)
                draw.line([(0, y), (WIDTH, y)], fill=f"#{r:02x}{gc:02x}{b:02x}")

            # 中央大馍
            mo_size = 120 + math.sin(t * 0.6) * 20
            draw_mo(WIDTH//2, HEIGHT//2 - 50, mo_size, "#ff8833", draw, t)
            draw_meat(WIDTH//2, HEIGHT//2 - 70, 55, "#dd5511", draw)

            # 蒸汽效果
            for i in range(25):
                sx = WIDTH//2 + math.sin(t * 2.5 + i * 0.5) * 150
                sy = max(0, HEIGHT//2 - 120 - (t * 30 + i * 8) % 200)
                ss = max(1, 2 + math.sin(t * 2 + i) * 3)
                draw.ellipse([max(0, sx-ss), max(0, sy-ss), min(WIDTH, sx+ss), min(HEIGHT, sy+ss)], fill="#ffffff")

            # 金色粒子
            for i in range(30):
                gx = WIDTH//2 + math.sin(t * 3 + i * 0.7) * 300
                gy = HEIGHT//2 + math.cos(t * 2.8 + i * 0.6) * 250
                gs = max(0.5, 1.5 + abs(math.sin(t * 4 + i)) * 3)
                draw.ellipse([max(0, gx-gs), max(0, gy-gs), min(WIDTH, gx+gs), min(HEIGHT, gy+gs)], fill="#ffcc00")

            # 标题
            draw.text((WIDTH//2 + 3, HEIGHT//2 + 73), current_scene["title"],
                     fill="#000000", anchor="mm",
                     font=renderer._get_font("msyh", 48))
            draw.text((WIDTH//2, HEIGHT//2 + 70), current_scene["title"],
                     fill="#ffcc44", anchor="mm",
                     font=renderer._get_font("msyh", 48))
            draw.text((WIDTH//2, HEIGHT//2 + 130), current_scene["subtitle"],
                     fill="#ff9944", anchor="mm",
                     font=renderer._get_font("msyh", 26))

        # 底部进度条
        progress_full = t / DURATION
        bar_y = HEIGHT - 8
        bar_h = 4
        draw.rectangle([0, bar_y, WIDTH, bar_y + bar_h], fill="#222222")
        draw.rectangle([0, bar_y, int(WIDTH * progress_full), bar_y + bar_h], fill=accent)

        frames.append(img)

        if frame_idx % (TOTAL_FRAMES // 10) == 0:
            pct = frame_idx / TOTAL_FRAMES * 100
            print(f"  [{int(pct):3d}%] 渲染 {frame_idx}/{TOTAL_FRAMES} 帧 | 场景: {current_scene['name']}")

    return frames


# ====== 主程序 ======
if __name__ == "__main__":
    output_dir = Path("D:/龙虾文件/github-projects/animation-creator")

    print("=" * 60)
    print("  🎬 肉夹馍的千年传奇 — AI 动画生成")
    print(f"  分辨率: {WIDTH}x{HEIGHT} | 帧率: {FPS} | 时长: {DURATION}s")
    print(f"  总帧数: {TOTAL_FRAMES} | 场景数: {len(SCENES)}")
    print("=" * 60)
    print()

    for sc in SCENES:
        print(f"  📍 {sc['start']:2d}s - {sc['end']:2d}s : {sc['name']}")

    print()
    print("  🎨 开始渲染...")

    frames = render_all_frames()

    print(f"\n  ✅ 渲染完成: {len(frames)} 帧")

    # 导出为 MP4
    print(f"\n  💾 导出 MP4 视频...")
    mp4_path = str(output_dir / "roujiamo_history.mp4")
    try:
        export_video(frames, mp4_path, fps=FPS, quality=6)
        print(f"  ✅ MP4 视频已保存: {mp4_path}")
    except Exception as e:
        print(f"  ⚠️ MP4 导出失败 (可能需要FFmpeg): {e}")
        print(f"  💡 降级为 GIF 导出...")
        gif_path = str(output_dir / "roujiamo_history.gif")
        export_gif(frames, gif_path, fps=FPS, loop=0)
        print(f"  ✅ GIF 动画已保存: {gif_path}")

    # 同时导出 GIF（方便分享）
    print(f"\n  💾 导出 GIF 动画...")
    gif_path = str(output_dir / "roujiamo_history.gif")
    try:
        export_gif(frames, gif_path, fps=FPS//2, loop=0)  # GIF 用一半帧率以减小文件
        print(f"  ✅ GIF 动画已保存: {gif_path}")
    except Exception as e:
        print(f"  ⚠️ GIF 导出失败: {e}")

    # 缩略图
    thumb = frames[TOTAL_FRAMES // 2]
    thumb_path = str(output_dir / "roujiamo_thumbnail.png")
    thumb.save(thumb_path)
    print(f"  ✅ 缩略图已保存: {thumb_path}")

    print(f"\n{'='*60}")
    print(f"  🎉 动画制作完成!")
    print(f"  📺 MP4: {mp4_path}")
    print(f"  🖼️ GIF: {gif_path}")
    print(f"  🖼️ 缩略图: {thumb_path}")
    print(f"{'='*60}")

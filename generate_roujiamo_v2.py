"""
肉夹馍千年历史 — 高清AI动画 v2
高画质版本：丰富细节、多层场景、粒子特效、平滑过渡
"""

import sys; sys.path.insert(0, '.')
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ====== 配置 ======
FPS, W, H = 30, 1280, 720
DURATION = 62
TOTAL = FPS * DURATION

# ====== 高质量调色板 ======
PALETTE = {
    "bg_deep": (10, 5, 2),
    "bg_warm": (30, 15, 5),
    "bg_gold": (40, 25, 10),
    "gold": (255, 170, 50),
    "fire": (240, 80, 20),
    "ember": (200, 60, 10),
    "cream": (255, 235, 200),
    "dark_wood": (60, 30, 10),
    "stone": (120, 100, 90),
    "red_lantern": (220, 40, 30),
    "tang_red": (180, 30, 40),
    "tang_gold": (220, 180, 80),
    "ink": (20, 15, 25),
    "parchment": (230, 210, 170),
    "meat": (180, 55, 20),
    "meat_dark": (130, 35, 10),
    "bread_light": (240, 200, 140),
    "bread_dark": (180, 130, 70),
    "steam": (255, 255, 250),
    "green_jade": (60, 140, 100),
    "sky_blue": (60, 120, 200),
}

def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def blend(c1, c2, t):
    return tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))

def color_str(c):
    return f"#{int(c[0]):02x}{int(c[1]):02x}{int(c[2]):02x}"

def safe_ellipse(draw, bbox, **kwargs):
    """安全的椭圆绘制，防止坐标溢出"""
    x0, y0, x1, y1 = bbox
    x0 = max(0, min(W, x0))
    y0 = max(0, min(H, y0))
    x1 = max(0, min(W, x1))
    y1 = max(0, min(H, y1))
    if x1 <= x0 or y1 <= y0:
        return
    draw.ellipse([x0, y0, x1, y1], **kwargs)

def lerp(a,b,t): return a+(b-a)*t

# ====== 字体 ======
_fonts = {}
def get_font(name, size):
    k = f"{name}_{size}"
    if k in _fonts: return _fonts[k]
    paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/STKAITI.ttf",
        "C:/Windows/Fonts/STXINGKA.ttf",
    ]
    for p in paths:
        try: _fonts[k] = ImageFont.truetype(p, size); return _fonts[k]
        except: pass
    _fonts[k] = ImageFont.load_default(); return _fonts[k]

# ====== 绘画工具 ======
def draw_mo(draw, cx, cy, size, t=0):
    """高品质肉夹馍"""
    rx, ry = size, size*0.55
    # 底部馍皮
    safe_ellipse(draw, [cx-rx, cy-ry+8, cx+rx, cy+ry+8], fill=color_str(PALETTE["bread_dark"]))
    # 主体
    safe_ellipse(draw, [cx-rx, cy-ry, cx+rx, cy+ry], fill=color_str(PALETTE["bread_light"]))
    # 顶部光泽
    lc = blend(PALETTE["bread_light"], (255,255,240), 0.5)
    safe_ellipse(draw, [cx-rx*0.75, cy-ry*0.9, cx+rx*0.75, cy-ry*0.1], fill=color_str(lc))
    # 开口
    draw.arc([cx-rx*0.5, cy-ry*0.2, cx+rx*0.5, cy+ry*0.6], 180, 360, fill=color_str(PALETTE["dark_wood"]), width=2)
    # 腊汁肉夹层
    meat_w = rx*0.8
    meat_h = ry*0.35
    safe_ellipse(draw, [cx-meat_w, cy-meat_h*0.3, cx+meat_w, cy+meat_h], fill=color_str(PALETTE["meat"]))
    # 肉质纹理
    for i in range(5):
        tx = cx + math.sin(i*1.3)*meat_w*0.4
        ty = cy - meat_h*0.1 + i*meat_h*0.12
        draw.line([(tx-meat_w*0.3, ty), (tx+meat_w*0.3, ty)], fill=color_str(PALETTE["meat_dark"]), width=1)

def draw_steam(draw, cx, cy, t, count=8):
    """蒸汽效果"""
    for i in range(count):
        sx = cx + math.sin(t*3.5+i*0.8)*40
        sy = cy - (t*25+i*12)%100
        alpha = 150 - (t*25+i*12)%100*1.5
        alpha = max(10, min(150, alpha))
        r = 3+math.sin(t*2+i)*2
        sc = (255,255,250,alpha)
        # 用半透明圆模拟
        safe_ellipse(draw, [sx-r, sy-r, sx+r, sy+r], fill=color_str(PALETTE["steam"]), outline=None)

def draw_lantern(draw, x, y, s, t):
    """红灯笼"""
    # 灯体
    safe_ellipse(draw, [x-s*0.3, y, x+s*0.3, y+s], fill=color_str(PALETTE["red_lantern"]))
    # 金边
    safe_ellipse(draw, [x-s*0.32, y+s*0.35, x+s*0.32, y+s*0.65], fill=color_str(PALETTE["tang_gold"]))
    # 顶部
    draw.rectangle([x-s*0.15, y-s*0.1, x+s*0.15, y+s*0.05], fill=color_str(PALETTE["tang_gold"]))
    # 灯穗
    sy = y+s
    for i in range(3):
        sx = x - s*0.1 + i*s*0.1
        sway = math.sin(t*4+i)*2
        draw.line([(sx, sy), (sx+sway, sy+s*0.3)], fill=color_str(PALETTE["tang_gold"]), width=1)

def draw_tang_house(draw, x, y, w, h, t):
    """唐代建筑"""
    # 主体墙
    draw.rectangle([x, y-h, x+w, y], fill=color_str((160, 100, 60)))
    # 柱子
    for i in range(4):
        px = x + (i+0.5)*w/4 - 4
        draw.rectangle([px, y-h*0.5, px+8, y], fill=color_str(PALETTE["dark_wood"]))
    # 屋顶飞檐
    roof = [
        (x-15, y-h), (x+w//2, y-h-35), (x+w+15, y-h),
        (x+w+20, y-h+8), (x+w//2, y-h-22), (x-20, y-h+8)
    ]
    draw.polygon(roof, fill=color_str((100, 50, 20)))
    # 窗
    wx = x + w*0.15
    wy = y - h*0.7
    ww, wh = w*0.2, h*0.25
    draw.rectangle([wx, wy, wx+ww, wy+wh], fill=color_str((255,220,150)), outline=color_str(PALETTE["dark_wood"]))
    wx2 = x + w*0.55
    draw.rectangle([wx2, wy, wx2+ww, wy+wh], fill=color_str((255,220,150)), outline=color_str(PALETTE["dark_wood"]))

def draw_ancient_pot(draw, cx, cy, s, t):
    """陶罐——腊汁肉的容器"""
    # 罐身
    safe_ellipse(draw, [cx-s*0.5, cy-s*0.2, cx+s*0.5, cy+s*0.8], fill=color_str((100, 55, 25)))
    # 罐口
    safe_ellipse(draw, [cx-s*0.3, cy-s*0.35, cx+s*0.3, cy-s*0.15], fill=color_str((140, 90, 50)))
    # 高光
    safe_ellipse(draw, [cx-s*0.1, cy-s*0.25, cx+s*0.05, cy-s*0.05], fill=color_str((180, 130, 80)))
    # 蒸汽
    draw_steam(draw, cx, cy-s*0.4, t, 6)

def draw_soldier_v2(draw, x, y, s, facing_right=True):
    """秦兵剪影 v2"""
    d = 1 if facing_right else -1
    # 头盔
    safe_ellipse(draw, [x-s*0.3, y-s*0.8, x+s*0.3, y-s*0.2], fill=color_str((40,35,30)))
    draw.rectangle([x-s*0.35, y-s*0.85, x+s*0.35, y-s*0.75], fill=color_str((60,55,50)))
    # 铠甲
    draw.rectangle([x-s*0.28, y-s*0.2, x+s*0.28, y+s*0.4], fill=color_str((50,45,40)))
    # 甲片纹理
    for i in range(4):
        ly = y - s*0.1 + i*s*0.12
        draw.line([(x-s*0.25, ly), (x+s*0.25, ly)], fill=color_str((70,65,60)), width=1)
    # 腿
    draw.line([(x-s*0.1, y+s*0.4), (x-s*0.15*d, y+s*0.85)], fill=color_str((40,35,30)), width=int(s*0.12))
    draw.line([(x+s*0.1, y+s*0.4), (x+s*0.15*d, y+s*0.85)], fill=color_str((40,35,30)), width=int(s*0.12))
    # 手臂持馍
    draw.line([(x+d*s*0.2, y-s*0.05), (x+d*s*0.55, y+s*0.1)], fill=color_str((50,45,40)), width=int(s*0.08))

def draw_mountain_range(draw, base_y, heights, color):
    """远山"""
    for i, h in enumerate(heights):
        mx = i*W/len(heights)
        mw = W/len(heights)*1.2
        draw.polygon([(mx-mw*0.1, base_y), (mx+mw*0.5, base_y-h), (mx+mw, base_y)], fill=color)

def draw_silk_road_map(draw, t):
    """丝绸之路/传播路线——世界地图风格"""
    # 简化的欧亚大陆轮廓
    land = [
        (100, 160, 280, 140),   # 欧洲
        (380, 120, 500, 200),   # 中亚
        (800, 140, 350, 240),   # 东亚(中国)
        (880, 400, 200, 120),   # 东南亚
    ]
    for lx, ly, lw, lh in land:
        safe_ellipse(draw, [lx, ly, lx+lw, ly+lh], fill=color_str((25,40,55)), outline=color_str((60,90,110)), width=2)

    # 西安起点
    xi_an = (1050, 210)
    safe_ellipse(draw, [xi_an[0]-8, xi_an[1]-8, xi_an[0]+8, xi_an[1]+8], fill=color_str(PALETTE["fire"]))

    # 传播路线
    routes = [
        [(1050,210), (950,200), (820,180), (700,190), (580,200), (480,210), (380,190), (280,180)],
        [(1050,210), (980,260), (850,300), (720,280), (600,300)],
        [(1050,210), (1000,350), (900,400), (800,380)],
    ]
    for route in routes:
        for i in range(len(route)-1):
            x1,y1 = route[i]; x2,y2 = route[i+1]
            progress = (t*0.15) % 1.0
            seg_p = i/(len(route)-1)
            if progress > seg_p:
                local_p = min(1.0, (progress-seg_p)/(1/(len(route)-1)))
                lx = lerp(x1, x2, local_p)
                ly = lerp(y1, y2, local_p)
                # 光点
                for j in range(3):
                    dot_x = lx + math.sin(t*8+j)*6
                    dot_y = ly + math.cos(t*8+j)*6
                    safe_ellipse(draw, [dot_x-3, dot_y-3, dot_x+3, dot_y+3], fill=color_str(PALETTE["gold"]))
                # 尾迹
                for trail in range(4):
                    alpha = (1-trail/4)
                    ts = 2*alpha
                    tx = lx - (x2-x1)*trail*0.06
                    ty = ly - (y2-y1)*trail*0.06
                    tc = blend(PALETTE["fire"], PALETTE["gold"], alpha)
                    safe_ellipse(draw, [tx-ts, ty-ts, tx+ts, ty+ts], fill=color_str(tc))

def draw_particle_aurora(draw, cx, cy, t, count, spread, palette, seed=0):
    """粒子极光效果"""
    for i in range(count):
        a = t*2 + i*0.5 + seed
        px = cx + math.sin(a*1.7)*spread*0.8
        py = cy + math.cos(a*2.3)*spread*0.6
        size = 1 + abs(math.sin(a*3))*3
        c = random.choice(palette)
        safe_ellipse(draw, [px-size, py-size, px+size, py+size], fill=color_str(c))

def draw_text_with_glow(draw, text, x, y, size, color, glow_color=None, anchor="mm"):
    """发光文字"""
    font = get_font("msyh", size)
    if glow_color:
        for dx,dy in [(-2,0),(2,0),(0,-2),(0,2),(-1,-1),(1,-1),(-1,1),(1,1)]:
            draw.text((x+dx, y+dy), text, fill=glow_color, anchor=anchor, font=font)
    draw.text((x, y), text, fill=color, anchor=anchor, font=font)

# ====== 场景渲染 ======

def render_scene_0_title(img, draw, t, dur):
    """片头——火中诞生的传奇 (0-7s)"""
    p = min(1.0, t/dur)

    # 背景：从深黑渐变为暗红
    for y in range(H):
        grad = y/H
        bg = blend(PALETTE["bg_deep"], (40,10,3), grad)
        draw.line([(0,y),(W,y)], fill=color_str(bg))

    # 中心火焰粒子
    draw_particle_aurora(draw, W//2, H//2-50, t, 80, 350,
                        [PALETTE["fire"],PALETTE["gold"],PALETTE["ember"],(255,120,30)], seed=42)

    # 底部余烬上升
    for i in range(40):
        ex = W//2 + math.sin(t*3+i*0.7)*200
        ey = H - (t*50 + i*15) % (H+100)
        es = max(0.5, 1.5 + math.sin(t*4+i)*2)
        x0, y0 = max(0, ex-es), max(0, ey-es)
        x1, y1 = min(W, ex+es), min(H, ey+es)
        if x1 > x0 and y1 > y0:
            safe_ellipse(draw, [x0, y0, x1, y1], fill=color_str(PALETTE["ember"]))

    # 大馍从火中显现
    fade_in = min(1.0, max(0, (p-0.15)/0.5))
    if fade_in > 0:
        mo_scale = 80 + math.sin(t*1.2)*12
        # 馍的光晕
        glow_s = mo_scale*1.5
        glow_c = blend(PALETTE["gold"], (255,200,100), 0.7)
        for r in range(5, 0, -1):
            alpha_glow = fade_in*(6-r)*0.04
            glow_sr = glow_s*(0.7+r*0.06)
            safe_ellipse(draw, [W//2-glow_sr, H//2-50-glow_sr*0.55, W//2+glow_sr, H//2-50+glow_sr*0.55],
                        fill=color_str(glow_c), outline=None)

        draw_mo(draw, W//2, H//2-50, int(mo_scale*fade_in), t)

    # 标题
    if p > 0.2:
        title_fade = min(1.0, (p-0.2)/0.4)
        tc = blend(PALETTE["cream"], PALETTE["gold"], title_fade)
        draw_text_with_glow(draw, "肉夹馍的千年传奇", W//2, H//2+70, 56,
                          color_str(tc), color_str((100,50,0)))

    if p > 0.35:
        sub_fade = min(1.0, (p-0.35)/0.3)
        draw_text_with_glow(draw, "从秦军干粮到世界美食", W//2, H//2+130, 28,
                          color_str(PALETTE["gold"]), color_str((80,40,0)))

def render_scene_1_qin(img, draw, t, dur):
    """秦朝——腊汁肉诞生 (7-16s)"""
    p = min(1.0, t/dur)

    # 背景：暖褐色渐变
    for y in range(H):
        bg = blend((40,20,8), (60,35,15), y/H)
        draw.line([(0,y),(W,y)], fill=color_str(bg))

    # 远山
    mt_heights = [120+math.sin(i*0.8)*40 for i in range(12)]
    draw_mountain_range(draw, H-200, mt_heights, color_str((50,35,20)))

    # 古代建筑群
    for i in range(5):
        bx = 80 + i*250
        bh = 160 + random.randint(-30,30)
        by = H - 180
        draw_tang_house(draw, bx, by, 160, bh, t+i*0.7)

    # 陶罐——腊汁肉熬制
    pot_x = W//2 + int(math.sin(t*0.4)*60)
    pot_y = H//2 + 30
    draw_ancient_pot(draw, pot_x, pot_y, 90, t)

    # 火堆
    fire_x, fire_y = pot_x, pot_y+50
    for i in range(50):
        fx = fire_x + random.randint(-35,35)
        fy = fire_y + random.randint(-5,20) - abs(math.sin(t*8+i*0.3))*45
        fs = 1.5 + random.random()*4
        fc = random.choice([(255,80,10),(255,140,20),(255,200,40),(255,40,5)])
        safe_ellipse(draw, [fx-fs, fy-fs, fx+fs, fy+fs], fill=color_str(fc))

    # 罐旁香料飘散
    for i in range(15):
        sx = pot_x + math.sin(t*2+i*0.6)*50
        sy = pot_y - 60 - (t*20+i*10)%120
        safe_ellipse(draw, [sx-2, sy-2, sx+2, sy+2], fill=color_str((200,150,80)))

    # 文字
    draw_text_with_glow(draw, "公元前221年 · 秦朝", W//2, 50, 40, color_str(PALETTE["cream"]), color_str((80,40,10)))
    draw_text_with_glow(draw, "腊汁肉——源自寒肉", W//2, 105, 24, color_str(PALETTE["gold"]), None)

    # 左侧：腌制场景简笔画
    meat_x = 180
    meat_y = H//2-20
    for i in range(4):
        mx = meat_x + (i-1.5)*35
        my = meat_y + math.sin(t+i)*5
        safe_ellipse(draw, [mx-20, my-12, mx+20, my+12], fill=color_str(PALETTE["meat"]))
        draw.line([(mx-15, my), (mx+15, my)], fill=color_str(PALETTE["meat_dark"]), width=1)
    draw.text((meat_x, meat_y+40), "腌制的猪肉块", fill=color_str((200,160,100)), anchor="mm", font=get_font("msyh", 14))

def render_scene_2_war(img, draw, t, dur):
    """战国——军中干粮白吉馍 (16-27s)"""
    p = min(1.0, t/dur)

    # 天空——战场黄昏
    for y in range(H):
        sky = blend((80,40,15), (40,25,10), y/H)
        draw.line([(0,y),(W,y)], fill=color_str(sky))

    # 远山+城墙
    draw_mountain_range(draw, H-250, [80+math.sin(i)*30 for i in range(14)], color_str((70,50,30)))
    # 城墙
    wall_y = H-210
    for i in range(15):
        wx = i*90
        wh = 30+random.randint(-10,10)
        draw.rectangle([wx, wall_y-wh, wx+85, wall_y], fill=color_str((120,100,80)))
        # 城垛
        draw.rectangle([wx+20, wall_y-wh-10, wx+40, wall_y-wh], fill=color_str((120,100,80)))
        draw.rectangle([wx+55, wall_y-wh-10, wx+75, wall_y-wh], fill=color_str((120,100,80)))

    # 战旗
    flag_x = W-200
    flag_y = wall_y-320
    sway = math.sin(t*2)*8
    draw.line([(flag_x, flag_y+300), (flag_x, flag_y)], fill=color_str((60,40,20)), width=4)
    draw.polygon([(flag_x, flag_y), (flag_x+80+sway, flag_y+25), (flag_x, flag_y+50)], fill=color_str((180,30,20)))
    draw.text((flag_x+20, flag_y+20), "秦", fill=color_str((255,220,80)), anchor="mm", font=get_font("msyh", 28))

    # 士兵行列
    for i in range(6):
        sx = 150 + i*180 + int(t*25)%180
        sy = H-180
        # 身体剪影
        draw_soldier_v2(draw, sx, sy, 40, facing_right=(i%3!=0))
        # 士兵手里/身旁的馍
        mo_x = sx + (55 if i%3!=0 else -55)
        draw_mo(draw, mo_x, sy-10, 14, t+i)

    # 篝火
    campfire_x = W-280
    campfire_y = H-140
    for i in range(40):
        fx = campfire_x + random.randint(-30,30)
        fy = campfire_y - random.randint(0,55) - abs(math.sin(t*10+i))*20
        safe_ellipse(draw, [fx-2, fy-2, fx+2, fy+2], fill=color_str(random.choice(
            [(255,60,10),(255,130,30),(255,200,50),(255,30,5)])))
    # 柴火
    for i in range(3):
        sx = campfire_x - 20 + i*15
        draw.line([(sx, campfire_y+5), (sx+15, campfire_y-5)], fill=color_str((80,50,30)), width=4)

    draw_text_with_glow(draw, "战国 · 军中干粮", W//2, 45, 40, color_str(PALETTE["cream"]), color_str((80,40,10)))
    draw_text_with_glow(draw, "白吉馍——行军途中的便携面饼", W//2, 100, 24, color_str(PALETTE["gold"]), None)

def render_scene_3_tang(img, draw, t, dur):
    """唐朝——长安街头风行 (27-38s)"""
    p = min(1.0, t/dur)

    # 天空
    for y in range(H):
        sky = blend((30,60,100), (60,100,160), y/H*0.7)
        draw.line([(0,y),(W,y)], fill=color_str(sky))

    # 长安城建筑群
    for i in range(8):
        bx = 40 + i*155
        bh = 140 + random.randint(-40,40)
        by = H - 200
        draw_tang_house(draw, bx, by, 130, bh, t+i*0.5)

    # 街道地面
    draw.rectangle([0, H-200, W, H], fill=color_str((150,130,110)))
    # 石板纹理
    for i in range(20):
        lx = i*65
        draw.line([(lx, H-200), (lx, H)], fill=color_str((130,110,90)), width=1)

    # 红灯笼阵列
    for i in range(6):
        lx = 80 + i*200
        ly = 120 + math.sin(t*3+i)*10
        draw_lantern(draw, lx, ly, 30, t+i)

    # 街边馍摊
    stall_x = W//2
    stall_y = H-150
    draw.rectangle([stall_x-90, stall_y-25, stall_x+90, stall_y+15], fill=color_str((180,140,80)))
    draw.rectangle([stall_x-95, stall_y-28, stall_x+95, stall_y-25], fill=color_str(PALETTE["dark_wood"]))
    # 摊上蒸笼
    for i in range(4):
        sx = stall_x - 50 + i*32
        sy = stall_y - 30 - i*4
        safe_ellipse(draw, [sx-14, sy-6, sx+14, sy+6], fill=color_str((200,170,120)))
    draw_steam(draw, stall_x, stall_y-45, t, 10)
    # 摊上的馍
    for i in range(5):
        draw_mo(draw, stall_x-60+i*30, stall_y-10, 16, t+i)

    # 唐代人物
    for i in range(5):
        px = 90 + i*240 + int(math.sin(t+i)*25)
        py = H-185
        # 简化唐装人物
        safe_ellipse(draw, [px-7, py-25, px+7, py-13], fill=color_str((230,190,150)))
        draw.rectangle([px-10, py-13, px+10, py+8], fill=color_str(random.choice([(190,40,50),(60,40,140),(50,120,60)])))
        draw.polygon([(px-12, py+8), (px+12, py+8), (px+8, py+25), (px-8, py+25)], fill=color_str((100,70,50)))

    draw_text_with_glow(draw, "唐朝 · 长安街头", W//2, 50, 42, color_str(PALETTE["cream"]), color_str((80,40,10)))
    draw_text_with_glow(draw, "腊汁肉夹白吉馍，风行长安城", W//2, 105, 24, color_str(PALETTE["gold"]), None)

def render_scene_4_shaanxi(img, draw, t, dur):
    """陕西名小吃——绝美展示 (38-49s)"""
    p = min(1.0, t/dur)

    # 温暖底色
    for y in range(H):
        bg = blend((60,30,10), (80,45,15), y/H)
        draw.line([(0,y),(W,y)], fill=color_str(bg))

    # 装饰花纹边框
    border_r = 20
    # 四角花纹
    for cx, cy in [(border_r,border_r),(W-border_r,border_r),(border_r,H-border_r),(W-border_r,H-border_r)]:
        for i in range(3):
            r = 15 + i*8
            a = t*2 + i*0.8
            draw.arc([cx-r, cy-r, cx+r, cy+r], int(a*30)%360, int(a*30+120)%360,
                    fill=color_str(PALETTE["gold"]), width=1)

    # 左侧——展示用肉夹馍大特写
    mo_cx, mo_cy = W//3, H//2-20
    mo_size = 100 + math.sin(t*0.7)*15

    # 光环
    for r in range(4,0,-1):
        glow_r = mo_size*(1.1+r*0.08)
        glow_a = int(60*(5-r)/5)
        glow_c = blend(PALETTE["gold"], (255,200,100), r/4)
        safe_ellipse(draw, [mo_cx-glow_r, mo_cy-glow_r*0.55, mo_cx+glow_r, mo_cy+glow_r*0.55],
                    fill=color_str(glow_c), outline=None)

    draw_mo(draw, mo_cx, mo_cy, int(mo_size), t)

    # 香料粒子环绕
    spice_colors = [(200,80,30),(220,140,50),(180,60,20),(240,180,80),(160,100,40)]
    for i in range(25):
        a = t*3 + i*math.pi*2/25
        r = mo_size*1.3 + math.sin(t*5+i)*20
        sx = mo_cx + math.cos(a)*r
        sy = mo_cy + math.sin(a)*r*0.55
        ss = 1.5 + abs(math.sin(t*3+i))*3
        safe_ellipse(draw, [sx-ss, sy-ss, sx+ss, sy+ss], fill=color_str(random.choice(spice_colors)))

    # 右侧——碗+筷子+蘸料
    bowl_x, bowl_y = W*2//3+30, H//2+10
    safe_ellipse(draw, [bowl_x-40, bowl_y+10, bowl_x+40, bowl_y+40], fill=color_str((220,210,190)))
    safe_ellipse(draw, [bowl_x-33, bowl_y+14, bowl_x+33, bowl_y+33], fill=color_str((150,100,50)))
    # 筷子
    draw.line([(bowl_x-8, bowl_y-50), (bowl_x+5, bowl_y+15)], fill=color_str((120,70,30)), width=3)
    draw.line([(bowl_x+5, bowl_y-50), (bowl_x+15, bowl_y+15)], fill=color_str((120,70,30)), width=3)

    # 文字——四字描述
    tags = ["馍酥", "肉烂", "肥而不腻", "瘦而不柴"]
    for i, tag in enumerate(tags):
        tx = W//2 + (i-1.5)*160
        ty = H-80
        appear = i*0.15
        if p > appear:
            tag_fade = min(1.0, (p-appear)/0.2)
            tc = blend(PALETTE["cream"], PALETTE["gold"], tag_fade)
            draw.text((tx, ty), tag, fill=color_str(tc), anchor="mm", font=get_font("STKAITI", 30))

    draw_text_with_glow(draw, "陕西 · 中华名小吃", W//2, 50, 42, color_str(PALETTE["cream"]), color_str((80,40,10)))

def render_scene_5_world(img, draw, t, dur):
    """走向世界——传播地图 (49-57s)"""
    p = min(1.0, t/dur)

    # 深蓝宇宙底色
    for y in range(H):
        bg = blend((8,15,30), (15,30,55), y/H)
        draw.line([(0,y),(W,y)], fill=color_str(bg))

    # 星星
    random.seed(100)
    for i in range(60):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        twinkle = 0.5 + 0.5*math.sin(t*5+i*7)
        ss = 0.5 + twinkle*1.5
        safe_ellipse(draw, [sx-ss, sy-ss, sx+ss, sy+ss], fill=color_str((255,255,240)))

    # 丝绸之路地图
    draw_silk_road_map(draw, t)

    # 西安发光标记
    xi_an = (1050, 210)
    pulse = 5 + math.sin(t*4)*3
    safe_ellipse(draw, [xi_an[0]-pulse, xi_an[1]-pulse, xi_an[0]+pulse, xi_an[1]+pulse],
                fill=color_str((255,100,30)), outline=None)
    draw.text((xi_an[0]+20, xi_an[1]-20), "西安", fill=color_str(PALETTE["gold"]), font=get_font("msyh", 18))

    # 目标城市光点
    cities = [("罗马", 180, 160), ("波斯", 480, 200), ("印度", 700, 320),
              ("日本", 1150, 120), ("东南亚", 950, 420)]
    for name, cx, cy in cities:
        appear_t = 0.15 + cities.index((name,cx,cy))*0.12
        if p > appear_t:
            city_fade = min(1.0, (p-appear_t)/0.2)
            dot_s = 6*city_fade
            safe_ellipse(draw, [cx-dot_s, cy-dot_s, cx+dot_s, cy+dot_s], fill=color_str(PALETTE["gold"]))
            draw.text((cx+12, cy-12), name, fill=color_str((200,220,255)), font=get_font("msyh", 13))

    # 小馍图标散布各地
    for i, (_, cx, cy) in enumerate(cities):
        appear_t = 0.2 + i*0.1
        if p > appear_t:
            local_p = min(1.0, (p-appear_t)/0.3)
            draw_mo(draw, cx, cy+20, int(12*local_p), t+i)

    draw_text_with_glow(draw, "从西安到世界", W//2, 40, 42, color_str((220,240,255)), color_str((40,80,140)))
    draw_text_with_glow(draw, "Chinese Hamburger——全球美食", W//2, 95, 24, color_str(PALETTE["gold"]), None)

def render_scene_6_ending(img, draw, t, dur):
    """结尾——饼中自有千年 (57-62s)"""
    p = min(1.0, t/dur)

    # 典雅暗底
    for y in range(H):
        bg = blend((12,6,2), (25,12,4), y/H)
        draw.line([(0,y),(W,y)], fill=color_str(bg))

    # 装饰金线
    for i in range(3):
        line_y = 80 + i*30
        a = 100 - i*30
        draw.line([(W*0.2, line_y), (W*0.8, line_y)], fill=color_str((a,a*0.7,a*0.3)), width=1)
        draw.line([(W*0.2, H-line_y), (W*0.8, H-line_y)], fill=color_str((a,a*0.7,a*0.3)), width=1)

    # 中心：金边馍
    mo_cx, mo_cy = W//2, H//2-30
    mo_size = 110 + math.sin(t*0.6)*15

    # 外发光
    for r in range(6,0,-1):
        glow_r = mo_size*(1.2 + r*0.07)
        glow_a = int(80*(7-r)/7)
        glow_c = blend(PALETTE["gold"], (40,20,5), r/6)
        safe_ellipse(draw, [mo_cx-glow_r, mo_cy-glow_r*0.55, mo_cx+glow_r, mo_cy+glow_r*0.55],
                    fill=color_str(glow_c), outline=None)

    draw_mo(draw, mo_cx, mo_cy, int(mo_size), t)

    # 环绕金色粒子
    for i in range(40):
        a = t*2.5 + i*math.pi*2/40
        r = mo_size*1.4 + math.sin(t*4+i)*25
        px = mo_cx + math.cos(a)*r
        py = mo_cy + math.sin(a)*r*0.55
        ps = 1 + abs(math.sin(t*5+i))*2.5
        safe_ellipse(draw, [px-ps, py-ps, px+ps, py+ps], fill=color_str(PALETTE["gold"]))

    # 上升蒸汽粒子
    for i in range(30):
        sx = mo_cx + math.sin(t*2.5+i*0.7)*200
        sy = mo_cy - 60 - (t*40 + i*10)%(H*0.9)
        ss = 1.5 + math.sin(t*3+i)*2
        safe_ellipse(draw, [sx-ss, sy-ss, sx+ss, sy+ss], fill=color_str((255,240,220)))

    # 标题
    draw_text_with_glow(draw, "咬一口 · 千年历史", W//2, H//2+100, 48,
                      color_str(PALETTE["gold"]), color_str((60,30,10)))
    draw_text_with_glow(draw, "肉夹馍 — 最中国的汉堡", W//2, H//2+155, 26,
                      color_str(PALETTE["cream"]), None)

    # 底部小字
    draw.text((W//2, H-30), "Made with AI · Animation Creator v0.3",
             fill=color_str((150,120,80)), anchor="mm", font=get_font("msyh", 12))

# ====== 主渲染 ======

SCENES = [
    (0, 7, render_scene_0_title, "片头标题"),
    (7, 16, render_scene_1_qin, "秦朝起源"),
    (16, 27, render_scene_2_war, "战国军粮"),
    (27, 38, render_scene_3_tang, "唐朝长安"),
    (38, 49, render_scene_4_shaanxi, "陕西名小吃"),
    (49, 57, render_scene_5_world, "走向世界"),
    (57, 62, render_scene_6_ending, "结尾"),
]

def render_all():
    frames = []
    for frame_idx in range(TOTAL):
        t = frame_idx/FPS
        img = Image.new("RGB", (W, H), color_str(PALETTE["bg_deep"]))
        draw = ImageDraw.Draw(img)

        # 找到场景
        current = SCENES[-1]
        for sc_start, sc_end, sc_fn, sc_name in SCENES:
            if sc_start <= t < sc_end:
                current = (sc_start, sc_end, sc_fn, sc_name)
                break

        sc_start, sc_end, sc_fn, sc_name = current
        sc_t = t - sc_start

        # 场景间交叉淡入淡出
        sc_fn(img, draw, sc_t, sc_end-sc_start)

        # 过渡叠加
        for prev_start, prev_end, prev_fn, prev_name in SCENES:
            if sc_start == prev_start:
                continue
            # 上一场景结束后的 0.5s 交叉
            if sc_start - 0.5 <= t < sc_start:
                overlap = 1.0 - (sc_start - t)/0.5
                overlay = Image.new("RGBA", (W, H), (0,0,0,0))
                ov_draw = ImageDraw.Draw(overlay)
                prev_t = (prev_end - prev_start - 1 + overlap)
                prev_fn(overlay, ov_draw, prev_t, prev_end-prev_start)
                # 简单透明度混合
                alpha = int(overlap*255)
                overlay.putalpha(alpha)
                img_rgba = img.convert("RGBA")
                img = Image.alpha_composite(img_rgba, overlay).convert("RGB")
                draw = ImageDraw.Draw(img)
                break

        # 进度条
        bar_y = H-6
        bar_h = 3
        draw.rectangle([0, bar_y, W, bar_y+bar_h], fill=color_str((30,20,10)))
        draw.rectangle([0, bar_y, int(W*t/DURATION), bar_y+bar_h], fill=color_str(PALETTE["gold"]))

        frames.append(img)

        if frame_idx % (TOTAL//10) == 0:
            pct = frame_idx*100//TOTAL
            print(f"  [{pct:3d}%] {frame_idx}/{TOTAL} 帧 | {sc_name}")

    return frames

# ====== 主程序 ======
if __name__ == "__main__":
    out = Path("D:/龙虾文件/github-projects/animation-creator")
    print("="*60)
    print("  🎬 肉夹馍千年传奇 — AI 动画 v2 (高清版)")
    print(f"  {W}x{H} | {FPS}FPS | {DURATION}s | {TOTAL}帧")
    print("="*60)
    for s,e,_,n in SCENES: print(f"  {s:2d}s-{e:2d}s : {n}")
    print("\n  🎨 渲染中...")

    frames = render_all()
    print(f"\n  ✅ {len(frames)} 帧完成")

    # MP4
    print("  💾 MP4...")
    from animation_creator.exporter import export_video, export_gif
    mp4 = str(out/"roujiamo_history_v2.mp4")
    try:
        export_video(frames, mp4, FPS, quality=5)
        print(f"  ✅ {mp4}")
    except Exception as e:
        print(f"  ⚠️ MP4失败: {e}")
        gif = str(out/"roujiamo_history_v2.gif")
        export_gif(frames, gif, FPS//2)
        print(f"  ✅ GIF: {gif}")

    # GIF
    print("  💾 GIF...")
    gif = str(out/"roujiamo_history_v2.gif")
    try:
        export_gif(frames, gif, FPS//2)
        print(f"  ✅ {gif}")
    except Exception as e:
        print(f"  ⚠️ GIF失败: {e}")

    # 缩略图
    thumb = str(out/"roujiamo_v2_thumb.png")
    frames[TOTAL//3].save(thumb)
    print(f"  ✅ {thumb}")
    print("\n🎉 完成!")

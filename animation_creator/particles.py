"""
粒子系统 (Particle System)
真实的粒子物理模拟引擎，支持火焰、烟雾、雨、雪、爆炸、闪光、气泡等效果。
纯本地物理计算。
"""

import random
import math
from typing import List, Dict, Any, Optional


class Particle:
    """单个粒子"""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 life: float, max_life: float, color: str, size: float,
                 gravity: float = 0.0, fade_out: bool = True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = max_life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.fade_out = fade_out
        self.alive = True

    def update(self, dt: float):
        """更新粒子状态"""
        if not self.alive:
            return

        # 重力
        self.vy += self.gravity * dt

        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 减小生命
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def to_dict(self) -> Dict[str, Any]:
        """转为渲染元素"""
        if not self.alive:
            return None

        life_ratio = max(0, self.life / self.max_life)
        opacity = float(life_ratio) if self.fade_out else 1.0
        size = float(self.size * (0.3 + 0.7 * life_ratio))

        return {
            "type": "circle",
            "x": float(self.x),
            "y": float(self.y),
            "size": size,
            "color": self.color,
            "opacity": opacity,
        }


class ParticleSystem:
    """粒子系统主类"""

    EFFECT_TYPES = ["fire", "smoke", "rain", "snow", "explosion",
                   "sparkle", "bubble", "confetti", "rocket_trail"]

    def __init__(self, effect_type: str = "fire", count: int = 500,
                 width: int = 800, height: int = 600):
        """
        Args:
            effect_type: 粒子效果类型
            count: 粒子最大数量
            width/height: 画布尺寸
        """
        self.effect_type = effect_type
        self.max_count = count
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.age = 0.0  # 系统已运行时间(秒)

        # 效果特定参数
        self._setup_effect(effect_type)

    def _setup_effect(self, effect_type: str):
        """根据效果类型设置参数"""
        configs = {
            "fire": {
                "emit_rate": 80,     # 每秒新粒子数
                "max_life": (0.3, 1.5),
                "vx_range": (-30, 30),
                "vy_range": (-180, -60),
                "gravity": -40.0,     # 上升
                "size_range": (3, 15),
                "colors": ["#ff4500", "#ff6600", "#ff8800", "#ffcc00", "#ff2200"],
                "origin": (self.width / 2, self.height - 30),
                "spread": (60, 10),
            },
            "smoke": {
                "emit_rate": 30,
                "max_life": (1.5, 4.0),
                "vx_range": (-20, 20),
                "vy_range": (-60, -20),
                "gravity": -10.0,
                "size_range": (10, 40),
                "colors": ["#666666", "#888888", "#aaaaaa", "#cccccc"],
                "origin": (self.width / 2, self.height - 30),
                "spread": (40, 10),
            },
            "rain": {
                "emit_rate": 200,
                "max_life": (0.8, 2.0),
                "vx_range": (-10, 10),
                "vy_range": (300, 600),
                "gravity": 100.0,
                "size_range": (1, 3),
                "colors": ["#4488cc", "#5599dd", "#6699ee", "#3377bb"],
                "origin": (self.width / 2, -20),
                "spread": (self.width / 2, 0),
            },
            "snow": {
                "emit_rate": 80,
                "max_life": (4.0, 10.0),
                "vx_range": (-20, 20),
                "vy_range": (20, 60),
                "gravity": 5.0,
                "size_range": (2, 8),
                "colors": ["#ffffff", "#eeeeff", "#f8f8ff", "#e8e8f8"],
                "origin": (self.width / 2, -20),
                "spread": (self.width / 2, 0),
            },
            "explosion": {
                "emit_rate": 500,     # 一次性大量
                "max_life": (0.5, 2.0),
                "vx_range": (-300, 300),
                "vy_range": (-300, 300),
                "gravity": 50.0,
                "size_range": (2, 10),
                "colors": ["#ff4400", "#ff8800", "#ffcc00", "#ffffff", "#ff2200"],
                "origin": (self.width / 2, self.height / 2),
                "spread": (0, 0),
                "one_shot": True,
            },
            "sparkle": {
                "emit_rate": 60,
                "max_life": (0.2, 1.0),
                "vx_range": (-50, 50),
                "vy_range": (-50, 50),
                "gravity": 0,
                "size_range": (1, 6),
                "colors": ["#ffdd00", "#ffffff", "#ffaa00", "#ffff88", "#ff8800"],
                "origin": (self.width / 2, self.height / 2),
                "spread": (100, 100),
            },
            "bubble": {
                "emit_rate": 20,
                "max_life": (1.5, 3.0),
                "vx_range": (-20, 20),
                "vy_range": (-80, -20),
                "gravity": -20.0,
                "size_range": (5, 25),
                "colors": ["#88ccff", "#aaddff", "#cceeff", "#99ddff"],
                "origin": (self.width / 2, self.height + 10),
                "spread": (80, 0),
            },
            "confetti": {
                "emit_rate": 100,
                "max_life": (1.5, 4.0),
                "vx_range": (-100, 100),
                "vy_range": (-200, 0),
                "gravity": 80.0,
                "size_range": (4, 12),
                "colors": ["#ff2244", "#ff8800", "#ffdd00", "#44ff44",
                          "#4488ff", "#cc44ff", "#ff66aa", "#00ccff"],
                "origin": (self.width / 2, -50),
                "spread": (self.width / 3, 0),
            },
            "rocket_trail": {
                "emit_rate": 100,
                "max_life": (0.2, 0.8),
                "vx_range": (-10, 10),
                "vy_range": (30, 80),
                "gravity": 0,
                "size_range": (2, 8),
                "colors": ["#ff4400", "#ff6600", "#ffaa00", "#ffffff"],
                "origin": (self.width / 2, self.height - 20),
                "spread": (5, 5),
            },
        }

        if effect_type not in configs:
            effect_type = "fire"

        cfg = configs[effect_type]
        self.emit_rate = cfg["emit_rate"]
        self.max_life_range = cfg["max_life"]
        self.vx_range = cfg["vx_range"]
        self.vy_range = cfg["vy_range"]
        self.gravity = cfg["gravity"]
        self.size_range = cfg["size_range"]
        self.colors = cfg["colors"]
        self.origin = cfg["origin"]
        self.spread = cfg["spread"]
        self.one_shot = cfg.get("one_shot", False)

        # 用于跟踪发射时间
        self._emit_accumulator = 0.0
        self._one_shot_done = False

    def update(self, dt: float):
        """更新整个粒子系统

        Args:
            dt: 时间步长(秒)，通常 1/fps
        """
        self.age += dt

        # 发射新粒子
        self._emit_particles(dt)

        # 更新所有粒子
        for p in self.particles:
            p.update(dt)

        # 移除死亡的粒子
        self.particles = [p for p in self.particles if p.alive]

    def _emit_particles(self, dt: float):
        """根据发射速率产生新粒子"""
        if self.one_shot:
            if self._one_shot_done:
                return
            count = self.emit_rate
            self._one_shot_done = True
        else:
            self._emit_accumulator += self.emit_rate * dt
            count = int(self._emit_accumulator)
            self._emit_accumulator -= count

        for _ in range(count):
            if len(self.particles) >= self.max_count:
                # 移除最老的粒子为新粒子腾空间
                if self.particles:
                    self.particles.pop(0)

            max_life = random.uniform(*self.max_life_range)
            particle = Particle(
                x=self.origin[0] + random.uniform(-self.spread[0], self.spread[0]),
                y=self.origin[1] + random.uniform(-self.spread[1], self.spread[1]),
                vx=random.uniform(*self.vx_range),
                vy=random.uniform(*self.vy_range),
                life=max_life,
                max_life=max_life,
                color=random.choice(self.colors),
                size=random.uniform(*self.size_range),
                gravity=self.gravity,
                fade_out=True,
            )
            self.particles.append(particle)

    def get_active_particles(self) -> List[Dict[str, Any]]:
        """获取所有存活粒子的渲染元素列表"""
        elements = []
        for p in self.particles:
            el = p.to_dict()
            if el is not None:
                elements.append(el)
        return elements

    def is_finished(self) -> bool:
        """检查系统是否已运行完毕（所有粒子死亡且不再产新）"""
        if not self.one_shot:
            return False  # 连续效果永不结束
        return self._one_shot_done and len(self.particles) == 0

    def particle_count(self) -> int:
        """当前活跃粒子数"""
        return len(self.particles)


def create_particle_system(effect: str, count: int = 500,
                          width: int = 800, height: int = 600) -> ParticleSystem:
    """创建粒子系统的便捷函数"""
    return ParticleSystem(effect, count, width, height)


def simulate_particles_frames(system: ParticleSystem, duration: float,
                             fps: int = 30) -> List[Dict[str, Any]]:
    """模拟粒子系统并返回所有帧的数据

    Args:
        system: 粒子系统
        duration: 模拟时长(秒)
        fps: 帧率

    Returns:
        帧数据列表，每帧是 {index, time, elements} dict
    """
    total_frames = int(duration * fps)
    dt = 1.0 / fps
    frames = []

    for i in range(total_frames):
        system.update(dt)

        if system.is_finished() and len(system.particles) == 0:
            break

        frames.append({
            "index": i,
            "time": i * dt,
            "elements": system.get_active_particles(),
        })

    return frames

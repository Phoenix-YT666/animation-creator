"""
🎬 动画制作工具 - 主入口
AI-powered animation creation tool with keyframe, skeleton, particles and AI assistance.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from animation_creator.engine import AnimationEngine


def main():
    parser = argparse.ArgumentParser(
        description="🎬 AI动画制作工具 - Animation Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 (Examples):
  # 文本生成动画 (Text-to-animation)
  python main.py create "一个红色爱心从屏幕中央放大并旋转飞出" -o heart.mp4

  # 使用预设模板 (Use preset)
  python main.py preset fire_particle -o fire.mp4

  # 骨骼动画 (Skeleton animation)
  python main.py skeleton walk --character human -o walk.gif

  # 启动交互模式 (Interactive mode)
  python main.py interactive
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # === create: AI 文本生成动画 ===
    create_parser = subparsers.add_parser("create", help="用自然语言描述创建动画")
    create_parser.add_argument("prompt", help="动画描述 (中文/English)")
    create_parser.add_argument("-o", "--output", default="output.mp4", help="输出文件路径")
    create_parser.add_argument("-d", "--duration", type=float, default=3.0, help="时长(秒)")
    create_parser.add_argument("--fps", type=int, default=30, help="帧率")
    create_parser.add_argument("--width", type=int, default=800, help="画布宽度")
    create_parser.add_argument("--height", type=int, default=600, help="画布高度")
    create_parser.add_argument("--bg-color", default="#1a1a2e", help="背景色")

    # === preset: 使用预设模板 ===
    preset_parser = subparsers.add_parser("preset", help="使用预设动画模板")
    preset_parser.add_argument("name", help="预设名称")
    preset_parser.add_argument("-o", "--output", default="output.mp4")
    preset_parser.add_argument("--fps", type=int, default=30)
    preset_parser.add_argument("--list", action="store_true", help="列出所有可用预设")

    # === skeleton: 骨骼动画 ===
    skeleton_parser = subparsers.add_parser("skeleton", help="骨骼动画")
    skeleton_parser.add_argument("action", choices=["walk", "run", "jump", "wave", "idle", "dance"])
    skeleton_parser.add_argument("--character", default="human", help="角色类型")
    skeleton_parser.add_argument("-o", "--output", default="skeleton.gif")
    skeleton_parser.add_argument("--fps", type=int, default=24)
    skeleton_parser.add_argument("--loop", action="store_true", help="循环播放")

    # === particles: 粒子特效 ===
    particles_parser = subparsers.add_parser("particles", help="粒子特效")
    particles_parser.add_argument("effect", choices=["fire", "smoke", "rain", "snow", "explosion", "sparkle", "bubble"])
    particles_parser.add_argument("-o", "--output", default="particles.mp4")
    particles_parser.add_argument("-d", "--duration", type=float, default=2.0)
    particles_parser.add_argument("--fps", type=int, default=30)
    particles_parser.add_argument("--count", type=int, default=500, help="粒子数量")

    # === interactive: 交互模式 ===
    interactive_parser = subparsers.add_parser("interactive", help="进入交互式创作模式")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    engine = AnimationEngine()

    if args.command == "create":
        print(f"🎨 正在根据描述生成动画: {args.prompt}")
        result = engine.create_animation(
            prompt=args.prompt,
            output=args.output,
            duration=args.duration,
            fps=args.fps,
            width=args.width,
            height=args.height,
            bg_color=args.bg_color,
        )
        print(f"✅ 动画已保存到: {result}")

    elif args.command == "preset":
        if hasattr(args, 'list') and args.list:
            engine.list_presets()
        else:
            print(f"📦 加载预设模板: {args.name}")
            result = engine.apply_preset(args.name, output=args.output, fps=args.fps)
            print(f"✅ 动画已保存到: {result}")

    elif args.command == "skeleton":
        print(f"🦴 生成骨骼动画: {args.action}")
        result = engine.skeleton_animation(
            action=args.action,
            character=args.character,
            output=args.output,
            fps=args.fps,
            loop=getattr(args, 'loop', False),
        )
        print(f"✅ 动画已保存到: {result}")

    elif args.command == "particles":
        print(f"💥 生成粒子特效: {args.effect}")
        result = engine.particle_effect(
            effect=args.effect,
            output=args.output,
            duration=args.duration,
            fps=args.fps,
            count=args.count,
        )
        print(f"✅ 动画已保存到: {result}")

    elif args.command == "interactive":
        print("🚀 启动交互式动画创作模式...")
        engine.interactive_mode()


if __name__ == "__main__":
    main()

"""
视频导出模块 (Exporter)
将帧序列导出为 MP4 / GIF / WebM / APNG 格式。
使用 imageio + Pillow 实现实际文件写入。
"""

from pathlib import Path
from typing import List, Optional
import tempfile

import numpy as np
from PIL import Image
import imageio


def export_video(frames: List[Image.Image], output_path: str,
                fps: int = 30, codec: str = "libx264",
                quality: int = 8) -> str:
    """将帧序列导出为 MP4 视频

    Args:
        frames: PIL Image 列表
        output_path: 输出文件路径 (.mp4)
        fps: 帧率
        codec: 视频编码器 (libx264=h.264, mpeg4, h264_nvenc)
        quality: 质量 (1-10, 越低越好)

    Returns:
        输出文件的绝对路径
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not frames:
        raise ValueError("帧列表为空，无法导出视频")

    # 将 PIL Images 转为 numpy arrays
    frame_arrays = [np.array(frame.convert("RGB")) for frame in frames]

    # 使用 imageio + ffmpeg 写入
    writer = imageio.get_writer(
        output_path,
        fps=fps,
        codec=codec,
        quality=quality,
        macro_block_size=None,  # 自动
    )

    try:
        for frame in frame_arrays:
            writer.append_data(frame)
    finally:
        writer.close()

    return str(output_path.absolute())


def export_gif(frames: List[Image.Image], output_path: str,
              fps: int = 24, loop: int = 0, optimize: bool = True) -> str:
    """将帧序列导出为 GIF 动画

    Args:
        frames: PIL Image 列表
        output_path: 输出文件路径 (.gif)
        fps: 帧率
        loop: 循环次数 (0=无限循环)
        optimize: 是否优化(减小文件大小)

    Returns:
        输出文件的绝对路径
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not frames:
        raise ValueError("帧列表为空，无法导出 GIF")

    # 计算每帧持续时间(毫秒)
    duration = int(1000 / fps)

    # 转为调色板模式以减小文件
    gif_frames = []
    for frame in frames:
        if frame.mode != "P":
            gif_frame = frame.convert("P", palette=Image.ADAPTIVE, colors=256)
        else:
            gif_frame = frame
        gif_frames.append(gif_frame)

    # 保存
    gif_frames[0].save(
        output_path,
        format="GIF",
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration,
        loop=loop,
        optimize=optimize,
        disposal=2,  # 每帧清除
    )

    return str(output_path.absolute())


def export_apng(frames: List[Image.Image], output_path: str,
               fps: int = 30, loop: int = 0) -> str:
    """将帧序列导出为 APNG (Animated PNG)

    Note: Pillow 的原生 APNG 支持有限。
    这里使用 PNG 序列 + 保存为 PNG（单帧）作为降级方案。
    对于真正的 APNG，推荐使用 apng 库或 PIL 的 save_all。
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not frames:
        raise ValueError("帧列表为空")

    duration = int(1000 / fps)

    try:
        # Pillow >= 9.0 支持 save_all for PNG (APNG)
        frames[0].save(
            output_path,
            format="PNG",
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=loop,
        )
    except (ValueError, TypeError):
        # 降级：保存第一帧为静态 PNG
        frames[0].save(output_path, format="PNG")

    return str(output_path.absolute())


def export_image_sequence(frames: List[Image.Image], output_dir: str,
                         prefix: str = "frame", fmt: str = "png") -> List[str]:
    """导出帧为图片序列

    Args:
        frames: PIL Image 列表
        output_dir: 输出目录
        prefix: 文件名前缀
        fmt: 图片格式 (png/jpg)

    Returns:
        输出文件路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for i, frame in enumerate(frames):
        path = output_dir / f"{prefix}_{i:05d}.{fmt}"
        frame.save(path)
        saved.append(str(path.absolute()))

    return saved


def make_thumbnail(input_path: str, output_path: str,
                  size: tuple = (320, 240), time: float = 0.0) -> str:
    """从视频文件提取缩略图

    Args:
        input_path: 视频文件路径
        output_path: 输出缩略图路径
        size: 缩略图尺寸
        time: 提取时间点(秒)

    Returns:
        缩略图路径
    """
    reader = imageio.get_reader(input_path)
    try:
        frame_idx = int(time * reader.get_meta_data().get("fps", 30))
        frame_idx = min(frame_idx, reader.count_frames() - 1)
        frame = reader.get_data(frame_idx)
        img = Image.fromarray(frame)
        img.thumbnail(size, Image.LANCZOS)
        img.save(output_path)
    finally:
        reader.close()

    return output_path

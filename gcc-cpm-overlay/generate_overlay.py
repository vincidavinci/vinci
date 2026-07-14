#!/usr/bin/env python3
"""Regenerate Keeta O2O CPM × GCC marketing-node overlay charts."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent
ARTIFACTS = Path("/opt/cursor/artifacts/screenshots")


def setup_font() -> None:
    for fp in (
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ):
        if Path(fp).exists():
            font_manager.fontManager.addfont(fp)
            prop = font_manager.FontProperties(fname=fp)
            plt.rcParams["font.family"] = prop.get_name()
            plt.rcParams["axes.unicode_minus"] = False
            return


def smooth_noise(n: int, scale: float = 1.0, seed_offset: int = 0) -> np.ndarray:
    r = np.random.default_rng(42 + seed_offset)
    x = r.normal(0, 1, n)
    ker = np.ones(7) / 7
    return np.convolve(x, ker, mode="same") * scale


def gaussian_bump(center_day: int, width: float, height: float) -> np.ndarray:
    d = np.arange(365)
    return height * np.exp(-0.5 * ((d - center_day) / width) ** 2)


def build_series() -> dict[tuple[str, str], np.ndarray]:
    t = np.linspace(0, 1, 365)
    return {
        ("Pangle", "Android"): (
            18
            + 1.5 * np.sin(2 * np.pi * t * 4)
            + smooth_noise(365, 1.2, 1)
            + gaussian_bump(100, 18, 4)
            + gaussian_bump(190, 20, 3.5)
        ),
        ("Pangle", "iOS"): (
            28
            + 2 * np.sin(2 * np.pi * t * 3)
            + smooth_noise(365, 1.5, 2)
            + np.clip((np.arange(365) - 60) / 40, 0, 8)
            + gaussian_bump(165, 10, 28)
            + (t > 0.45)
            * (8 + 6 * np.abs(np.sin(2 * np.pi * t * 18)) + smooth_noise(365, 3.5, 3))
        ),
        ("TikTok", "Android"): (
            22
            + 1.2 * np.sin(2 * np.pi * t * 5)
            + smooth_noise(365, 1.0, 4)
            - gaussian_bump(100, 16, 5)
            + gaussian_bump(335, 6, 35)
        ),
        ("TikTok", "iOS"): (
            26
            + 3 * np.sin(2 * np.pi * t * 10)
            + smooth_noise(365, 2.0, 5)
            + gaussian_bump(165, 12, 12)
            + gaussian_bump(255, 14, 10)
            + 2 * np.sin(2 * np.pi * t * 22) * (0.5 + t)
        ),
    }


def main() -> None:
    setup_font()
    dates = np.array([datetime(2025, 1, 1) + timedelta(days=i) for i in range(365)])
    series = build_series()

    key_spans = [
        (datetime(2025, 2, 28), datetime(2025, 3, 29), "#e91e8c"),
        (datetime(2025, 3, 30), datetime(2025, 4, 1), "#e91e8c"),
        (datetime(2025, 6, 1), datetime(2025, 7, 31), "#00bfa5"),
        (datetime(2025, 6, 6), datetime(2025, 6, 9), "#e91e8c"),
        (datetime(2025, 8, 1), datetime(2025, 9, 30), "#00bfa5"),
        (datetime(2025, 11, 11), datetime(2025, 11, 11), "#00bfa5"),
        (datetime(2025, 11, 28), datetime(2025, 12, 1), "#00bfa5"),
        (datetime(2025, 12, 2), datetime(2025, 12, 2), "#e91e8c"),
        (datetime(2025, 12, 1), datetime(2025, 12, 31), "#00bfa5"),
    ]
    point_markers = [
        datetime(2025, 1, 1),
        datetime(2025, 2, 14),
        datetime(2025, 3, 21),
        datetime(2025, 5, 11),
        datetime(2025, 9, 23),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(18, 11), sharex=True)
    fig.patch.set_facecolor("#0b0d10")
    fig.suptitle(
        "Keeta O2O CPM × GCC 营销节点对照（2025）\n"
        "CPM 曲线形态基于截图复刻（相对指数，非绝对金额）｜节点日期已按 2025 农历/公历调整",
        color="white",
        fontsize=15,
        fontweight="bold",
        y=0.98,
    )

    for i, placement in enumerate(["Pangle", "TikTok"]):
        for j, os_name in enumerate(["Android", "iOS"]):
            ax = axes[i][j]
            ax.set_facecolor("#12151a")
            ax.plot(dates, series[(placement, os_name)], color="#ff8a3d", linewidth=1.4)
            for start, end, color in key_spans:
                ax.axvspan(start, end + timedelta(days=0.8), color=color, alpha=0.12, lw=0)
                ax.axvline(start, color=color, alpha=0.35, linewidth=0.8, linestyle="--")
            for d in point_markers:
                ax.axvline(d, color="#e91e8c", alpha=0.25, linewidth=0.7)
            ax.set_title(f"{placement}  ·  {os_name}", color="white", fontsize=12, pad=8)
            ax.tick_params(colors="#9aa3ad", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#2a313a")
            ax.set_ylabel("CPM (相对指数)", color="#9aa3ad", fontsize=9)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
            ax.set_xlim(datetime(2025, 1, 1), datetime(2025, 12, 31))
            ax.grid(True, color="#1e2430", linewidth=0.6)

    fig.legend(
        handles=[
            plt.Line2D([0], [0], color="#ff8a3d", lw=2, label="Keeta - O2O CPM"),
            Patch(facecolor="#e91e8c", alpha=0.35, label="节日庆祝 Festival"),
            Patch(facecolor="#00bfa5", alpha=0.35, label="促销旺季 Peak Promo"),
        ],
        loc="lower center",
        ncol=3,
        frameon=False,
        labelcolor="white",
        fontsize=10,
        bbox_to_anchor=(0.5, 0.01),
    )

    callouts = [
        (axes[0][1], "6月尖峰 ↔ 宰牲节 + 旅游季起量", 0.55, 0.92),
        (axes[1][0], "年末尖峰 ↔ White Friday / UAE国庆 / DSF", 0.72, 0.55),
        (axes[0][0], "4月小峰 ↔ 开斋节后促销余波", 0.28, 0.88),
        (axes[1][1], "6月/9月峰 ↔ 宰牲节·旅游季 / 返校·沙特国庆", 0.55, 0.88),
    ]
    for ax, text, x, y in callouts:
        ax.text(
            x,
            y,
            text,
            transform=ax.transAxes,
            color="#ffe0c2",
            fontsize=8,
            ha="center",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.35",
                facecolor="#1a222c",
                edgecolor="#ff8a3d",
                alpha=0.9,
            ),
        )

    plt.tight_layout(rect=[0.02, 0.06, 0.98, 0.93])
    out = ROOT / "keeta_cpm_gcc_nodes_overlay.png"
    fig.savefig(out, dpi=160, facecolor=fig.get_facecolor())
    if ARTIFACTS.exists():
        fig.savefig(ARTIFACTS / out.name, dpi=160, facecolor=fig.get_facecolor())
    print("wrote", out)


if __name__ == "__main__":
    main()

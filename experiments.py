#!/usr/bin/env python3
"""Эксперименты с порогом поддержки и визуализация результатов."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

from apriori import apriori, load_transactions, sort_itemsets, format_itemset
import time


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "baskets.csv"
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"

SUPPORTS = [0.01, 0.03, 0.05, 0.10, 0.15]


def run_experiments() -> list[dict]:
    transactions = load_transactions(str(DATA))
    n_tx = len(transactions)
    rows: list[dict] = []

    for minsup in SUPPORTS:
        t0 = time.perf_counter()
        found = apriori(transactions, minsup)
        elapsed = time.perf_counter() - t0

        by_len: dict[int, int] = defaultdict(int)
        for itemset, _ in found:
            by_len[len(itemset)] += 1

        sorted_found = sort_itemsets(found, "support")
        preview = [
            {"itemset": sorted(itemset), "support": supp}
            for itemset, supp in sorted_found[:20]
        ]

        row = {
            "min_support": minsup,
            "min_support_pct": f"{minsup * 100:.0f}%",
            "n_transactions": n_tx,
            "n_itemsets": len(found),
            "time_sec": elapsed,
            "by_length": dict(sorted(by_len.items())),
            "top20_by_support": preview,
        }
        rows.append(row)

        out_path = RESULTS / f"itemsets_support_{int(minsup * 100):02d}.txt"
        with out_path.open("w", encoding="utf-8") as f:
            f.write(f"min_support={minsup}\n")
            f.write(f"n_itemsets={len(found)}\n")
            f.write(f"time_sec={elapsed:.6f}\n")
            f.write("набор\tподдержка\n")
            for itemset, supp in sorted_found:
                f.write(f"{format_itemset(itemset)}\t{supp:.6f}\n")

        print(
            f"support={minsup:.2f}: {len(found)} наборов, "
            f"{elapsed:.3f} с, длины={dict(by_len)}"
        )

    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    return rows


def plot_runtime(rows: list[dict]) -> None:
    xs = [r["min_support"] * 100 for r in rows]
    ys = [r["time_sec"] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(xs, ys, marker="o", linewidth=2)
    ax.set_xlabel("Порог поддержки, %")
    ax.set_ylabel("Время работы, с")
    ax.set_title("Быстродействие Apriori при изменении порога поддержки")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(FIGURES / "runtime_vs_support.png", dpi=150)
    plt.close(fig)


def plot_counts_by_length(rows: list[dict]) -> None:
    lengths = sorted({k for r in rows for k in map(int, r["by_length"].keys())})
    x = range(len(rows))
    width = 0.8 / max(len(lengths), 1)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, length in enumerate(lengths):
        ys = [r["by_length"].get(str(length), r["by_length"].get(length, 0)) for r in rows]
        offset = (i - (len(lengths) - 1) / 2) * width
        ax.bar([xi + offset for xi in x], ys, width=width, label=f"длина {length}")
    ax.set_xticks(list(x))
    ax.set_xticklabels([r["min_support_pct"] for r in rows])
    ax.set_xlabel("Порог поддержки")
    ax.set_ylabel("Число частых наборов")
    ax.set_title("Количество частых наборов разной длины")
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig(FIGURES / "itemsets_by_length.png", dpi=150)
    plt.close(fig)


def main() -> None:
    plt.rcParams["font.family"] = "DejaVu Sans"
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows = run_experiments()
    plot_runtime(rows)
    plot_counts_by_length(rows)
    print(f"Графики сохранены в {FIGURES}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Поиск частых наборов объектов алгоритмом Apriori."""

from __future__ import annotations

import argparse
import csv
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from typing import Iterable


Itemset = frozenset[str]


def load_transactions(path: str, encoding: str = "cp1251") -> list[set[str]]:
    """Читает транзакции: каждая строка CSV — набор товаров в одной покупке."""
    transactions: list[set[str]] = []
    with open(path, "r", encoding=encoding, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            items = {item.strip() for item in row if item and item.strip()}
            if items:
                transactions.append(items)
    return transactions


def _join_candidates(prev: list[Itemset], k: int) -> list[Itemset]:
    """Генерация кандидатов C_k соединением частых наборов длины k-1."""
    prev_sorted = [tuple(sorted(s)) for s in prev]
    prev_sorted.sort()
    candidates: list[Itemset] = []
    n = len(prev_sorted)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = prev_sorted[i], prev_sorted[j]
            if a[: k - 2] != b[: k - 2]:
                break
            union = a + (b[-1],)
            candidates.append(frozenset(union))
    return candidates


def _prune_candidates(
    candidates: list[Itemset], prev_set: set[Itemset], k: int
) -> list[Itemset]:
    """Отбрасывает кандидатов, у которых есть нечастый (k-1)-поднабор."""
    kept: list[Itemset] = []
    for cand in candidates:
        if all(frozenset(subset) in prev_set for subset in combinations(cand, k - 1)):
            kept.append(cand)
    return kept


def apriori(
    transactions: list[set[str]],
    min_support: float,
) -> list[tuple[Itemset, float]]:
    """
    Ищет частые наборы.

    min_support — относительная поддержка в (0, 1], например 0.05 = 5%.
    Возвращает список пар (набор, поддержка).
    """
    if not 0 < min_support <= 1:
        raise ValueError("min_support должен быть в интервале (0, 1]")

    n_tx = len(transactions)
    min_count = min_support * n_tx

    item_counts: Counter[str] = Counter()
    for t in transactions:
        item_counts.update(t)

    frequent: dict[Itemset, float] = {}
    l_k: dict[Itemset, int] = {
        frozenset([item]): cnt for item, cnt in item_counts.items() if cnt >= min_count
    }
    for itemset, cnt in l_k.items():
        frequent[itemset] = cnt / n_tx

    frequent_items = {next(iter(s)) for s in l_k}
    filtered = [{item for item in t if item in frequent_items} for t in transactions]

    k = 2
    while l_k:
        prev_list = list(l_k.keys())
        prev_set = set(prev_list)
        candidates = _prune_candidates(_join_candidates(prev_list, k), prev_set, k)
        if not candidates:
            break

        cand_set = set(candidates)
        counts: dict[Itemset, int] = defaultdict(int)
        for t in filtered:
            if len(t) < k:
                continue
            for cand in combinations(sorted(t), k):
                fs = frozenset(cand)
                if fs in cand_set:
                    counts[fs] += 1

        l_k = {itemset: cnt for itemset, cnt in counts.items() if cnt >= min_count}
        for itemset, cnt in l_k.items():
            frequent[itemset] = cnt / n_tx
        k += 1

    return [(itemset, supp) for itemset, supp in frequent.items()]


def sort_itemsets(
    itemsets: Iterable[tuple[Itemset, float]],
    order: str,
) -> list[tuple[Itemset, float]]:
    if order == "support":
        return sorted(itemsets, key=lambda x: (-x[1], tuple(sorted(x[0]))))
    if order == "lex":
        return sorted(itemsets, key=lambda x: (tuple(sorted(x[0])), -x[1]))
    raise ValueError("order должен быть 'support' или 'lex'")


def format_itemset(itemset: Itemset) -> str:
    return "{" + ", ".join(sorted(itemset)) + "}"


def parse_support(value: str) -> float:
    text = value.strip()
    if text.endswith("%"):
        return float(text[:-1].replace(",", ".")) / 100.0
    num = float(text.replace(",", "."))
    if num > 1:
        return num / 100.0
    return num


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Поиск частых наборов объектов алгоритмом Apriori."
    )
    parser.add_argument("--data", required=True, help="Путь к CSV с транзакциями")
    parser.add_argument(
        "--min-support",
        required=True,
        help="Порог поддержки: 0.05, 5 или 5%",
    )
    parser.add_argument(
        "--order",
        choices=("support", "lex"),
        default="support",
        help="Упорядочивание: по убыванию поддержки или лексикографическое",
    )
    parser.add_argument("--encoding", default="cp1251", help="Кодировка CSV")
    parser.add_argument("-o", "--output", help="Файл для сохранения результата")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    min_support = parse_support(args.min_support)
    transactions = load_transactions(args.data, encoding=args.encoding)

    started = time.perf_counter()
    found = apriori(transactions, min_support)
    elapsed = time.perf_counter() - started
    found = sort_itemsets(found, args.order)

    lines = [
        f"# транзакций: {len(transactions)}",
        f"# частых наборов: {len(found)}",
        f"min_support: {min_support:.4f}",
        f"порядок: {args.order}",
        f"время, с: {elapsed:.4f}",
        "набор\tподдержка",
    ]
    for itemset, supp in found:
        lines.append(f"{format_itemset(itemset)}\t{supp:.6f}")
    text = "\n".join(lines) + "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

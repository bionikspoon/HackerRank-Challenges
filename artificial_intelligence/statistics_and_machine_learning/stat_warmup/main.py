# coding=utf-8
from collections import namedtuple
from textwrap import dedent

import numpy as np
import sys

from scipy import stats

DescribeResult = namedtuple('DescribeResult', 'mean median mode std interval')


def describe(*args, C=1.96):
    data = np.array(args)
    mean, std = np.mean(data), np.std(data)
    interval = tuple(mean + constant * (std / np.sqrt(data.size)) for constant in [-C, C])
    return DescribeResult(
        mean=round(mean, 1),
        median=np.median(data),
        mode=np.min(stats.mode(data).mode),
        std=round(std, 1),
        interval=tuple(round(i, 1) for i in interval)
    )


def main():
    _ = sys.stdin.readline()
    data = [int(n) for n in sys.stdin.readline().strip().split(' ')]
    summary = describe(*data)

    print(dedent("""
        {0.mean:.1f}
        {0.median:.1f}
        {0.mode:d}
        {0.std:.1f}
        {0.interval[0]:.1f} {0.interval[1]:.1f}
    """)[1:-1].format(summary))


if __name__ == '__main__':
    main()

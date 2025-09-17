import matplotlib.pyplot as plt
import numpy as np


def plot_lob(df, label):
    n_rows = len(df)
    fig, axes = plt.subplots(n_rows, 1, figsize=(6, 2 * n_rows), sharex=False, sharey=False)

    # 把价格列和量列分别规整成 list，方便后面按顺序读取
    bid_prices = [f'bid_price_{i}' for i in range(1, 6)]
    bid_volumes = [f'bid_volume_{i}' for i in range(1, 6)]
    ask_prices = [f'ask_price_{i}' for i in range(1, 6)]
    ask_volumes = [f'ask_volume_{i}' for i in range(1, 6)]
    df.set_index('datetime', inplace=True)
    df = df.loc[:, bid_prices + bid_volumes + ask_prices + ask_volumes]
    assert df.isna().sum().sum() == 0

    # 如果只有一行，axes 会退化成一个 Axes，不是数组
    if n_rows == 1:
        axes = [axes]

    for idx, ax in enumerate(axes):
        # 取出该时间戳的买卖价量
        bp = df.loc[df.index[idx], bid_prices].values
        bv = df.loc[df.index[idx], bid_volumes].values
        ap = df.loc[df.index[idx], ask_prices].values
        av = df.loc[df.index[idx], ask_volumes].values

        # 绘制买量（红色，向右为正）
        ax.barh(bp, bv, color='red', height=0.8, label='Buy')
        # 绘制卖量（绿色，向左为负）
        ax.barh(ap, -av, color='green', height=0.8, label='Sell')

        # 在 y 轴上标出档位
        all_prices = np.unique(np.concatenate([bp, ap]))
        ax.set_yticks(all_prices)
        ax.set_yticklabels([f'{p:.2f}' for p in all_prices])

        # 美化
        ax.invert_yaxis()  # 价格高的在上面
        ax.grid(axis='x', linestyle='--', alpha=0.4)
        ax.axvline(0, color='black', linewidth=0.8)  # 零轴
        ax.set_title(f'Timestamp {df.index[idx]}, index {idx}')
        if idx == 0:
            ax.legend(loc='upper right')

    # 统一横轴标签
    fig.text(0.5, 0.04, f'Label {label}', ha='center', va='center')
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    plt.show()
    return fig
import japanize_matplotlib
import matplotlib.pyplot as plt


def plot_diff_by_y(y_train, y_train_pred, y_test, y_pred):
    if max(y_test.shape) <= 2:
        return
    # 予測値と残差をプロット（学習データ）
    plt.scatter(y_train,                   # グラフのx値(予測値)
                y_train_pred,   # グラフのy値(予測値と学習値の差)
                c='blue',                 # プロットの色
                marker='o',               # マーカーの種類
                s=40,                     # マーカーサイズ
                alpha=0.7,                # 透明度
                label='学習データ')         # ラベルの文字

    # 予測値と残差をプロット（テストデータ）
    plt.scatter(y_test,
                y_pred,
                c='red',
                marker='o',
                s=40,
                alpha=0.7,
                label='テストデータ')

    # グラフの書式設定
    plt.xlabel('正解データ')
    plt.ylabel('予測値')
    plt.legend(loc='upper left')
    # plt.hlines(y=0, xmin=-200, xmax=200, lw=2, color='black')
    plt.axline((0, 0), slope=1, color="black")
    plt.xlim([-20, 100])
    plt.ylim([-20, 100])
    plt.tight_layout()
    plt.show()


def plot_diff_by_x(X, feature, y, estimator):
    diffs = {
        "鼻から首元までの距離": [[], [], []],
        "スマートフォンの角度（度）": [[], [], []],
        "スマートフォンに対する顔の角度（度）": [[], [], []],
    }
    for j, f in enumerate(feature):
        yp = estimator.predict([f])[0]
        diff = yp - y[j]
        for i, key in enumerate(diffs.keys()):
            diffs[key][0].append(X[j][i])
            diffs[key][1].append(diff)
            diffs[key][2].append(X[j][1])
    for key, values in diffs.items():
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        im = ax.scatter(x=values[0], y=values[1], c=values[2], cmap="jet")
        fig.colorbar(im, ax=ax).set_label("正解データ（度）")
        plt.xlabel(key)
        plt.ylabel("予測残差（度）")
        plt.show()

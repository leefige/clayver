from extract import extract
from feature import getFeature
from sys import argv
from matplotlib import pyplot as plt
# from keras.layers import Conv1D

GROUP_SIZE = 10

# def balanceBias(windows:list):
#     total = len(windows)
#     groups = int(total / GROUP_SIZE)
#     noBias_min = []
#     noBias_mean = []
#     for i in range(groups):


if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: %s filename" % argv[0])
        exit(-1)

    filename = argv[1]
    windows = extract(filename)
    # windows = windows[15:]
    figs = []
    axs = []
    # for i in range (0, 6):
    #     fig, ax=plt.subplots()
    #     figs.append(fig)
    #     axs.append(ax)
    
    for i in range(0, 6):
        plt.subplot(2, 3, i+1)
        mi = []
        ma = []
        me = []
        idx = []
        cur = 0
        for win in windows:
            idx.append(cur)
            cur += 1
            mi.append(win.getMin(i))
            ma.append(win.getMax(i))
            me.append(win.getMean(i))
        plt.title(filename+"_%d"%i)
        plt.plot(idx, mi, "-c")
        plt.plot(idx, ma, "-m")
        plt.plot(idx, me, "-y")

    plt.show()
    getFeature(windows)

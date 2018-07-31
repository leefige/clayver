from extract import extract
from feature import getFeature
from sys import argv
from matplotlib import pyplot as plt

if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: %s filename" % argv[0])
        exit(-1)

    filename = argv[1]
    windows = extract(filename)
    windows = windows[10:]
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
        plt.title(filename)
        plt.plot(idx, mi, "-r")
        # plt.plot(idx, ma, "--b")
        # plt.plot(idx, me, ".-g")

    plt.show()
    getFeature(windows)
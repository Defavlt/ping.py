import matplotlib.pyplot as plt
import matplotlib.animation as anim
import operator

def plot_cont(fun, lock):
    y = []
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    def update(i):
        with lock:
            y = fun()
            x = range(len(y))
        
            ax.clear()
            ax.plot(x, y)

            # Arbitrary number,
            #  at 35 values the arrows look acceptable
            #  (according to me :))
            if len(y) > 35:
                min_i, min_v = min(enumerate(y), key=operator.itemgetter(1))
                max_i, max_v = max(enumerate(y), key=operator.itemgetter(1))
                ax.annotate(f'min ({min_v})', xy=(min_i, min_v,), xytext=(min_i + 10, min_v + 10), arrowprops=dict(facecolor='black', shrink=0.05))
                ax.annotate(f'max ({max_v})', xy=(max_i, max_v,), xytext=(max_i + 10, max_v + 10), arrowprops=dict(facecolor='black', shrink=0.05))

    a = anim.FuncAnimation(fig, update, cache_frame_data=False, repeat=False)
    plt.show()

def set():
    values = []
    def append(v):
        values.append(v)
        
    def get():
        return values
    
    def reset():
        values = []
            
    return append, get, reset

import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))

from datavyz.dependencies import *

from datavyz.draw_figure import figure
from datavyz.adjust_plots import set_plot
from datavyz.legend import build_bar_legend_continuous


###########################################################
######  Histogram
###########################################################

def hist(graph,
         x, bins=20, ax=None,
         orientation='horizontal',
         edgecolor='k', facecolor='lightgray',
         color=None,label='',
         lw=0.3, alpha=1.,
         xlabel='', ylabel='count', title='',
         normed=False, log=False,
         fig_args={}, axes_args={}):
    """
    based on the numpy.histogram function
    """
    
    hist, be = np.histogram(x, bins=bins, density=normed)
    if log:
        hist = np.clip(hist, np.min(hist[hist>0]), hist.max())
        axes_args['yscale'] = 'log'

    if color is not None:
        facecolor = color
        lw = 0
        
    if ax is None:
        fig, ax = graph.figure(**fig_args)
    else:
        fig = plt.gcf()

    if orientation=='vertical':
        ax.barh(.5*(be[1:]+be[:-1]), hist, height=be[1:]-be[:-1],
                edgecolor=edgecolor, facecolor=facecolor, lw=lw, label=label,
                alpha=alpha)
    elif orientation=='horizontal':
        ax.bar(.5*(be[1:]+be[:-1]), hist, width=be[1:]-be[:-1], 
                edgecolor=edgecolor, facecolor=facecolor, lw=lw, label=label,
                alpha=alpha)

    if 'xlabel' not in axes_args:
        axes_args['xlabel'] = xlabel
    if 'ylabel' not in axes_args:
        axes_args['ylabel'] = ylabel
        
    graph.set_plot(ax, **axes_args)
    if title!='':
        graph.title(ax, title)
    
    return fig, ax


def hist2d(graph, x, y,
           bins=20, ax=None,
           colormap=plt.cm.viridis,
           xlabel='', ylabel='', title='',
           normed=False, log=False,
           with_colorbar=False, ax_colorbar=None,
           fig_args=dict(figsize=(1.,1.1)), axes_args={}):
    """
    based on the numpy.histogram2d function
    """
    
    hist, be1, be2 = np.histogram2d(x, y, bins=bins, density=normed)
    if log:
        hist = np.clip(hist, np.min(hist[hist>0]), hist.max())
        axes_args['yscale'] = 'log'

    if ax is None and with_colorbar:
        fig, ax = graph.figure(**fig_args, right=7.)
        ax_colorbar = graph.inset(fig, [.65,.4,.03,.4])
    elif ax is None:
        fig, ax = graph.figure(**fig_args)
    else:
        fig = plt.gcf()

        
    graph.matrix(hist, x=be1, y=be2, colormap=colormap, ax=ax, aspect='auto')

    if ax_colorbar is not None:

        # ticks = [int(hist.min()), int(.5*(hist.max()+hist.min())), int(hist.max())]
        ticks = [int(hist.min()), int(hist.max())]
        graph.bar_legend(None, colormap=colormap, ax_colorbar=ax_colorbar,
                         bounds=[hist.min(), int(hist.max())],
                         ticks = ticks, ticks_labels = ['%i'%t for t in ticks],
                         label='count')
        
        
    if 'xlabel' not in axes_args:
        axes_args['xlabel'] = xlabel
    if 'ylabel' not in axes_args:
        axes_args['ylabel'] = ylabel
        
    graph.set_plot(ax, **axes_args)
    if title!='':
        graph.title(ax, title)
    
    return fig, ax


if __name__=='__main__':

    from datavyz import ge

    # 1d
    fig, ax = ge.hist(np.random.randn(100), bins=[-3,-1,0.1,0.2,2,5], xlabel='some value', log=False)

    # 2d
    fig, ax = ge.hist2d(np.random.randn(100), 10.*np.random.randn(100),
                        bins=(np.linspace(-2,2,4),np.linspace(-20,20,4)), with_colorbar=True)
    
    # ge.savefig(fig, 'docs/hist-plot.png')
    ge.show()









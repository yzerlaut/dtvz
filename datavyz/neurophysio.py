import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))

from datavyz.dependencies import *

def Ca_trace_plot(graph, Data,
                  Data_original=None, t=None,
                  tzoom=[0, np.inf],
                  colors = None,
                  ax=None,
                  fig_args = None,
                  title='',
                  bar_fraction=0.7,
                  Tbar=10, Tbar_label=None, lw=0.5):
    

    keys = [key for key in Data]
    ncells = len(keys)
    if t is None:
        t = np.arange(len(Data[keys[0]]))
    t_cond = (t>=tzoom[0]) & (t>=tzoom[0])

    if ax is None:
        if fig_args is None:
            fig_args = dict(axes_extents=(4, int(.3*len(keys))+1), left=.5, bottom=0., top=.5)
        fig, ax = graph.figure(**fig_args)
    else:
        fig = None
    ax.axis('off')
    
    if colors is None:
        colors = [graph.colors[i%10] for i, k in enumerate(Data)]
        
    for i, key in enumerate(Data):
        if Data_original is not None:
            norm_factor = 1./(np.max(Data_original[key][t_cond])-np.min(Data_original[key][t_cond]))
            baseline = np.min(Data_original[key][t_cond])
            norm_Data_original = (Data_original[key][t_cond]-baseline)*norm_factor
            ax.plot(t[t_cond], ncells-i+norm_Data_original, colors[i], lw=0.2, alpha=.3)
        else:
            norm_factor = 1./(np.max(Data[key][t_cond])-np.min(Data[key][t_cond]))
            baseline = np.min(Data[key][t_cond]) 
           
        norm_Data = norm_factor*(Data[key][t_cond]-baseline)

        ax.plot(t[t_cond], ncells-i+norm_Data, colors[i], lw=lw)
        graph.annotate(ax, key, (t[t_cond][-1], ncells-i+1), color=colors[i],
                    xycoords='data', ha='left', size='small', va='top')
        
        # scale for that cell
        ax.plot([0, 0], [ncells-i, ncells-i+bar_fraction], color=graph.default_color)
        if 100.*norm_factor<1:
            graph.annotate(ax, '%.1f%%' % (100.*norm_factor),
                    (0, ncells-i), xycoords='data', ha='right', size='small')
        else:
            graph.annotate(ax, '%i%%' % int(100.*norm_factor),
                    (0, ncells-i), xycoords='data', ha='right', size='small')
        
    ax.plot([0, Tbar], [ncells+1, ncells+1], color=graph.default_color)
    if Tbar_label is None:
        Tbar_label = '%is' % Tbar
    graph.annotate(ax, Tbar_label, (0, ncells+1), xycoords='data', size='small')

    if title!='':
        graph.annotate(ax, title, (.5, 1.), ha='center', va='top')
        
    return fig, ax

if __name__=='__main__':

    from datavyz import ge
    
    data = {}
    for i in range(30):
        data['cell%i' % (i+1)] = np.random.randn(1000)

    fig, ax = ge.figure(axes_extents=(5,5), top=0., bottom=0., right=0.5, left=0.1)
    ge.Ca_trace_plot(data, Tbar_label='X-s', title='Ca activity', ax=ax)
    ge.show()

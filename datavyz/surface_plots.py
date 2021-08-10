import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))

from datavyz.dependencies import *

from datavyz.scaling import *
from datavyz.legend import build_bar_legend_continuous
    
def twoD_plot(graph,
              x, y, z,
              ax=None, acb=None, fig=None,
              diverging=False,
              colormap=cm.viridis,
              alpha=1.,
              vmin=None,
              vmax=None,
              scale='',
              # axes props
              axes_args=dict(xlim_enhancement=0., ylim_enhancement=0., tck_outward=0),
              fig_args=dict(figsize=(.9,1), with_legend_space=True),
              xlabel=None, ylabel=None, title=None,
              # bar legend
              bar_legend_args=None,
              aspect='auto',
              interpolation='none'):
    """
    surface plots for x, y and z 1 dimensional data

    switch to bar_legend=None to remove the bar legend
    """
    
    if (ax is None):
        fig, ax = graph.figure(**fig_args)
    else:
        fig = plt.gcf()
        
    if diverging and (colormap==cm.viridis):
        colormap = cm.PiYG # we switch to a diverging colormap
        
    x, y = np.array(x), np.array(y)
    Z = np.ones((len(np.unique(y)), len(np.unique(x))))*np.nan
    for i, yy in enumerate(np.unique(y)):
        cond1 = y==yy
        for j, xx in enumerate(np.unique(x[cond1])):
            try:
                Z[i,j] = z[cond1][x[cond1]==xx]
            except ValueError:
                print('multiple values for the same (x=', xx, ', y=', yy, ') couple: ', z[cond1][x[cond1]==xx])
                Z[i,j] = np.mean(z[cond1][x[cond1]==xx])
    # z1 = np.array(Z).reshape(len(np.unique(y)), len(np.unique(x)))
    z1 = Z
    
    if vmin is None:
        if diverging:
            vmin = -np.max(np.abs(z))
        else:
            vmin = np.min(z)
    if vmax is None:
        if diverging:
            vmax = np.max(np.abs(z))
        else:
            vmax = np.max(z)
            
    ac = ax.imshow(z1,
                   interpolation=interpolation,
                   extent = (x.min(), x.max(), y.min(), y.max()),
                   vmin = vmin,
                   vmax = vmax,
                   alpha=alpha,
                   cmap=colormap,
                   origin='lower',
                   aspect=aspect)


    if bar_legend_args is not None:

        if 'bounds' not in bar_legend_args:
            bar_legend_args['bounds'] = [vmin, vmax]
        if 'colormap' not in bar_legend_args:
            bar_legend_args['colormap'] = colormap
        acb = graph.bar_legend(fig, **bar_legend_args)
        
    else:
        
        acb = None
        
    axes_args = graph.add_to_axes_args(xlabel, ylabel, title, axes_args)
    
    graph.set_plot(ax, **axes_args)
    
    return fig, ax, acb
    

def matrix(graph, z,
           x=None, y=None, 
           ax=None, acb=None, fig=None,
           diverging=False,
           colormap=cm.viridis,
           alpha=1.,
           vmin=None, vmax=None,
           aspect='equal', # switch to 'auto' if needed
           origin='lower',
           # axes props
           axes_args=dict(xlim_enhancement=0., ylim_enhancement=0., tck_outward=0),
           fig_args=dict(figsize=(.9,1), with_legend_space=True),
           xlabel=None, ylabel=None, title=None,
           # bar legend
           bar_legend_args=None,
           # other args
           interpolation='none'):

    if (x is None) and (y is None):
        x, y = np.meshgrid(np.arange(z.shape[0]), np.arange(z.shape[1]), indexing='ij')
        
    if (ax is None) and (acb is None):
        fig, ax = graph.figure(**fig_args)
    else:
        fig = plt.gcf()
        
    if diverging and (colormap==cm.viridis):
        colormap = cm.PiYG # we switch to a diverging colormap

    if vmin is None:
        vmin=z.min()
    if vmax is None:
        vmax=z.max()

    im = ax.imshow(z.T,
                   interpolation=interpolation,
                   extent = (x.min(), x.max(), y.min(), y.max()),
                   vmin = vmin,
                   vmax = vmax,
                   alpha=alpha,
                   cmap=colormap,
                   origin=origin,
                   aspect=aspect)
    
    if bar_legend_args is not None:

        if 'bounds' not in bar_legend_args:
            bar_legend_args['bounds'] = [vmin, vmax]
        if 'colormap' not in bar_legend_args:
            bar_legend_args['colormap'] = colormap
        acb = graph.bar_legend(fig, **bar_legend_args)
        
    else:
        
        acb = None
        
    axes_args = graph.add_to_axes_args(xlabel, ylabel, title, axes_args)
    
    graph.set_plot(ax, **axes_args)
    
    return fig, ax, acb


if __name__=='__main__':
    
    from datavyz import ges as ge

    x, y = np.meshgrid(np.arange(1, 11), np.arange(1, 20), indexing='ij')
    z = y*x*x

    fig1, ax, _ = matrix(ge, z, aspect='equal',
                         xlabel='x-label (X)', ylabel='y-label (Y)')

    x, y, z = np.array(x).flatten(),\
              np.array(y).flatten(),\
              np.array(z).flatten()*np.random.randn(len(z.flatten()))
    index = (x<15) & (y<x)
    # np.random.shuffle(index)
    x, y, z = x[index], y[index], z[index]

    fig2, ax, acb = twoD_plot(ge, x, y, z,
                              vmin=-7, vmax=7,
                              bar_legend_args={'label':'color',
                                               'ticks':[-7, 0, 7],
                                               'ticks_labels':['-7', '0', '>7'],
                                               'color_discretization':20})
    ge.set_plot(ax, xlabel='x-label (X)', ylabel='y-label (Y)')
    
    fig2.savefig('docs/surface-plot.png')

    ge.show()

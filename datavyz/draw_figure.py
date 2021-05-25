import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from datavyz.dependencies import *
from datavyz.scaling import mm2inch

def dimension_calculus(cls,
                       figsize,
                       left, right,
                       bottom, top,
                       wspace, hspace,
                       x_plots, y_plots):
    """
    calculate the dimension quantities required by *matplotlib* plt.figure object
    """
    dimension = {}
    
    # horizontal 
    dimension['full_width'] = left*figsize[0]*cls.left_size+\
        right*figsize[0]*cls.right_size+\
        x_plots*figsize[0]*figsize[0]*cls.single_plot_size[0]+\
        wspace*(x_plots-1)*figsize[0]*cls.wspace_size
    dimension['left'] = left*figsize[0]*cls.left_size/dimension['full_width']
    dimension['right'] = right*figsize[0]*cls.right_size/dimension['full_width']
    dimension['wspace'] = wspace*figsize[0]*cls.wspace_size/figsize[0]/cls.single_plot_size[0]

    # vertical
    dimension['full_height'] = bottom*figsize[1]*cls.bottom_size+\
        top*figsize[1]*cls.top_size+\
        y_plots*figsize[1]*cls.single_plot_size[1]+\
        hspace*figsize[1]*(y_plots-1)*cls.hspace_size
    dimension['bottom'] = bottom*figsize[1]*cls.bottom_size/dimension['full_height']
    dimension['top'] = top*figsize[1]*cls.top_size/dimension['full_height']
    dimension['hspace'] = hspace*figsize[1]*cls.hspace_size/figsize[1]/cls.single_plot_size[1]

    return dimension


def figure(cls,
           axes = (1,1),
           axes_extents=None,
           grid=None,
           figsize=(1.,1.),
           left=1., right=1.,
           bottom=1., top=1.,
           wspace=1., hspace=1.,
           reshape_axes=True):
    
    """
    scales figures according to the specification of "settings.py" (for each graph environment)

    the wspace, hspace, ... values are factor that modulates the wspace0, hspace0
    -> then use >1 to make bigger, and <1 to make smaller...

    Subplots are build with this convention for the geometry:
    (X,Y)
    ------ X -------------->
    |                 |     |
    |      (3,1)      |(1,1)|
    |                 |     |
    |-----------------------|
    Y     |           |     |
    |(1,1)|   (2,1)   |(1,1)|
    |     |           |     |
    |------------------------
    |
    v

    TO PRODUCE THIS, RUN:
    figure(axes_extents=[\
                         [[3,1], [1,1] ],
                         [[1,1], [2,1], [1,1] ] ] )
    show()


    OTHERWISE, you can use the "grid" arguments that corresponds to "subplot2grid"
    TO PRODUCE THIS, RUN:
    figure(grid=[(0,0,1,4),
                 (x,y,dx,dy)])

    """

    AX = []
    
    if grid is not None:
        x_plots = np.max([g[0]+g[2] for g in grid])
        y_plots = np.max([g[1]+g[3] for g in grid])

        dim =  dimension_calculus(cls, figsize,left, right, bottom, top, wspace, hspace, x_plots, y_plots)
        
        fig = plt.figure(figsize=(mm2inch(dim['full_width']),
                                  mm2inch(dim['full_height'])), facecolor=cls.facecolor)
        for g in grid:
            ax = plt.subplot2grid((y_plots, x_plots),
                                  (g[1], g[0]),
                                  colspan=g[2],
                                  rowspan=g[3], facecolor=cls.facecolor)
            AX.append(ax)
    else:
        if axes_extents is not None:
            if type(axes_extents) is tuple:
                axes_extents = [[axes_extents]]
        else:
            axes_extents = [[[1,1] for j in range(axes[0])]\
                            for i in range(axes[1])]
                
        x_plots = np.sum([axes_extents[0][j][0] \
                          for j in range(len(axes_extents[0]))])
        y_plots = np.sum([axes_extents[i][0][1] \
                          for i in range(len(axes_extents))])

        dim =  dimension_calculus(cls, figsize,left, right, bottom, top, wspace, hspace, x_plots, y_plots)
        
        fig = plt.figure(figsize=(mm2inch(dim['full_width']),
                                  mm2inch(dim['full_height'])), facecolor=cls.facecolor)
        
        j0_row = 0
        for j in range(len(axes_extents)):
            AX_line = []
            i0_line = 0
            for i in range(len(axes_extents[j])):
                AX_line.append(plt.subplot2grid(\
                                                (y_plots, x_plots),
                                                (j0_row, i0_line),\
                                                colspan=axes_extents[j][i][0],
                                                rowspan=axes_extents[j][i][1],
                                                facecolor=cls.facecolor))
                i0_line += axes_extents[j][i][0]
            j0_row += axes_extents[j][i][1]
            AX.append(AX_line)

    
    if dim['left']>=(1-dim['right']):
        print('left=%.2f and right=%.2f leads to a too large space' % (dim['left'], dim['right']),
              'set to 0.2, & 0.95 respectively')
        dim['left'], dim['right'] = 0.2, 0.95
    if dim['bottom']>=(1-dim['top']):
        print('left=%.2f and right=%.2f leads to a too large space' % (dim['bottom'], dim['top']),
              'set to 0.2, & 0.95 respectively')
        dim['bottom'], dim['top'] = 0.2, 0.95

        
    # # Subplots placements adjustements
    plt.subplots_adjust(left=dim['left'],
                        bottom=dim['bottom'],
                        top=1.-dim['top'],
                        right=1.-dim['right'],
                        wspace=dim['wspace'],
                        hspace=dim['hspace'])

    if (grid is not None) or (reshape_axes is False):
        return fig, AX
    elif len(AX)==1 and (len(AX[0])==1):
        return fig, AX[0][0]
    elif (len(AX[0])==1) and (len(AX[-1])==1):
        return fig, [AX[i][0] for i in range(len(AX))]
    elif len(AX)==1:
        return fig, AX[0]
    else:
        return fig, AX

    
if __name__=='__main__':
    
    import itertools, string
    
    from datavyz.main import graph_env
    ge = graph_env('manuscript')

    # fig, ax = ge.figure()
    fig1, AX1 = ge.figure(axes=(2,2))
    for l, ax in zip(list(string.ascii_lowercase), itertools.chain(*AX1)):
        ge.top_left_letter(ax, l+'     ')
        ge.set_plot(ax, xlabel='xlabel (xunit)', ylabel='ylabel (yunit)', grid=True)
    fig1.savefig('fig1.svg')

    # fig2, AX2 = ge.figure(axes_extents=[\
    #                                     [[1,1], [1,1], [1,1]],
    #                                     [[2,2], [1,2]]])
    
    fig2, AX2 = ge.figure(axes_extents=[\
                                        [[1,1], [3,1]],
                                        [[4,1]],
                                        [[1,1], [2,1], [1,1] ] ],
                          figsize=[.95,.95])

    t = np.linspace(0, 10, 1e3)
    y = np.cos(5*t)+np.random.randn(len(t))

    # leave first axis empty for drawing
    AX2[0][0].axis('off') # space for docs/schematic.svg
    
    # time series plot
    AX2[0][1].plot(t, y)
    ge.set_plot(AX2[0][1], xlabel='xlabel (xunit)', ylabel='ylabel (yunit)')

    # more time series plot
    AX2[1][0].plot(t[t>9], y[t>9], label='raw')
    AX2[1][0].plot(t[t>9][1:], np.diff(y[t>9]), label='deriv.')
    AX2[1][0].plot(t[t>9][1:-1], np.diff(np.diff(y[t>9])), label='2nd deriv.')
    ge.set_plot(AX2[1][0], xlabel='xlabel (xunit)', ylabel='ylabel (yunit)')

    # histogram
    ge.scatter(t[::10], t[::10]+np.random.randn(100),
               ax=AX2[2][0], xlabel='ylabel (yunit)')


    # histogram
    ge.bar(np.random.randn(8),
           COLORS=[ge.viridis(i/7) for i in range(8)],
            ax=AX2[2][1], xlabel='ylabel (yunit)')
    
    # pie plot
    ge.pie([0.25,0.4,0.35], ax=AX2[2][2], ext_labels=['Set 1', 'Set 2', 'Set 3'])

    
    # looping on all plots to add the top left letter:
    for i, fig, AX in zip(range(3), [fig1, fig2], [AX1, AX2]):
        for l, ax in zip(list(string.ascii_lowercase), itertools.chain(*AX)):
            ge.top_left_letter(ax, l+'     ')

    # saving the figure with all plots
    fig2.savefig('fig2.svg')

    # generating the figure with the addition of the drawing
    from datavyz.plot_export import put_list_of_figs_to_svg_fig
    put_list_of_figs_to_svg_fig(['docs/schematic.svg', fig],
                                fig_name='fig.svg',
                                Props={'XCOORD':[0,0], 'YCOORD':[0,0]})
        
    ge.show()


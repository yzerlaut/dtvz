import sys, pathlib, os, json
import numpy as np

import matplotlib.animation as animation
from matplotlib.collections import LineCollection, PatchCollection
import matplotlib.patches as mpatches
from matplotlib.cm import viridis_r


def coordinate_projection(x, y, z, x0 ,y0, z0, polar_angle, azimuth_angle):
    """
    /!\
    need to do this propertly, not working yet !!
    """
    x = np.cos(polar_angle)*(x-x0)+np.sin(polar_angle)*(y-y0)
    y = np.sin(polar_angle)*(x-x0)+np.cos(polar_angle)*(y-y0)
    z = z
    return x, y, z


def plot_nrn_shape(graph,
                   SEGMENTS,
                   comp_type=None,
                   ax=None,
                   center = {'x0':0, 'y0':0., 'z0':0.},
                   bar_scale_args=dict(Ybar=100., Ybar_label='100$\mu$m'),
                   xshift=0.,
                   polar_angle=0, azimuth_angle=np.pi/2., 
                   density_quantity=None,
                   colors=None,
                   annotation_color=None,
                   diameter_magnification=2.,
                   lw=1):
    """
    by default: soma_comp = COMP_LIST[0]
    """

    if ax is None:
        fig, ax = graph.figure(figsize=(2.,4.),
                               left=0., top=0., bottom=0., right=0.)
    else:
        fig = None


    if comp_type is None:
        comp_type = np.unique(SEGMENTS['comp_type'])

    incl_cond = np.array([True if (c in comp_type) else False for c in SEGMENTS['comp_type']])
    
    # possibility to control the center of the rotation         
    x0, y0, z0 = center['x0'], center['y0'], center['z0']

    segments, seg_diameters, circles, circle_colors = [], [], [], []
    
    for iseg in np.arange(len(SEGMENTS['x']))[incl_cond]:

        if (SEGMENTS['start_x'][iseg]==SEGMENTS['end_x'][iseg]) and\
           (SEGMENTS['start_y'][iseg]==SEGMENTS['end_y'][iseg]) and\
           (SEGMENTS['start_z'][iseg]==SEGMENTS['end_z'][iseg]):
            
            # circle of diameter
            sx, sy, _ = coordinate_projection(SEGMENTS['start_x'][iseg],
                                              SEGMENTS['start_y'][iseg],
                                              SEGMENTS['start_z'][iseg],
                                              x0 ,y0, z0, polar_angle, azimuth_angle)
            if colors is None:
                circles.append(mpatches.Circle((1e6*sx, 1e6*sy), 1e6*SEGMENTS['diameter'][iseg]/2., color=graph.default_color))
            else:
                circles.append(mpatches.Circle((1e6*sx, 1e6*sy), 1e6*SEGMENTS['diameter'][iseg]/2.,
                                               color=colors[iseg]))
        else:
            sx, sy, _ = coordinate_projection(SEGMENTS['start_x'][iseg],
                                              SEGMENTS['start_y'][iseg],
                                              SEGMENTS['start_z'][iseg],
                                              x0 ,y0, z0, polar_angle, azimuth_angle)
            ex, ey, _ = coordinate_projection(SEGMENTS['end_x'][iseg],
                                              SEGMENTS['end_y'][iseg],
                                              SEGMENTS['end_z'][iseg],
                                              x0 ,y0, z0, polar_angle, azimuth_angle)
            segments.append([(1e6*(sx+xshift), 1e6*sy),(1e6*(ex+xshift), 1e6*ey)])
            seg_diameters.append(1e6*SEGMENTS['diameter'][iseg])

    if colors is None:
        colors = [graph.default_color for i in range(len(segments))]

    line_segments = LineCollection(segments, linewidths=seg_diameters, colors=colors, linestyles='solid')
    ax.add_collection(line_segments)
    collection = PatchCollection(circles)
    ax.add_collection(collection)
    ax.autoscale()

    ax.set_aspect('equal')

    # adding a bar for the spatial scale
    if bar_scale_args is not None:
        graph.draw_bar_scales(ax, **bar_scale_args)
        
    ax.axis('off')
        
    return fig, ax

def add_dot_on_morpho(graph, ax,
                      comp,
                      index=0,
                      soma_comp=None,
                      polar_angle=0, azimuth_angle=np.pi/2., 
                      color=None,
                      edgecolor=None,
                      facecolor='none',
                      marker='o',
                      alpha=1.,
                      lw=3, markersize=None):
    """
    """
    
    if edgecolor is None:
        edgecolor = graph.default_color
    if markersize is None:
        markersize = graph.markersize
        
    if soma_comp is None:
        print('Need to pass the somatic compartment to project coordinates')
        print('Taking (0, 0, 0) as the default coordinates !')
        x0, y0, z0 = 0, 0, 0
    else:
        [x0, y0, z0] = soma_comp[0].x, soma_comp[0].y, soma_comp[0].z
        
    x, y, z = comp['x'][index], comp['y'][index], comp['z'][index]
    x, y, _ = coordinate_projection(x, y, z, x0 ,y0, z0, polar_angle, azimuth_angle)
    
    ax.scatter([1e6*x], [1e6*y],
               s=markersize, edgecolors=edgecolor,
               facecolors=facecolor,
               marker=marker, lw=lw, alpha=alpha)
    

def dist_to_soma(comp, soma):
    return np.sqrt((comp.x-soma.x)**2+\
                   (comp.y-soma.y)**2+\
                   (comp.z-soma.z)**2)[0]/brian2.um


def show_animated_time_varying_trace(t, Quant0, SEGMENT_LIST,
                                     fig, ax, graph,
                                     picked_locations = None,
                                     polar_angle=0, azimuth_angle=np.pi/2.,
                                     quant_label='$V_m$ (mV)',
                                     time_label='time (ms)',
                                     segment_condition=None,
                                     colormap=viridis_r,
                                     ms=0.5):
    """

    "picked_locations" should be given as a compartment index
    we highlight the first picked_locations with a special marker because it will usually be the stimulation point
    """
    # preparing animations params
    if segment_condition is None:
        segment_condition = np.empty(Quant0.shape[0], dtype=bool)+True
    Quant = (Quant0[segment_condition]-Quant0[segment_condition].min())/(Quant0[segment_condition].max()-Quant0[segment_condition].min())

    # adding inset of time plots and bar legends
    ax2 = graph.inset(ax, rect=[0.1,-0.05,.9,.1])
    ax3 = graph.inset(ax, rect=[0.83,0.8,.03,.2])
    graph.build_bar_legend(np.linspace(Quant0[segment_condition].min(),
                                       Quant0[segment_condition].max(), 5), ax3, colormap,
                     color_discretization=30, label=quant_label)
    
    # picking up locations
    if picked_locations is None:
        picked_locations = np.concatenate([[0], np.random.randint(1, Quant.shape[0], 4)])
    for pp, p in enumerate(picked_locations):
        ax2.plot(t, Quant0[segment_condition,:][p,:], 'k:', lw=1)
        ax.scatter([1e6*SEGMENT_LIST['xcoords'][segment_condition][p]],
                   [1e6*SEGMENT_LIST['ycoords'][segment_condition][p]], 
                   s=25+30*(1-np.sign(pp)),
                   c=list(['k']+graph.colors)[pp])
    graph.set_plot(ax2, xlabel=time_label, ylabel=quant_label, num_yticks=2)

    LINES = []
    # plotting each segment
    line = ax.scatter(1e6*SEGMENT_LIST['xcoords'][segment_condition], 1e6*SEGMENT_LIST['ycoords'][segment_condition],
                      color=colormap(Quant[:,0]), s=ms, marker='o')
    LINES.append(line)
    # then highlighted points
    for pp, p in enumerate(picked_locations):
        line, = ax2.plot([t[0]], [Quant0[segment_condition,:][p,0]], 'o',
                         ms=4+4*(1-np.sign(pp)),
                         color=list(['k']+graph.colors)[pp])
        LINES.append(line)
    
    # Init only required for blitting to give a clean slate.
    def init():
        return LINES

    def animate(i):
        LINES[0].set_color(colormap(Quant[:,i]))  # update the data
        for pp, p in enumerate(picked_locations):
            LINES[pp+1].set_xdata([t[i]])
            LINES[pp+1].set_ydata([Quant0[segment_condition,:][p,i]])
        return LINES


    ani = animation.FuncAnimation(fig, animate, np.arange(len(t)),
                                  init_func=init,
                                  interval=50, blit=True)
    return ani



if __name__=='__main__':

    import argparse
    # First a nice documentation 
    parser=argparse.ArgumentParser(description=""" 
         Plots a 2D representation of the morphological reconstruction of a single cell
         """,formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("-lw", "--linewidth",help="", type=float, default=0.2)
    parser.add_argument("-ac", "--axon_color",help="", default='r')
    parser.add_argument("-pa", "--polar_angle",help="", type=float, default=0.)
    parser.add_argument("-aa", "--azimuth_angle",help="", type=float, default=0.)
    parser.add_argument("-wa", "--without_axon",help="", action="store_true")
    parser.add_argument("-m", "--movie_demo",help="", action="store_true")
    parser.add_argument("--filename", '-f', help="filename", type=str, default='')
    parser.add_argument("--directory", '-d', help="directory", type=str, default='')
    
    args = parser.parse_args()

    from datavyz import ges as ge

    # specific modules
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
    from neural_network_dynamics import main as ntwk # based on Brian2

    
    if (args.filename=='') and (args.directory==''):
        print("""
        please provide as arguments either a filename of a morphology or a directory containing some
        FOR EXAMPLE:
        python nrn_morpho.py --filename ./neural_network_dynamics/single_cell_integration/morphologies/Jiang_et_al_2015/L5pyr-j140408b.CNG.swc
        OR:
        python nrn_morpho.py --directory ./neural_network_dynamics/single_cell_integration/morphologies/Jiang_et_al_2015/
        """)
    elif args.directory!='':
        file_list = [fn for fn in os.listdir(args.directory) if fn.endswith('.swc')]

        fig, AX = ge.figure(figsize=(.6,.6), axes=(int(len(file_list)/8)+1,8))
        
        n = 0
        for fn, ax in zip(file_list, ge.flat(AX)):
            morpho = ntwk.Morphology.from_swc_file(os.path.join(args.directory, fn))
            SEGMENTS = ntwk.morpho_analysis.compute_segments(morpho)
            colors = [ge.green if comp_type=='axon' else ge.red for comp_type in SEGMENTS['comp_type']]
            plot_nrn_shape(ge, SEGMENTS, colors=colors, ax=ax)
            ge.title(ax, fn.split('-')[0], bold=True, style='italic', size='')
            n+=1
        while n<len(ge.flat(AX)):
            ge.flat(AX)[n].axis('off')
            n+=1
    else:

        if args.movie_demo:
            t = np.arange(100)*1e-3
            Quant = np.array([.5*(1-np.cos(20*np.pi*t))*i/len(SEGMENT_LIST['xcoords']) \
                              for i in np.arange(len(SEGMENT_LIST['xcoords']))])*20-70
            ani = show_animated_time_varying_trace(1e3*t, Quant, SEGMENT_LIST,
                                                   fig, ax,
                                                   polar_angle=args.polar_angle, azimuth_angle=args.azimuth_angle)

        print('[...] loading morphology')
        morpho = ntwk.Morphology.from_swc_file(args.filename)
        print('[...] creating list of compartments')
        SEGMENTS = ntwk.morpho_analysis.compute_segments(morpho)
    
        fig, ax = plot_nrn_shape(ge,
                                 SEGMENTS,
                                 # comp_type=['dend', 'soma', 'apic'],
                                 lw=args.linewidth,
                                 polar_angle=args.polar_angle,
                                 azimuth_angle=args.azimuth_angle)
        
        add_dot_on_morpho(ge, ax,
                          SEGMENTS,
                          index=2000,
                          soma_comp=None,
                          edgecolor=ge.r,
                          # facecolor=ge.r,
                          polar_angle=args.polar_angle,
                          azimuth_angle=args.azimuth_angle)
        
    ge.show()

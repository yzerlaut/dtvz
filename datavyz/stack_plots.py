import sys, pathlib, os
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from tempfile import gettempdir
import string, datetime

# SPECIAL PYTHON PACKAGES FOR:
import svgutils.compose as sg # SVG

from datavyz.scaling import inch2cm, cm2inch
from datavyz.dependencies import *
from datavyz.plot_export import export_as_png


def export_drawing_as_png(fig_name, dpi=100, background='white'):
    instruction = 'inkscape %s --export-area-drawing --export-background="%s" --export-type=png --export-filename="%s" --export-dpi=%i' % (fig_name, background, fig_name.replace('.svg', '.png'), dpi)
    print('RUNNING:', instruction)
    os.system(instruction)
    if os.path.isfile(fig_name.replace('.svg', '.png')):
        print('[ok] figure successfully exported as: %s' % fig_name.replace('.svg', '.png'))
    else:
        print('[!!] %s not exported as png' % fig_name)


def add_plot_to_svg(fig, svg_fig,
                    temp_name=os.path.join(gettempdir(), 'temp.svg')):
    """
    the two figures need to be identical
    """
    
    fig.savefig(temp_name, transparent=True)
    PANELS = [sg.Panel(sg.SVG(svg_fig)).move(0,0),
              sg.Panel(sg.SVG(temp_name).move(0,0))]
              

    sg.Figure("%.2fcm" % inch2cm(fig.get_size_inches()[0]),
              "%.2fcm" % inch2cm(fig.get_size_inches()[1]),
              *PANELS).scale(1).save(svg_fig)

    

    
if __name__=='__main__':

    from datavyz import ge

    fig_name = os.path.join(os.path.expanduser('~'), 'Desktop', 'fig.svg')

    fig1, ax1 = ge.figure()
    ge.scatter(np.arange(10), np.random.randn(10), ax=ax1)
    ge.set_plot(ax1, xlabel='time (s)', ylabel='value (a.u.)')
    fig1.savefig(fig_name)
    
    fig2, ax2 = ge.figure()
    ge.scatter(np.arange(10), np.random.randn(10), color=ge.blue, ax=ax2)
    ge.set_plot(ax2, ax_refs=ax1)
    add_plot_to_svg(fig2, fig_name)

    # LOCATIONS, PANELS = [], []
    # for i, fig in enumerate([fig1, fig2]):
    #     LOCATIONS.append(os.path.join(gettempdir(), str(i)+'.svg'))
    #     fig.savefig(LOCATIONS[i], transparent=True)
    #     PANELS.append(sg.Panel(sg.SVG(LOCATIONS[i])).move(0,0))

    # sg.Figure("%.2fcm" % inch2cm(fig.get_size_inches()[0]),
    #           "%.2fcm" % inch2cm(fig.get_size_inches()[1]),
    #           *PANELS).scale(1).save(fig_name)

    export_drawing_as_png(fig_name)
    

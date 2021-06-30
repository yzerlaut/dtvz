import sys, os, platform
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))

desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')+os.path.sep
home = os.path.expanduser('~')+os.path.sep

from datavyz.dependencies import *

# module that construct the plot settings
import datavyz.draw_figure as df
import datavyz.adjust_plots as ap

from datavyz import annotations, line_plots, scatter_plots, legend, features_plot, cross_correl_plot
from datavyz.cross_correl_plot import cross_correl_plot_func
from datavyz.parallel_plots import parallel_plot, components_plot
from datavyz.hist_plots import hist
from datavyz.inset import inset
from datavyz.surface_plots import twoD_plot, matrix
from datavyz.bar_plots import bar, related_samples_two_conditions_comparison, unrelated_samples_two_conditions_comparison
from datavyz.pie_plots import pie
import datavyz.single_cell_plots as scp
from datavyz.plot_export import put_list_of_figs_to_svg_fig, multipanel_figure
from datavyz.dynamic_plot import movie_plot, animated_plot
from datavyz.time_freq import time_freq_plot
from datavyz.neurophysio import Ca_trace_plot

from datavyz.colors import give_color_attributes, viridis, binary_r

from datavyz.settings import set_env_variables #, update_rcParams
    
class graph_env:
    
    def __init__(self,
                 env='manuscript'):
        """
        accepts the styles described in 'settings.py'

        use of seaborn and ggplot deprecated ....
        """
        set_env_variables(self, env)

        self.override_style=True
        
        # if ('dark' in env) or (self.background is 'dark'):
        #     self.set_style('dark_background')
        # elif 'ggplot' in env:
        #     self.default_color = 'dimgrey'
        #     self.set_style('ggplot')
        #     self.override_style = False
        # elif 'seaborn' in env:
        #     self.set_style('seaborn')
        #     self.override_style = False

        # update_rcParams(self)

        give_color_attributes(self)
        
    def set_style(self, style='default'):
        plt.style.use(style)
        if style=='dark_background':
            self.default_color = 'w'

    def figure(self,
               axes = (1,1),
               axes_extents=None,
               grid=None,
               figsize=(1.,1.),
               left=1., right=1.,
               bottom=1., top=1.,
               wspace=1., hspace=1.,
               with_legend_space=False,
               with_bar_legend=False,
               bar_inset_loc=None,
               with_panel_label=False,
               shift_up=0., shrink=1.,
               reshape_axes=True):

        if with_legend_space:
            fig, ax = df.figure(self,
                                axes, axes_extents, grid,
                                right=5.5,
                                figsize=figsize,
                                reshape_axes=reshape_axes)
            return fig, ax
            
        elif with_bar_legend:
            fig, ax = df.figure(self,
                                axes, axes_extents, grid,
                                right=5,
                                figsize=figsize,
                                reshape_axes=reshape_axes)
            acb = self.inset(ax,
                             [1.17, -.08+shift_up, .08, shrink*1.],
                             facecolor=self.facecolor)
            return fig, ax, acb
        else:
            fig, AX = df.figure(self,
                                axes, axes_extents, grid,
                                np.array(figsize),
                                left, right, bottom, top, wspace, hspace,
                                reshape_axes=reshape_axes)
            if bar_inset_loc is not None:
                if type(AX) is list:
                    acb = self.inset(AX[-1], bar_inset_loc,
                                     facecolor=self.facecolor)
                else:
                    acb = self.inset(AX, bar_inset_loc,
                                     facecolor=self.facecolor)
                return fig, AX, acb
            else:
                return fig, AX


    def plot(self,
             x=None, y=None, sy=None, sy1=None, sy2=None, color=None,
             X=None, Y=None, sY=None, sY1=None, sY2=None,
             COLORS=None, colormap=viridis,
             fig = None, ax=None,
             lw=1, alpha_std=0.3, ms=0, m='', ls='-',alpha=1.,
             xlabel='', ylabel='', bar_label='', title='',
             label=None, LABELS=None,
             fig_args={},
             axes_args={},
             bar_scale_args=None,
             bar_legend_args=None,
             legend_args=None, no_set=False):
        
        """    
        return fig, ax
        """
        # getting or creating the axis
        if ax is None:
            fig, ax = self.figure(**fig_args)
            
        if color is None:
            color = self.default_color
            
        if (y is None) and (Y is None):
            y = x
            x = np.arange(len(y))

        if (Y is not None):
            if (X is None) and (x is not None):
                X = [x for i in range(len(Y))]
            elif (X is None):
                X = [np.arange(len(y)) for y in Y]

            line_plots.multiple_curves(ax, X, Y, sY, COLORS, LABELS,
                                       sY1=sY1, sY2=sY2,
                                       alpha_std=alpha_std,
                                       colormap=colormap,
                                       lw=lw, ls=ls, m=m, ms=ms,
                                       alpha=alpha)
        else:
            line_plots.single_curve(ax, x, y, sy,
                                    sy1=sy1, sy2=sy2,
                                    color=color,
                                    alpha_std=alpha_std,
                                    lw=lw, label=label, ls=ls, m=m, ms=ms,
                                    alpha=alpha)

        if bar_legend_args is not None:
            self.bar_legend(ax, **bar_legend_args)

        if (label is not None) or (LABELS is not None):
            if legend_args is not None:
                self.legend(ax, **legend_args)
            else:
                self.legend(ax, frameon=False, size='small', loc='best')

        if bar_scale_args is not None:
            self.draw_bar_scales(ax, **bar_scale_args)
            self.set_plot(ax, [], **axes_args)
        else:
            if 'title' not in axes_args:
                axes_args['title'] = title
            if 'xlabel' not in axes_args:
                axes_args['xlabel'] = xlabel
            if 'ylabel' not in axes_args:
                axes_args['ylabel'] = ylabel
            if not no_set:
                self.set_plot(ax, **axes_args)

        return fig, ax

    def scatter(self,
                x=None, y=None, sx=None, sy=None, color=None,
                X=None, Y=None, sX=None, sY=None,
                COLORS=None, colormap=viridis,
                ax=None, fig=None,
                lw=0, alpha_std=0.3,
                ms=None,
                m='', ls='-',
                xlabel='', ylabel='', bar_label='', title='',
                label=None,
                LABELS=None,
                fig_args={},
                axes_args={},
                bar_legend_args=None,
                legend_args=None,
                no_set=False):
        
        """    
        return fig, ax
        """
        # getting or creating the axis
        if ax is None:
            fig, ax = self.figure(**fig_args)
            
        if color is None:
            color = self.default_color
        if ms is None:
            ms = self.markersize
            
        if (y is None) and (Y is None):
            y = x
            x = np.arange(len(y))

        if (Y is not None):
            if (X is None) and (x is not None):
                X = [x for i in range(len(Y))]
            elif (X is None):
                X = [np.arange(len(y)) for y in Y]

            scatter_plots.multiple_curves(ax, X, Y, sX, sY, COLORS, LABELS,
                                          colormap=colormap,
                                          lw=lw, ms=ms)
        else:
            scatter_plots.single_curve(ax, x, y, sx, sy,
                                       color=color, label=label,
                                       lw=lw,
                                       ms=ms)

        if bar_legend_args is not None:
            cb = add_inset(ax, **bar_legend_args)
            build_bar_legend(np.arange(len(LABELS)+1),
                             cb,
                             colormap,
                             label=bar_label,
                             ticks_labels=LABELS)

        if legend_args is not None:
            ax.legend(**legend_args)

        if 'xlabel' not in axes_args:
            axes_args['xlabel'] = xlabel
        if 'ylabel' not in axes_args:
            axes_args['ylabel'] = ylabel

        if not no_set:
            self.set_plot(ax, **axes_args)
        if title!='':
            self.title(ax, title)

        return fig, ax

    ################################################
    ###### Classical plot functions ################
    ################################################

    def multicolored_line(self, x, y, norm_color_value, **args):
        return line_plots.multicolored_line(self, x, y, norm_color_value, **args)

    def parallel_plot(self, Y, **args):
        return parallel_plot(self, Y, **args)
    
    def components_plot(self, Y, **args):
        return components_plot(self, Y, **args)
    
    # histogram 
    def hist(self, x, **args):
        return hist(self, x, **args)

    def boxplot(self, data,
                fig_args=dict(figsize=(.6,1.)),
                axes_args={}, **args):
        fig, ax = self.figure(**fig_args)
        ax.boxplot(data, **args)
        self.set_plot(ax, **axes_args)
        return fig, ax
    
    # bar plot
    def bar(self, x, **args):
        return bar(self, x, **args)

    # pie plot
    def pie(self, x, **args):
        return pie(self, x, **args)
    
    # features plot
    def features_plot(self, data, **args):
        return features_plot.features_plot(self, data, **args)

    # cross_correl_plot
    def cross_correl_plot(self, data, **args):
        return cross_correl_plot_func(self, data, **args)

    # animated plot
    def animated_plot(self, x, time_dep_y, **args):
        return animated_plot(self, x, time_dep_y, **args)
    
    # twoD-plot with x-y axis from bottom left
    def twoD_plot(self, x, y, z, **args):
        return twoD_plot(self, x, y, z, **args)

    def matrix(self, x, **args):
        return matrix(self, x, **args)

    # image plot
    def image(self, X, cmap=binary_r, alpha=1., ax=None, title=''):
        if ax is None:
            fig, ax = self.figure()
        else:
            fig = plt.gcf()
        ax.imshow(X.T, cmap=cmap, alpha=alpha,
                  interpolation=None,
                  origin='lower',
                  aspect='equal')
        ax.axis('off')
        if title!='':
            self.title(ax, title)
        return fig, ax

    # movie plot
    def movie(self, array, **args):
        return movie_plot(self, array, **args)
    
    def related_samples_two_conditions_comparison(self, data1, data2,**args):
        return related_samples_two_conditions_comparison(self, data1, data2,**args)
    
    def unrelated_samples_two_conditions_comparison(self, data1, data2,**args):
        return unrelated_samples_two_conditions_comparison(self, data1, data2,**args)
        
    
        
    ################################################
    ###### Annotate function #######################
    ################################################
    def title(self, ax, title, **args):
        annotations.title(self, ax, title, **args)
        
    def annotate(self, stuff, s, xy, **args):
        annotations.annotate(self, stuff, s, xy, **args)

    def top_left_letter(self, stuff, s, loc=(0,1), **args):
        annotations.annotate(self, stuff, s, loc, ha='right', bold=True, **args)

    def panel_label(self, stuff, s, xy=(-.01,1.01), size='large', ha='right', bold=True, **args):
        annotations.annotate(self, stuff, s, xy, size=size, ha=ha, bold=bold, **args)
        
    def draw_bar_scales(self, ax, **args):
        return annotations.draw_bar_scales(self, ax, **args)

    def arrow(self, stuff, rect, **args):
        return annotations.arrow(self, stuff, rect, **args)

    def int_to_roman(self, integer, capitals=False):
        return annotations.int_to_roman(integer, capitals=capitals)

    def int_to_letter(self, integer, capitals=False):
        return annotations.int_to_letter(integer, capitals=capitals)
    
    def sci_str(self, x, **args):
        return annotations.sci_str(x, **args)
    
    def from_pval_to_star(self, x, **args):
        return annotations.from_pval_to_star(x, **args)
    
    ################################################
    ###### legend function #######################
    ################################################

    # def legend(self, list_of_lines, list_of_labels, **args):
    #     return legend.legend(list_of_lines, list_of_labels, **args)
    def legend(self, ax, **args):
        return legend.legend(self, ax, **args)

    def bar_legend(self, stuff, **args): # stuff can be either ax or fig
        return legend.bar_legend(self, stuff, **args)

    def build_bar_legend(self, X, ax, mymap, **args):
        return legend.build_bar_legend(X, ax, mymap, **args)

    def build_bar_legend_continuous(self, ax, mymap, **args):
        return legend.build_bar_legend_continuous(ax, mymap, **args)
    
    def get_linear_colormap(self, **args):
        return legend.get_linear_colormap(**args)
    
    ################################################
    ###### Axes function #######################
    ################################################
    
    def inset(self, stuff, rect=[.5,.5,.5,.4], facecolor=None):
        return inset(self, stuff, rect=rect, facecolor=facecolor)

    def adjust_spines(ax, spines, tck_outward=3, tck_length=4.,
                      xcolor='w', ycolor='w'):
        if xcolor is None:
            xcolor = self.default_color
        if ycolor is None:
            ycolor = self.default_color
        ap.adjust_spines(ax, spines, tck_outward=3, tck_length=4.,
                             xcolor=xcolor, ycolor=ycolor)

    def set_plot(self, ax, spines=['left', 'bottom'], **args):
        ap.set_plot(self, ax, spines, **args)

    def add_to_axes_args(self, xlabel, ylabel, title, axes_args):
        if xlabel is not None:
            axes_args['xlabel'] = xlabel
        if ylabel is not None:
            axes_args['ylabel'] = ylabel
        if title is not None:
            axes_args['title'] = title
        return axes_args
    
    ################################################
    ###### signal plots ########################
    ################################################
    def time_freq_plot(self, t, freqs, data, coefs, **args):
        return time_freq_plot(self, t, freqs, data, coefs, **args)

    ################################################
    ###### stat plots ########################
    ################################################

    def two_variable_analysis(self, first_observations, second_observations, **args):
        return scatter_plots.two_variable_analysis(first_observations, second_observations, cls=self, **args)

    ################################################
    ###### electrophy plots ########################
    ################################################

    def Ca_trace_plot(self, Data, **args):
        return Ca_trace_plot(self, Data, **args)

    def response_to_current_pulse(self, t, Vm, I, spikes, **args):
        return scp.response_to_current_pulse(self, t, Vm, I, spikes, **args)

    def response_to_multiple_current_pulse(self, t, VMS, II, SPIKES, **args):
        return scp.response_to_multiple_current_pulse(self, t, VMS, II, SPIKES, **args)
    
    ##################################################
    ######  FIG TOOLS   ##############################
    ##################################################
    
    def flat(self, AX):
        """
        to be used in 
        "for ax in ge.flat(AX)"
        """
        List = []
        for ax in AX:
            if type(AX) is list:
                List = List+ax
            else:
                List.append(ax)        
        return np.array(List).flatten()
    
    ##################################################
    ######  FIG OUTPUT  ##############################
    ##################################################

    def multipanel_figure(self, FIGS, **args):
        return multipanel_figure(self, FIGS, **args)

    
    def show(self, block=False):
        if platform.system()=='Windows':
            plt.show()
        elif platform.system()=='Darwin':
            plt.show(block=block)
            input('Hit Enter To Close')
            plt.close()
        else:
            plt.show()

        
    def savefig(self, fig, figname='temp.svg',
                dpi=None, transparent=None, facecolor=None):
        if dpi is None:
            dpi=self.dpi
        if transparent is None:
            transparent=self.transparency
        if facecolor is None:
            facecolor=self.facecolor
        fig.savefig(figname,
                    dpi=dpi, transparent=transparent,
                    facecolor=facecolor)
        
    def save_on_desktop(self, fig, figname='temp.svg', dpi=None):
        if figname.endswith('.png'):
            self.savefig(fig, desktop+figname, dpi=dpi)
        else:
            self.savefig(fig, desktop+figname)

    def gcf(self):
        return plt.gcf()



if __name__=='__main__':

    # fig, AX = figure(axes_extents=[\
    #                               [[3,2], [1,2] ],
    #                                [[1,1], [1,1], [2,1] ] ],
    #                  left=.3, bottom=.4, hspace=1.4, wspace=1.2,
    #                  figsize=[.8, .35])
    
    # plot(Y=[
    #     np.random.randn(20),
    #     np.random.randn(20),
    #     np.random.randn(20),
    #     np.random.randn(20)],
    #      sY=[
    #          np.ones(20),
    #          np.ones(20),
    #          np.random.randn(20),
    #          np.random.randn(20)],
    #      ax=AX[0][0],
    #      COLORS=[Red, Purple, Blue, Green],
    #      legend_args={'frameon':False},
    #      axes_args={'spines':['left']})
    
    # scatter(X=np.random.randn(4,5), Y=np.random.randn(4,5),
    #         sX=np.random.randn(4,5),sY=np.random.randn(4,5),
    #         ax=AX[1][0],
    #         bar_legend_args={},
    #         bar_label='condition')
    
    # plot(np.random.randn(20), sy=np.random.randn(20),
    #      ax=AX[1][2])
    # scatter(np.random.randn(20), sy=np.random.randn(20),
    #         ax=AX[1][2])
    # plot(np.random.randn(20), sy=np.random.randn(20),
    #         ax=AX[1][2], color=Red)
    # scatter(np.random.randn(20), sy=np.random.randn(20),
    #         ax=AX[1][2], color=Red)
    # plot(np.sin(np.linspace(0,1,30)*3*np.pi)*2,
    #      ax=AX[1][2], color=Purple)
    # plot(np.cos(np.linspace(0,1,30)*3*np.pi)*2,
    #      ax=AX[1][2], color=Green)
    
    # hist(np.random.randn(200), ax=AX[0][1],\
    #      orientation='vertical',
    #      axes_args={'ylim':AX[0][0].get_ylim(), 'spines':['left']})
    
    # AX[1][1].axis('off')
    # fig.savefig('fig.png', dpi=200)
    # save_on_desktop(fig, figname='fig.png')

    # fig2, AX = figure(axes=(2,1),
    #                   left=.4, bottom=.4, hspace=1.4, wspace=1.2,
    #                   figsize=[.45, .3])
    # import itertools
    # for i in range(2):
    #     plot(np.random.randn(20), sy=np.random.randn(20),
    #          ax=AX[i])
    # # fig2.savefig('fig2.png', dpi=200)
    # fig1, AX = figure(axes_extents=[\
    #                                [[3,1], [1,1] ],
    #                                [[1,1], [2,1], [1,1] ] ] )
    # fig2, AX = figure(axes=(2,1))
    # for ax in AX:
    #     scatter(np.abs(np.exp(np.random.randn(100))), np.abs(np.exp(np.random.randn(100))), ax=ax)
    #     set_plot(ax, yscale='log', xscale='log')
    # show()
    # print('should be 1, 1')
    # fig2, AX = figure(axes=(1,1))
    # print('should be 2, 1')
    # fig2, AX = figure(axes=(2,1))
    # print('should be 1, 2')
    # fig2, AX = figure(axes=(1,2))
    # print('should be 3, 2')
    # fig2, AX = figure(axes=(3,2))
    # # show()

    # fig, _ = figure()
    # fig, _ = plot(Y=np.random.randn(4, 10), sY=np.random.randn(4, 10),
    #               axes_args={'spines':['left', 'bottom'], 'xlabel':'my-x value', 'ylabel':'my-y value'})
    # save_on_desktop(fig, figname='2.svg')
    # show()

    # mg = graphs('ggplot_npotebook')
    # mg = graphs()
    # mg.hist(np.random.randn(100), xlabel='ksjdfh')
    
    from datavyz import ges as ge

    # ge.boxplot(np.exp(np.random.randn(100)),
    #            axes_args=dict(xticks=[1],
    #                           xticks_labels=['data']))
    
    fig_lf, AX = ge.figure(axes_extents=[[[3,1]],[[1,2],[1,2],[1,2]]], figsize=(1.,.5), wspace=3., hspace=2.)
    for ax in [item for sublist in AX for item in sublist]:
        ge.top_left_letter(ax, 'a')
    # _, ax, _ = ge.figure(with_bar_legend=True)
    AX[1][0].hist(np.random.randn(100))
    fig, ax = ge.figure()
    ax.hist(np.random.randn(100))
    ge.panel_label(ax, 'a')
    ge.annotate(ax, 'blabla', (0.7, 0.8), italic=True)
    ge.set_plot(ax)
    ge.show()


    ge.show()


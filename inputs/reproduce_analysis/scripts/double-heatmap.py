#!/usr/bin/env python3

__author__ = "Matthew Stapylton"
__copyright__ = "Copyright 2020, The Clemente Lab"
__credits__ = ["Jose C. Clemente", "Matthew Stapylton"]
__license__ = "GPL"
__version__ = "0.1-dev"
__maintainer__ = "Matthew Stapylton"
__email__ = "mkstapylton@gmail.com"

import click
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import gcf
from modules.pandas_utils import filter_by_col_val
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import pyplot as plt


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1')
@click.option('-n', '--name',
              required=True,
              help='Name for the heatmap filename: "name"_heatmap.png')
@click.option('-p', '--tsv_path',
              required=True,
              help='Path to input tsv file.')
@click.option('-fs', '--fig_size',
              nargs=2,
              type=int,
              default=[200, 100],
              help='Width, height of the figure: -fs 200, 100. defaults are good for powerpoint')
@click.option('-fo', '--font_size',
              help='Font size: xx-small, x-small, small, medium, large, x-large, xx-large',
              default='large')
@click.option('-hc', '--heatmap_colorscheme',
              help='color scheme for heatmap. qualitative: pastel, muted, bright, deep, colorblind, dark\n\
              circular: hls, hsul, set2, Paired\n\
              sequential uniform: rocket, mako, flare, crest, magma, viridis, rocket_r\n\
              cubehelix: cubehelix, ch:start=.2,rot=-.3, ch:start=-.2,rot=.6\n\
              divergent: vlag, icefire, Spectral, coolwarm, coolwarm_r',
              default='coolwarm')
@click.option('-tl', '--title',
              default='',
              help='Title for the heatmap, appears directly above main figure.')
@click.option('-ca', '--cluster_algorithm',
              default='average',
              help='Clustering algorithm for the heatmap:\
              average, single, complete, weighted, centroid, median, ward')
@click.option('-dm', '--distance_metric',
              default='euclidean',
              help='Distance metric for the heatmap: braycurtis, canberra, chebyshev, cityblock,\n\
              correlation, cosine, dice, euclidean, hamming, jaccard, jensenshannon, kulsinski,\n\
              mahalanobis, matching, minkowski, rogerstanimoto, russellrao, seuclidean, sokalmichener,\
              sokalsneath, sqeuclidean, yule')
@click.option('-z_score', '--z_score',
              default=None,
              type=int,
              help='Recalculate values as z-scores. Either 0 for rows or 1 for columns.')
@click.option('-c', '--cluster',
              is_flag=True,
              help='use clustermap instead of regular heatmap, add this flag if using any other clustering settings')
@click.option('-rc', '--row_cluster',
              is_flag=True,
              help='Flag to cluster rows')
@click.option('-cc', '--col_cluster',
              is_flag=True,
              help='Flag to cluster columns')
@click.option('-rt', '--row_title',
              help='Title for y-axis',
              default='')
@click.option('-ct', '--col_title',
              default='',
              help='Title for x-axis')
@click.option('-rg', '--row_group',
              is_flag=True,
              help='Set true if there are row group values as the first row of the tsv_file')
@click.option('-rg2', '--row_group2',
              is_flag=True,
              help='Set true if there are row group values as the second row of the tsv_file')
@click.option('-cg', '--col_group',
              is_flag=True,
              help='Set true if there is are col group values as the first row of the tsv_file')
@click.option('-rgt', '--row_group_title',
              default='Title for row group if one exists',
              help='')
@click.option('-cgt', '--col_group_title',
              default='',
              help='Color scheme for col groups, see color_scheme click option for details.')
@click.option('-rgc', '--row_group_colorscheme',
              default='vlag',
              help='Colorscheme for the row groups, see color_scheme click option for details.')
@click.option('-cgc', '--col_group_colorscheme',
              default='icefire',
              help='Color scheme for column groups, see color_scheme click option for details.')
@click.option('-rf', '--row_filters',
              multiple=True,
              default=[],
              help='Filter out rows that pattern match passed strings:\n\
              -rf lactobacillus -rf bacteroidetes')
@click.option('-o', '--output_folder',
              default='./',
              help='Output folder for heatmaps')
@click.option('-s', '--scaling',
              default=3,
              type=int,
              help='font scaling for x and y axis labels')
@click.option('-t', '--transform',
              is_flag=True,
              help='transform dataframe')
@click.option('-rtx', '--rotate_ticks',
              is_flag=True,
              help='rotate x axis ticks')
def gen_heatmap(name,
                tsv_path,
                fig_size,
                font_size,
                heatmap_colorscheme,
                title,
                cluster_algorithm,
                distance_metric,
                z_score,
                cluster,
                row_cluster,
                col_cluster,
                row_title,
                col_title,
                row_group,
                row_group2,
                col_group,
                row_group_title,
                col_group_title,
                row_group_colorscheme,
                col_group_colorscheme,
                row_filters,
                output_folder,
                scaling,
                transform,
                rotate_ticks):
    """
    Wrapper for seaborn's clustermap.
    Input is a tsv file of a data table.
    The tsv_file / data table may have an additional column, row to group the data by --
    To group column values, add the groups as the first row in the tsv_file / data table.
    To group row values, add the groups as the first column in the tsv_file / data table.
    Then specify -rg or -cg to group rows and/or columns when running this script.
    The groups become color-coded in the resulting heatmap.
    """
    pd.set_option('display.float_format', lambda x: '%,g' % x)

    # set global formatting
    #sns.set_context('notebook')
    #sns.set_style("ticks")
    sns.set(font_scale=scaling)

    # For col/row groups we set a multiindex for the cols/rows of the dataframe.
    if col_group:
        df = pd.read_csv(tsv_path, sep='\t', header=[0, 1])
    else:
        df = pd.read_csv(tsv_path, sep='\t')

    if row_group:
        df.set_index([df.columns[0], df.columns[1]], inplace=True)

    # handle multiple row groups
    if row_group2:
        df.set_index(df.columns[0], inplace=True, append=True)

    if not (row_group or row_group2):
        df.set_index(df.columns[0], inplace=True)

    if transform:
        df = df.T

    # Main heatmap colorscheme
    #colormap = sns.color_palette(heatmap_colorscheme, as_cmap=True)

    colormap = LinearSegmentedColormap.from_list('my_gradient', (
    (0.000, (0.369, 0.118, 0.808)),
    (0.250, (0.773, 0.478, 0.941)),
    (0.500, (1.000, 1.000, 1.000)),
    (0.750, (1.000, 0.929, 0.475)),
    (1.000, (0.827, 0.812, 0.259))))

    df1 = df.copy()
    df2 = df.copy()

    df1 = df1.T
    df1.reset_index(inplace=True)
    df1 = filter_by_col_val(df1, ['Strain:Igha+/+'], 'filter_like')
    df1.set_index('index', inplace=True)
    df1.drop(columns='Strain', inplace=True)
    df1 = df1.T
    df1 = df1.astype(float)

    df2 = df2.T
    df2.reset_index(inplace=True)
    df2 = filter_by_col_val(df2, ['Strain:Igha-/-'], 'filter_like')
    df2.set_index('index', inplace=True)
    df2.drop(columns='Strain', inplace=True)
    df2 = df2.T
    df2 = df2.astype(float)

    vmin = min(df1.values.min(), df2.values.min())
    vmax = max(df1.values.max(), df2.values.max())

    #fig, ax = plt.subplots(figsize=fig_size, ncols=2)
    #fig, ax = plt.subplots(figsize=fig_size, ncols=3, gridspec_kw={'width_ratios': [.48,.48,.04]}, sharex=True)
    #fig, ax = plt.subplot_mosaic([['A', 'B', 'C'], ['A', 'B', 'D']], gridspec_kw={'width_ratios': [.48,.48,.04]},
    #                             figsize=fig_size,
    #                             constrained_layout=True)

    fig, ax = plt.subplot_mosaic([['A', 'B', 'C'], ['A', 'B', 'C'], ['A', 'B', 'D']], gridspec_kw={'width_ratios': [.48,.48,.04]},
                                 figsize=fig_size,
                                 constrained_layout=True)

    plt.subplots_adjust(wspace=.1)

    #gs = ax[1, 2].get_gridspec()
    #axsbig = fig.add_subplot(gs[1:, -1])

    ax['C'].axis('off')


    #df1 = df1.iloc[1:]
    hmap1 = sns.heatmap(df1,
                        cmap=colormap,
                        cbar=False,
                        yticklabels=df1.index,
                        ax=ax['A'], vmin=vmin, vmax=vmax,
                        xticklabels=False)

    #df2 = df2.iloc[1:]
    hmap2 = sns.heatmap(df2,
                        cmap=colormap,
                        cbar=False,
                        ax=ax['B'], vmin=vmin, vmax=vmax,
                        xticklabels=False,
                        yticklabels=False)

    #fig

    #ax[2].set(ylim=(0,.25))
    plt.colorbar(ax['A'].collections[0], cax=ax['D'], label='z_score')




    #plt.colorbar(shrink=.5)

    if title:
        #hmap1.set_title('Igha+/+', fontsize=font_size, pad=50)
        #hmap2.set_title('Igha-/-', fontsize=font_size, pad=50)
        #fig.suptitle(title, y=.95, x=.48, fontsize=font_size)

        # changes May 4th
        #fig.title(title, y=.95, x=.48, fontsize=font_size)

        # changes May 12th
        #fig.suptitle('Igha', y=.95, x=.48, fontsize=font_size, style='italic')

        #TODO: make just +/+ -/- superscript
        hmap1.set_title('Igha $^{+/+}$', fontsize=font_size, pad=100)
        hmap2.set_title('Igha $^{-/-}$', fontsize=font_size, pad=100)

    if row_title:
        hmap1.set_xlabel(row_title, fontsize=font_size)
        #hmap2.set_xlabel(row_title, fontsize=font_size)

    if col_title:
        hmap1.set_ylabel(col_title, fontsize=font_size)
        #hmap2.set_ylabel(col_title, fontsize=font_size)


    hmap1.set_xlabel('', fontsize=font_size)
    hmap1.set_ylabel('', fontsize=font_size)

    hmap2.set_xlabel('', fontsize=font_size)
    hmap2.set_ylabel('', fontsize=font_size)

    # new
    #ax[0].tick_params(axis='y', labelsize=50)
    # hmap1.set_xticklabels(hmap1.get_ymajorticklabels(), fontsize=30)


    plt.subplots_adjust(top=0.9)

    # Save figure to disk.
    fig.savefig(f'{output_folder}/{name}_heatmap.png', bbox_inches="tight")
    #fig.savefig(f'{output_folder}/{name}_heatmap.png', dpi=171, bbox_inches="tight")
    #fig.savefig(f'{output_folder}/{name}_heatmap.png', dpi=190, bbox_inches="tight")


    #fig.savefig(f'{output_folder}/{name}_heatmap.png')



if __name__ == "__main__":
    gen_heatmap()

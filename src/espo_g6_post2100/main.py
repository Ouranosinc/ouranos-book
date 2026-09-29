from pathlib import Path

import postprocess as pp
import graphics
import tables
from matplotlib import pyplot as plt
import config

from importlib import reload
reload(graphics)
reload(pp)

FIG_DIR = config.FIGS


def make_data_analysis():
    """For reference, the final data is committed to this repo."""
    # Create intermediate data - this will take more than a day to run... 
    pp.decadal_stats()

    # Create final data for graphics
    paths = Path("data").glob("qs_*.nc")
    for path in paths:
        pp.run(path)


def make_graphics():
    """Create graphics for the user guide."""
    #fig = graphics.graph_domain_map()
    #fig.savefig(FIG_DIR/f"{fig.name}.png")
    #plt.close()

    fig = graphics.graph_bukovsky_map()
    fig.savefig(FIG_DIR/f"{fig.name}.png")
    plt.close()

    fig = graphics.graph_compare_scenario_emissions()
    fig.savefig(FIG_DIR/f"{fig.name}.pdf")
    plt.close()
    
    fig = graphics.graph_ssp_cumulative_emissions()
    fig.savefig(FIG_DIR/f"{fig.name}.pdf")
    plt.close()

    fig = graphics.graph_ecs_sherwood()
    fig.savefig(FIG_DIR/f"{fig.name}.pdf")
    plt.close()

    fig = graphics.graph_espo_g6_sims()
    fig.savefig(FIG_DIR/f"{fig.name}.pdf")
    plt.close()

    #_make_ts()
    #_make_maps()


def make_tables():
    tables.save_ts_table_and_annexes()
    tables.save_maps_table_and_annexes()


def _make_ts():
    # Get spatial averages
    savg = pp.get_savg_mean(pp.merge_savg())

    # Create the interactive SVGs
    for r in savg.region:
        fig, svg = graphics.graph_guide_region_ts(savg.sel(region=r))  
        (FIG_DIR/f"annex/{fig.name}.svg").write_text(svg)
        plt.close(fig)


def _make_maps():
    # Create maps
    files = list((config.DATA / "analysis").glob("stats_*.nc"))
    for file in files:
        fig = graphics.graph_guide_maps(file)
        fig.savefig(f"{FIG_DIR}/annex/{fig.name}.png")
        plt.close(fig)


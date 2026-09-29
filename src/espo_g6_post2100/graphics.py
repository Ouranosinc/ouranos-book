import io
import json
import re
from pathlib import Path
import datetime as dt
import numpy as np
import xarray as xr
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.transforms as mtransforms
import matplotlib.patches as mpatch
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.axes_grid1 import make_axes_locatable
import xml.etree.ElementTree as ET
from cartopy import crs as ccrs
from cartopy import feature as cfeature
import geopandas as gpd
import shapely.geometry as sg

import pandas as pd
import geopandas as gpd
from collections import defaultdict
from dpca.io import ssp_emissions, gcb, sherwood, zelinka

from styling import ecolors, elabels, context
import config


"""
Graphics:
 - ``graph_ssp_cumulative_emissions``: Cumulative CO₂ emissions for SSP scenarios.
 - ``graph_compare_scenario_emissions``: Comparison of scenario emissions between CMIP5 and CMIP6.
 - ``graph_ecs_sherwood``: ECS posterior based on Sherwood et al. with Zelinka's ECS for the ESPO models.
 - ``graph_domain_map``: Domain map
 - ``graph_bukovsky_map``: Bukovsky regions.
 - ``graph_guide_region_ts``: Time series of spatial averages
 - ``graph_guide_maps``: Maps of absolute min/max values

Note that the time series graphic includes SVG interactivity. 
I first create the figure elements, then save the figure in SVG and 
edit that SVG to add interactivity (tooltips, clickable legend items).
"""

@mpl.rc_context(context)
def graph_espo_g6_sims():
    """Graph number of ESPO-G6-C3-P2100 simulations per year from 2005 to 2300, color-coded by scenario."""
    with open(config.DATA / "espo-g6-p2100_attributes.json") as f:
        attrs = json.load(f)

    data = []
    for attr in attrs["meta"].values():
        a = attr["attrs"]
        record = (a["source"], a["experiment"], a["member"], attr["datetime_start"], attr["datetime_end"])
        data.append(record)
    
    df = pd.DataFrame(data, columns=["source", "experiment", "member", "datetime_start", "datetime_end"]).drop_duplicates()
    df = df.set_index(["source", "experiment", "member"])
    
    df =  df.map(lambda x: np.datetime64(x, "D"))
    
    ind = df.index.remove_unused_levels()
    sources, exps, member_ids = ind.levels
    sources = sources.sort_values()
    
    # Figure
    fig, axes = plt.subplots(ncols=len(exps), nrows=len(sources), figsize=(6.5, 3), sharex=True)
    fig.subplots_adjust(hspace=0.6, wspace=0.3, right=.98, left=0.2, bottom=.15, top=.92)
    fax = fig.add_axes([0, 0, 1, 1], frame_on=False)

    for i, exp in enumerate(exps):
        for j, source in enumerate(sources):
            ax = axes[j, i]

            if j == len(sources) - 1:  # X-axis
                strip_ax(ax)
                ax.spines['bottom'].set_position(("outward", 10))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            else:            # Labels and titles
                ax.set_axis_off()

            try:
                row = df.loc[source].loc[exp]
                member = row.index.values.item()
                x = row[["datetime_start", "datetime_end"]].values[0]
                c = ecolors[exp]
                ax.plot(x, [1, 1], color=c, lw=3)
            except Exception:
                pass
            
    for i, source in enumerate(sources):
        axes[i, 0].text(-.1, .25, source, transform=axes[i, 0].transAxes, ha='right',)

        # A fancy box with round corners. pad=0.1
        add_fancy_patch_around(axes[i,0], fax, boxstyle="round,pad=0.01")

    for j, exp in enumerate(exps):
        axes[0, j].set_title(elabels[exp], fontsize="medium", color=ecolors[exp], weight="bold", y=1.1)

    ax.set_xticks(["2100", "2200", "2300"])
    ax.set_xticklabels(["      2100", "", "2300      "])
    ax.set_xlim(dt.datetime(2100, 1, 1), dt.datetime(2300, 1, 1))
    fig.name = "graph_espo_g6_sims"
    return fig


@mpl.rc_context(context)
def graph_ssp_cumulative_emissions():
    obs = gcb.load().sel(time=slice("1850", None))
    e6 = ssp_emissions.load().sel(time=slice("1850", "2300"))

    co = obs.cumsum(dim="time")
    c6 = e6.resample(time="YE").asfreq().interpolate_na(dim="time").cumsum(dim="time")

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 3))
    ax.plot(co.time.dt.year, co.values, '-', lw=1.5, color="k",  label="Observations", zorder=10)
    for i, exp in enumerate(['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp460', 'ssp534-over', 'ssp585']):
        y = c6.sel(experiment_id=exp)
        ax.plot(y.time.dt.year, y.values, '-', lw=1, color=ecolors[exp], label=elabels[exp])
    ax.legend(loc="upper left", bbox_to_anchor=(.01, 1.03), frameon=False, ncol=1,
              fontsize="small", handlelength=1.5, handletextpad=0.3, borderaxespad=0, columnspacing=.5, 
              title="Emission pathways")
    ax.set_ylabel("Cumulative CO₂ emissions (PgC)")
    fancy(ax)
    ax.set_xlim(1850, 2300)
    fig.name = "graph_ssp_cumulative_emissions"
    return fig


@mpl.rc_context(context)
def graph_compare_scenario_emissions(lang="en", show_rcp=True):
    """Graphic comparing scenario concentrations between CMIP5 and CMIP6."""
    
    obs = gcb.load().sel(time=slice("1960", None))
    
    da6 = e6 = ssp_emissions.load().sel(time=slice("2015", "2300"))
    lw = 1

    
    ssps = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp460', 'ssp534-over', 'ssp585']

    with plt.rc_context(context):

        fig, ax = plt.subplots(1, 1, figsize=(6.5, 3))
        fig.subplots_adjust(left=.08, right=.95, bottom=.08, top=.905)

        # Obs
        h5 = ax.plot(obs.time.dt.year, obs.values, '-', lw=1.5, color="k",  label="Observations", zorder=-10)

        # SSPs
        h6 = []
        for i, exp in enumerate(ssps):
            y = da6.sel(experiment_id=exp)
            h6.extend(ax.plot(y.time.dt.year, y.values, '-', lw=lw, color=ecolors[exp], label=elabels[exp]))

        l6 = ax.legend(h6, [h.get_label() for h in h6], loc="upper left", bbox_to_anchor=(.87, 1.00), frameon=False, ncol=1,
                  fontsize=8, handlelength=1.5, handletextpad=0.3, borderaxespad=0, columnspacing=.5)

        if lang == "en":
            ax.set_ylabel("CO₂ emissions (PgC)")
        elif lang == "fr":
            ax.set_ylabel("Émissions de CO₂ (PgC)")

        fancy(ax)
        ax.axvline(2100, ymax=1, color="#3B3B3B", lw=1, clip_on=False, alpha=1)
        yt = 1.05
        trans = mpl.transforms.blended_transform_factory(ax.transData, ax.transAxes)
        ax.set_xlim(1950, 2300)
        ax.text(2095, yt, "IAM emissions", transform=trans, ha="right", color="w", fontsize=10)
        ax.text(2105, yt, "Stylized emissions", transform=trans, ha="left", color="w", fontsize=10)
        ax.axvspan(2005, 2100-1, yt-.02, yt+.06, zorder=-10, color='#3B3B3B', clip_on=False)
        ax.axvspan(2100+1, 2300, yt-.02, yt+.06, zorder=-10, color='#3B3B3B', clip_on=False)
        fig.name = "graph_compare_scenario_emissions"
        return fig
    

@mpl.rc_context(context)
def graph_ecs_sherwood():
    """Graph the ECS values of the ESPO ensemble along with the ECS posterior from Sherwood."""

    # Load ECS values for ESPO models
    ecs = zelinka.load()
    models = ["CanESM5", "CNRM-ESM2-1", "ACCESS-CM2", "ACCESS-ESM1-5", "EC-Earth3-Veg", "UKESM1-0-LL", "MRI-ESM2-0", "NorESM2-MM"]
    sub = {model: ecs.loc[model].item() for model in models}

    # Load Sherwood ECS posterior
    pdf = xr.DataArray(sherwood.load()["pdf"])

    fig = plt.figure(figsize=(455/72, 4))
    fig.subplots_adjust(right=.99, top=0.97, left=.1)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(pdf.ECS, pdf.values, color="k", lw=1.5)

    x0 = 3
    xy = {model: (x0, 0) for model in sub}  # Example offsets for annotations
    xy["ACCESS-CM2"] = (x0, 2)  # Adjust annotation offset for ACCESS-CM2 if needed
    xy["CNRM-ESM2-1"] = (x0, -2)  # Adjust annotation offset for CNRM-ESM2-1 if needed
    xy["UKESM1-0-LL"] = (x0, 1)  # Adjust annotation offset for UKESM1-0-LL if needed    
    xy["CanESM5"] = (x0, -15)  # Adjust annotation offset for CanESM5 if needed

    # For each model, plot a marker on the pdf and annotate with the model name.
    for model, value in sub.items():
        y = pdf.interp(ECS=sub[model])
        ax.plot([sub[model]], y, "ko", markerfacecolor="w")
        ax.annotate(model, 
                    (sub[model], pdf.sel(ECS=sub[model], method="nearest")), 
                    xytext=xy[model], textcoords="offset points", 
                    fontsize=8, ha="left", va="bottom")

    # Show AR6 likely range in IPCC blue
    ax.axvspan(2.5, 4, color="#1f77b4", alpha=0.3, edgecolor="none")  # AR6 likely range in IPCC blue
    ax.text(3.25, 0.1*ax.get_ylim()[1], "AR6 likely range\n2.5–4°C", color="k", fontsize=9, ha="center")

    ax.set_xlabel("Equilibrium Climate Sensitivity (°C)")
    ax.set_ylabel("Probability density (°C$^{-1}$)")
    ax.set_xlim(1, 7.5)
    fancy(ax)
    fig.name = "graph_ecs_sherwood"
    return fig


@mpl.rc_context(context)
def graph_domain_map():
    """Map of domain, showing elevation."""

    fig = plt.figure(figsize=(4, 4))
    fig.subplots_adjust(left=0.0, right=1, top=1, bottom=.05)
    
    url = "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/dodsC/datasets/simulations/bias_adjusted/cmip6/ouranos/ESPO-G/ESPO-G6-post2100v1.0/day_ESPO-G6-post2100_v1.0_CMIP6_ScenarioMIP_NAM-C3_MRI_MRI-ESM2-0_ssp126_r1i1p1f1_1950-2300.ncml"
    # Map
    with xr.open_dataset(url) as ds:

        rotp = ccrs.RotatedPole(
            pole_longitude=ds.rotated_pole.grid_north_pole_longitude,
            pole_latitude=ds.rotated_pole.grid_north_pole_latitude,
        )
        ortho = ccrs.Orthographic(central_longitude=-110, central_latitude=65)
        pc = ccrs.PlateCarree()

        rlon, rlat = np.meshgrid(ds.rlon, ds.rlat)
        p = grid_boundary(rlon, rlat, rotp) 
        gb = split_across_dateline(p, kind="dateline")

        ax = fig.add_subplot(1, 1, 1, projection=ortho)
        style_basemap(ax, True, True)

        da = ds.orog
        m = ax.pcolormesh(da.rlon, da.rlat, da, transform=rotp, zorder=10, cmap="terrain")

    divider = make_axes_locatable(ax)
    ax_cb = divider.append_axes("bottom", size="5%", pad=0.1, axes_class=plt.Axes)
    fig.add_axes(ax_cb)
    gb.plot(ax=ax, transform=pc, facecolor="none", edgecolor="gray", aspect=None, lw=1.5)

    
    cb = plt.colorbar(mappable=m, cax=ax_cb, orientation="horizontal")
    cb.set_label("Elevation (m)")
    fig.tight_layout()
    fig.name = "graph_domain_map"
    return fig


@mpl.rc_context(context)
def graph_bukovsky_map():
    """Map of the Bukovski regions."""

    fig = plt.figure(figsize=(4, 4))
    fig.subplots_adjust(left=0.01, right=.99, top=.99, bottom=.01)
    
    rotp = ccrs.RotatedPole(
        pole_longitude=87.59703130293302,
        pole_latitude=31.758312454493154,
    )
    
    ax = fig.add_subplot(1, 1, 1, projection=rotp)
    
    # Bukovksi region
    buk = gpd.read_file(config.DATA / "bukovsky.geojson").to_crs(rotp)
    buk.plot(ax=ax, facecolor="#314D2E", edgecolor="white", alpha=.2, lw=2)
    buk.apply(lambda row: ax.annotate(text=row["region"], 
                                      xy=(row.geometry.representative_point().x, row.geometry.representative_point().y), 
                                      xycoords='data', 
                                      ha="center", 
                                      fontsize=7), 
                                      axis=1)

    style_basemap(ax, gridlines=False, coastlines=True)
    fig.name = "graph_bukovsky_map"
    return fig


@mpl.rc_context(context)
def graph_guide_region_ts(ds):
    
    pat = r"(?<=\d)-(?=\d)"
    
    fig, axes = plt.subplots(2, 1, 
                             sharex=True,
                             figsize=(7, 6), 
                             layout="constrained")
    
    # Unique models
    models = sorted(list(set(ds.source.data)))
    
    # Legend controls (keyed by legend id)
    controls = defaultdict(list)
    
    for ax, var in zip(axes, ["tas", "pr"]):
        for key in models:
            # Do not plot the 2300 decade, since there's only one year in the best case.
            da = ds.data_vars[var].sel(source=key).sel(decade=slice(None, "2290"))
            for exp in da.experiment:
                
                l = ax.plot(da.decade, da.sel(experiment=exp), color=ecolors[exp.item()], lw=2)
                gid = f"line_{var}_{key}_{exp.item()}"
                l[0].set_gid(gid)
                controls[key].append(gid)
                
        fancy(ax)
        ax.set_ylabel(f"{da.attrs["long_name"]} ({da.attrs["units"]})")

    # Model legend
    source_proxy_handles = [mpl.lines.Line2D([], [], color="gray") for key in models]
    leg = fig.legend(source_proxy_handles, [re.sub(pat, ".", m) for m in models], frameon=False, loc="outside right upper")
    leg.set_title("Models")
    leg._legend_box.align = "left"
        
    # SSP legend
    exps = ["ssp126", "ssp245", "ssp370", "ssp534-over", "ssp585"]
    exp_proxy_handles = [mpl.lines.Line2D([], [], color=ecolors[exp]) for exp in exps]
    exp_labels = [elabels[exp] for exp in exps]
    sleg = axes[0].legend(exp_proxy_handles, exp_labels, frameon=False, loc="upper left")
    sleg.set_title("Experiments")
    sleg._legend_box.align = "left"
    
    fig.name = f"graph_guide_region_ts_{ds.region.item()}"
    
    svg = interactive_legend_control_svg(fig, leg, controls)
    return fig, svg


def graph_guide_maps(path) -> plt.Figure:
    """Maps of max(tasmax), min(tasmin), max(pr) over entire time series."""
    fig = plt.figure(figsize=(7,8))
    gs = fig.add_gridspec(nrows=4, ncols=3)
    fig.subplots_adjust(left=0, right=1, hspace=0.1, wspace=.05, bottom=0, top=.95)
    cbar_kwargs={"orientation": "horizontal", "shrink": .7, "pad": 0.01, "fraction":.08, "extend": "both"}
    
    labels = {"min_tasmin": "Min(T)", "max_tasmax": "Max(T)", "max_pr": "Max(P)"}
    
    with xr.open_dataset(path, chunks="auto") as ds:
        rotp = ccrs.RotatedPole(
            pole_longitude=ds.rotated_pole.grid_north_pole_longitude,
            pole_latitude=ds.rotated_pole.grid_north_pole_latitude,
        )
        for i, (key, da) in enumerate(ds.data_vars.items()):
            
            if "tas" in key:
                da -= 273.15
                label = "T (°C)"
                if "tasmin" in key:
                    cmap = plt.cm.Blues_r
                if "tasmax" in key:
                    cmap = plt.cm.Reds
            else:
                da *= 3600* 24
                label = "P (mm/d)"
                cmap = plt.cm.viridis
    
            #norm = mpl.colors.Normalize(np.nanmin(da), np.nanmax(da))
            norm = PercentileNorm(da, .5, 99.5)
            
            axes = []
            for j, season in enumerate(["DJF", "MAM", "JJA", "SON"]):
                ax = fig.add_subplot(gs[j, i], projection=rotp)
                axes.append(ax)
                x = da.sel(season=season)
                
                ax.coastlines()
                im = x.plot(ax=ax, transform=rotp, norm=norm, cmap=cmap,
                            add_colorbar=False,
                           )
                
                ax.set_frame_on(False)
            
                if i == 0:
                    ax.text(-0.1, 0.5, season, 
                            va='center', ha='center', 
                            rotation='vertical', 
                            transform=ax.transAxes) 
        
                if j == 0:
                    ax.set_title(labels[key])
                else:
                    ax.set_title("")
    
            cb = plt.colorbar(im, ax=axes, **cbar_kwargs)
            cb.set_label(label)
            
        
        fig.name = f"graph_guide_maps_{path.stem}"
        
        return fig


class PercentileNorm(mpl.colors.Normalize):
    def __init__(self, data, low_percentile=1, high_percentile=99, clip=False):
        """
        Normalize data based on percentiles to handle heavy outliers.
        """
        # Calculate the value thresholds matching the target percentiles
        vmin = np.nanpercentile(data, low_percentile)
        vmax = np.nanpercentile(data, high_percentile)
        
        # Initialize the base class with calculated vmin and vmax
        super().__init__(vmin=vmin, vmax=vmax, clip=clip)


def _legend_controls(fig, legend, ids):
    """Add transparent box covering the legend handle and text.
     
    This acts as a button that users can click on. Without this, we need
    to click precisely on the legend handle or label letters."""
    
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    handles = list(legend.legend_handles)
    labels = list(legend.texts)

    # Set ids to legend handles and labels
    handle_gids = [f"legend-handle-{gid}" for gid in ids]
    label_gids = [f"legend-label-{gid}" for gid in ids]

    for artist, gid in zip(handles + labels, handle_gids + label_gids):
        artist.set_gid(gid)

    # Create control boxes over legend handles and labels
    control_gids = []
    for handle, label, gid in zip(handles, labels, ids):
        bounds = mtransforms.Bbox.union([
            handle.get_window_extent(renderer),
            label.get_window_extent(renderer),
        ]).padded(3)
        bounds = bounds.transformed(fig.transFigure.inverted())
        control = mpatch.Rectangle(
            (bounds.x0, bounds.y0),
            bounds.width,
            bounds.height,
            transform=fig.transFigure,
            facecolor="white",
            edgecolor="none",
            alpha=0.5,
            clip_on=False,
            zorder=legend.get_zorder() + 1,
        )
        control.set_gid(gid)
        control_gids.append(gid)
        fig.add_artist(control)
        
    return control_gids, handle_gids, label_gids


def interactive_legend_control_svg(fig, legend, targets) -> str:
    """Create an interactive SVG version of the figure with legend controls.
    
    Parameters
    ----------
    fig : plt.Figure
      Figure object containing the plot.
    legend : matplotlib.legend.Legend
      Legend object
    targets : dict
      Dictionary mapping legend entries to target element IDs in the SVG. The user is responsible
      for assigning unique target IDs for every plot element in `fig` that needs to be toggled. Note 
      that `targets` keys will be displayed as tooltips for the plot elements.


    Returns
    -------
    str
      SVG representation of the figure with interactive legend controls.
    """

    # Create the legend control boxes over the legend handles and labels
    # Creates the ids for legend controls based on the `targets` keys.
    control_gids, handle_gids, label_gids = _legend_controls(fig, legend, list(targets.keys()))

    # Save fig to SVG
    svg_buffer = io.BytesIO()
    fig.savefig(svg_buffer, format="svg")

    # Parse the SVG as an XML tree
    svg_namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root, elements = ET.XMLID(svg_buffer.getvalue())

    # Adjust the SVG root element to be responsive when included in HTML
    root.set("width", "100%")
    root.attrib.pop("height", None)
    root.set("style", "width: 100%; height: auto; display: block")
    root.set("preserveAspectRatio", "xMidYMid meet")

    # For each legend entry, assign control and target classes and attributes
    for gid, handle_gid, label_gid, control_gid in zip(
        targets.keys(), handle_gids, label_gids, control_gids
    ):
        # Sanity check
        target_gids = tuple(targets[gid])
        required_gids = target_gids + (handle_gid, label_gid, control_gid)
        missing_gids = [gid for gid in required_gids if gid not in elements]
        if missing_gids:
            raise ValueError(f"SVG does not contain elements {missing_gids!r}")

        # Set toggle classes
        for target_gid in target_gids:
            elements[target_gid].set("class", "toggle-target")
        elements[handle_gid].set("class", "toggle-legend-part")
        elements[label_gid].set("class", "toggle-legend-part")

        # Tooltips
        for target_gid in target_gids:
            for path in elements[target_gid].iter(f"{{{svg_namespace}}}path"):
                title = ET.Element(f"{{{svg_namespace}}}title")
                title.text = gid
                path.insert(0, title)
                path.set("pointer-events", "stroke")

        control = elements[control_gid]
        control.set("class", "toggle-control")
        control.set("data-target", json.dumps(target_gids))
        control.set("data-handle", handle_gid)
        control.set("data-label", label_gid)
        control.set("role", "button")
        control.set("tabindex", "0")
        control.set("aria-controls", " ".join(target_gids))
        control.set("aria-pressed", "true")

    style = root.find('.//{http://www.w3.org/2000/svg}style')
    style.text += """
        .toggle-control { cursor: pointer; pointer-events: all; }
        .toggle-control path { fill: transparent !important; stroke: none !important; pointer-events: all; }
        .toggle-control:hover path, .toggle-control:focus path { stroke: #555 !important; stroke-dasharray: 2 2; stroke-width: 1.5;}
        .toggle-target.is-hidden { display: none; }
        .toggle-legend-part.is-hidden { opacity: 0.35; }
    """
    root.insert(0, style)

    script = """
        <script type="text/ecmascript">
        <![CDATA[
        document.querySelectorAll('.toggle-control').forEach(function (control) {
            var targets = JSON.parse(control.dataset.target).map(function (id) {
                return document.getElementById(id);
            });
            var handle = document.getElementById(control.dataset.handle);
            var label = document.getElementById(control.dataset.label);
            
            function toggle() {
                var hidden = targets.some(function (target) {
                    return !target.classList.contains('is-hidden');
                });

                targets.forEach(function (target) {
                    target.classList.toggle('is-hidden', hidden);
                });
                
                handle.classList.toggle('is-hidden', hidden);
                label.classList.toggle('is-hidden', hidden);
                control.setAttribute('aria-pressed', String(!hidden));
                console.log(handle)
            }
            control.addEventListener('click', toggle);
            control.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    toggle();
                }
            });
        });
        ]]>
        </script>
    """
    root.append(ET.XML(script))
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def fancy(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()


def strip_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_yticks([])
    ax.get_xaxis().tick_bottom()


def add_fancy_patch_around(ax, fax, **kwargs):
    bb = ax.get_position()
    bb.x0 = 0.02
    bb.x1 = 0.98
    kwargs = {
        'facecolor': (0, 0.0, 0, 0.05),
        'edgecolor': (0, 0, 0, 0.15),
        'lw': .5,
        **kwargs
    }
    fancy = FancyBboxPatch(bb.p0, bb.width, bb.height, clip_on=False, **kwargs)
    fax.add_patch(fancy)
    return fancy


def style_basemap(ax, gridlines=False, coastlines=False):    
    # Ocean color for maps
    oc = "#e7f1f6"

    # 0.035 inches = 0.09mm -> 
    if coastlines:
        ax.coastlines(linewidth=.5, color="#000000", zorder=6 * gridlines)
    
    if gridlines:
        gl = ax.gridlines(draw_labels=False, linewidth=0.5, color="gray", alpha=1, zorder=-1)
        gl.top_labels = False
        gl.bottom_labels = False
        gl.right_labels = False
        gl.xlines = False
        gl.ylabel_style = {'size': 7, 'color': 'gray'}

    ax.add_feature(cfeature.LAND, facecolor="white", zorder=-1 + 6 * gridlines)
    ax.add_feature(cfeature.OCEAN, facecolor=oc, zorder=-2)


def grid_boundary(lon: xr.DataArray, lat: xr.DataArray, proj) -> gpd.GeoDataFrame:
    """Return boundary of grid as a GeoDataFrame."""
    # Get the coordinates of the boundarys of the domain
    blon = np.concat([lon[0, :], lon[:, -1], lon[-1, ::-1], lon[::-1, 0]])
    blat = np.concat([lat[0, :], lat[:, -1], lat[-1, ::-1], lat[::-1, 0]])

    poly = sg.Polygon(zip(blon, blat))
    return gpd.GeoDataFrame(geometry=[poly], crs=proj, index=["grid"])


def split_across_dateline(geom: gpd.GeoDataFrame, kind="dateline") -> sg.MultiPolygon:
    """Split a geometry across the dateline if it intersects it, and return the resulting geometry in lat/lon."""


    npole = sg.Point(-180, 90)
    spole = sg.Point(-180, -90)
    equator = sg.Point(-180, 0)

    # Create the shape describing the map contour
    if kind == "np":
        proj = ccrs.NorthPolarStereo()
        cut = gpd.GeoSeries(sg.LineString([npole, equator]), crs="EPSG:4326")
        buffer=1000
    elif kind == "sp":
        proj = ccrs.SouthPolarStereo()
        cut = gpd.GeoSeries(sg.LineString([spole, equator]), crs="EPSG:4326")
        buffer=1000
    elif kind == "dateline":
        proj = ccrs.PlateCarree(central_longitude=180)
        cut = gpd.GeoSeries(sg.LineString([npole, spole]), crs="EPSG:4326")
        buffer=.1
    else:
        return geom.to_crs("EPSG:4326")
    
    # Project the cut line to a projection where the domain will look flat and continuous
    mask = cut.to_crs(proj).buffer(buffer, resolution=64)

    # Intersect the cut line with the domain geometry, and if it intersects, split it into two parts.
    poly = geom.to_crs(proj)
    if poly.intersects(mask, align=False).any():
        poly = poly.difference(mask, align=False).segmentize(1000)
    
    # Project back to lat/lon   
    return gpd.GeoDataFrame(geometry=poly.to_crs("EPSG:4326"))
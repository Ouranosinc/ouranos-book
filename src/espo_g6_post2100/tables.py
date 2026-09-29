# Create tables for the user guide.
from collections import defaultdict
import re
import textwrap
import geopandas as gpd
import config
from styling import elabels

def save_ts_table_and_annexes():
    """Save the table to be included in the user guide linking to 
    time series figures.
    
    Print the markdown to display the regional means over 
    the bukovsky regions.
    
    Note that the SVG is included in an iframe.
    To render in pdf using typst, remove the iframe and set the figure path as usual.

    I think the solution would be to generate two appendix file, one for html and 
    one for pdf, then select them using 
    
    +++{"no-pdf": true}
    ```{include} annex_figs_ts_html.md
    ```
    +++
    +++{"no-pdf": false}
    ```{include} annex_figs_ts_pdf.md
    ```
    +++
    """

    html_template = textwrap.dedent(
        """
        ### {region}

        :::{{figure}}
        :label: fig-ts-{region}
        :width: 95%

        <iframe src="/annex/graph_guide_region_ts_{region}.svg"/>
        
        Decadal mean time series of temperature and precipitation over the {region} region.
        :::
        ```{{raw}} typst
        #pagebreak()
        ```
        """
    )

    pdf_template = textwrap.dedent(
        """
        ### {region}

        :::{{figure}} figs/annex/graph_guide_region_ts_{region}.svg
        :label: fig-ts-{region}
        :width: 95%

        Decadal mean time series of temperature and precipitation over the {region} region.
        :::
        ```{{raw}} typst
        #pagebreak()
        ```
        """
    )

    buk = gpd.read_file(config.DATA / "bukovsky.geojson")
    r = list(buk["region"])

    # Markdown table with links to figures
    out = textwrap.dedent(
    """
    :::{table}
    :label: table-fig-ts

    Links to the time series figures for each Bukovsky region.

    | Regions | Figure | | Regions | Figure |
    | --- | --- | --- | --- | --- |
    """)

    for i in range(len(buk)//2):
        out += f"| {r[i]} | @fig-ts-{r[i]} || {r[i + len(buk)//2]} | @fig-ts-{r[i + len(buk)//2]} |\n"

    out += ":::\n"
    (config.DOCS / "table_fig_ts.md").write_text(out)
    

    # Appendix with figure directives
    with open(config.DOCS / "annex_figs_ts_html.md", "w") as f:
        for region in buk["region"]:
            f.write(html_template.format(region=region))

    with open(config.DOCS / "annex_figs_ts_pdf.md", "w") as f:
        for region in buk["region"]:
            f.write(pdf_template.format(region=region))


def save_maps_table_and_annexes():
    """Print the table with the links to the maps."""
    
    pat = r"(?<=\d)-(?=\d)"

    _sims = [('ACCESS-CM2', 'ssp585'),
            ('ACCESS-ESM1-5', 'ssp126'),
            ('CanESM5', 'ssp126'),
            ('CanESM5', 'ssp585'),
            ('CanESM5', 'ssp534-over'),
            ('CNRM-ESM2-1', 'ssp534-over'),
            ('ACCESS-ESM1-5', 'ssp585'),
            ('EC-Earth3-Veg', 'ssp126'),
            ('EC-Earth3-Veg', 'ssp245'),
            ('EC-Earth3-Veg', 'ssp370'),
            ('EC-Earth3-Veg', 'ssp585'),
            ('UKESM1-0-LL', 'ssp126'),
            ('UKESM1-0-LL', 'ssp585'),
            ('MRI-ESM2-0', 'ssp126'),
            ('MRI-ESM2-0', 'ssp534-over'),
            ('MRI-ESM2-0', 'ssp585'),
            ('NorESM2-MM', 'ssp585')]

    sims = defaultdict(list)
    
    for source, exp in _sims:
        sims[source].append(exp)

    template = textwrap.dedent(        
            """
            :::{{figure}} figs/annex/graph_guide_maps_stats_qs_{source}_{exp}.png
            :label: fig-map-{source}-{exp}
            :width: 95%
                
            Maps of extreme daily temperature and precipitation per season over the entire simulation.
            :::
            ```{{raw}} typst
            #pagebreak()
            ```
            """
        )
    
    out = ""
    for source, exps in sims.items():
        out += f"### {re.sub(pat, '.', source)}\n\n"
        
        for exp in exps:
            out += f"#### {elabels[exp]}\n\n"
            out += template.format(source=source, exp=exp)
            out += "\n"

    with open(config.DOCS / "annex_figs_maps.md", "w") as f:
        f.write(out)
            
    
    out = textwrap.dedent(
        """
        :::{table}
        :label: table-fig-maps

        Links to the map figures for each Bukovsky region.

        | Models | SSP1-2.6 | SSP2-4.5 | SSP3-7.0 | SSP5-3.4-OS | SSP5-8.5 |
        | --- | --- | --- | --- | --- | --- |
        """
    )

    for source, exps in sims.items():
        out += f"| {re.sub(pat, '.', source)} "
        for exp in ["ssp126", "ssp245", "ssp370", "ssp534-over", "ssp585"]:
            if exp in exps:
                out += f"| @fig-map-{source}-{exp} "
            else:
                out += "| "
        out += "|\n"

    out += ":::"

    with open(config.DOCS / "table_fig_maps.md", "w") as f:
        f.write(out)


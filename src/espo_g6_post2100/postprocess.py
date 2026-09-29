import json
from pathlib import Path
import datetime as dt
import requests

from siphon.catalog import TDSCatalog
from dask.distributed import Client
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
import config
import xbitinfo as xb
import xesmf


time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)

# Source: get_xbit_info
keepbits = {"tasmax": 11, "tasmin": 11, "pr": 12}

# Link to the aggregated datasets
url = "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/datasets/simulations/bias_adjusted/cmip6/ouranos/ESPO-G/ESPO-G6-post2100v1.0/catalog.xml"


def decadal_stats():
    """Compute the decadal min, max and mean of all ESPO-G6-post2100 
    bias-adjusted simulation.
    
    This computation takes a long while, and dask is possibly not the best option
    here. A suggestion by Travis is to use ``mp.Pool``. 
    """

    # Create catalog
    cat = TDSCatalog(url)

    # Get the opendap links to each aggregated dataset
    links = [val.access_urls["OPEnDAP"] for (key, val) in cat.datasets.items()]

    # Create data directory if it doesn't exist
    Path("data").mkdir(parents=True, exist_ok=True)

    with Client(n_workers=10, threads_per_worker=1, memory_limit="4GB") as client:
        for link in links:
            with xr.open_dataset(link, decode_times=time_coder, chunks={"time": 366*10, "rlon": 50, "rlat": 50})[["tasmax", "tasmin", "pr"]] as ds:
                name = f"data/qs_{ds.attrs["source"]}_{ds.attrs["experiment"]}.nc"
                if Path(name).exists():
                    continue
                ds = ds.assign_coords(decade = ds.time.dt.year // 10 * 10)
                g = ds.groupby(["decade", "time.season"])
                mn = g.min()
                mx = g.max()
                mu = g.mean()
                out = xr.concat([mn, mu, mx], dim="stat")
                out = out.assign_coords(stat=["min", "mean", "max"])
                out.attrs = ds.attrs
                out = xb.xr_bitround(out, keepbits)
                
                out.to_compressed_netcdf(name)



def long_term_stats(ds, stats=None)->xr.Dataset:
    """Compute temporal stats over variables over entire tire series."""
    stats = stats or [("tasmin", "min"), 
             ("tasmax", "max"),
             ("pr", "max")]

    out = {}
    for i, (v, stat) in enumerate(stats):
        key = f"{stat}_{v}"
        da = ds.data_vars[v].sel(stat=stat, drop=True)
        out[key] = getattr(da, stat)(dim="decade")
        out[key].attrs["stat"] = stat

    return xr.Dataset(data_vars=out, attrs=ds.attrs)


def spatial_average(ds)->xr.Dataset:
    """Compute average over Bukosky regions."""
    geo = gpd.read_file(config.DATA / "bukovsky.geojson")

    ds = ds.cf.add_bounds(["lon", "lat"])   
    sa = xesmf.SpatialAverager(ds, geo.geometry, geom_dim_name="region")
    return sa(ds, keep_attrs=True, skipna=True).assign_coords(region=geo.region)

    
def run_all(path: Path):
    out_dir = config.DATA / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    with xr.open_dataset(path, chunks="auto") as ds:
        out = long_term_stats(ds)
        sa = spatial_average(ds.sel(stat="mean", decade=slice(None, "2290")))
        
        kb = {}
        for v in out.data_vars:
            vn = v.split("_")[1]
            kb[v] = keepbits[vn]
        
        out = xb.xr_bitround(out, kb)    
        out.to_compressed_netcdf(out_dir / "stats_" + path.name)

        sa = xb.xr_bitround(sa, keepbits)    
        sa.to_compressed_netcdf(out_dir / "savg_" + path.name)


def merge_savg():
    """Merge all spatially averaged NetCDF files into a single dataset."""
    files = list((config.DATA / "analysis").glob("savg_*.nc"))
    
    data = [] #defaultdict(list)
    for file in files:
        with xr.open_dataset(file, decode_times=time_coder) as ds:
            source = ds.attrs["source"]
            exp = ds.attrs["experiment"]
            data.append(ds.expand_dims(source=[source], experiment=[exp]).stack(sim=["source", "experiment"]))
            
    return xr.concat(data, dim="sim", join="outer")


def get_savg_mean(ds):
    """Return graphic-ready dataset of mean tas and mean pr."""
    tas = ((ds.tasmax + ds.tasmin) / 2).mean(dim="season") - 273.15
    tas.attrs["long_name"] = "Mean temperature"
    tas.attrs["units"] = "°C"
            
    pr = ds.pr.mean(dim="season") * 24 * 3600
    pr.attrs["long_name"] = "Mean precipitation"
    pr.attrs["units"] = "mm/d"

    return xr.Dataset({"tas": tas, "pr": pr})


def get_xb_info(ds):
    """Ran this on a result sample to determine the appropriate bit rounding."""
    bitinfo = xb.get_bitinformation(ds.isel(time=0), implementation="python")
    keepbits = xb.get_keepbits(bitinfo, inflevel=.99)
    return xb.xr_bitround(ds.isel(time=0), keepbits.max(dim="dim"))



def extract_file_attributes():
    """Get global attributes and start and end times from each simulation."""

    # Create catalog
    cat = TDSCatalog(url)

    # Get the opendap links to each aggregated dataset
    # Another option would be to use NCML links together with xncml.
    # resp = requests.Session().get(link)
    # xncml.Dataset.from_text(resp.text).to_cf_dict()
    links = [val.access_urls["OPEnDAP"] for (key, val) in cat.datasets.items()]

    out = {"date": str(dt.datetime.now()), "meta": {}}
    for link in links:
        with xr.open_dataset(link, decode_times=time_coder) as ds:
            out["meta"][link] = {"attrs": ds.attrs, "datetime_start": str(ds.time.values[0]), "datetime_end": str(ds.time.values[-1])}
            
    return out


def save_ds_attributes():
    attrs = extract_file_attributes()
    with open(config.DATA / "espo-g6-p2100_attributes.json", "w") as f:
        json.dump(attrs, f, indent=2)






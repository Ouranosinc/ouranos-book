# Data 

## Input data

Input data is stored on PAVICS as virtual NcML aggregations. 
See https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/datasets/simulations/bias_adjusted/cmip6/ouranos/ESPO-G/ESPO-G6-post2100v1.0/catalog.xml

## Intermediate data

Decadal min, max and mean are computed for tasmin, tasmax and pr over the full 1950–2300 period. See ``src/postprocess.py``. Intermediate data is  available in David Huard's folder on [PAVICS](https://pavics.ouranos.ca/jupyter/hub/user-redirect/lab/tree/mypublic/ESPO-G6-post2100/data)

## Final data

This is data required to create the figures for the user guide. It is committed to this repo using `git lfs`. You'll find the result of the post-processing of intermediate data it in ``analysis/``. 




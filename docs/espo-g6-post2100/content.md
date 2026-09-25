---
title: User Guide
abstract: ESPO-G6-post2100 is a small ensemble of climate projections over North America extending from 1950 to 2300. Using and interpreting simulations extending so far into the future comes with challenges. This guide is meant to address some of the issues users will be faced with when using projections from this ensemble. [Link to data](https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/birdhouse/disk3/ouranos/ESPO-G/ESPO-G6-post2100_v1.0/catalog.html)
subtitle: Context and issues
authors:
  - bresson
  - huard
license:
  content: CC-BY-SA-3.0
open_access: true
date: 2026-09-25
bibliography:
- main.bib
---


# Introduction

The intent of this document is to provide guidance on the use and interpretation of ESPO-G6-post2100 [@lavoie_small_2026], a relatively small ensemble of bias-adjusted climate model simulations that covers North America (see {ref}`fig:map`) over the period 1950–2300. To our knowledge, it is the first publicly available bias-adjusted CMIP6 climate projection ensemble dataset extending beyond 2100. There is comparatively little experience with the use of post-2100 simulations, and as a consequence, end-users should exercise caution using and interpreting the results. This document is meant to highlight limitations and potential pitfalls, building on an analysis of the simulations themselves and broader reflections emerging from a literature review on climate services post-2100 [@huard_systematic_2026].

:::{figure} figs/graph_guide_map.png
:label: fig:map
:width: 60%

Topography over dataset domain.
:::

The ESPO-G6-post2100 ensemble includes 17 bias-adjusted climate model simulations ({ref}`fig:SimESPO`). Raw simulations were bias-adjusted with the ESPO method [@lavoie_espo_2024] using CaSR 3.2 as the reference [@khedhaouiria_canadian_2026]. Health checks were performed to ensure a robust ensemble without corrupted data (see Section [](#evaluation)). The ensemble horizontal resolution is 10 km. The variables available in the dataset are maximum and minimum daily temperature and daily precipitation. For a more detailed dataset description, please refer to [@lavoie_small_2026].

:::{figure} figs/graph_espo-g6-c3-p2100_sims.png
:label: fig:SimESPO
:width: 95%

ESPO-G6-post2100 ensemble composition matrix.
:::


# Context

Climate projections are the result of multiple decisions made by different scientific communities with their own objectives. Generally speaking, those decisions are guided by research questions, not the delivery of services. In the emission modelling community responsible for the definition of greenhouse gas (GHG) and land-use scenarios, research questions usually revolve around what policies and socioeconomic conditions allow societies to meet emission mitigation targets. In the Earth system modelling community, scientists are motivated by seeking to understand where and why models err, how to fix discrepancies, improve model realism and how the climate responds to different GHG trajectories. The end result is that the set of available climate model projections and their driving scenarios are not ideally suited to meet operational needs for adaptation decision-making or climate risk assessments.

## Stylized concentration scenarios

Before 2100, GHG and aerosol emissions used by ScenarioMIP [@oneill_scenario_2016; @tebaldi_climate_2021] are simulated by Integrated Assessment Models (IAM), models that describe interactions between demographic, economic, technological and political trends and their influence on GHG emissions. As a result, pre-2100 emissions follow internally consistent pathways in line with the hypotheses underlying IAMs. After 2100, emissions pathways are extended on the basis of simple hypotheses, such as a steady return to zero emissions at some given year. The switch to those so-called _stylized pathways_ causes abrupt changes in emission pathways that break the internal consistency of IAMs and lead to unrealistically abrupt changes in emissions (see {ref}`fig:ssps`).

:::{figure} figs/graph_compare_scenario_emissions.png
:label: fig:ssps
:width: 95%

Observed and projected emission pathways, note the abrupt changes in emission trends in 2100.
:::

All ScenarioMIP scenarios assume that emissions drop to zero before or by 2250, in what appears to be an aspirational objective rather than an inference. As a result of this strong hypothesis, scenarios all have the same CO₂ emissions beyond 2250, discounting a source of uncertainty. While there is confidence that pre-2100 emissions do a reasonable job in capturing a wide range of plausible pathways, it is doubtful the same can be said about emissions after 2250.

## Uncertainty growth

As we go further into the future, at least three factors conspire to increase the spread between simulations and the uncertainty around climate impacts. The first two are tightly connected through a relationship between global warming ($\Delta T$) and cumulative carbon emissions ($E$). Indeed, @Matthews2009 have shown that global temperature change scales almost linearly with cumulative CO₂ equivalent emissions:

$$
\Delta T \propto \mathrm{TCRE} \times E
$$

where $\mathrm{TCRE}$ is the transient response to cumulative carbon emissions, a constant quantifying the change in global temperature as a result of cumulative carbon emissions. If the spread in cumulative emissions ($\delta E$) increases across pathways, it will lead to an increase in the spread in temperature change. And indeed, {ref}`fig:cume` shows clearly that differences in cumulative emissions grow until 2250, even as all emissions go back to zero.

:::{figure} figs/graph_ssp_cumulative_emissions.png
:label: fig:cume
:width: 95%

Cumulative CO₂ emissions for SSPs, 1850--2300. Differences between scenarios grow over time, even as all emissions return to zero.
:::

By the same principle, differences in the climate responses _across models_ grow as cumulative emissions grow. Indeed, each model has its own climate responses (TCRE) emerging out of its physics and dynamics, so a model ensemble can be characterized by its TCRE variability ($\delta$TCRE). These differences translate to a spread in global temperature change across models proportional to cumulative emissions. For all scenarios that do not engage in carbon capture, post-2100 simulations see their cumulative emissions increase, and as a result, a wider spread in ensemble statistics compared to pre-2100 climate analyses should be expected.

The third factor relates to the dynamic nature of the climate system, where numerous feedbacks compound uncertainties over long simulations. Indeed, random climate anomalies can be amplified by feedbacks, and the chance of those random anomalies occurring increases over time. Romanou et al. [@Romanou2023; @Romanou2025] also argue that extreme events could trigger tipping points, pushing the climate system into a new regime. For example, an anomalous freshwater input to the Atlantic Ocean could trigger a slowdown of the Atlantic meridional overturning circulation (AMOC), which would have a massive impact on the global climate system. As the climate system approaches those tipping points, it might become more and more difficult to make reliable climate projections into the future.

More generally, it is worthwhile to keep in mind that climate models are largely built based on our understanding of the modern historical climate. While there are paleoclimate experiments simulating warm periods in the past, observations are few to evaluate model performance. This suggests that as the climate evolves outside of historical conditions, the reliability of climate models is likely to suffer.

# Issues with CMIP6 post-2100 projections

As discussed in @huard_systematic_2026, there are very few simulations available post-2100 compared to pre-2100. This is due to the costs of running and archiving simulations over long periods, and possibly the decreasing credibility of emission scenarios. For end users of ESPO-G6-post2100, this raises a number of issues related to the small number of participating models and driving scenario choices.

## Hot model problem

@lavoie_small_2026 note that the models composing the ensemble lean towards a high equilibrium climate sensitivity (ECS, see {ref}`fig:ecs`). Indeed, the IPCC AR6 assessed the likely range of ECS as 2.5 to 4°C, and five out of the eight models in ESPO-G6-post2100 have an ECS higher than 4°C. In practice, this means that users should account for this warm bias when computing ensemble statistics. One option would be to use the approach of @cannon_impact_2024, but owing to the relatively small ensemble size, it might give undue importance to the few models below and within the likely range. Whenever possible, we rather recommend to display results from all models and keep in mind their individual ECS to make proper inferences from the results.

:::{figure} figs/graph_ecs_sherwood.pdf
:label: fig:ecs
:width: 95%

Probability distribution for the equilibrium climate sensitivity (ECS) estimated by @sherwood_assessment_2020, overlaid with the ECS of the models from the ESPO-G6-post2100 ensemble [@zelinka_mzelinkacmip56_forcing_feedback_ecs_2022].
:::

## Scenario composition

As {ref}`fig:SimESPO` illustrates, there are only three scenarios for which multiple modeling groups have published post-2100 simulations: SSP1-2.6 assuming rapid mitigation efforts and large scale carbon capture; SSP5-8.5 depicting a reversal of current mitigation policies and trends towards renewable energy; and SSP5-3.4-OS tracking SSP5-8.5 until 2040, then implementing rapid and drastic reductions in GHG emissions, in addition to aggressive carbon capture. SSP5-3.4-OS simulations are meant to support research on *overshoot* scenarios, where emissions exceed policy targets but are brougth down rapidly to meet temperature targets by the end of the century. 

None of these scenarios represent business-as-usual scenarios, nor track current trajectories particularly well. It is thus hard to argue that these scenarios reflect plausible futures, which complicates the interpretation of post-2100 projections. It can nonetheless be assumed that SSP1-2.6 and SSP5-8.5 constitute lower and upper bounds for future GHG concentrations, useful for sensitivity analyses. In the context of evaluating climate impacts and assessing adaptation actions, an adaptation that performs well under both SSP1-2.6 and SSP5-8.5 could be said to be robust to a very wide range of future climate conditions, at least until 2200. Beyond 2250, all emissions are set to zero, and the ensemble fails to capture GHG scenario uncertainty.

(evaluation)=
# Dataset evaluation
This section discusses issues with ESPO-G6-post2100 simulations. It is divided into two sections: decadal means of temperature and precipitation over Bukovsky regions (see @fig:bukovsky), and maps of absolute seasonal minima and maxima over the entire time period. 


## Regional time series

Here, time series of decadal mean temperature {math}`(\frac{t_{min} + t_{max}}{2})` and mean precipitation are shown for each of the 24 region shown in @fig:bukovsky. The actual figures are in the [](#sec:ts) appendix, simply click on the link appearing in  @table-fig-ts. 

:::{figure} figs/graph_guide_bukovski.png
:label: fig:bukovsky
:width: 60%

Regions outline from @Bukovsky2011.
:::


:::{include} ./table_fig_ts.md
:::

:::{margin}
:::{note}
Clicking on the model name in the legend toggles its visibility, and hovering over lines reveals the model name.
:::


## Extreme values

For each bias-adjusted simulation, maps of minimum daily minimum temperature, maximum daily maximum tempeature and maximum daily precipitation. The intent of those figures is to diagnose problematic model behavior. For example, some simulations project temperatures and precipitations for outside the range of plausible values. For context, @tab:records shows weather extremes over Canada, the USA and the world. Again, the actual figures appear in the [](#sec:maps) appendix, simply click on the link appread in @table-fig-maps. The colorbar values are capped at the 0.5 and 99.5 percentiles in order to damp the influence of outliers. 


:::{table} 
:label: tab:records
:align: left

Weather records from Canada, the USA and the world. Source: [Statistics Canada, Weather records](https://web.archive.org/web/20110726143617/http://www.statcan.gc.ca/kits-trousses/cyb-adc1999/ecozone/edu04_0092f-eng.htm).

| Record | Canada | United States | World |
|---|---|---|---|
| Maximum temperature | 45.0°C — Midale and Yellowgrass, Saskatchewan (July 5, 1937) | 56.7°C — Death Valley, California (July 10, 1913) | 58.0°C — Al'Azizyah, Libya (September 13, 1922) |
| Minimum temperature | −63.0°C — Snag, Yukon (February 3, 1947) | −62.1°C — Prospect Creek Camp, Alaska (January 23, 1971) | −89.6°C — Vostok, Antarctica (July 21, 1983) |
| Maximum 24-hour precipitation | 489.2 mm — Ucluelet Brynnor Mines, British Columbia (October 6, 1967) | 1,090 mm — Alvin, Texas (July 28, 1979) | 1,869.9 mm — Cilaos, Réunion Island (March 15, 1952) |
| | | | |
:::


:::{include} ./table_fig_maps.md
:::

Simulation from ACCESS-CM2 driven by SSP5-8.5 displays extremely high precipitation values around Mexico, some grid cells reaching values above 4,000 mm in a single day. UK-ESM1.0-LL SSP5-8.5 also reaches high precipitation values along the Mexican coasts. For ACCESS-ESM1.5 SSP5-8.5, a minimum temperature of about -100°C is reached on January 10, 1984, on Greenland. CanESM5 is known for its high climate sensitivity, and even though the SSP5-8.5 simulation stops in 2180, it manages to reach values above 60°C. 


# Conclusion

The ESPO-G6-post2100 ensemble is small, sparse and mostly includes simulations from SSP1-2.6 and SSP5-8.5, scenarios at the lower and upper end of the range. Most of its models have a high climate sensitivity. As a result, impact studies relying on this ensemble should take care to avoid computing ensemble means without correcting for these issues. Chances are that CMIP7 will provide more and better material to assess post-2100 climate change impacts. In the meantime, this dataset provides a gateway to explore issues around long-term adaptation. 



+++ { "part": "data_availability"}

ESPO-G6-post2100 data can be downloaded as netCDF files or streamed through the OPeNDAP protocol from this [THREDDS catalog](https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/birdhouse/disk3/ouranos/ESPO-G/ESPO-G6-post2100_v1.0/catalog.html). Eventual future changes to this URL will be propagated to @lavoie_espo-g6-post2100_2026. Users might also consider [virtual aggregations](https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/datasets/simulations/bias_adjusted/cmip6/ouranos/ESPO-G/ESPO-G6-post2100v1.0/catalog.html) for easier access.


+++ 


```{bibliography}
```


# Appendix

(sec:ts)=
## Regional time series

:::{include} annex_figs_ts.md
:::    

(sec:maps)=
## Extremes values

:::{include} annex_figs_maps.md
:::

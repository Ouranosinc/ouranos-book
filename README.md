# Ouranos technical documentation

Public docs for research projects, datasets, etc.

## Installation

```bash
mamba install -c conda-forge "jupyter-book"
```

Note that all figures (*.png, *.jpg, *.svg, *.pdf) are committed to this repo through `git lfs`. This means that only the text content is version controlled, not the graphical content. This is done to avoid cluttering the repo with multiple versions of the same figures.

To export to PDF, also install ``typst``

``bash

mamba install typst
```

## Build 

To launch an HTML web server, go into the ``docs`` directory, then run jupyter book:

```bash

jupyter book start
```
The result should be visible in your browser at http://localhost:3000


To create PDFs of individual sections, run:
```bash

jupyter book build --pdf
```



## Book configuration and content

The site-wide configuration files and content resides directly in the ``docs/`` directory. 

 * [myst.yml](./myst.yml) Site configuration 
 * [authors.yml](./authors.yml) Description of authors and their affiliations
 * [toc.yml](./toc.yml) Table of content
 * [abbreviations.yml](./abbreviations.yml) Project wide list of abbreviations / acronyms
 * [glossary.md](./glossary.md) Definitions
 * [root.md](./root.md)  Introduction to the entire document
 * [images](./images) Project wide images, e.g. logos, icons, banners, etc. 
 * [custom.css](./custom.css) Style sheet

To add a new entry to the documentation, add a directory inside ``docs/`` with markdown files and notebooks, then refer to these in the `toc.yml`. For example, the ESPO-G6-post2100 user guide and case studies are configured as:

```yaml
- title: ESPO-G6-post2100
  children:
  - file: espo-g6-post2100/intro.md
  - file: espo-g6-post2100/content.md
  - file: espo-g6-post2100/case_studies.md
```

## Interactive SVGs

It's nice to be able to include interactive content, but I find that the libraries that convert matplotlib figures into interactive HTML often mess with the rendering. One approach that preserves the original matplotlib figure is to save the figure in SVG, then add javascript functions that respond to click and hover actions. The SVG can then be inserted in the HTML, not as an image, but directly in the DOM. 

Using the jupyter-book ``{figure} fig.svg`` directive however converts SVG files into PNGs for rendering, and we lose the interactivity. The solution I found is to include the SVG using a ``<iframe>``:

```markdown
:::{figure}
:label: fig-label
:width: 95%

<iframe src="/annex/<path>.svg"/>

Caption text
:::
```

where the path is relative to the lower level directory defined in the `static_files` configuration parameter (see ``toc.yml``):

```yml
static_files: 
  - espo-g6-post2100/figs/annex
```

The issue with this approach is that the renderer does not know what size the figure is. We solve this by making sure the ``<svg>`` element has these attributes:
```xml
<svg width:"100%" preserverAspectRatio:"xMidYMid meet" style:"width: 100%; height: auto; display: block">
```
and that a ``custom.css`` includes the following rule:

```css
.relative.inline-block:has(> iframe[src*="/annex/graph_guide_region_ts_"]) {
  width: 100% !important;
  padding-bottom: 85% !important;
```
where ``width`` is set to 100%, and ``padding-bottom`` to the height/width ratio of the figure, here 85% because ``figsize=(7,6)``, and 6/7=0.857. 

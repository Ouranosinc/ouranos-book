# IPCC colors for scenarios
ecolors = {'ssp119': '#1e9684',
           'ssp126': '#1d3354',
           'ssp245': '#eadd3d',
           'ssp370': '#f21111',
           'ssp370-lowNTCF': '#f21111',
           'ssp434': '#63bde5',
           'ssp460': '#e88831',
           'ssp534-over': '#9a6dc9',
           'ssp534': '#9a6dc9',
           'ssp585': '#840b22',
           'historical': '#7E7F7F'}

# IPCC labels for scenarios
elabels = {'ssp370': 'SSP3-7.0',
        'ssp370-lowNTCF': 'SSP3-LowNTCF',
        'ssp434': 'SSP4-3.4',
        'ssp460': 'SSP4-6.0',
        'ssp119': 'SSP1-1.9',
        'ssp126': 'SSP1-2.6',
        'ssp245': 'SSP2-4.5',
        'ssp534-over': 'SSP5-3.4-OS',
        'ssp534': 'SSP5-3.4-OS',
        'ssp585': 'SSP5-8.5',
        'historical': 'Historical',
        }

# Matplotlib context for consistent styling
context = {"figure.facecolor": "w",
           "text.usetex": False,
           "font.family": "sans-serif",
           "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
           "font.size": 9.0,
           "mathtext.fontset": "stixsans",
           "mathtext.default": "rm",
           "legend.fontsize": "medium",}
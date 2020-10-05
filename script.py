# https://gitlab.com/warsquid/smallerize/-/blob/master/examples/ps1975_simulations.ipynb

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from tools import (
    simulate_multiprocessing,
    get_factor_imbalances,
    get_n_imbalances,
    plot_factor_imbalances,
    plot_n_imbalances
)

sim_results = simulate_multiprocessing(
    n_simulations=100,
    n_participants=50,
    max_factors=8
)

# Make the plots look nice
ax_style = sns.axes_style('darkgrid')
ax_style['figure.facecolor'] = "#404040"
ax_style['axes.facecolor'] = "#505050"
ax_style['axes.edgecolor'] = "#656565"
ax_style['text.color'] = "#dad0a5"
ax_style['xtick.color'] = "#dad0a5"
ax_style['ytick.color'] = "#dad0a5"
ax_style['axes.labelcolor'] = "#dad0a5"
ax_style['grid.color'] = "#606060"
ax_style['patch.edgecolor'] = "#34495e"
sns.set(context='notebook', style=ax_style, font='Ubuntu')

factor_cdf_bins = np.arange(0, 0.30 + 0.02, 0.02)
fig = plot_factor_imbalances(sim_results, factor_cdf_bins)
fig.set_size_inches(9, 4)
fig.savefig('ps1975_factor_imbalance.png',
            dpi=150,
            facecolor=ax_style['figure.facecolor'])

arm_cdf_bins = np.arange(0, 20)
fig = plot_n_imbalances(sim_results, arm_cdf_bins)
fig.set_size_inches(9, 4)
fig.savefig('ps1975_n_imbalance.png',
            dpi=150,
            facecolor=ax_style['figure.facecolor'])

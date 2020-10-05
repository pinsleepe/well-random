import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from smallerize import simulate
from smallerize import Arm, Factor, Minimizer


class SimResults:
    """
    Collects and analyses the results from a single minimizer and
    simulation, using the measures outlined in Pocock + Simon (1975).
    Note that this only works for trials with two arms and
    factors with two levels, as in the original article.
    """

    def __init__(self, minimizer, results):
        self.minimizer = minimizer
        self.results = results
        self.results_df = pd.DataFrame.from_records(results)

    def get_all_factor_imbalances(self):
        """
        Calculate ``|q_1 - q_2|``, the difference in the proportions
        assigned to the first arm within each factor
        :return: factor_name -> imbalance score dictionary
        :rtype: dict
        """
        imbalances = {}
        for factor in self.minimizer.factor_names:
            imbalances[factor] = self.get_factor_imbalance(factor)
        return imbalances

    def get_factor_imbalance(self, factor_name):
        arm1, arm2 = self.minimizer.arm_names
        grouped = self.results_df.groupby([factor_name, 'arm'])
        factor_assignments = grouped['prob'].count()
        arm_counts = factor_assignments.unstack(level='arm')
        qs = arm_counts[arm1] / (arm_counts[arm1] + arm_counts[arm2])
        imbalance = abs(qs[0] - qs[1])
        return imbalance

    def get_arm_imbalance(self):
        arm1, arm2 = self.minimizer.arm_names
        arm_counts = self.results_df.groupby('arm')['prob'].count()
        imbalance = abs(arm_counts[arm1] - arm_counts[arm2])
        return imbalance


def get_default_factors(n_factors=8) -> list:
    """
    Create n binary factors, all with levels 'A', 'B'.
    """
    factors = [
        Factor('Factor' + str(factor_num), levels=['A', 'B'])
        for factor_num in range(1, n_factors + 1)
    ]
    return factors


def get_default_arms() -> list:
    """
    Create two arms.
    """
    return [Arm('Arm1'), Arm('Arm2')]


def create_simulator(n_factors: int = 1,
                     include_pure_random: bool = True) -> simulate.SimulatedTrial:
    """
    Create a SimulatedTrial object with 3 different Minimizers ,
    each with n_factors different binary factors,
    as demonstrated in the Pocock + Simon (1975) article.

    The 3 Minimizers created are:

    - minimizer_p07: Minimization, where imbalance within
      factors is scored using the range, and the arm
      with the lowest imbalance is chosen with probability
      0.7.
    - minimizer_p10: Minimization, where imbalance within
      factors is scored using the range, and the
      preferred arm is always chosen since p = 1.0.
    - pure_random: Random assignment, each arm is chosen
      with equal probability regardless of imbalance. Can
      be disabled using ``include_pure_random=False``
      as this simulation only needs to be done once,
      not for different numbers of factors.
    """
    current_factors = get_default_factors(n_factors)

    assigners = {}

    assigners['minimizer_p07'] = Minimizer(
        factors=current_factors,
        arms=get_default_arms(),
        d_imbalance_method='range',
        probability_method='best_only',
        preferred_p=0.7
    )
    assigners['minimizer_p10'] = Minimizer(
        factors=current_factors,
        arms=get_default_arms(),
        d_imbalance_method='range',
        probability_method='best_only',
        preferred_p=1.0
    )

    if include_pure_random:
        assigners['pure_random'] = Minimizer(
            factors=current_factors,
            arms=get_default_arms(),
            d_imbalance_method='range',
            probability_method='pure_random'
        )

    sim = simulate.SimulatedTrial(
        minimizers=assigners,
        factors=current_factors
    )
    return sim


def do_one_simulation(sim_number: int, n_factors: int,
                      n_participants: int,
                      include_pure_random: bool = False):
    simulator = create_simulator(n_factors)
    results = simulator.simulate(n_participants)

    all_imbalances = []

    for minimizer_name, minimizer in simulator.minimizers.items():
        min_results = SimResults(
            minimizer,
            results[minimizer_name]
        )

        factor_imbalances = min_results.get_all_factor_imbalances()
        max_factor_imbalance = max(factor_imbalances.values())
        arm_imbalance = min_results.get_arm_imbalance()

        imbalances = {
            'SimNumber': sim_number,
            'Method': minimizer_name,
            'Factors': n_factors,
            'FactorImbalances': list(factor_imbalances.values()),
            'MaxFactorImbalance': max_factor_imbalance,
            'ArmImbalance': arm_imbalance
        }
        all_imbalances.append(imbalances)

    return all_imbalances


def simulate_multiprocessing(n_simulations: int = 100,
                             n_participants: int = 50,
                             max_factors: int = 8,
                             n_cpus: int = None):
    import multiprocessing

    if n_cpus is None:
        import psutil
        # Limit processes by number of physical cores
        # (Subtract one so we don't hog all the CPU)
        n_cpus = psutil.cpu_count(logical=False) - 1

    pool = multiprocessing.Pool(
        processes=n_cpus,
        # Limit tasks per child to avoid too much memory use
        maxtasksperchild=500
    )
    pool_results = []

    for sim_number in range(1, n_simulations + 1):
        for n_factors in range(1, max_factors + 1):
            # Only run pure random simulation on n_factors == 1
            # as results will be the same across all numbers
            include_pure_random = n_factors == 1
            sim = pool.apply_async(
                do_one_simulation,
                (sim_number, n_factors, n_participants, include_pure_random)
            )
            pool_results.append(sim)

    all_rows = []
    for sim in pool_results:
        for row in sim.get():
            all_rows.append(row)

    result_df = pd.DataFrame.from_records(all_rows)
    return result_df


def simulate_slow(n_simulations: int = 100,
                  n_participants: int = 50,
                  max_factors: int = 8):
    """
    Simulate without multiprocessing.
    """
    all_results = []

    for sim_number in range(1, n_simulations + 1):
        for n_factors in range(1, max_factors + 1):
            # Only run pure random simulation on n_factors == 1
            # as results will be the same across all numbers
            include_pure_random = n_factors == 1
            sim = do_one_simulation(sim_number, n_factors, n_participants,
                                    include_pure_random)
            for row in sim:
                all_results.append(row)

    result_df = pd.DataFrame.from_records(all_results)
    return result_df


def get_cdf(x, bins):
    """
    Return the 'cdf' as used in PS1975: the proportion of x values
    greater than each value in bins
    :param x: Array of scores (e.g. level of imbalance)
    :param bins: Array of cutpoints to evaluate the cdf at
    :return: DataFrame with two columns: 'Bin' and 'Cdf'
    """
    n = len(x)
    cdf_vals = []
    for bin_start in bins:
        cdf_val = sum(x >= bin_start) / n
        cdf_vals.append(cdf_val)

    return pd.DataFrame({
        'Bin': bins,
        'Cdf': cdf_vals
    })


def unpack_lists(lists):
    """
    Unpack a list of lists into a single list of values.
    """
    vals = []
    for current_list in lists:
        vals += current_list
    return vals


def get_factor_imbalances(sim_results, bins):
    # FactorImbalances column contains lists that need to be unpacked
    # before calculating cdf
    def _get_cdf_from_lists(lists, bins):
        x = unpack_lists(lists)
        return get_cdf(x, bins)

    grouped = sim_results.groupby(['Method', 'Factors'])
    factor_imbalances = grouped['FactorImbalances'].apply(
        _get_cdf_from_lists,
        bins=bins
    )
    # Result includes unneeded int index
    factor_imbalances.index = factor_imbalances.index.droplevel(2)
    # Make results a flat table
    factor_imbalances = factor_imbalances.reset_index()

    return factor_imbalances


def plot_factor_imbalances(sim_results, bins):
    factor_imbalances = get_factor_imbalances(sim_results, bins)
    factor_imbalances['Factors'] = factor_imbalances['Factors'].map(
        lambda n: str(n) + ' factor' + ('s' if n > 1 else '')
    )

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True)
    palette = sns.color_palette('magma', n_colors=8, desat=0.8)

    random_factor_plot = sns.lineplot(
        x='Bin',
        y='Cdf',
        data=factor_imbalances.query('Method == "pure_random"'),
        ci=None,
        ax=ax1
    )
    random_factor_plot.set_title("Purely random assignment")
    # Only label the middle plot
    random_factor_plot.set_xlabel("")

    minimizer_p07_plot = sns.lineplot(
        x='Bin',
        y='Cdf',
        hue='Factors',
        data=factor_imbalances.query('Method == "minimizer_p07"'),
        palette=palette,
        ci=None,
        ax=ax2,
        legend=False
    )
    minimizer_p07_plot.set_title("Minimization, p = 0.7")
    minimizer_p07_plot.set_xlabel("Imbalance within factors")

    minimizer_p10_plot = sns.lineplot(
        x='Bin',
        y='Cdf',
        hue='Factors',
        data=factor_imbalances.query('Method == "minimizer_p10"'),
        palette=palette,
        ci=None,
        ax=ax3,
        legend='full'
    )
    minimizer_p10_plot.set_title("Minimization, p = 1.0")
    minimizer_p10_plot.set_xlabel("")

    return fig


def get_n_imbalances(sim_results, bins):
    grouped = sim_results.groupby(['Method', 'Factors'])
    arm_imbalances = grouped['ArmImbalance'].apply(
        get_cdf,
        bins=bins
    )
    # Result includes unneeded int index
    arm_imbalances.index = arm_imbalances.index.droplevel(2)
    # Make results a flat table
    arm_imbalances = arm_imbalances.reset_index()

    return arm_imbalances


def plot_n_imbalances(sim_results, bins):
    n_imbalances = get_n_imbalances(sim_results, bins)
    n_imbalances['Factors'] = n_imbalances['Factors'].map(
        lambda n: str(n) + ' factor' + ('s' if n > 1 else '')
    )

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True)
    palette = sns.color_palette('magma', n_colors=8, desat=0.8)

    random_plot = sns.lineplot(
        x='Bin',
        y='Cdf',
        data=n_imbalances.query('Method == "pure_random"'),
        ci=None,
        ax=ax1
    )
    random_plot.set_title("Purely random assignment")
    # Only label the middle plot
    random_plot.set_xlabel("")

    minimizer_p07_plot = sns.lineplot(
        x='Bin',
        y='Cdf',
        hue='Factors',
        data=n_imbalances.query('Method == "minimizer_p07"'),
        palette=palette,
        ci=None,
        ax=ax2,
        legend=False
    )
    minimizer_p07_plot.set_title("Minimization, p = 0.7")
    minimizer_p07_plot.set_xlabel("Overall treatment imbalance")

    minimizer_p10_plot = sns.lineplot(
        x='Bin',
        y='Cdf',
        hue='Factors',
        data=n_imbalances.query('Method == "minimizer_p10"'),
        palette=palette,
        ci=None,
        ax=ax3,
        legend='full'
    )
    minimizer_p10_plot.set_title("Minimization, p = 1.0")
    minimizer_p10_plot.set_xlabel("")

    return fig

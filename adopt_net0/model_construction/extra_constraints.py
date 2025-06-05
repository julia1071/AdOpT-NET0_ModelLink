from adopt_net0.utilities import get_set_t
import pyomo.environ as pyo


def set_annual_export_demand(modelhub, period, carrier_demand_dict):
    """
        Adds constraints to the model to enforce annual export demands for specific energy carriers.

        For each carrier in `carrier_demand_dict`, this function constrains the total (exported) product
        (summed over all nodes, technologies, and modeled time steps) to equal the specified annual demand,
        adjusted by the fraction of the year being modeled.

        Parameters:
        ----------
        modelhub : object
            The model hub containing model structure, data, and solution configuration.
        period : str or int
            The model period for which the export demand is being applied.
        carrier_demand_dict : dict
            A dictionary mapping carrier names (str) to their annual export demand (float, in energy units).
        """
    model = modelhub.model[modelhub.info_solving_algorithms["aggregation_model"]]
    b_period = model.periods[period]
    b_ebalance = model.block_energybalance
    set_t = get_set_t(modelhub.data.model_config, b_period)
    fraction_of_year_modelled = modelhub.data.topology["fraction_of_year_modelled"]

    # Create an indexed Constraint for the specified carriers
    model.carrier_demand_set = pyo.Set(initialize=list(carrier_demand_dict.keys()))

    def demand_export_rule(b, carrier):
        total_output = sum(
            sum(
                sum(
                    b_period.node_blocks[node]
                    .tech_blocks_active[tec]
                    .var_output_tot[t, carrier]
                    for tec in b_period.node_blocks[node].set_technologies
                    if carrier in b_period.node_blocks[node].tech_blocks_active[tec].set_output_carriers_all
                )
                for node in model.set_nodes
            )
            for t in set_t
        )
        return total_output == carrier_demand_dict[carrier] * fraction_of_year_modelled

    model.const_export_demand_dynamic = pyo.Constraint(
        model.carrier_demand_set, rule=demand_export_rule
    )

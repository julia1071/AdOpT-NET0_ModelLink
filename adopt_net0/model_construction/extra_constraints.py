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


def set_negative_CO2_limit(modelhub, period, tec_set_CO2):
    """
    Adds a constraint to limit net CO₂ exports to the CO₂ produced within the system, which is the sum of captured
    CO₂ from fluegas and CO₂ captured from syngas streams.

    This constraint ensures that total CO₂ exported from the system does not exceed
    the sum of CO₂ captured by capture technologies and CO₂ that is part of syngas
    production (e.g., from methanation or similar processes). This avoids
    accounting for negative emissions that are not supported by capture or synthesis
    within the system.

    Parameters
    ----------
    modelhub : object
        The model hub containing the Pyomo model, model data, and configuration.
    period : str or int
        The time period for which the constraint is applied.
    tec_set_CO2 : list
        A set of technology names that produce CO₂ as part of syngas production (so excluding CO₂ storage).

    """

    model = modelhub.model[modelhub.info_solving_algorithms["aggregation_model"]]
    b_period = model.periods[period]
    set_t = get_set_t(modelhub.data.model_config, b_period)

    def init_export_CCS_limit(const):
        export_CO2 = sum(sum(
            b_period.node_blocks[node].var_export_flow[t, 'CO2']
            for node in model.set_nodes
            if 'CO2' in b_period.node_blocks[node].set_carriers
        ) for t in set_t)

        captd_CO2 = sum(
            sum(sum(
                b_period.node_blocks[node]
                .tech_blocks_active[tec]
                .var_output_tot[t, 'CO2captured']
                for tec in b_period.node_blocks[node].set_technologies
                if 'CO2captured' in b_period.node_blocks[node].tech_blocks_active[tec].set_output_carriers_all
            )
                for node in model.set_nodes
                ) for t in set_t)

        syngas_CO2 = sum(
            sum(sum(
                b_period.node_blocks[node]
                .tech_blocks_active[tec]
                .var_output_tot[t, 'CO2']
                for tec in tec_set_CO2
                if tec in b_period.node_blocks[node].set_technologies and
                'CO2' in b_period.node_blocks[node]
                .tech_blocks_active[tec]
                .set_output_carriers_all
            )
                for node in model.set_nodes
                ) for t in set_t)

        return export_CO2 <= captd_CO2 + syngas_CO2

    model.const_CCS_export_limit = pyo.Constraint(rule=init_export_CCS_limit)
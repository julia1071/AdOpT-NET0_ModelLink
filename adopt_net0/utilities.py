import json
from pathlib import Path

from pyomo.environ import SolverFactory


def get_gurobi_parameters(solveroptions: dict):
    """
    Initiates the gurobi solver and defines solver parameters

    :param dict solveroptions: dict with solver parameters
    :return: Gurobi Solver
    """
    solver = SolverFactory(solveroptions["solver"]["value"], solver_io="python")
    solver.options["TimeLimit"] = solveroptions["timelim"]["value"] * 3600
    solver.options["MIPGap"] = solveroptions["mipgap"]["value"]
    solver.options["MIPFocus"] = solveroptions["mipfocus"]["value"]
    solver.options["Threads"] = solveroptions["threads"]["value"]
    solver.options["NodefileStart"] = solveroptions["nodefilestart"]["value"]
    solver.options["Method"] = solveroptions["method"]["value"]
    solver.options["Heuristics"] = solveroptions["heuristics"]["value"]
    solver.options["Presolve"] = solveroptions["presolve"]["value"]
    solver.options["BranchDir"] = solveroptions["branchdir"]["value"]
    solver.options["LPWarmStart"] = solveroptions["lpwarmstart"]["value"]
    solver.options["IntFeasTol"] = solveroptions["intfeastol"]["value"]
    solver.options["FeasibilityTol"] = solveroptions["feastol"]["value"]
    solver.options["Cuts"] = solveroptions["cuts"]["value"]
    solver.options["NumericFocus"] = solveroptions["numericfocus"]["value"]
    # solver.options["SubMIPNodes"] = solveroptions["SubMIPNodes"]["value"]
    # solver.options["ScaleFlag"] = solveroptions["ScaleFlag"]["value"]

    return solver


def get_glpk_parameters(solveroptions: dict):
    """
    Initiates the glpk solver and defines solver parameters

    :param dict solveroptions: dict with solver parameters
    :return: Gurobi Solver
    """
    solver = SolverFactory("glpk")

    return solver


def get_set_t(config: dict, model_block):
    """
    Returns the correct set_t for different clustering options

    :param dict config: config dict
    :param model_block: pyomo block holding set_t_full and set_t_clustered
    :return: set_t
    """
    if config["optimization"]["typicaldays"]["N"]["value"] == 0:
        return model_block.set_t_full
    elif config["optimization"]["typicaldays"]["method"]["value"] == 1:
        return model_block.set_t_clustered
    elif config["optimization"]["typicaldays"]["method"]["value"] == 2:
        return model_block.set_t_full


def get_hour_factors(config: dict, data, period: str) -> list:
    """
    Returns the correct hour factors to use for global balances

    :param dict config: config dict
    :param data: DataHandle
    :return: hour factors
    """
    if config["optimization"]["typicaldays"]["N"]["value"] == 0:
        return [1] * len(data.topology["time_index"]["full"])
    elif config["optimization"]["typicaldays"]["method"]["value"] == 1:
        return data.k_means_specs[period]["factors"]
    elif config["optimization"]["typicaldays"]["method"]["value"] == 2:
        return [1] * len(data.topology["time_index"]["full"])


def get_nr_timesteps_averaged(config: dict) -> int:
    """
    Returns the correct number of timesteps averaged

    :param dict config: config dict
    :return: nr_timesteps_averaged
    """
    if config["optimization"]["timestaging"]["value"] != 0:
        nr_timesteps_averaged = config["optimization"]["timestaging"]["value"]
    else:
        nr_timesteps_averaged = 1

    return nr_timesteps_averaged


def fix_technology_sizes_zero(m, all_tecs, node, period):
    for tec in all_tecs.keys():
        if tec in m.model[m.info_solving_algorithms["aggregation_model"]].periods[period].node_blocks[node].tech_blocks_active:
            if all_tecs[tec]:
                m.model[m.info_solving_algorithms["aggregation_model"]].periods[period].node_blocks[node].tech_blocks_active[tec].var_size.fix(0)
            else:
                m.model[m.info_solving_algorithms["aggregation_model"]].periods[period].node_blocks[node].tech_blocks_active[tec].var_size.unfix()

    return m


def fix_installed_capacities(m, scenario, prev_scenario, node, exceptions):
    """
    Set the capacity of a technology to a minimum capacity for the next brownfield simulation
    """
    model = m[scenario].model[m[scenario].info_solving_algorithms["aggregation_model"]].periods[scenario]
    prev_model = m[prev_scenario].model[m[scenario].info_solving_algorithms["aggregation_model"]].periods[prev_scenario]

    b_node = model.node_blocks[node]
    b_node_prev = prev_model.node_blocks[node]

    for tec_name in b_node_prev.set_technologies:
        if tec_name not in exceptions:
            b_tec = b_node.tech_blocks_active[tec_name]
            prev_tec_size = b_node_prev.tech_blocks_active[tec_name].var_size.value

            b_tec.var_size.setlb(prev_tec_size)

    return m


def installed_capacities_existing(m, scenario, prev_scenario, node, casepath):
    """
    Set the capacity of a technology to a minimum capacity for the next brownfield simulation
    """
    prev_model = m[prev_scenario].model[m[prev_scenario].info_solving_algorithms["aggregation_model"]].periods[prev_scenario]

    b_node_prev = prev_model.node_blocks[node]

    size_tecs_existing = {}

    for tec_name in b_node_prev.set_technologies:
        prev_tec_size = b_node_prev.tech_blocks_active[tec_name].var_size.value

        if prev_tec_size > 0:
            if 'existing' in tec_name:
                tec_name = tec_name[:-9]
            size_tecs_existing[tec_name] = prev_tec_size


    # Read the JSON technology file
    casepath = Path(casepath)
    json_tec_file_path = (
            casepath / scenario / "node_data" / node / "Technologies.json"
    )
    with open(json_tec_file_path, "r") as json_tec_file:
        json_tec = json.load(json_tec_file)

    json_tec['existing'] = size_tecs_existing
    with open(json_tec_file_path, "w") as json_tec_file:
        json.dump(json_tec, json_tec_file, indent=4)


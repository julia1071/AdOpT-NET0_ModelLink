[![Documentation Status](https://readthedocs.org/projects/adopt-net0/badge/?version=latest)](https://adopt-net0.readthedocs.io/en/latest/?badge=latest)
![Testing](https://github.com/UU-ER/AdOpT-NET0/actions/workflows/00deploy.yml/badge.svg?branch=develop)
[![codecov](https://codecov.io/gh/UU-ER/AdOpT-NET0/graph/badge.svg?token=RVR402OGG0)](https://codecov.io/gh/UU-ER/AdOpT-NET0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/adopt-net0.svg)](https://pypi.org/project/adopt-net0/)
[![status](https://joss.theoj.org/papers/12578885161d419241e50c5e745b7a11/status.svg)](https://joss.theoj.org/papers/12578885161d419241e50c5e745b7a11)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13384688.svg)](https://doi.org/10.5281/zenodo.13384688)

# AdOpT-NET0: Coupling National and Cluster-Level Models

This repository contains the code, data, and results used in the paper:

Tiggeloven, J. L., West, K., Mulder, A.J., Faaij, A. P. C., Kramer, G. J., Koning, V., & Gazzani, M.  
*Supporting the transition to a net-zero chemical industry by coupling national and cluster-level models.*  

This repository is **based on the original AdOpT-NET0 tool**, but includes adaptations specific to this work. It 
contains all input datasets, case studies, and raw results required to reproduce the analyses in the paper. Users can 
regenerate the results by running the corresponding scripts, e.g., `run_standalone.py` for the standalone scenario, and 
`main_model_linking.py` for the linked models. The linked model requires also the installation of AIMMS.

## Installation

Clone this repository and install the required dependencies:

```bash
git clone https://github.com/julia1071/AdOpT-NET0_AmmEth_EmisRed.git
cd AdOpT-NET0_AmmEth_EmisRed
pip install -r requirements.txt
```

Additionally, you need a [solver installed, that is supported by pyomo](https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html#supported-solvers)
(we recommend gurobi, which has a free academic licence).

Note for mac users: The export of the optimization results require a working
[hdf5 library](https://www.hdfgroup.org/solutions/hdf5/). On windows this should be
installed by default. On mac, you can install it with homebrew:

```brew install hdf5```

## Usage and documentation
The documentation and minimal examples of how to use the package can be found 
[here](https://adopt-net0.readthedocs.io/en/latest/index.html). We also provide a 
[visualization tool](https://resultvisualization.streamlit.app/) that is compatible 
with AdOpT-NET0.

## Dependencies
The package relies heavily on other python packages. Among others this package uses:

- [pyomo](https://github.com/Pyomo/pyomo) for compiling and constructing the model
- [pvlib](https://github.com/pvlib/pvlib-python) for converting climate data into 
  electricity output
- [tsam](https://github.com/FZJ-IEK3-VSA/tsam) for the aggregation of time series

## Credits
This tool was developed at Utrecht University.

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
from scipy.sparse import coo_matrix,diags


def shift_HK(x, tau, omega):
    y = np.where(np.abs(x) <= tau, omega * x, 0)
    
    return(y)


# get params dictionary
def get_params(argv):
    data_name = str(argv[1])
    # load network_params
    data = np.load(f"data/network_params_{data_name}.npz", allow_pickle=True)
    network_params = {key: data[key] for key in data.keys()}
    for network_param in ['A', 'E', 'E_in']:
        network_params[network_param] = network_params[network_param].item()
    
    # Input simulation params
    control_steps = int(argv[9])
    sim_steps = 24
    thres = 0.7

    # Define additional_params dictionary with default values
    additional_params = {
        'data_name': data_name,
        'shift': getattr(sys.modules[__name__], argv[2]),
        'tau': float(argv[3]),
        'omega': float(argv[4]),
        'OBJECTIVE_range': argv[5].split(),
        'smax_range': [float(x) for x in argv[6].split(',')],
        'sedge_range': [float(x) for x in argv[7].split(',')],
        'expr_bool': str(argv[8]),
        'Tf': control_steps,
        'control_steps': control_steps,
        'sim_steps': sim_steps,
        'thres': thres
    }

    # Combine network_params and additional_params into params
    params = {**network_params, **additional_params}

    return params


# out-degree edges indices
def OD_edges_indices(E, nv):
    nv_edges_indices = np.empty(nv, dtype=object)
    for i in range(nv):
        nv_edges_indices[i] = E.col[E.row == i]
    
    return nv_edges_indices


# out-degree vertices indices
def OD_vertices_indices(A, nv):
    nv_vertices_indices = np.empty(nv, dtype=object)
    for i in range(nv):
        nv_vertices_indices[i] = A.col[A.row == i]
    
    return nv_vertices_indices

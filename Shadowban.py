import sys # command line arguments
import numpy as np
from scipy.optimize import linprog # linear programming solver
import networkx as nx # create synthetic network
import matplotlib.pyplot as plt
import time # check running time


from scripts.opinion_data import * # load twitter network
from scripts.dynamics_simulator import * # class for shadow ban LP optimization and RK simulation
from scripts.opinion_visualization import * # plot simulation results and create dataframes


data_dir = f""
save_dir = f""

params = get_params(sys.argv)
data_path = f"{data_dir}/results/{params['data_name']}"
save_path = f"{save_dir}/results/{params['data_name']}"


T_sim = np.linspace(0, params['Tf'], params['sim_steps']*params['control_steps'] + 1)# for plots
for OBJECTIVE in params['OBJECTIVE_range']:
    params['OBJECTIVE'] = OBJECTIVE

    for smax in params['smax_range']:# smax sensitivity
        for sedge in params['sedge_range']:# sedge sensitivity
            params['smax'] = smax
            params['sedge'] = sedge
            file_name = (f"{save_path}/{OBJECTIVE}/Shadow_Ban_{OBJECTIVE}_{params['shift'].__name__}_tau={params['tau']}_omega={params['omega']}"
                        f"_smax={smax}_sedge={sedge}_expr={params['expr_bool']}_Tf={params['Tf']}")

            # shadow ban
            start_time = time.time()
            env_ban = OpinionSimulatorContinuous(params, shadowban=True)
            Opinions_ban, Controls_ban = opinion_simulation_array(env_ban)
            obj_ban = cost_sim(OBJECTIVE, Opinions_ban, Controls_ban, params['thres'], alpha=0)
            print(f"Took {(time.time()-start_time)/60:.0f} mins to simulate {params['data_name']} {OBJECTIVE} Tf={params['Tf']} "
                  f"smax={smax:.2f} sedge={sedge:.2f}, obj={abs(obj_ban):.4f}")
            
            # save all controls over time
            np.savez(f"{file_name}_allcontrols.npz", Controls_all=Controls_ban)
                
            # save shadow ban result (incl. no ban where smax==0)
            np.savez(f"{file_name}.npz", T_sim=T_sim, obj=obj_ban, Opinions=Opinions_ban, Controls_mean=np.mean(Controls_ban, axis=1))

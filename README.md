# Shadowbanning
This repo provides the Python code (shadowban.py and in scripts/) and network data (in data/) to produce the simulation results in the paper *Shaping Opinions in Social Networks with Shadow Banning*. It solves for shadow banning controls using linear programming, and simulates resulting opinoins using the Runge-Kutta method. It is also an *opinion dynamics simulator* when one models continuous time opinion dynamics using differential equations. This repo provides two datasets - 2016 U.S. election and 2018 Gilets Jaunes.

To use this package, enter in command line following below sequence of command-line arguments.

python Shadowban.py "{data_name}" {shift_name} {shift_param1} {shift_param2} "{objective}" "{s_network}" "{s_edge}" "{experiment_bool}" {simulation_days}

For example, if we want to simulate our shadow banning policies for the U.S. election dataset, for 365 days, for an objective of maximizing the mean, under the bounded confidence model with parameters $\epsilon=0.01$ and $\omega=0.003$, and with shadow banning strength constraints of $s_{network}=0.05$ and $s_{edge}=1$, we would enter below in command line.

python Shadowban.py "US Election_sample" shift_HK 0.01 0.003 "MEAN" "0.05" "1" "False" 365

Brief descriptions on each script are as follows.

## Shadowban.py
Generate a state array for opinions of each node over time, and a control array for shadow banning decisions on each edge over time. This script will call the functions in the scripts under the folder `scripts`. Update directory paths before running the code.

## scripts/opinion_data.py
Parse command-line arguments and create parameter dictionary for the simulator.

## scripts/dynamics_simulator.py
Simulate opinion dynamics over time using a linear programming solver for shadow banning decisions, and using the Runge-Kutta method for solving an ordinary differential equation for the resulting opinions.

## scripts/opinion_visualization.py
Visualize simulation results by plotting opinion quantile evolutions and opinion densities.
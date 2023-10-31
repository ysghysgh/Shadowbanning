import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import gaussian_kde # calculate kernel density


from scripts.dynamics_simulator import * # class for shadow ban LP optimization and RK simulation


#########################################################
#Plotting functions

def plot_opinions(T, Opinions, U = None):
    plt.plot(T, Opinions)
    if U is not None:
        plt.plot(T, 1-U.mean(axis=1), '.-', color = 'red', label='Mean shadow \nban strength')
        plt.legend(loc='upper right')
    plt.grid()
    plt.xlabel("Time [days]")
    plt.ylabel("Opinion")
    
    
def plot_opinion_quantiles(T , Opinions, q=[50, 25, 75, 5, 95], U = None):
    if U is not None:
        plt.plot(1-U, marker='.', color = 'red', label='Mean shadow \nban strength')
        plt.legend(loc='upper right')

    # Plot quantiles    
    quantiles = np.percentile(Opinions, q=q, axis=1)
    plt.plot(T, quantiles[0], color='black')#, label='Median Opinion')
    plt.fill_between(T, quantiles[1], quantiles[2], color='blue', alpha=0.5)#, label='25th-75th Quantiles')
    plt.fill_between(T, quantiles[3], quantiles[4], color='pink', alpha=0.5)#, label='5th-95th Quantiles')
    plt.grid()
        

# density of one opinions row
def plot_opinion_density(opinions, label):
    # Create a kernel density estimate for each time point
    kde = gaussian_kde(opinions)
    # Create an x-axis range for the opinion values
    x = np.linspace(0, 1, 100)
    # Evaluate the density estimates on the x-axis range
    density = kde(x)

    plt.plot(x, density, label=label)
    plt.fill_between(x, density, alpha=0.3)


def draw_network(G):
    nv = G.number_of_nodes()    
    if nv<=100:
        colors = []
        for v in G.nodes():
            if (G.nodes[v]['opinion']<0.5) & (G.nodes[v]['opinion']>=0):
                colors.append('blue')
            elif (G.nodes[v]['opinion']>0.5) & (G.nodes[v]['opinion']<=1):
                colors.append('red')
            elif G.nodes[v]['opinion']==0.5:
                colors.append('purple')
            else:
                colors.append('green')
        pos = nx.kamada_kawai_layout(G)
        fig = plt.figure(figsize = (3,3))
        nx.draw(G,pos, node_color = colors, node_size = 50)
        plt.show()
    else:
        print("Network has more than 100 nodes.  Dont draw it cuz it takes too long")
        fig = None
    return fig
    
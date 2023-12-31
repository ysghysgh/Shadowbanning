import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix,diags


# cost function
def cost_sim(OBJECTIVE, Opinions, U = None, thres = 0.95, alpha = 0):
    '''Cost of opinions and control in simulator.'''
    if U is None:
        U = np.ones(Opinions.shape)
    cu = -alpha*U.mean(axis=1)

    if OBJECTIVE == 'MEAN':
        cx = -Opinions.mean(axis = 1)
    elif  OBJECTIVE == 'VARMAX':
        cx = -Opinions.var(axis = 1)
    elif  OBJECTIVE == 'VARMIN':
        cx = Opinions.var(axis = 1)
    elif  OBJECTIVE == 'EXTMAX':
        cx = -np.mean(Opinions >= thres, axis=1) # ratio of extreme opinions
    elif  OBJECTIVE == 'EXTMIN':
        cx = np.mean(Opinions >= thres, axis=1)
    else:
        print("Error: Wrong Objective.  Choose from NONE, MEAN, VARMAX, VARMIN, EXTMAX, EXTMIN")
        cx = None
    
    return np.mean(cu) + np.mean(cx)


class OpinionSimulatorContinuous():
    def __init__(self, params, shadowban):
        self.shift = params['shift']
        self.tau = params['tau']
        self.omega = params['omega']

        self.A = params['A']
        self.nv = self.A.shape[0]
        self.ne = self.A.data.shape[0]

        self.opinions_initial = params['opinions0'].copy()
        self.opinions = params['opinions0'].copy()
        assert len(self.opinions_initial)==self.nv

        self.rate = params['rates']
        self.Rate_matrix = diags(self.rate,0)

        self.control_steps = params['control_steps'] # overall control points
        self.sim_steps = params['sim_steps'] # state eval steps within one control step
        self.dt = 1/self.sim_steps # days
        
        self.control_step_counter = 0
        self.sim_step_counter = 0

        self.OBJECTIVE = params['OBJECTIVE']
        self.thres = params['thres']
        self.shadowban = shadowban
        self.smax = params['smax']
        self.sedge = params['sedge']

        self.expr_bool = params['expr_bool']
        self.expr_factor = np.ones(self.ne)

        
    def get_B(self, state):        
        # d_r / d_thetai
        if self.OBJECTIVE == 'MEAN':
            C = -np.ones(self.nv)#-1/self.nv*np.ones(self.nv)
            
        elif self.OBJECTIVE == 'VARMIN':
            mu = np.mean(state)
            C = (state-mu)#2/self.nv*(state-mu)
            
        elif self.OBJECTIVE == 'VARMAX':
            mu = np.mean(state)
            C = -(state-mu)#-2/self.nv*(state-mu)         
            
        B = C[self.A.col] * self.rate[self.A.row] * self.shift(state[self.A.row]-state[self.A.col], self.tau, self.omega)
        
        return B
  

    def shadowban_LP(self, state):
        # Control variable coefficient
        c = self.get_B(state)
        # Round c to shorter numbers to avoid solver error
        c = np.round(c, decimals=5)
        
        # Average ban constraint
        A_ub = -np.ones((1,self.ne))
        b_ub = -self.ne*(1-self.smax)

        # scipy.optimize.linprog()
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(1-self.sedge,1))
        control = np.array(res.x)

        return control, c

    
    def control_step(self, state):
        if self.shadowban == True:
            control, c = self.shadowban_LP(state)
        else:
            control = np.ones(self.ne)

        if self.control_step_counter >= self.control_steps - 1:
            done = True
        else: 
            done = False
        self.control_step_counter += 1
        
        return control, done, c


    # if emulating an experiment
    def expr(self, expr_bool):
        if expr_bool == True:
            expr_variable = 1 - 0.3
            for edge_idx in range(self.ne):
                # Get the indices of the follower and following for the current edge
                follower_idx = self.A.col[edge_idx]
                following_idx = self.A.row[edge_idx]

                # Check conditions and apply multiplication
                if self.opinions_initial[follower_idx] <= 0.5 and self.opinions_initial[following_idx] <= 0.4:
                    self.expr_factor[edge_idx] *= expr_variable
                elif self.opinions_initial[follower_idx] > 0.5 and self.opinions_initial[following_idx] >= 0.6:
                    self.expr_factor[edge_idx] *= expr_variable
    

    def sim_slope(self, state, U):
        data = self.shift((state[self.A.row] - state[self.A.col])*self.expr_factor, self.tau, self.omega)# True if emulating experiment
        Shift_matrix = coo_matrix((data, (self.A.row, self.A.col)), shape=self.A.shape)
        scaled_Shift_matrix = Shift_matrix.multiply(U) #scale each edge

        # contribution from following of nodes
        D = self.Rate_matrix @ scaled_Shift_matrix
        Dxdt = D.sum(axis = 0).A1 #sum of each column. A1 flattens the resulting matrix into a 1D array

        return Dxdt


    def sim_step(self, state, control):
        U_row = self.A.row
        U_col = self.A.col
        U = coo_matrix((control, (U_row, U_col)), shape=self.A.shape)
        
        # Runge-Kutta derivative
        state = self.opinions.copy()
        k1 = self.sim_slope(state, U)
        y1 = state + self.dt/2*k1
        k2 = self.sim_slope(y1, U)
        y2 = state + self.dt/2*k2
        k3 = self.sim_slope(y2, U)
        y3 = state + self.dt*k3
        k4 = self.sim_slope(y3, U)
        Dxdt_rk = (k1 + 2*k2 + 2*k3 + k4)/6
        
        self.opinions += Dxdt_rk*self.dt
        self.opinions = np.clip(self.opinions, 0.0, 1.0) #clip opinions between 0 and 1
        state = self.opinions.copy()

        self.sim_step_counter += 1
        if self.sim_step_counter >= self.sim_steps:
            done = True
            self.sim_step_counter = 0
        else: 
            done = False

        return state, done

    
    def reset(self):
        self.control_step_counter = 0
        self.sim_step_counter = 0
        self.opinions = self.opinions_initial.copy()
        self.expr(self.expr_bool)# emulate an experiment
        
        state = self.opinions_initial.copy()
        control_done = False
        sim_done = False
        
        return state, control_done, sim_done


def opinion_simulation_array(env):
    control_steps = env.control_steps
    sim_steps = env.sim_steps
    nv = env.nv
    ne = env.ne
    
    opinions = np.empty((sim_steps * control_steps + 1, nv))
    controls = np.empty((control_steps, ne))

    # i, j = 0
    state, control_done, sim_done = env.reset()
    opinions[0] = state

    opinion_index = 1
    control_index = 0

    while not control_done:# i = 0 ~ (control_steps-1)
        control, control_done, c = env.control_step(state)
        controls[control_index] = control
        control_index += 1

        sim_done = False # Reset sim_done for each control interval
        while not sim_done:# j = 1 ~ sim_steps
            state, sim_done = env.sim_step(state, control)
            opinions[opinion_index] = state
            opinion_index += 1
        
    return opinions, controls

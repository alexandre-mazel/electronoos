import matplotlib.pyplot as plt
import numpy as np
import time

nbr_motor = 6
class GraphData:
    def __init__( self ):
        #~ self.t = [0]
        self.t = np.linspace(0, 10, 100)
        #  list of all last pos for each motors
        self.pos = []
        self.order = []
        for i in range(nbr_motor):
            self.pos.append(list(np.linspace(-127, 127, 100)) )
            self.order.append( list(np.linspace(-127, 127, 100)) )
        
        self.fig = None
        self.pos_plots = [] # list of each graph of pos
        self.order_plots = []
        self.nbr_render = 0
        
    def create( self ):
        # On active le mode interactif
        plt.ion()   # ion => interactive on / ioff => interactive off

        self.fig, ax = plt.subplots()
        color_list = ["red","blue", "orange", "yellow", "green","magenta"]
        color_list_dark = ["darkred","darkblue", "darkorange", "khaki", "darkgreen","darkmagenta"]
        for i in range(nbr_motor):
            pos_plot, = ax.plot(self.t, self.pos[i], label="pos %d" % i, color=color_list[i])
            order_plot, = ax.plot(self.t, self.order[i], label="order %d" % i, color=color_list_dark[i])
            order_plot.set_linestyle(':')
            self.pos_plots.append(pos_plot)
            self.order_plots.append(order_plot)
            
        plt.legend()
        self.fig.tight_layout()
        
    def update_added_data( self ):
        #~ if len(self.t) < len( self.pos ):
            #~ self.t.append(time.time())
        #~ if len(self.t) < len( self.order ):
            #~ self.t.append(time.time())
        pass
        
        
    def refresh_render( self ):
        #~ print("DBG: refresh_render: len self.t: %d" % len( self.t) )
        #~ print("DBG: refresh_render: len self.pos: %d" % len( self.pos) )
        #~ print("DBG: refresh_render: len self.order: %d" % len( self.order) )
        
        self.nbr_render += 1
        if (self.nbr_render % 6) != 0: # don't update graphe every time
            return
        
        for i in range(nbr_motor):
            self.pos_plots[i].set_ydata(self.pos[i])
            self.order_plots[i].set_ydata(self.order[i])
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        #~ plt.pause(0.1)

graphData = GraphData()

def create_graph():
    graphData.create()

def add_graph_order( idx_motor, val ):
    del graphData.order[idx_motor][0]
    graphData.order[idx_motor].append(val)
    #~ graphData.update_added_data()
    pass
    
def add_graph_pos( idx_motor, val ):
    del graphData.pos[idx_motor][0]
    graphData.pos[idx_motor].append(val)
    #~ graphData.update_added_data()
    pass
    
def refresh_render():
    graphData.refresh_render()
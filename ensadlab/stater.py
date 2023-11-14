"""
Yet another statistics tools.
Store statistics and send them to osc viewer
"""

class Stater:
    
    def __init__( period = 1, viewer_ip="localhost" ):
        self.period = period
        self.viewer_ip = viewer_ip
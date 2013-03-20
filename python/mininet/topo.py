'''
Simulating a three Switch Topology
@author: bdadson
 
Priliminary:
........................................
1. Create topology with three switches
2. Attach switch 1,2,4 with four nodes
3. Configure topology with mininet
4. All switches are linked together
.......................................
 
Pseudo-code:
 
(def:
    (Switch:s1)
        (nodes)
            +(s1h1)(s1h2)(s1h3)(s1h4)
     (Switch:s2)
         (nodes)
             +(s2h1)(s2h2)(s2h3)(s2h4)
     (Switch:s3)
         (nodes)
             +(s3h1)(s3h2)(s3h3)(s3h4)
    ).mininet.configure(CLI)

Connect the switches together
.............................
 
(def:
    (Link)
        +(s1)->(s2)
        +(s2)->(s3)
        +(s1)->(s3)
        ).link()
'''
def build_network():
    topo = SimulatingVlanTopo(s=3, n=4)
    network = Mininet(topo, switch=OVSKernelSwitch);
    network.run(CLI, network)
    
from mininet.topo import Topo
from mininet.net import Mininet
# from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
class SimulatingVlanTopo(Topo):
     
    # default topology with minimum of 1 switch and node
    
    
    def __init__(self, s=1, n=1, **opts):
        super(SimulatingVlanTopo, self).__init__(**opts)
        self.configure(s, n)
        self.assign_ipv4_addr()
     
    
    def assign_ipv4_addr(self):
        hosts = self.nodes()
        #for host in hosts:
            #if(host.isSwitch()):
                
        

    def link_switches(self, p_switch, switch):
        if p_switch is not None:
            self.addLink(p_switch, switch)
        return p_switch
    
    
    def configure(self, s, n):
        '''
        :param s: Switch
        :param n: Attached nodes to a switch
        '''
        p_switch = None
        for sn in range(s):
            switch = ('s%s' % (sn + 1))
            self.addSwitch(switch)
            
            for h in range(n):
                host = self.addHost(switch + ('h%s' % (h + 1)))
                self.addLink(host, switch)
                
            p_switch = self.link_switches(p_switch, switch)
            if (p_switch is not None) and (s in p_switch):
                self.addLink(p_switch, 's%s' % (s - (s - 1)))
                

'''if __name__ == '__main__':
    setLogLevel('info')
    build_network();'''
 
topos = {'simulating_vlan_topo': lambda : SimulatingVlanTopo(s=3, n=4)}

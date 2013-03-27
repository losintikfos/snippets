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
from mininet.topo import Topo
from mininet.net import Mininet

from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
class SimulatingVlanTopo(Topo):
     
    # default topology with minimum of 1 switch and node
    def __init__(self, s=1, n=1, **opts):
        super(SimulatingVlanTopo, self).__init__(**opts)
        self.configure(s, n)
     
    def link_switches(self, p_switch, switch):
        if p_switch is not None:
            self.addLink(p_switch, switch)
        return p_switch
    
    def assign_ipv4_addr(self, switch, host, index):
        def default():
            print("No switch found matching {0}", switch)
        {
            's1': lambda : host.setIP("192.168.0." + str(index + 1)),
            's2': lambda : host.setIP("192.168.1." + str(index + 1)),
            's3': lambda : host.setIP("192.168.2." + str(index + 1))
         }.get(switch, default)()
         
    
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
                 
def _assign_host_ip(fn):
    if fn is None:
        return
    
    topo = fn();
    net = Mininet(topo)
    hosts, switches = net.hosts, net.switches
     
    n = 0
    for node in hosts:
        print '{0} -> {1} -> {2}'.format(n, node.name, node.name[:2])
        topo.assign_ipv4_addr(node.name[:2], node, n)
        
    for switch in switches:
        topo.assign_ipv4_addr(switch.name, switch, 0)
            
fn = lambda : SimulatingVlanTopo(s=3, n=4)

_assign_host_ip(fn)
topos = {'simulating_vlan_topo': fn}

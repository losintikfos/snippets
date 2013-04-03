
from mininet.log import debug
import os
import sys
import subprocess


# TODO: setuptool
sys.path.append(str(os.getcwd()) + '/python')

from mininet.cli import CLI, CLI
from mininet.log import setLogLevel
from mininet.net import Mininet

from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo
from network import sql_queries
from db.db_access import DataAccess


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

class SimulatingVlanTopo(Topo):
     
    # default topology with minimum of 1 switch and node
    def __init__(self, **opts):
        super(SimulatingVlanTopo, self).__init__(**opts)
        self.dao = DataAccess()
        
    
    def link_switches(self, p_switch, switch):
        if p_switch is not None:
            self.addLink(p_switch, switch)
        return p_switch
    
    def assign_ipv4_addr(self, host, switch=None, index=0):
        print "++++++++++++++++++++++++++++Assigning IP address to ", host.name
        
        sql = sql_queries.GET_IP_ADDR + repr(host.name)
        host.setIP(self.dao.select(sql)) 
        
        def default():
            print ("No switch found matching %s", switch)
            
        def _sh_(shell_cmd):    
            p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while(True):
              retcode = p.poll()  # returns None while subprocess is running
              line = p.stdout.readline()
              print line
              if(retcode is not None):
                break
            
        if switch is not None:
            {'s1': lambda : sh("ovs-vsctl set bridge s1 protocols=OpenFlow10,OpenFlow12,OpenFlow13"),
                's2': lambda : sh("ovs-vsctl set bridge s2 protocols=OpenFlow10,OpenFlow12,OpenFlow13"),
                 's3': lambda : sh("ovs-vsctl set bridge s3 protocols=OpenFlow10,OpenFlow12,OpenFlow13")
            }.get(host.name, default)()   
    
    def configure(self, s, n):
        '''
        @param s: Switch
        @param n: Attached nodes to a switch
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
                 
    def _configure_network(self, s=1, n=1):
        self.configure(s, n)
        # TODO: Take controller from database
        c0 = RemoteController('c0', ip='10.100.1.61')
        
        net = Mininet(self, switch=OVSSwitch, build=False)
        hosts, switches = net.hosts, net.switches
        
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", hosts
         
        for index, node in enumerate(hosts):
            print ('++++++++++++++>%s', node.name)
            topo.assign_ipv4_addr(host=node)    
        
        for switch in switches:
            topo.assign_ipv4_addr(host=switch)
            
        net.controllers = [c0]
        net.build()
        net.start()
        
        CLI(net)

        net.stop()
        
if __name__ == '__main__':
    setLogLevel('info') 
    
    topo = SimulatingVlanTopo()
    topo._configure_network(s=3, n=4)
# #topos = {'simulating_vlan_topo': fn}

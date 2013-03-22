
from ryu.base import app_manager
from ryu.ofproto import ether, ofproto_v1_2
from ryu.controller import dpset, ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER
import logging

logger = logging.getLogger(__name__)
'''
Requirement psuedocode:
@author: bdadson

PREAMBLE:   Install VLAN on switches for customers.
            Customer specific 802.1ad VLAN in TOR(Top of Rack),
            using multi switch ports segregation via Q-in-Q. 


KEY:
....................    
s0        = Switch 0
port1     = port 0
cust      = customer
....................

(def:

value_pair=({
    cust1    :    [s0_eth1, s0_eth2]
    cust2    :    [s1_eth1, s1_eth2, s0_eth3]
    cust3    :    [s2_eth0, s2_eth1, s1_eth3]
    trunk    :    [s0_eth4, s1_por4, s2_eth4]
})

loop until value_pair.end() |key|
(
  (if key like 'cust')
  {
    ((MATCH):
        +(INSTRUCTIONS)
        {
            +(WRITE_ACTIONS)
                push-VLAN
                    +(ACTION_LIST)
                        [push 0x88a8 , push 0x8100]
            -(CLEAR_ACTION)
            -(WRITE_ACTION)
            -(GOTO_ACTION)
         }.add_to_flow(..)
    }
       
    
  (if key like 'trunk')
  {
    ((MATCH):
        +(INSTRUCTIONS)
        {
            +(APPLY_ACTIONS)
                push-VLAN
                    +(ACTION_LIST)
                        [push 0x88a8]
            -(CLEAR_ACTION)
            -(WRITE_ACTION)
            -(GOTO_ACTION)
         }.add_to_flow(..)
    }
))

'''
class SimulateStargateVlan(app_manager.RyuApp):

    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]

    def __init__(self, *_args, **_kvargs):
       super(SimulateStargateVlan, self).__init__(*_args, **_kvargs)
  
    def install_vpn_flow(self, dp):
        logger.info("++++++++++++++++++++++++++")
    
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, event):
        if event.enter:
            logger.info("@@@@ Installing flow for VLAN+++++++")
            self.install_vpn_flow(event.dp)


    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        logger.info(">>>>>>>>>>>>>> debuggin %s", msg.datapath)


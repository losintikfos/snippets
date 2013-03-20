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
from ryu.base.app_manager import RyuApp
from ryu.ofproto import ether, ofproto_v1_2
from ryu.controller import dpset
from ryu.controller.handler import set_ev_cls
import logging

logger = logging.getLogger(__name__)

class SimulateStargateVlan(RyuApp):
    
    VLAN_TAG_802_1Q = 0x8100  # VLAN-tagged frame (IEEE 802.1Q) & Shortest Path Bridging IEEE 802.1aq
    BRIDGE_TAG_802_1AD = 0x88A8  # Provider Bridging (IEEE 802.1ad) & Shortest Path Bridging IEEE 802.1aq
    
    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]
    
    def __init__(self, *_args, **_kvargs):
       super(SimulateStargateVlan, self).__init__(*_args, **_kvargs)

    '''
    Add  a new flow entry to the the switch flow table
    
    '''
    def _add_flow(self, datapath, match, actions):
        inst = [datapath.ofproto_parser.OFPInstructionActions(
            datapath.ofproto.OFPIT_WRITE_ACTIONS, actions)]
    
        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath, cookie=0, cookie_mask=0, table_id=0,
            command=datapath.ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=0xff, buffer_id=0xffffffff,
            out_port=datapath.ofproto.OFPG_ANY, out_group=datapath.ofproto.OFPG_ANY,
            flags=0, match=match, instructions=inst)
        
        datapath.send_msg(mod)
        
    def build_match(self, port):
        match = datapth.ofproto_parser.OFPMatch()
        match.set_in_port(port)
        match.set_dl_type(ether.ETH_TYPE_IP)
        return match
    
    def tag_vlan(self, port, vlan_id, datapath):
        field = datapath.ofproto_parser.OFPMatchField.make(
            datapath.ofproto.OXM_OF_VLAN_VID, vlan_id)
        
        actions = [datapath.ofproto_parser.OFPActionPushVlan(BRIDGE_TAG_802_1AD),
            datapath.ofproto_parser.OFPActionPushVlan(VLAN_TAG_802_1Q),
            datapath.ofproto_parser.OFPActionSetField(field)]
        self._add_flow(datapath, self.build_match(port), actions)
    
    
    '''
    Add customer host(s) to VLAN using Q-in-Q.
    Ethertype: 0x8100, 0x88a8
    '''
    def tag_customer_vlan(self, alue, vlan_id, datapath):
        for port in value:
            logger.debug("Tagging port=> %s with VLAN ID %s", port, vlan_id)
            self.tag_vlan(port, vlan_id, datapath)    
    
    '''
    Ethertype: 0x88a8
    '''
    def tag_trunk(port, trunk_id, datapath):
        actions = [datapath.ofproto_parser.OFPActionPushVlan(BRIDGE_TAG_802_1AD)]
        self._add_flow(datapath, self.build_match(port), actions)
    
    
    def tag_trunk_vlan(value, trunk_id, datapath):
        for port in value:
            logger.debug("Tagging port=> %s with TRUNK_ID => %s", port, trunk_id)
            self.tag_trunk(port, trunk_id, datapath)
    
    
    def install_vpn_flow(datapath):
        # Static value of customer and aggregated switch ports
        # Note this value is use purposely for test only
        value_pair = {'cust1'    :    ['s0_eth1', 's0_eth2'],
                      'cust2'    :    ['s1_eth1', 's1_eth2', 's0_eth3'],
                      'cust3'    :    ['s2_eth0', 's2_eth1', 's1_eth3'],
                      'trunk'    :    ['s0_eth4', 's1_por4', 's2_eth4']}
        
        trunk_id, vlan_id = -1, -1
        for key, value in reversed(value_pair.items()):
            
            if'cust' in key:
                vlan_id += 1
                self.tag_customer_vlan(value, vlan_id, datapath)
        
            elif 'trunk' in key:
                trunk_id += 1
                self.tag_trunk_vlan(value, trunk_id, datapath)
    
    '''
    Install DataPath event dispatcher to invoke this method,
    anytime there's event dispatched to the DataPath from controller.
    '''
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, event):
        if event.enter:
            logger.info("@@@@ Installing flow for VLAN+++++++")
            self.install_vpn_flow(event.dp)


    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        logger.info(">>>>>>>>>>>>>> debuggin %s", msg.datapath)
    
if(__name__ == "__main__"):
    if False:
        h = 7
        while  h:
            print (h  if ((h - 1) > -1) else h + 1) 
            h -= 1

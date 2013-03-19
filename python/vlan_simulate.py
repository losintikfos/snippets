'''
Requirement psuedocode:
@author: bdadson

PREAMBLE:   Customer specific 802.1ad VLAN in TOR(Top of Rack),
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

class SimulateStargateVlan(RyuApp):
    def __init__(self, *_args, **_kvargs):
       super(SimulateStargateVlan, self).__init__(*_args, **_kvargs)

    '''
    Add  a new flow entry to the the switch flow table
    
    '''
    def _add_flow(self, dp, match, actions):
        inst = [dp.ofproto_parser.OFPInstructionActions(
            dp.ofproto.OFPIT_WRITE_ACTIONS, actions)]
    
        mod = dp.ofproto_parser.OFPFlowMod(
            dp, cookie=0, cookie_mask=0, table_id=0,
            command=dp.ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=0xff, buffer_id=0xffffffff,
            out_port=dp.ofproto.OFPG_ANY, out_group=dp.ofproto.OFPG_ANY,
            flags=0, match=match, instructions=inst)
        
        dp.send_msg(mod)
        
    def tag_vlan(port, vlan_id, dp):
        match = dp.ofproto_parser.OFPMatch()
        match.set_in_port(in_port)
        match.set_dl_type(eth_IP)
        match.set_vlan_vid(m_vid)
        actions = [dp.ofproto_parser.OFPActionPopVlan(),
                   dp.ofproto_parser.OFPActionOutput(out_port, 0)]
        self._add_flow(dp, match, actions)
    
    
    '''
    Add all customer host(s) to VLAN using Q-in-Q.
    Ethertype: 0x8100
    '''
    def tag_customer_vlan(value, vlan_id, dp):
        for port in value:
            print "Tagging port=>", port, "with VLAN_ID =>", vlan_id
            tag_vlan(port, vlan_id, dp)
        print '\n',
    
    
    '''
    Ethertype: 0x88a8
    '''
    def tag_trunk(port, trunk_id, dp):
        pass
    
    
    def tag_trunk_vlan(value, trunk_id, dp):
        for port in value:
            print "Tagging port=>", port, "with TRUNK_ID", trunk_id
            tag_trunk(port, trunk_id, dp)
    
    
    def test():
        #Static value of customer and aggregated switch ports
        #Note this value is use purposely for test only
        value_pair = ({
        'cust1'    :    ['s0_eth1', 's0_eth2'],
        'cust2'    :    ['s1_eth1', 's1_eth2', 's0_eth3'],
        'cust3'    :    ['s2_eth0', 's2_eth1', 's1_eth3'],
        'trunk'    :    ['s0_eth4', 's1_por4', 's2_eth4']
        })#
        
        trunk_id, vlan_id = -1, -1
        for key, value in reversed(value_pair.items()):
            print key, "=>", value
            
            if'cust' in key:
                vlan_id += 1
                self.tag_customer_vlan(value, vlan_id, dp)
        
            elif 'trunk' in key:
                trunk_id += 1
                self.tag_trunk_vlan(value, trunk_id, dp)
    
if(__name__ == "__main__"):
    test()
    if False:
        h = 7
        while  h:
            print (h  if ((h - 1) > -1) else h + 1) 
            h -= 1
         


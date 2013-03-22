
from ryu.base import app_manager
from ryu.ofproto import ether, ofproto_v1_2
from ryu.controller import dpset, ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER
import logging

logger = logging.getLogger(__name__)

class BrightVLANTest(app_manager.RyuApp):

    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(BrightVLANTest, self).__init__(*args, **kwargs)
  
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


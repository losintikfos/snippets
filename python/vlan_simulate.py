
from ryu.base import app_manager
from ryu.ofproto import ether, ofproto_v1_2
from ryu.controller import dpset, ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER
import logging

logger = logging.getLogger(__name__)

class RunTestMininet(app_manager.RyuApp):

    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_2.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RunTestMininet, self).__init__(*args, **kwargs)
  
    def _define_flow(self, dp):
        logger.info("++++++++++++++++++++++++++")
    
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        LOG.info("<<>><><><><><><><><><><><><>")
        if ev.enter:
            self._define_flow(ev.dp)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dst, src, eth_type = struct.unpack_from('!6s6sH', buffer(msg.data), 0)
        in_port = msg.match.fields[0].value

        LOG.info("----------------------------------------")
        LOG.info("* PacketIn")
        LOG.info("in_port=%d, eth_type: %s", in_port, hex(eth_type))
        LOG.info("packet reason=%d buffer_id=%d", msg.reason, msg.buffer_id)
        LOG.info("packet in datapath_id=%s src=%s dst=%s",
                 msg.datapath.id, haddr_to_str(src), haddr_to_str(dst))


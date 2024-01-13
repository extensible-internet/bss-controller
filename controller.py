from pox.core import core
from pox.web.jsonrpc import JSONRPCHandler
from .receiver_tracker import ReceiversTracker, ReceiverInfo, ReceiveStatus
from .stream_tracker import StreamsTracker, StreamStatus

receivers_tracker = ReceiversTracker()
streams_tracker = StreamsTracker()
log = core.getLogger()

class BSSController (JSONRPCHandler):
  def __init__ (self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @classmethod
  def shutdown(cls):
    receivers_tracker.to_kill_thread = True

  def _exec_create_stream (self, stream_note: str = ""):
    """
    Creates stream and returns stream id. Used by sender.
    """
    return {
      "stream_id": streams_tracker.add_stream(note= stream_note).id
    }
  
  def _exec_update_stream (self, stream_id: str, lowest_block_at_sender: int, 
                           highest_block: int, highest_block_time: int, finished: bool,
                           blocks_per_second: float):
    """
    Method used by senders to tell the controller they just pushed blocks.

    Args:
        stream_id (str): Stream ID Hex
        lowest_block_at_sender (int): Lowest block # at sender (that was just pushed)
        highest_block (int): Highest block # at sender
        highest_block_time (int): Timestamp for the highest block #
        finished (bool): Whether the stream is finished
        blocks_per_second (float): Blocks per second
    """
    stream : StreamStatus = streams_tracker.get_stream(stream_id)
    if stream is None:
      return {"success": False}
    
    stream.update_stream({
      "lowest_block_at_sender": lowest_block_at_sender,
      "highest_block": highest_block,
      "highest_block_time": highest_block_time,
      "finished": finished,
      "blocks_per_second": blocks_per_second
    })
    return {"success": True}

  def _exec_receiver_rollcall (self, info, status):
    """
    Tells controller about a receiver and its stream receive status
    Returns which stream this receiver is to follow
    This is the only method used by receivers
    """
    receiver : ReceiverInfo = receivers_tracker.receiver_rollcall(info)

    if not receiver.receiver_stream_override and "stream_id" in status:
      receive_status = ReceiveStatus(status)
      receiver.add_status(receive_status)
    else:
      receiver.receiver_stream_override = False
    
    if receiver.current_status is not None:
      return {
        "status": streams_tracker.get_stream(receiver.current_status.stream_id).to_dict()
      }
    else:
      return {"status": None}
  
  def _exec_get_streams_status (self):
    """
    Get a list of `StreamStatus` objects
    """
    return {
      "status": [
        status.to_dict() for status in streams_tracker.get_streams()
      ]
    }
  
  def _exec_get_receivers_status (self):
    """
    Get a list of objects which each have a `ReceiverInfo` per receiver and
      a `ReceiveStatus` for info for its active stream
    """
    return {
      "status": [
        {
          "receiver": receiver.to_dict(),
          "status": receiver.current_status.to_dict() if receiver.current_status else None 
        } for receiver in receivers_tracker.get_receivers()
      ]
    }
  
  def _exec_join_receiver (self, receiver: str, stream: str):
    """
    Add a stream to be received by a receiver.
    The receiver will receive this information in the next roll call.

    Args:
        receiver (str): Receiver UUID hex
        stream (str): Stream UUID hex
    """
    receiver_info: ReceiverInfo = receivers_tracker.get_receiver(receiver)
    if receiver_info is None:
      return {"success": False}
    
    new_status : ReceiveStatus = ReceiveStatus({"stream_id": stream})
    receiver_info.add_status(new_status)
    receiver_info.receiver_stream_override = True
    return {"success": True}
  
  def _exec_disjoin_receiver (self, receiver: str, stream: str):
    """
    Set a stream to not be received by a receiver.
    The receiver will receive this information in the next roll call.

    Args:
        receiver (str): Receiver UUID hex
        stream (str): Stream UUID hex
    """
    #TODO: How is this communicated to the receiver
    pass

from pox.core import core
from pox.web.jsonrpc import JSONRPCHandler
from .receiver_tracker import ReceiversTracker, ReceiverInfo, ReceiveStatus
from .stream_tracker import StreamsTracker, StreamStatus
from .uuid_tracker import UUIDTracker

uuid_tracker = UUIDTracker()
receivers_tracker = ReceiversTracker(uuid_tracker)
streams_tracker = StreamsTracker(uuid_tracker)
log = core.getLogger()

class BSSController (JSONRPCHandler):
  def __init__ (self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @classmethod
  def get_response(cls, **kwargs):
    return {
      "response": kwargs
    }

  def _exec_hello (self):
    return BSSController.get_response(success=True)

  def _exec_get_uuid (self):
    return BSSController.get_response(uuid=uuid_tracker.get_uuid())

  def _exec_create_stream (self, uuid: str):
    """
    Creates stream with the given stream id. Used by sender.
    """
    created_stream = streams_tracker.add_stream(uuid_stream=uuid)
    return BSSController.get_response(success=created_stream is not None)

  def update_stream (self, stream_id: str, lowest_block: int,
                           highest_block: int, highest_block_time: int,
                           finished: bool, missing_blocks: list[int], current_source: list[int],
                           **kwargs):
    stream : StreamStatus = streams_tracker.get_stream(stream_id)
    log.info("Updating stream %s" % stream_id)
    if stream is None:
      log.info("Stream ID not found. Creating...")
      stream = streams_tracker.add_stream(uuid_stream=stream_id)
      if stream is None:
        return False

    streams_tracker.update_stream(stream, {
      "lowest_block": lowest_block,
      "highest_block": highest_block,
      "highest_block_time": highest_block_time,
      "finished": finished,
      "missing_blocks": missing_blocks,
      "current_source": current_source
    })
    return True


  def _exec_update_stream (self, **kwargs):
    """
    Method used by senders to tell the controller they just pushed blocks.

    Args:
        stream_id (str): Stream ID Hex
        lowest_block (int): Lowest block # at sender (that was just pushed)
        highest_block (int): Highest block # at sender
        highest_block_time (int): Timestamp for the highest block #
        creation_time (int): Timestamp for when stream was created at sender
        finished (bool): Whether the stream is finished
        missing_blocks (list[int]): Block #s that are missing
        current_source (list[int]): DSP of the current source reperesented as an array of three integers
    """
    try:
      return BSSController.get_response(success=self.update_stream(**kwargs))
    except TypeError: # probably because a required field is not given in kwargs
      return BSSController.get_response(success=False)

  def _exec_update_streams (self, streams: list):
    """
    Method used by senders to update multiple streams at once
    Args:
      streams (list): List of objects, each of which maps to an `update_stream` call
    """
    update_list = []
    for obj in streams:
      if "stream_id" not in obj: continue
      update = {"stream_id": obj["stream_id"], "success": False}
      try:
        update["success"] = self.update_stream(**obj)
      except TypeError: # presumably because obj is incomplete
        pass
      update_list.append(update)

    return BSSController.get_response(update_list=update_list)

  def _exec_delete_stream (self, stream_id: str, owner: bool, finished: bool, current_source: list[int]):
    """
    Deletes stream corresponding to the stream_id. First verifies if it is finished.
    """
    if not owner or not finished:
      return BSSController.get_response(success=False)

    # verify finished in stream tracker
    stream : StreamStatus = streams_tracker.get_stream(stream_id)
    if stream is None or not stream.finished: # No such stream or stream exists but is not finished
      return BSSController.get_response(success=False)

    return BSSController.get_response(success=streams_tracker.remove_stream(stream_id))

  def _exec_set_note (self, stream_id: str, note: str):
    stream : StreamStatus = streams_tracker.get_stream(stream_id)
    if stream is None:
      return BSSController.get_response(success=False)

    streams_tracker.update_stream(stream, {
      "note": note
    })
    return BSSController.get_response(success=True)

  def _exec_get_stream_status (self, stream_id: str):
    stream : StreamStatus = streams_tracker.get_stream(stream_id)
    if stream is None:
      return BSSController.get_response(success=False)
    return BSSController.get_response(success=True, **stream.to_dict())

  def _exec_receiver_rollcall (self, info, streams):
    """
    Tells controller about a receiver and its stream receive status
    Returns which stream this receiver is to follow
    This is the only method used by receivers
    """
    receiver : ReceiverInfo = receivers_tracker.receiver_rollcall(info)

    for status in streams:
      if "stream_id" in status:
        receive_status = ReceiveStatus(status)
        receivers_tracker.update_status(receiver, receive_status)

    current_stream_statuses = [streams_tracker.get_stream(current_status.stream_id).to_dict()
                               for current_status in receiver.current_statuses]

    return BSSController.get_response(receiver_status=receiver.to_dict(), joined_streams=current_stream_statuses)

  def _exec_get_streams_status (self):
    """
    Get a list of `StreamStatus` objects
    """
    return BSSController.get_response(
      status= [
        status.to_dict() for status in streams_tracker.get_streams()
      ]
    )

  def _exec_get_receivers_status (self):
    """
    Get a list of objects which each have a `ReceiverInfo` per receiver and
      a `ReceiveStatus` for info for its active stream
    """
    statuses = []
    for receiver in receivers_tracker.get_receivers():
      for status in receiver.current_statuses:
        statuses.append({
          "receiver": receiver.to_dict(),
          "status": status
        })
      if receiver.current_statuses == []:
        statuses.append({
          "receiver": receiver.to_dict(),
          "status": None
        })

    return BSSController.get_response(
        status= statuses
    )

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
      return BSSController.get_response(success=False)

    new_status : ReceiveStatus = ReceiveStatus({"stream_id": stream})
    receivers_tracker.add_status(receiver_info, new_status)
    return BSSController.get_response(success=True)

  def _exec_disjoin_receiver (self, receiver: str, stream: str):
    """
    Set a stream to not be received by a receiver.
    The receiver will receive this information in the next roll call.

    Args:
        receiver (str): Receiver UUID hex
        stream (str): Stream UUID hex
    """
    receiver_info: ReceiverInfo = receivers_tracker.get_receiver(receiver)
    if receiver_info is None:
      return BSSController.get_response(success=False)

    return BSSController.get_response(success=receivers_tracker.remove_status(receiver_info, stream))

  # def _exec_destroy_stream (self, stream_id: str):
  #   """
  #   Destroy a stream record

  #   Args:
  #       stream_id (str): Stream UUID hex
  #   """
  #   stream: StreamStatus = streams_tracker.get_stream(stream_id)
  #   if stream is None:
  #     return BSSController.get_response(success=False)

  #   return BSSController.get_response(
  #     success=streams_tracker.remove_stream(stream_id)
  #   )

  # def _exec_get_uuid (self):
  #   """
  #   Get a uuid guaranteed to be unique amongst the receivers and the streams
  #   """
  #   uuid_str = uuid_tracker.get_uuid()
  #   return BSSController.get_response(
  #     uuid= uuid_str
  #   )

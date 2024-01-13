from pox.core import core
import time
import threading

log = core.getLogger()

class ReceiveStatus:
  def __init__ (self, received_status_obj):
    self.stream_id = received_status_obj["stream_id"]
    self.lowest_received_block = received_status_obj.get("lowest_received_block", 0)
    self.highest_received_block = received_status_obj.get("highest_received_block", 0)
    self.highest_received_block_time = received_status_obj.get("highest_received_block_time", 0)
  
  def to_dict (self):
    return {
      "stream_id": self.stream_id,
      "skipped_blocks": 0,
      "lowest_received_block": self.lowest_received_block,
      "highest_received_block": self.highest_received_block,
      "highest_received_block_time": self.highest_received_block_time
    }

class ReceiverInfo:
  def __init__ (self, receiver_obj, roll_call_timestamp : float):
    self.id : str = receiver_obj["receiver_id"]
    self.note : str = receiver_obj.get("receiver_note", "")
    self.first_hop = receiver_obj.get("first_hop", [0,0,0])
    self.last_rollcall = roll_call_timestamp
    self.current_status = None
    self.receiver_stream_override = False
  
  def refresh (self, roll_call_timestamp):
    self.last_rollcall = roll_call_timestamp
  
  def add_status (self, status: ReceiveStatus):
    self.current_status = status
    
  def to_dict (self):
    return {
      "receiver_id": self.id,
      "receiver_note": self.note,
      "receiver_first_hop": self.first_hop,
      "timestamp": self.last_rollcall
    }

class ReceiversTracker:
  STALE_THREAD_SLEEP = 2
  DEAD_ROLL_CALL_INTERVAL = 5

  def __init__ (self):
    self.receivers : dict[str, ReceiverInfo] = {}
    
    # For thread to kill stale receiver info records
    self.receivers_lock = threading.Lock()
    self.to_kill_thread = False
    thread = threading.Thread(target=self.roll_call_update, args=[])
    thread.start()
  
  def get_receiver (self, receiver_id):
    return self.receivers.get(receiver_id, None)
  
  def get_receivers (self):
    with self.receivers_lock:
      receivers = list(self.receivers.values())
    return receivers
  
  def roll_call_update (self):
    while not self.to_kill_thread:
      time.sleep(ReceiversTracker.STALE_THREAD_SLEEP)

      for receiver_id in set(self.receivers.keys()):
        receiver = self.receivers[receiver_id]
        if receiver.last_rollcall <= time.time() - ReceiversTracker.DEAD_ROLL_CALL_INTERVAL:
          with self.receivers_lock:
            del self.receivers[receiver_id]

      print("Rollcall stale check, receivers", self.receivers)
    
  def receiver_rollcall (self, receiver):
    essential_keys = ["receiver_id"] # keys needed in object
    for key in essential_keys:
      if key not in receiver:
        return None
    
    receiver_id = receiver["receiver_id"]
    with self.receivers_lock:
      if receiver_id not in self.receivers:
        self.receivers[receiver_id] = ReceiverInfo(receiver, time.time())
      else:
        self.receivers[receiver_id].refresh(time.time())
    
    return self.receivers[receiver_id]

from pox.core import core
import time
import threading
import dbm
import pickle

log = core.getLogger()

class ReceiveStatus:
  def __init__ (self, received_status_obj):
    self.stream_id = received_status_obj["stream_id"]
    self.lowest_received_block = received_status_obj.get("lowest_received_block", 0)
    self.highest_received_block = received_status_obj.get("highest_received_block", 0)
    self.highest_received_block_time = received_status_obj.get("highest_received_block_time", 0)
    self.skipped_blocks = received_status_obj.get("skipped_blocks", 0)

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
    self.first_hop: list[int] = receiver_obj.get("first_hop", [0,0,0])
    self.last_rollcall: float = roll_call_timestamp
    self.current_status: ReceiveStatus = None
    self.receiver_stream_override: bool = False

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

  def __init__ (self, filename="receivers.db"):
    self.receivers : dict[str, ReceiverInfo] = dbm.open(filename, "n")
    self.receivers_lock = threading.Lock()
    self.roll_call_update()

  def __del__ (self):
    #TODO: Trigger this via POX
    print("Destructor for ReceiversTracker is being called")
    self.receivers.close()

  def get_receiver (self, receiver_id):
    receiver = self.receivers.get(receiver_id, None)
    if receiver is None:
      return None
    return pickle.loads(receiver)

  def get_receivers (self):
    #TODO: pagination?
    receiver_list = []
    with self.receivers_lock:
      k = self.receivers.firstkey()
      while k is not None:
        receiver_list.append(pickle.loads(self.receivers[k]))
        k = self.receivers.nextkey(k)

    return receiver_list

  def roll_call_update (self):
    for receiver_id in set(self.receivers.keys()):
      receiver = pickle.loads(self.receivers[receiver_id])
      if (receiver.last_rollcall
            <= time.time() - ReceiversTracker.DEAD_ROLL_CALL_INTERVAL 
          and receiver.current_status is None):
        with self.receivers_lock:
          del self.receivers[receiver_id]

    print("Rollcall stale check, receivers", self.receivers)
    core.call_delayed(ReceiversTracker.STALE_THREAD_SLEEP, 
                      self.roll_call_update)

  def persist (self, receiver_info_obj):
    # Called on a change to an object stored under the tracker
    self.receivers[receiver_info_obj.id] = pickle.dumps(receiver_info_obj)

  def refresh (self, receiver_info_obj, roll_call_timestamp):
    receiver_info_obj.last_rollcall = roll_call_timestamp
    self.persist(receiver_info_obj)

  def add_status (self, receiver_info_obj, status: ReceiveStatus, override=False):
    receiver_info_obj.current_status = status
    receiver_info_obj.receiver_stream_override = override
    self.persist(receiver_info_obj)

  def receiver_rollcall (self, receiver):
    essential_keys = ["receiver_id"] # keys needed in object
    for key in essential_keys:
      if key not in receiver:
        return None

    receiver_id = receiver["receiver_id"]
    with self.receivers_lock:
      if receiver_id not in self.receivers:
        obj = ReceiverInfo(receiver, time.time())
        self.persist(obj)
      else:
        obj = pickle.loads(self.receivers[receiver_id])
        self.refresh(obj, time.time())

    return obj

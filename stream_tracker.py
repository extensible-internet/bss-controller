from pox.core import core
import time
from .uuid_tracker import UUIDTracker
import dbm.gnu
import pickle
import uuid

log = core.getLogger()

class StreamStatus:
  default_time = 0

  def __init__ (self, id):
    self.id = id
    self.creation_time = time.time()
    self.update_stream()

  def update_stream (self, update_object = {}):
    defaults = {
      "lowest_block": 0,
      "highest_block": 100,
      "highest_block_time": StreamStatus.default_time,
      "owner": True,
      "finished": False,
      "current_source": [0,0,0],
      "missing_blocks": [],
      "note": None
    }

    for k in defaults:
      if hasattr(self, k) and k in update_object: # field already defined overriden by update
        setattr(self, k, update_object[k])
      elif not hasattr(self, k):
        setattr(self, k, update_object.get(k, defaults[k]))

  def to_dict (self):
    return {
      "stream_id": self.id,
      
      **{
        key: getattr(self, key) for key in [
          "note",
          "lowest_block",
          "highest_block",
          "highest_block_time",
          "owner",
          "finished",
          "current_source",
          "missing_blocks"
        ]
      }
    }

class StreamsTracker:
  def __init__ (self, uuid_tracker: UUIDTracker, filename="streams.db"):
    self.streams : dict[str, StreamStatus] = dbm.gnu.open(filename, "n")
    self.uuid_tracker = uuid_tracker
    uuid_tracker.add_store(self.streams)

  def get_stream (self, id):
    stream = self.streams.get(id, None)
    if stream is None:
      return None
    return pickle.loads(stream)

  def update_stream(self, obj: StreamStatus, to_update):
    # Trust that obj is in self.streams
    obj.update_stream(to_update)
    self.streams[obj.id] = pickle.dumps(obj)

  def remove_stream (self, id):
    try:
      del self.streams[id]
      return True
    except KeyError:
      return False

  def add_stream (self, uuid_stream, *args, **kwargs):
    if self.uuid_tracker.uuid_in_kv_stores(uuid_stream):
      return None
    stream = StreamStatus(uuid_stream, *args, **kwargs)
    self.streams[stream.id] = pickle.dumps(stream)
    return stream

  def get_streams (self):
    stream_list = []
    k = self.streams.firstkey()
    while k is not None:
      stream_list.append(pickle.loads(self.streams[k]))
      k = self.streams.nextkey(k)
    return stream_list

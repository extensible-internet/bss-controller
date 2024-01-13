from pox.core import core
import time
import uuid

log = core.getLogger()

class StreamStatus:
  default_time = 0

  def __init__ (self, note):
    self.note = note
    self.id = uuid.uuid4().hex
    self.creation_time = time.time()
    self.update_stream()
  
  def update_stream (self, update_object = {}):
    self.current_source = [0, 0, 0]
    
    # 0 in this field indicates there are no blocks at sender
    self.lowest_block_at_sender = update_object.get("lowest_block_at_sender", 0)
    
    self.highest_block = update_object.get("highest_block", 0)
    self.blocks_per_second = update_object.get("blocks_per_second", 0.)
    self.highest_block_time = update_object.get("highest_block_time", StreamStatus.default_time)
  
  def to_dict (self):
    return {
      "stream_id": self.id,
      "stream_note": self.note,
      
      **{
        key: getattr(self, key) for key in [
          "blocks_per_second",
          "creation_time",
          "current_source",
          "lowest_block_at_sender",
          "highest_block",
          "highest_block_time"
        ]
      }
    }

class StreamsTracker:
  def __init__ (self):
    self.streams : dict[str, StreamStatus] = {}
  
  def get_stream (self, id):
    return self.streams.get(id, None)
  
  def add_stream (self, *args, **kwargs):
    stream = StreamStatus(*args, **kwargs)
    self.streams[stream.id] = stream
    return stream
  
  def get_streams (self):
    return list(self.streams.values())

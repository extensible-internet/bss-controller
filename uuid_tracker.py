import uuid

class UUIDTracker:
  def __init__ (self):
    """
    Initializes an empty list of kv stores, where the keys are uuids
    """
    self.kv_stores = []

  def add_store (self, kv_store):
    self.kv_stores.append(kv_store)
  
  def uuid_in_kv_stores (self, possible_uuid):
    for kv_store in self.kv_stores:
      if possible_uuid in kv_store:
        return True
    return False
  
  def get_uuid (self):
    first = True
    while first or self.uuid_in_kv_stores(possible_uuid):
      possible_uuid = uuid.uuid4().hex
      first = False
    return possible_uuid
  
import requests

def call_rpc_method (method, params={}, id=1):
  r = requests.post("http://0.0.0.0:8000/bss/", json={
    "id": id,
      "jsonrpc": "2.0",
      "method": method,
      "params": params
  })
  res = r.json()
  assert "response" in res
  return res["response"]

print("Starting test ...")

assert call_rpc_method("hello")["success"]
print("Tested hello")

stream_id = call_rpc_method("get_uuid")["uuid"]
assert call_rpc_method("create_stream", {"uuid": stream_id})["success"]
print("Tested get uuid and create stream")

receiver_id = "test_receiver"

note = "Test Note"
assert call_rpc_method("set_note", {"stream_id": stream_id, "note": note})["success"]
list_of_streams = call_rpc_method("get_streams_status")["status"]
assert len(list_of_streams) == 1 and list_of_streams[0]["stream_id"] == stream_id
single_stream = call_rpc_method("get_stream_status", {"stream_id": stream_id})
assert single_stream["stream_id"] == stream_id
assert single_stream["note"] == note
print("Tested set note, get streams status and get stream status")

stream_config = {
  "lowest_block": 23,
  "highest_block": 100,
  "highest_block_time": 90234802389, 
  "owner": True,
  "finished": True,
  "missing_blocks": [95, 98],
  "current_source": [1, 2, 43]
}

assert call_rpc_method("update_stream", {"stream_id": stream_id, **stream_config})["success"]
list_of_streams = call_rpc_method("get_streams_status")["status"]

assert len(list_of_streams) == 1 and list_of_streams[0]["stream_id"] == stream_id
assert list_of_streams[0]["lowest_block"] == 23
print("Tested update stream")

second_stream_id = call_rpc_method("get_uuid")["uuid"]
assert not call_rpc_method("create_stream", {"uuid": stream_id})["success"]
assert call_rpc_method("create_stream", {"uuid": second_stream_id})["success"]

stream_config["lowest_block"] = 24
assert call_rpc_method("update_streams", {"streams": [
  {"stream_id": second_stream_id, **stream_config},
  {"stream_id": stream_id, **stream_config}
  ]})

list_of_streams = call_rpc_method("get_streams_status")["status"]
assert len(list_of_streams) == 2
assert list_of_streams[0]["lowest_block"] == 24 and list_of_streams[1]["lowest_block"] == 24
print("Tested update streams")

assert call_rpc_method("delete_stream", {"stream_id": second_stream_id, "owner": True, "finished": True, "current_source": []})["success"]
list_of_streams = call_rpc_method("get_streams_status")["status"]
assert len(list_of_streams) == 1
assert list_of_streams[0]["lowest_block"] == 24 and list_of_streams[0]["stream_id"] == stream_id
print("Tested delete stream")

rollcall_res = call_rpc_method("receiver_rollcall", {
          "info": {
            "receiver_id": receiver_id
          },
          "streams": []
      })

assert call_rpc_method("join_receiver", {"stream": stream_id, "receiver": receiver_id})["success"]
print("Tested empty rollcall and join receiver")

receiver_note = "Receiver Note Test"
rollcall_res = call_rpc_method("receiver_rollcall", {
          "info": {
            "receiver_id": receiver_id,
            "receiver_note": receiver_note
          },
          "streams": rollcall_res["joined_streams"]
      })
assert len(rollcall_res["joined_streams"]) == 1
assert rollcall_res["joined_streams"][0]["stream_id"] == stream_id
assert rollcall_res["receiver_status"]["receiver_id"] == receiver_id
assert rollcall_res["receiver_status"]["receiver_note"] == receiver_note
print("Tested rollcall")

assert call_rpc_method("disjoin_receiver", {"stream": stream_id, "receiver": receiver_id})["success"]
rollcall_res = call_rpc_method("receiver_rollcall", {
          "info": {
            "receiver_id": receiver_id
          },
          "streams": rollcall_res["joined_streams"]
      })
assert len(rollcall_res["joined_streams"]) == 0
print("Tested disjoin receiver")

list_of_receivers = call_rpc_method("get_receivers_status")["status"]
assert len(list_of_receivers) == 1 and list_of_receivers[0]["receiver"]["receiver_id"] == receiver_id
print("Tested get receivers status")

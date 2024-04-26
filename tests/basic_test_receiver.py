import requests
#TODO: naye rollcall ka implementation, redo this, spec go over

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

stream_id = call_rpc_method("get_uuid")["uuid"]
res = call_rpc_method("create_stream", {"uuid": stream_id})

assert res["success"]
receiver_id = "test_receiver"

list_of_streams = call_rpc_method("get_streams_status")["status"]
print(f'Get Streams Status: {list_of_streams}')
assert len(list_of_streams) == 1 and list_of_streams[0]["stream_id"] == stream_id

rollcall_res = call_rpc_method("receiver_rollcall", {
          "info": {
            "receiver_id": receiver_id
          },
          "streams": []
      })

res = call_rpc_method("join_receiver", {"stream": stream_id, "receiver": receiver_id})
assert res["success"]

rollcall_res = call_rpc_method("receiver_rollcall", {
          "info": {
            "receiver_id": receiver_id
          },
          "streams": rollcall_res["joined_streams"]
      })
assert len(rollcall_res["joined_streams"]) == 1
assert rollcall_res["joined_streams"][0]["stream_id"] == stream_id

list_of_receivers = call_rpc_method("get_receivers_status")["status"]
print(f'Get Receivers Status: {list_of_receivers}')
assert len(list_of_receivers) == 1 and list_of_receivers[0]["receiver"]["receiver_id"] == receiver_id

sample_uuid = call_rpc_method("get_uuid")["uuid"]
assert sample_uuid != ""

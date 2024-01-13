import requests

def call_rpc_method (method, params={}, id=1):
  r = requests.post("http://0.0.0.0:8080", json={
    "id": id,
      "jsonrpc": "2.0",
      "method": method,
      "params": params
  })
  return r.json()

res = call_rpc_method("create_stream", {"stream_note": "Hello World"})

stream_id = res["stream_id"]
receiver_id = "test_receiver"

list_of_streams = call_rpc_method("get_streams_status")["status"]
print(f'Get Streams Status: {list_of_streams}')
assert len(list_of_streams) == 1 and list_of_streams[0]["stream_id"] == stream_id

rollcall_res = call_rpc_method("receiver_rollcall", {
          "info": {
            "receiver_id": receiver_id
          },
          "status": {}
      })

res = call_rpc_method("join_receiver", {"stream": stream_id, "receiver": receiver_id})
assert res["success"]

rollcall_res = call_rpc_method("receiver_rollcall", {
          "info": {
            "receiver_id": receiver_id
          },
          "status": rollcall_res["status"]
      })
assert rollcall_res["status"]["stream_id"] == stream_id

list_of_receivers = call_rpc_method("get_receivers_status")["status"]
print(f'Get Receivers Status: {list_of_receivers}')
assert len(list_of_receivers) == 1 and list_of_receivers[0]["receiver"]["receiver_id"] == receiver_id

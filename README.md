# BSS Controller API Specification
- Needs to be updated when the controller api is changed
- This is using the JSON RPC protocol, for more information visit its [docs](https://www.jsonrpc.org/specification)
- Unless otherwise specified, values in the Request/Response object simply demonstrate the type, and the actual values are purely for example purpose

## Hello
- RPC: "hello"
- Used for testing, always responds with `success` being `true`
- Request:
```json
{}
```
- Response:
```json
{
  "success": true
}
```

## Create Stream
- RPC: "create_stream"
- Create a stream with the given note. Returns back the id of the stream. Supposed to be used by Senders.
- Request:
```json
{
  "stream_note": "[NOTE]"
}
```
- Response:
```json
{
  "stream_id": "[Hex UUID of newly created stream]"
}
```

## Update Stream
- RPC: "update_stream"
- Update stream status at the controller with updated values from the sender.
- Request (values just demonstrate type):
```json
{
  "stream_id": "[Hex UUID of stream]",
  "lowest_block_at_sender": 10,
  "highest_block": 100,
  "highest_block_time": 90234802389, // unix timestamp
  "finished": false,
  "blocks_per_second": 2.3,
  "current_source": [1, 2, 43], // DSP represented as array of three integers
}
```
- Response:
```json
{
  "success": true
}
```

## Receiver Rollcall
- RPC: "receiver_rollcall"
- Tells controller about a receiver and its stream receive status, returns information about the stream this receiver is to receive for
- Request takes in a ReceiverInfo and a ReceiveStatus as defined in the Design Document, and the response has a StreamStatus as defined in the Design Document
- Request:
```json
{
  "info": {
    "receiver_id": "[Hex UUID of the receiver]",
    "receiver_note": "[Receiver Note]",
    "receiver_first_hop": [1, 2] // DS represented as array of 2 integers
  },
  "status": {
    "stream_id": "[Hex UUID of stream currently receiving]",
    "lowest_received_block": 10,
    "highest_received_block": 100,
    "highest_received_block_time": 90234802389, // unix timestamp
    "skipped_blocks": 10
  }
}
```
- Response:
```json
{
  "status": 
}
```

## Get Streams' Status
- RPC: "get_streams_status"
- Returns back every stream's StreamStatus object
- Request:
```json
{}
```
- Response:
```json
{
  "status": [
    {
      "stream_id": "[Hex UUID]",
      "stream_note": "Stream Note sent in create_stream",
      "blocks_per_second": 10,
      "creation_time": 90234802389, // unix timestamp of when this stream was added to controller
      "current_source": [1, 2, 43], // DSP represented as array of three integers
      "lowest_block_at_sender": 10,
      "highest_block": 100,
      "highest_block_time": 90234802389, // unix timestamp
    },
    // more such objects
  ]
}
```

## Get Receivers' Status
- RPC: "get_receivers_status"
- Returns back every receiver's ReceiverInfo and ReceiveStatus objects
- Request:
```json
{}
```
- Response:
```json
{
  "status": [
    {
      "receiver": {
        "receiver_id": "[Hex UUID]",
        "receiver_note": "[Receiver Note sent in rollcall]",
        "receiver_first_hop": [1,2],
        "timestamp": 90234802389 // Last rollcall time at Controller
      },
      "status": {
        "stream_id": "[Hex UUID]",
        "skipped_blocks": 10,
        "lowest_received_block": 10,
        "highest_received_block": 100,
        "highest_received_block_time": 90234802389
      }
    }
    // more such objects
  ]
}
```

## Join Receiver
- RPC: "join_receiver"
- Tells controller to make a specific Receiver receive a specific Stream from now on
- Request:
```json
{
  "receiver": "[Hex UUID]",
  "stream": "[Hex UUID]"
}
```
- Response:
```json
{
  "success": true
}
```

## Disjoin Receiver
- RPC: "disjoin_receiver"
- Tells controller to not make a specific Receiver receive a specific Stream from now on
- Stream ID is not used
- Request:
```json
{
  "receiver": "[Hex UUID]",
  "stream": "[Hex UUID]"
}
```
- Response:
```json
{
  "success": true
}
```

## Get UUID
- RPC: "get_uuid"
- Gives back a UUID that is unique amongst all stream uuids and receiver uuids
- Request:
```json
{}
```
- Response:
```json
{
  "uuid": "[Hex UUID]"
}
```

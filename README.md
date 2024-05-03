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

## Get UUID
- RPC: "get_uuid"
- Gives back a UUID that is unique amongst all stream and receiver UUIDs
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

## Create Stream
- RPC: "create_stream"
- Create a stream with the given UUID. Returns whether or not the stream was created successfully.
- Request:
```json
{
  "uuid": "[Hex UUID]"
}
```
- Response:
```json
{
  "success": true
}
```

## Update Stream
- RPC: "update_stream"
- Update stream status at the controller with updated values from the sender.
- Request (values just demonstrate type):
```json
{
  "stream_id": "[Hex UUID of stream]",
  "lowest_block": 1,
  "highest_block": 100,
  "highest_block_time": 90234802389, // unix timestamp
  "owner": true, // True if owner/source of stream, false if receiver
  "finished": false, // If this is true, the stream is done and won't be updated any more
  "missing_blocks": [95, 98],
  "current_source": [1, 2, 43], // DSP represented as array of three integers, blank if not known
}
```
- Response:
```json
{
  "success": true
}
```

## Update Streams
- RPC: "update_streams"
- The same as update_stream, but with multiple objects
- Request:
```json
{
  "streams": [
    {
      "stream_id": "[Hex UUID of stream]",
      "lowest_block": 1,
      "highest_block": 100,
      "highest_block_time": 90234802389, // unix timestamp
      "owner": true, // True if owner/source of stream, false if receiver
      "finished": false, // If this is true, the stream is done and won't be updated any more
      "missing_blocks": [95, 98],
      "current_source": [1, 2, 43], // DSP represented as array of three integers, blank if not known
    },
    ... // More entries follow
  ]
}
```
- Response:
```json
{
  "success": true
}
```

## Delete Stream
- RPC: "delete_stream"
- Deletes the stream and all its properties at the controller. The stream's UUID is freed for use elsewhere.
- Request:
```json
{
  "stream_id": "[Hex UUID of stream]",
  "owner": true, // If this isn't true, don't delete the stream
  "finished": true, // If this hasn't also been true in a previous update_stream call, do not delete
  "current_source": [1, 4, 32],
}
```
- Response:
```json
{
  "success": true
}
```

## Set Note
- RPC: "set_note"
- Sets the note on a stream
- Request:
```json
{
  "stream_id": "[Hex UUID of stream]",
  "note": "This is a note describing a stream",
}
```
- Response:
```json
{
  "success": true
}
```

## Get Stream Status
- RPC: "get_stream_status
- Returns back a single stream's StreamStatus object
- Request:
```json
{
  "stream_id": "[Hex UUID]"
}
```
Response:
```json
{
  "stream_id": "[Hex UUID]",
  "note": "Stream note, if any",
  "blocks_per_second": 10,
  "creation_time": 90234802389, // unix timestamp in microseconds of when this stream was added to controller
  "current_source": [1, 2, 43],
  "finished": false,
  "lowest_block": 10,
  "highest_block": 100,
  "highest_block_time": 90234802389, // unix timestamp in microseconds
  "missing_blocks": [11, 52]
}
```


## Get Streams Status
- RPC: "get_streams_status"
- Returns back every stream's StreamStatus object  (TODO: Optional filter by receiver in request)
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
      "note": "Stream note, if any",
      "blocks_per_second": 10,
      "creation_time": 90234802389, // unix timestamp in microseconds of when this stream was added to controller
      "current_source": [1, 2, 43],
      "finished": false,
      "lowest_block": 10,
      "highest_block": 100,
      "highest_block_time": 90234802389, // unix timestamp in microseconds
      "missing_blocks": [11, 52]
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
- Tells controller to not send information about a specific Stream from now on via receiver_rollcall
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
- Tells controller to not send information about a specific Stream from now on via receiver_rollcall
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

## Receiver Rollcall
- RPC: "receiver_rollcall"
- Tells controller about a receiver and its stream receive status, returns information about the stream this receiver is to receive for
- Request takes in a ReceiverInfo and a ReceiveStatus as defined in the Design Document, and the response has a StreamStatus as defined in the Design Document
- Request:
```json
{
  "info": {
    "receiver_id": "[Hex UUID]", // Only field truly required in info
    "first_hop": [1, 5, 10],
    "receiver_note": "Some note"
  },
  "streams": [
    {
      "stream_id": "[Hex UUID]",
      "lowest_block": 1,
      "highest_block": 45,
      "highest_block_time": 398195718933,
      "owner": false, // Should always be false, since these are receiever updates
      "missing_blocks": [35, 42], // Blocks the receiver is missing
      "current_source": [2, 5, 7], // What the receiver thinks the source is
    },
  ]
}
```
- Response:
```json
{
  "receiver_status": {
    "reciever_id": "[Hex UUID]",
    "first_hop": [1, 5, 10],
    "receiver_note": "A note, if the receiver has any",
    "last_rollcall": 918573830 // Last rollcall time at controller
  },
  "joined_streams": [
    {
      "stream_id": "[Hex UUID]",
      "lowest_block": 1,
      "highest_block": 73,
      "highest_block_time": 398195718933,
      "missing_blocks": [10, 53],
      "current_source": [3, 1, 12]
    },
    ... // More streams follow
  ]
}
```

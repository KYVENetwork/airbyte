import json


def preprocess_tendermint_data_item(data_item):
    begin_block_events = data_item["value"]["block_results"].pop("begin_block_events")
    end_block_events = data_item["value"]["block_results"].pop("end_block_events")
    txs_results = data_item["value"]["block_results"].pop("txs_results")

    height = int(data_item.pop("key"))

    data_item["height"] = height

    preprocessed_data_item = [data_item]

    preprocessed_data_item.extend(get_event_rows(begin_block_events, height, data_item["offset"]))
    preprocessed_data_item.extend(get_event_rows(end_block_events, height, data_item["offset"]))
    preprocessed_data_item.extend(get_event_rows(txs_results, height, data_item["offset"]))

    return preprocessed_data_item


def get_event_rows(events, height, offset):
    event_rows = []
    if events is not None:
        for index, event in enumerate(events):
            # Convert event to JSON-serializable format
            event_json = json.loads(json.dumps(event))
            event_rows.append(json.loads(json.dumps(
                {
                    "height": height,
                    "value": event_json,
                    "type": "txs_result",
                    "arr_idx": index,
                    "offset": offset
                }
            )))

    return event_rows

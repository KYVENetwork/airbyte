#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import math
import requests
import sys
import textwrap


def estimate_size(obj):
    size = sys.getsizeof(obj)
    if hasattr(obj, '__iter__'):
        if hasattr(obj, 'items'):
            # For dictionaries
            size += sum(estimate_size(v) for v in obj.items())
        elif not isinstance(obj, str):
            # For lists, sets, tuples
            size += sum(estimate_size(i) for i in obj)
    return size


def query_endpoint(endpoint):
    try:
        if not (endpoint.startswith("https://") or endpoint.startswith("http://")):
            endpoint = "https://" + endpoint
        response = requests.get(endpoint)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Failed to query {endpoint}: {e}")
        return None


def split_string_in_chunks(string, chunk_amount):
    chunk_length = math.floor(len(string) / chunk_amount)
    return textwrap.wrap(string, chunk_length)


def split_data_item_in_chunks(data_item, chunk_amount):
    chunks = split_string_in_chunks(str(data_item["value"]), chunk_amount)

    res = []
    for index, chunk in enumerate(chunks):
        chunked_data_item = {"key": data_item["key"], "value": chunk, "offset": data_item["offset"], "chunk_index": index}

        res.append(chunked_data_item)

    return res

#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import math
import requests
import textwrap


def bytes_to_mb(bytes_data):
    size_in_mb = len(bytes_data) / (1024 * 1024)

    return size_in_mb


def object_to_bytes(obj):
    str_obj = str(obj)
    bytes_data = str_obj.encode('utf-8')

    return bytes_data


def size_of_object(obj):
    # Get and return size of data_item in MB
    data_item_in_bytes = object_to_bytes(obj)

    return bytes_to_mb(data_item_in_bytes)


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

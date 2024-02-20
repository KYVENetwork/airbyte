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
        res.append({"key": data_item["key"], "value": chunk, "offset": data_item["offset"],
                    "chunk_index": index})

    return res


def transform_bundle(decompressed_as_json, bundle_id, max_MB):
    transformed_data = []

    for data_item in decompressed_as_json:
        # Add offset
        data_item["offset"] = bundle_id

        # Get size of data_item in MB
        data_item_in_bytes = object_to_bytes(data_item)
        size_of_data_item = bytes_to_mb(data_item_in_bytes)

        # Split if data_item > max_MB
        if size_of_data_item > max_MB:
            print("Data item with key", data_item["key"], "is larger than", max_MB, "MB, start chunking")
            chunks_amount = math.ceil(size_of_data_item / max_MB)
            chunks = split_data_item_in_chunks(data_item, chunks_amount)
            print("Chunked successfully")

            # Add each chunk to transformed_data
            for chunk in chunks:
                transformed_data.append(chunk)
        else:
            transformed_data.append(data_item)

    return transformed_data

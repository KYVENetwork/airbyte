#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import math
import requests
import textwrap


def query_endpoint(endpoint):
    try:
        if not (endpoint.startswith("https://") or endpoint.startswith("http://")):
            endpoint = "https://" + endpoint
        response = requests.get(endpoint)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Failed to query {endpoint}: {e}")
        return None


def query_endpoint_in_gateway_endpoints(gateway_endpoints, storage_id, logger):
    # Try to query each endpoint in the given order and break loop if query was successful
    # If no endpoint is successful, skip the bundle
    for endpoint in gateway_endpoints:
        response_from_storage_provider = query_endpoint(f"{endpoint}{storage_id}")
        if response_from_storage_provider is not None:
            return response_from_storage_provider
    else:
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

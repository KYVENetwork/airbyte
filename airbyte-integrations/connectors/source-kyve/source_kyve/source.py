#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream import KYVEStream


class SourceKyve(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # check that pools and bundles are the same length
        pools = config.get("pool_ids").split(",")
        start_ids = config.get("start_ids").split(",")
        data_item_size_limit = config.get("data_item_size_limit")
        tendermint_normalization = config.get("enable_tendermint_normalization")

        if config.get("start_keys"):
            start_keys = config.get("start_keys").split(",")
            if not len(pools) == len(start_ids) == len(start_keys):
                return False, "Please add a start_id and a start_key for every pool"

        if config.get("end_keys"):
            end_keys = config.get("end_keys").split(",")
            if not len(pools) == len(start_ids) == len(end_keys):
                return False, "Please add a start_id and a end_key for every pool"

        if not len(pools) == len(start_ids):
            return False, "Please add a start_id for every pool"

        if data_item_size_limit < 10 and data_item_size_limit != 0:
            return False, "Data item size limit needs to be greater than or equal to 10MB"

        if tendermint_normalization and data_item_size_limit != 0:
            return False, "Please choose either Data item size limt or Tendermint normalization - both are not allowed"

        for pool_id in pools:
            try:
                # check if endpoint is available and returns valid data
                response = requests.get(f"{config['url_base']}/kyve/query/v1beta1/pool/{pool_id}")
                if not response.ok:
                    # todo improve error handling for cases like pool not found
                    return False, response.json()
            except Exception as e:
                return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams: List[Stream] = []

        pools = config.get("pool_ids").split(",")
        start_ids = config.get("start_ids").split(",")
        tendermint_normalization = config.get("enable_tendermint_normalization")

        for i, (pool_id, start_id) in enumerate(zip(pools, start_ids)):
            response = requests.get(f"{config['url_base']}/kyve/query/v1beta1/pool/{pool_id}")
            pool_data = response.json().get("pool").get("data")

            config_copy = dict(deepcopy(config))
            config_copy["start_ids"] = int(start_id)
            config_copy["start_keys"] = int(-1e18)
            config_copy["end_keys"] = int(1e18)
            config_copy["data_item_size_limit"] = 0
            config_copy["tendermint_normalization"] = tendermint_normalization

            if config.get("start_keys"):
                config_copy["start_keys"] = int(config.get("start_keys").split(",")[i])

            if config.get("end_keys"):
                config_copy["end_keys"] = int(config.get("end_keys").split(",")[i])

            if config.get("data_item_size_limit"):
                config_copy["data_item_size_limit"] = int(config.get("data_item_size_limit"))

            streams.append(KYVEStream(config=config_copy, pool_data=pool_data))

        return streams

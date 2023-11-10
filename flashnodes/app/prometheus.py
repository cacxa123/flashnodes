from math import ceil
from typing import List, Literal

import requests
from requests.auth import HTTPBasicAuth

from app.core.config import settings


def generate_time_slice(timerange: Literal["1h", "1d", "7d", "30d"]):
    if timerange == "1h":
        return "[1h:10m]"
    elif timerange == "1d":
        return "[1d:3h]"
    elif timerange == "7d":
        return "[7d:1d]"
    elif timerange == "30d":
        return "[30d:5d]"


def get_analytics(api_key: str, timerange: Literal["1h", "1d", "7d", "30d"]) -> List:
    response = requests.get(settings.PROMETHEUS_URL + '/api/v1/query',
                            params={
                                "query": 'delta(%s{api_key="%s",envoy_cluster_name=~"user_.*_http"}[1m])%s' %
                                         (settings.PROMETHEUS_METRIC, api_key, generate_time_slice(timerange))},
                            auth=HTTPBasicAuth(settings.PROMETHEUS_USER, settings.PROMETHEUS_PASSWORD))
    result = response.json()["data"]["result"]
    if result:
        return [
            {
                "timestamp": item[0],
                "value": ceil(float(item[1]))
            } for item in response.json()["data"]["result"][0]["values"]
        ]
    return []


def get_analytics_total(api_key_list: List[str], timerange: Literal["1h", "1d", "7d", "30d"]):
    response = requests.get(settings.PROMETHEUS_URL + '/api/v1/query',
                            params={
                                "query": 'delta(%s{api_key=~"%s",envoy_cluster_name=~"user_.*_http"}[1m])%s' %
                                         (settings.PROMETHEUS_METRIC, "|".join(api_key_list), generate_time_slice(timerange))},
                            auth=HTTPBasicAuth(settings.PROMETHEUS_USER, settings.PROMETHEUS_PASSWORD))
    result = response.json()["data"]["result"]
    single_response = {}
    for metric in result:
        for timestamp, value in metric["values"]:
            if timestamp not in single_response:
                single_response[timestamp] = ceil(float(value))
            else:
                single_response[timestamp] += ceil(float(value))
    if single_response:
        return [{
            "timestamp": timestamp,
            "value": value
        } for timestamp, value in single_response.items()]
    return []


if __name__ == '__main__':
    print(get_analytics_total(["cte7aju2-z8f96p4b-ag0039p6-lea465v92", "cte7aju2-z8f96p4b-ag0039p6-lea465v92"], "1h"))

#!/usr/bin/env python

from flask import Flask
from flask import render_template
from flask import jsonify

import elasticsearch

import json

app = Flask(__name__, static_url_path="")
es = elasticsearch.Elasticsearch("glados")

def get_hosts():
    hosts = []
    query = {
            "size":256,
            "aggs": {
                "all_hosts" : {
                    "cardinality" : {
                        "field" : "hostname"
                    }
                }
             }
    }
    host_data = es.search("network-scan", "host", body=query)
    for host_entry in host_data["hits"]["hits"]:
        hosts.append(host_entry["_source"]["hostname"])
    hosts = list(set(hosts))

    for i in range(len(hosts)):
        hosts[i] = tuple((int(x) for x in hosts[i].split(".")))

    hosts.sort()

    for i in range(len(hosts)):
        hosts[i] = ".".join((str(x) for x in hosts[i]))

    return hosts

def get_host_detail(host):
    scantimes= []
    scans = es.search("network-scan", "scan")
    for scan in scans["hits"]["hits"]:
        scantimes.append(scan["_source"]["timestamp"])

        scantimes.sort()
    scantimes = set(scantimes)

    query = {
                "query" : {
                    "term" : { "hostname": host}
                }
            }

    host_data = es.search("network-scan", "host", body=query)
    timestamps = []
    for host_entry in host_data["hits"]["hits"]:
        timestamps.append( host_entry["_source"]["timestamp"])

    timestamps.sort()
    #host_times = {}
    up_count = 0
    for stamp in scantimes:
        if stamp in timestamps:
            #host_times[stamp] = True
            up_count += 1
        #else:
            #host_times[stamp] = False
    uptime = float(up_count) / float(len(scantimes))
    downtime = (1 - uptime) * 100
    uptime = uptime * 100

    return [{ "label":"uptime", "count":uptime},
            { "label":"downtime", "count":downtime}]

def get_detailed_hosts():
    hosts = {}

    for host in get_hosts():
        host_data = get_host_detail(host)
        hosts[host] = host_data

    return hosts

@app.route("/")
def index():
    hosts = get_detailed_hosts()
    ips = hosts.keys()

    for i in range(len(ips)):
        ips[i] = tuple((int(x) for x in ips[i].split(".")))

    ips.sort()

    for i in range(len(ips)):
        ips[i] = ".".join((str(x) for x in ips[i]))

    data = {"hosts":hosts, "ordered_hosts":ips}
    return render_template("index.html", **data)

@app.route("/api/v1/hosts")
def all_hosts():
    return json.dumps(get_hosts())

@app.route("/api/v1/hosts/<host>")
def host_detail(host):

    return json.dumps(host_times)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)

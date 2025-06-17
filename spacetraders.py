#!/bin/python3
# spacetraders-client
# Copyright (C) 2025  LumenLuminis
# SPDX-License-Identifier: GPL-3.0-or-later

#---

#!/bin/python3

# TODO use Textual for TUI
# - Yeet by price
# - -> Market Database
# create list of traits etc so can do matching "market" instead of "MARKETPLACE" etc
# create classes such that loc based funcs can have ship inputs and use loc of ship

__DEBUG__=False

import requests
import time
from datetime import datetime, timezone
import json
from response import Response
from header import headers
# from survey import Survey

url = "https://api.spacetraders.io/v2/"
ships = "my/ships/"
systems = "systems/"
scans = "/scan/"
waypoints = "/waypoints/"
contracts = "my/contracts/"

get = requests.get
post = requests.post

get_agent = "my/agent"

def dwrapper(res):
    return res[0] if len(res)==1 else res

def dewrapper(req):
    if type(req)==str:
        return req
    keys=[req.json()[item] if item in req.json().keys() else [] for item in ["data","error","events"]]
    resp = Response(*keys)
    if __DEBUG__:
        pprint(resp)
    return resp

def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))

dget = compose(dewrapper,get)
dpost = compose(dewrapper,post)

def pprint(content):
    if type(content)==Response:
        print(json.dumps(content.to_json(), indent=2))
    else:
        print(content)

def timestamp_parse(ts):
    if ts.endswith("Z"):
        ts=ts.rstrip("Z")
    return datetime.fromisoformat(ts)

def sysSymFromFull(path):
    return path.rsplit("-",1)[0]

# CONTRACTS
def get_contracts():
    return dget(url+"my/contracts", headers = headers)

def get_contract(contract_id):
    return dget(url+"my/contracts/"+contract_id, headers = headers)

def list_contracts(contracts):
    for contract in contracts:
        print(contract["id"], contract["type"])
    return contracts[0]["id"]

def acc_contract(contract_id):
    return dewrapper(requests.post(url+contracts[:-2]+contract_id+"/accept", headers=headers))

def contract_still_possible(contract_id):
    if contract_expired(contract_id) or contract_fulfilled(contract_id):
        return True
    return False

def contract_fulfilled_or_expired(contract_id, traveltime = 0):
    cont = get_contract(contract_id)
    remaining_time = (timestamp_parse(cont["terms"]["deadline"])-datetime.utcnow()).total_seconds()
    if remaining_time <= traveltime:
        return True

def contract_fulfilled(contract_id):
    cont = get_contract(contract_id)
    if cont["deliver"]["unitsRequired"]>=cont["deliver"]["unitsFulfilled"]:
        return True

def fulfill_contract(contract_id):
    return dpost(url+contracts+contract_id+"/fulfill", headers=headers)

def negotiate_contract(ship):
    return dpost(url+ships+ship+"/negotiate/contract", headers=headers)

# SENSORS
def get_systems():
    return dget(url+systems)

def get_current_waypoint(ship):
    return dget(url+ships+ship, headers=headers)["nav"]["route"]["destination"]["symbol"]

def get_current_system(ship):
    return sysSymFromFull(get_current_waypoint(ship))

def sense_system(sysSym):
    return dget(url+"systems/"+sysSym+"/waypoints")

def sense_planet(waySym):
    sysSym = sysSymFromFull(waySym)
    return dewrapper(requests.get(url+"systems/"+sysSym+"/waypoints/"+waySym, headers = headers))

def sense_for_in_system(sysSym, ftype = "", ftraits = "", fmods = ""):
    filters = {}
    filtertypes = {"type":ftype,"traits":ftraits,"modifiers":fmods}
    for key, value in filtertypes.items():
        filters[key] = value.split(",") if value!="" else None
    return dget(url+"systems/"+sysSym+"/waypoints", params = filters)

def create_chart(ship):
    return dpost(url+ships+ship+"/chart", headers=headers)

def create_survey(ship):
    return dpost(url+ships+ship+"/survey", headers=headers)

# Shipyard
def avail_ships(planWay):
    return dewrapper(requests.get(url+"systems/"+sysSymFromFull(planWay)+"/waypoints/"+planWay+"/shipyard"))

def buy_ship(shipType, waySym):
    return requests.post(url+"my/ships", headers = headers, data = {"shipType": shipType, "waypointSymbol": waySym} ).json()

# Ship Maintenance and Inventory
def get_all_ships():
    return dget(url+"my/ships", headers=headers)

def get_ship(ship):
    return dget(url+ships+ship, headers=headers)

def get_ship_cooldown(ship):
    return dget(url+ships+ship+"/cooldown", headers=headers)


# Navigation and Flying
def orbit(ship):
    return post(url+"my/ships/"+ship+"/orbit", headers = headers)

def dock(ship):
    return dewrapper(requests.post(url+ships+ship+"/dock", headers=headers))

def refuel(ship):
    return dewrapper(requests.post(url+ships+ship+"/refuel", headers=headers))

def nav(ship, waySym):
    return dpost(url+ships+ship+"/navigate", headers = headers, data = {"waypointSymbol":waySym})

navigate=nav

def fly_to(ship, waySym, stance="Cruise"):
    orbit(ship)
    return nav(ship,waySym)

def scan(ship, target):
    return dewrapper(post(url+ships+ship+scans+target, headers=headers))

def get_status(ship):
    return dget(url+ships+ship, headers=headers)

## Cargo
def transfer(send,rec,cargo,units):
    return dpost(url+ships+send+"/transfer", headers=headers, json = {"tradeSymbol":cargo, "units":int(units), "shipSymbol":rec})

def get_cargo(ship):
    return dget(url+ships+ship+"/cargo", headers=headers)

def get_cargo_capacity(ship):
    return dget(url+ships+ship+"/cargo", headers = headers)["capacity"]

def get_cargo_rem_space(ship):
    ship_cargo = dget(url+ships+ship+"/cargo", headers = headers)
    return ship_cargo["capacity"]-ship_cargo["units"]

def get_cargo_types(ship):
    return [item["symbol"] for item in get_cargo(ship)["inventory"]]

def get_cargo_amount(ship, cargo):
    return sum([item["units"] for item in get_cargo(ship)["inventory"] if cargo in item["symbol"]])

def yeet(ship, cargo, units):
    return dpost(url+ships+ship+"/jettison", json={"symbol":cargo, "units":int(units)}, headers=headers)

def yeet_all(ship, cargo):
    return yeet(ship, cargo, get_cargo_amount(ship, cargo))

# Mining
def extract(ship):
    return dewrapper(requests.post(url+ships+ship+"/extract", headers=headers))

def extract_with_survey(ship, survey):
    return dpost(url+ships+ship+"/extract/survey", headers=headers, json=survey)

# Admin
def list_ships():
    return requests.get(url+"my/ships", headers = headers).json()

def mine_for(ship, ore, cooldown=70, thresh=0.9):
    cargo = get_cargo(ship)
    first_luck = True
    while not any(ore.lower() in item["symbol"].lower() for item in cargo["inventory"]):
        print(extract(ship))
        if cargo["units"]>=thresh*cargo["capacity"]: ## Add yeet by price, for that make market db
            print(yeet(ship, cargo["inventory"][-1]["symbol"],cargo["inventory"][-1]["units"]))
        if first_luck == False: ## In case the first extract is already successful, we just don't sleep
            time.sleep(cooldown)
        first_luck = False
        cargo = get_cargo(ship)
        print([carg["symbol"] for carg in cargo["inventory"]])

def get_market_data(waypoint):
    sys = sysSymFromFull(waypoint)
    return dget(url+systems+sys+waypoints+waypoint+"/market", headers=headers)

def sell(ship, goods, units=-1):
    if units==-1:
        units = get_cargo_amount(ship, goods)
    return dpost(url+ships+ship+"/sell", json={"symbol":goods, "units":units}, headers=headers)

def deliver(ship, contract_id, goods, units=-1): #if unit unspec -> deliver all
    dock(ship)
    if units==-1:
        units = get_cargo_amount(ship, goods)
    return dpost(url+contracts+contract_id+"/deliver", headers=headers, json={"shipSymbol": ship, "tradeSymbol": goods, "units": units})

def await_fly_to(ship, waypoint, stance=None):
    dest_json = fly_to(ship, waypoint, stance)
    pprint(dest_json)
    if dest_json.error!=[] and dest_json.error["code"]==4204:
        return "Already there"
    elif dest_json.error!=[] and dest_json.error["code"]==4214:
        return "In Trans"
    if not "nav" in dest_json.data:
        return dest_json
    if dest_json["nav"]["status"]:
        arriv=timestamp_parse(dest_json.data["nav"]["route"]["arrival"].rstrip("Z"))
    else:
        arriv=timestamp_parse(dest_json.data["nav"]["arrival"].rstrip("Z"))
    delay = (arriv-datetime.utcnow()).total_seconds()
    print("En route, ETA:", delay)
    time.sleep(delay)
    return "Arrived"



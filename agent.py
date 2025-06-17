#!/bin/python3
# spacetraders-client
# Copyright (C) 2025  LumenLuminis
# All Rights Reserved
nprint=print
import spacetraders as sp
from spacetraders import pprint as print
import time
import math
import argparse

parser = argparse.ArgumentParser(
        prog = "CLI Single Task Spacetraders Client",
        description = "duh"
        )
subparsers = parser.add_subparsers(dest="command")
parser_mine_contract = subparsers.add_parser("mine_contract", help="Contract command help")
parser_mine_contract.add_argument("ship")
parser_mine_contract.add_argument("mine_location")
parser_mine_contract.add_argument("contract_id")
parser_mine_contract.add_argument("--yeet_overflow")
parser_mine_contract.add_argument("--overflow_market")
parser_mine_contract.add_argument("--market_search")
parser_mine_contract.add_argument("--cooldown")
parser_mine_contract.add_argument("--cargo_threshold")

parser_navigate = subparsers.add_parser('navigate', help='Navigate command help')
parser_navigate.add_argument("ship")
parser_navigate.add_argument('waypoint', type=str, help='Waypoint')
parser_navigate.add_argument('--stance', type=str, help='Stance')

parser_contract = subparsers.add_parser("get_contract", help="Contract command help")
parser_contract.add_argument("--id", help="Only get specified contract")

parser_scan = subparsers.add_parser("scan", help="Only specify one option or none for all systems")
parser_scan.add_argument("--sys", help="scan system")
parser_scan.add_argument("--ship", help="scan around ship")

args = parser.parse_args()
print(args)



conts = sp.get_contracts()
# print(conts)
c_id = conts[0]["id"]
# print(mine_contract(ship="OWL_01-4", mine_location="X1-DU70-XA5A", contract_id = c_id, yeet_overflow=False))

#print(sp.get_contracts()) # THIS FOOKIN WORKS! YAY

def mine_contract(ship, mine_location, contract_id, yeet_overflow=True, overflow_market=None, market_search=False, cooldown=70, thresh=1):
    # We have to redo the default values since argparse passes none for undefined variables...
    if yeet_overflow==None:
        yeet_overflow=True
    if market_search == None:
        market_search=False
    if cooldown == None:
        cooldown=70
    if thresh == None:
        thresh=1
    ### TO DO THIS CONTRACT WE HAVE TO
    # - FLY TO THE MINE
    # - FILL OUR CARGOSPACE; IF overflow IS yeet, WE CAN YEET HERE
    # - FLY TO CONTRACT DELIVERY
    # - DELIVER CONTRACT; IF overflow_market IS NONE, SELL HERE, IF IMPOSSIBLE, yeet
    # - FLY TO MARKET; SELL ALL
    # repeat until contract fulfilled or expired
    cargo_capacity = sp.get_cargo_capacity(ship)
    cont = sp.get_contract(contract_id)
    print(cont)
    cont_terms = cont["terms"]
    contract_item = [item["tradeSymbol"] for item in cont_terms["deliver"]]
    contract_location = cont_terms["deliver"][0]["destinationSymbol"] #### WARNING THIS WILL ONLY WORK IF ALL HAVE TO BE DELIVERED TO THE SAME LOCATION
    # to fix this i have to rewrite the function to allow delivery location, then i can just call the function multiple times for all locations
    if overflow_market==None and yeet_overflow!=True:
        if market_search:## Implement market search
            print("ERROR MARKET SERACH NOT YET IMPLEMENTED")
        if "marketplace" in map(str.lower,[trait["symbol"] for trait in sp.sense_planet(contract_location)["traits"]]):
            overflow_market = contract_location
        else:
            yeet_overflow = True
            print("ERROR LOCATION HAS NO MARKET AND SEARCH IS OFF")
            # SHOULD I THROW THIS?
    while not sp.contract_fulfilled_or_expired(contract_id, traveltime=cooldown*1.1): 
        while sp.get_cargo_rem_space(ship)>math.ceil((1-thresh)*cargo_capacity):
            print(sp.await_fly_to(ship, mine_location))
            print(sp.extract(ship))
            time.sleep(cooldown)
            if yeet_overflow==True:
                for item in sp.get_cargo_types(ship):
                    if item not in contract_item:
                        print(sp.yeet_all(ship, item))
        # This is potentially useless / wastefull since we fly there even if we don't have the materials, so only if we sell waste and deliver!=shop
        print(sp.await_fly_to(ship, contract_location))
        print(sp.deliver(ship, contract_id, contract_item[0])) # ALSO HACKED FOR LISTS
        if yeet_overflow != True:
            if sp.get_cargo_rem_space(ship)!=0 and overflow_market!=contract_location:
                print(sp.await_fly_to(ship, overflow_market))
            for item in sp.get_cargo_types(ship):
                sellcode = sp.sell(ship, item)
                if sellcode.error!=[]:
                    sp.yeet_all(ship,item)
            sp.dock(ship)
            print(sp.refuel(ship))
            sp.orbit(ship)
    if sp.contract_expired(contract_id):
        print("[EE] Contract Expired")
    else:
        print(sp.fulfill_contract(contract_id))

def navigate(ship, waypoint):
    print(sp.fly_to(ship, waypoint))

# print(sp.await_fly_to("OWL_01-4", "X1-DU70-H51")


if args.command=="mine_contract":
    mine_contract(args.ship, args.mine_location, args.contract_id, args.yeet_overflow, args.overflow_market, args.market_search, cooldown=args.cooldown, thresh=args.cargo_threshold)

if args.command=="navigate":
    navigate(args.ship, args.waypoint)

if args.command=="scan":
    nprint("scan")
    if args.sys:
        print(sp.sense_system(args.sys))
    elif args.ship:
        print(sp.sense_system(sp.get_current_system(args.ship)))
    else:
        print(sp.get_systems())

if args.command=="get_contract":
    print(sp.get_contracts())

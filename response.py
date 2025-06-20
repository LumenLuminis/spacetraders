#!/bin/python3
# spacetraders-client
# Copyright (C) 2025  LumenLuminis
# SPDX-License-Identifier: GPL-3.0-or-later

class Response:
    def __init__(self, data, error, events):
        self.data=data
        self.error=error
        self.events=events

    def __str__(self):
        return str({"data":self.data, "error":self.error, "event":self.events})

    def __getitem__(self,key):
        return self.data[key]

    # def __getattr__(self, name):
    #     return self.data.name

    def to_json(self):
        return {"data":self.data, "error":self.error, "event":self.events}

class Response:
    def __init__(self, data, error, event):
        self.data=data
        self.error=error
        self.event=event

    def __str__(self):
        return str({"data":self.data, "error":self.error, "event":self.event})

    def __getitem__(self,key):
        return self.data[key]

    # def __getattr__(self, name):
    #     return self.data.name

    def to_json(self):
        return {"data":self.data, "error":self.error, "event":self.event}

'''
This is supposed to interface with the external network stuff.
'''
class Request:
  class GetPatientRecords:
    def __init__(self, kw):
      self.kw = kw
  class GetRecordContents:
    def __init__(self, record):
      self.record = record
  class ActivateRole:
    def __init__(self, role):
      self.role = role
  class ConsentToTreatment:
    def __init__(self, prin):
      self.prin = prin

def nextRequest():
  # Return a principle, a credential, and a request.
  pass

class Response:
  class RecordList:
    def __init__(self, records):
      self.records = records
  class RecordContents:
    def __init__(date, v, annots):
      self.date = date
      self.v = v
      self.annots = annots
  class Denied:
    def __init__(self, s):
      self.s = s
  class Ok:
    pass

def respond(response):
  pass

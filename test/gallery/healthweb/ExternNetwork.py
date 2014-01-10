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
    def __eq__(self, other):
      return self.records == other.records
  class RecordContents:
    def __init__(date, v, annots):
      self.date = date
      self.v = v
      self.annots = annots
    def __eq__(self, other):
      return (self.date == other.date and self.v == other.v and
        self.annots == self.annots)
  class Denied:
    def __init__(self, s):
      self.s = s
    def __eq__(self, other):
      return self.s == other.s
  class Ok:
    def __eq__(self, other):
      return isinstance(other, Ok)

def respond(response):
  pass

'''
This is supposed to interface with the external network stuff.
'''

'''
type request =
  | GetPatientRecords: string -> request
  | GetRecordContents: record -> request
  | ActivateRole: role -> request
  | ConsentToTreatment: prin -> request
'''
def nextRequest():
  # Return a principle, a credential, and a request.
  pass

'''
type response =
  | RecordList: records -> response
  | RecordContents: date -> string -> annots -> response
  | Denied: string -> response
  | Ok: response
'''
def respond(response):
  pass

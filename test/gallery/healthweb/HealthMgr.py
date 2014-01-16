import ExternNetwork
import HealthDB
from ExternNetwork import Request, Response
from HealthDB import AuthAPI
from PolicyTypes import Attribute, RoleType

'''
Event loop. Runs everything by processing requests from the network. Each
iteration of the loop gets the next request from the network and returns a
response.
'''
# TODO: Jeeves-ify this.
# @jeeves
def evtLoop(s, tok):
  # Each request comes with a principal, some credentials, and the body of the
  # request. (We'll just be mocking the request for now...)
  (p, cred, request) = ExternNetwork.nextRequest()
  # If this is a request for patient records
  if isinstance(request, Request.GetPatientRecords):
    test = (PolicyTypes.checkIn(PolicyTypes.ActiveRole(p, RoleType.Doctor), s)
            or PolicyTypes.checkIn(Attribute.ActiveRole(p, RoleType.Nurse), s)
            or PolicyTypes.checkIn(Attribute.ActiveRole(
                p, RoleType.InsuranceProvider), s))
    if test:
      records, tokNew = searchByKw(p, cred, kw, s, tok)
      ExternNetwork.respond(Response.RecordList(records))
      evtLoop(s, tokNew)
    else:
      ExternNetwork.respond(Response.Denied("Sorry, insufficient privilege"))
      evtLoop(s, tok)
  elif isinstance(request, Request.GetRecordContents):
    r = request.record   
    test = (p == r.author or
            ((p == r.patient) and
              PolicyTypes.checkIn(
                Attribute.ActiveRole(p, RoleType.Patient), s)) or
            (PolicyTypes.checkIn(Attribute.IsTreating(p, r.patient), s) and
              ((isinstance(r.subject, HealthDB.Psychiatric) and
                  PolicyTypes.checkIn(
                    Attribute.ActiveRole(p, RoleType.Psychiatrist), s)) or
               ((not isinstance(r.subject, HealthDB.Psychiatric) and 
                  PolicyTypes.checkIn(
                    Attribute.ActiveRole(p, RoleType.Doctor), s))))))
    if test:
      d, con, al, tokNew = HealthDB.readContents(p, cred, r, s, tok)
      ExternNetwork.respond(Response.RecordContents(d, con, al))
      evtloop(s, tokNew)
    else:
      ExternNetwork.respond(Response.Denied("Sorry, insufficient privilege"))
      evtLoop(s, tok)
  if isinstance(request, Request.ActivateRole):
    r = request.role   
    test = PolicyTypes.checkIn(Attribute.CanBeInRole(p, r), s)
    if test:
      sNew, tokNew = HealthDB.activateRole(p, cred, r, s, tok)
      ExternNetwork.respond(ExternNework.Ok)
      evtLoop(sNew, tokNew)
    else:
      ExternNetwork.respond(
        ExternNetwork.Denied("Sorry, insufficient privilege"))
      evtloop(s, tok)
  if isinstance(request, Request.ConsentToTreatment):
    doc = request.prin
    test = (PolicyTypes.checkIn(Attribute.ActiveRole(p, RoleType.Patient), s)
              and policyTypes.checkIn(Attribute.CanBeInRole(doc, Doctor), s))
    if test:
      sNew, tokNew = AuthAPI.consentToTreatment(p, cred, doc, s, tok)
      ExternNetwork.respond(Response.Ok)
      evtLoop(sNew, tokNew)
    else:
      ExternNetwork.respond(Response.Denied("Sorry, insufficient privilege"))
      evtLoop(s, tok)

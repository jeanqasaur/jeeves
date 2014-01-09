import ExternDB
from PolicyTypes import Sign

'''
Data model.
'''
class Subject:
  pass
class General(Subject):
  pass
class Psychiatric(Subject):
  pass
class HIV(Subject):
  pass
class Other(Subject):
  def __init__(self, ty):
    self.ty = ty

class Annotation:
  def __init__(self, author, date, contents):
    self.author = author
    self.date = date
    self.contents = contents

class Contents:
  def __init__(self, d, v, a):
    self.d = d
    self.v = v
    self.a = a

class Record:
  def __init__(self, recid, patient, author, subject, privateContents):
    self.recid = recid
    self.patient = patient # Prin
    self.author = author
    self.subject = subject
    self.privateContents = privateContents		 
              
''' 
Signatures of external utility functions
'''
class Extern:
  # Returns a record.
  def parseDbRecord(dbrecord):
    pass
  def unparseRecord(record):
    pass
  def parseAuthstate(stateStr):
    pass

'''
Public API to database.
'''
class DatabaseAPI:
  # Returns a record and state. 
  # s is a permit; tok is an authstate
  def searchByKW(prin, cred, kw, s, tok):
    dbrecs = ExternDB.findRecordByKeyword(kw)
    recs = map(ExternDB.parseDBRecord, dbrecs)
    return recs, tok

  val read_contents: p:prin -> cred p -> r:record -> 
                     s:permit p (Read r.recid) -> StateIs s -> 
                     (date * string * annots * StateIs s)
  def readContents(prin, cred, r, s, tok):
    pc = r.privateContents
    return (pc.d, pc.c, pc.a, tok)

'''
Public API for authorization-related functions.
'''
def AuthAPI:
  def activateRole(p, c, r, s, tok):
    # TODO: Define ActiveRole.
    s.append(ActiveRole(p, r))
    return (s, Sign(s))

  val consent_to_treatment: pat:prin -> cred pat -> doc:prin ->
                            s:permit pat (ConsentTo doc) -> StateIs s ->
                            (t:extendedstate s (IsTreating doc pat) * StateIs t)
  def consentToTreatment(patient, cred, doc, s, tok):
    s.addElt
    return s, Sign(s)
  
  '''
  val annotate_record: p:prin -> cred p -> r:record -> a:annotation ->
                       s:permit p (Annotate r.recid) -> StateIs s -> StateIs s
  '''
  def annotateRecord(p, c, r, a, s, tok):                    
    r.privateContents.a.append(a)
    ExternDP.persistRecord(unparseRec(r))
    return tok

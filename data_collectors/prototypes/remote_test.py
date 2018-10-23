import htcondor
import classad

coll = htcondor.Collector("csv2-dev.heprc.uvic.ca")
scheddAd = coll.locate(htcondor.DaemonTypes.Schedd, "csv2-dev.heprc.uvic.ca")
schedd = htcondor.Schedd(scheddAd)
jobs = schedd.xquery()
print(jobs)
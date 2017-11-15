import cdms2

f = cdms2.open("https://feedback.llnl.gov/mod_visus?action=readdataset&dataset=nature_2007_met1_hourly")

import pdb
pdb.set_trace()
dir(f)
mydata=f['TAULOW']
pass



import time
import numpy as np
import numpy.ma as ma
import cdms2, cdutil, cdtime, genutil

infile = 'performance/TREFHT_200001_201412.nc'
varname = 'TREFHT'

## Make sure the axes' bounds will be generated automatically, if they
## are missing
#cdms2.setAutoBounds('on')

# Read all time steps
f = cdms2.open(infile)
var = f(varname)
f.close()

var_time = var.getTime()
var_time_absolute = var_time.asComponentTime()
print(var_time_absolute[0],var_time_absolute[-1])

print 'Variable shape =', var.shape
print 'Time axis from %s to %s' % (var_time_absolute[0], var_time_absolute[-1])
#print 'Latitude values =', var.getLatitude()[:]
#print 'Longitude values =', var.getLongitude()[:]

#############################
# Climatology using cdutil #
#############################

print("Computing climatology with cdutil...")
t1 = time.time()
climo1 = cdutil.ANNUALCYCLE.climatology(var)
t2 = time.time()
print("time = %f" % (t2-t1))

##################################
# Compute climatology with numpy #
##################################

print("Computing climatology with numpy...")
t3 = time.time()

# Redefine time to be in the middle of the time interval
tbounds = var_time.getBounds()
var_time[:] = 0.5*(tbounds[:,0]+tbounds[:,1])
var_time_absolute = var_time.asComponentTime()

# Compute time length
dt = tbounds[:,1] - tbounds[:,0]

# Convert to masked array
v = var.asma()

# Compute monthly climatologies
climo2 = ma.zeros([12]+list(np.shape(v))[1:])
month = np.array( [ var_time_absolute[i].month for i in range(len(var_time_absolute)) ], dtype=np.int)
for i in range(1,13):
  idx = (month==i).nonzero()
  climo2[i-1] = ma.average(v[idx],axis=0,weights=dt[idx])

t4 = time.time()
print("time = %f" % (t4-t3))

#########################
# Check for differences #
#########################

# Conver to masked array
climo1 = climo1.asma()

# Compute differences
for i in range(1,13):
    tmp = ma.abs(climo1[i-1] - climo2[i-1])
    dmax = ma.max(tmp)
    dmin = ma.min(tmp)
    print 'Difference range for month %i = %s %s' % (i, dmin, dmax)

print 'Acceleration =', (t2-t1)/(t4-t3)



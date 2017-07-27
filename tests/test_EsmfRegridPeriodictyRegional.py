import cdat_info
import os
import sys
import cdms2

f = cdms2.open(cdat_info.get_sampledata_path() +
               '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
s = f('so')[0, 0, :, :]
s = s.astype("float64")
lon_dest = cdms2.createAxis([135., 137., 139., 141., 143., 145., 147., 149., 151.,
                             153., 155., 157., 159., 161., 163., 165., 167., 169.,
                             171., 173., 175., 177., 179., 181., 183., 185., 187.,
                             189., 191., 193., 195., 197., 199., 201., 203., 205.,
                             207., 209., 211., 213., 215., 217., 219., 221., 223.,
                             225., 227., 229., 231., 233., 235.])
lon_dest.designateLongitude()
lon_dest.id = "longitude"
lon_dest.units = "degrees_east"

lat_dest = cdms2.createAxis([-29., -27., -25., -23., -21., -19., -17., -15., -13., -11., -9.,
                             -7., -5., -3., -1., 1., 3., 5., 7., 9., 11., 13.,
                             15., 17., 19., 21., 23., 25., 27., 29.])
lat_dest.designateLatitude()
lat_dest.units = "degrees_north"

dummy = cdms2.MV2.ones((len(lat_dest), len(lon_dest)))
dummy.setAxisList((lat_dest, lon_dest))

grid_dest = dummy.getGrid()
s.id = "orig"
s_regrid2 = s.regrid(grid_dest, regridTool="libcf")
s_regrid2.id = "regrid2"

s_esmf_lin = s.regrid(grid_dest)
s_esmf_lin.id = "ESMF Linear"

s_esmf_con = s.regrid(
    grid_dest,
    regridTool="esmf",
    regridMethod="conservative")
s_esmf_lin.id = "ESMF Conservative"

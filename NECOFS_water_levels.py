
# coding: utf-8

# # Extract NECOFS water levels using NetCDF4-Python and analyze/visualize with Pandas

# In[1]:

# Plot forecast water levels from NECOFS model from list of lon,lat locations
# (uses the nearest point, no interpolation)
import netCDF4
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from retrying import retry
get_ipython().magic('matplotlib inline')


# In[2]:

# Specify which forecast model 

#NECOFS MassBay grid
model='Massbay'
url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'

# GOM3 Grid
#model='GOM3'
#url='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'


# In[3]:

# Enter desired (Station, Lat, Lon) values here:
x = '''
Station, Lat, Lon
Boston,             42.368186, -71.047984
Scituate Harbor,    42.199447, -70.720090
Scituate Beach,     42.209973, -70.724523
Falmouth Harbor,    41.541575, -70.608020
Marion,             41.689008, -70.746576
Marshfield,         42.108480, -70.648691
Provincetown,       42.042745, -70.171180
Sandwich,           41.767990, -70.466219
Hampton Bay,        42.900103, -70.818510
Gloucester,         42.610253, -70.660570
'''


# In[4]:

# Enter desired (Station, Lat, Lon) values here:
x = '''
Station, Lat, Lon
Boston,             42.368186, -71.047984
Scituate Harbor,    42.199447, -70.720090
Sandwich,           41.767990, -70.466219
'''


# In[5]:

# Create a Pandas DataFrame from the station list
obs=pd.read_csv(StringIO(x.strip()), sep=",\s*",index_col='Station', engine='python')


# In[6]:

obs


# In[7]:

# find the indices of the points in (x,y) closest to the points in (xi,yi)
def nearxy(x,y,xi,yi):
    ind = np.ones(len(xi),dtype=int)
    for i in np.arange(len(xi)):
        dist = np.sqrt((x-xi[i])**2+(y-yi[i])**2)
        ind[i] = dist.argmin()
    return ind


# In[8]:

@retry(stop_max_attempt_number=5, wait_fixed=3000)
def get_nc(url):
    nc=netCDF4.Dataset(url)
    return nc


# In[9]:

nc = get_nc(url)


# In[10]:

# find closest NECOFS nodes to station locations
obs['0-Based Index'] = nearxy(nc['lon'][:],nc['lat'][:],obs['Lon'],obs['Lat'])
obs


# In[11]:

# get time values and convert to datetime objects
times = nc['time']
jd = netCDF4.num2date(times[:],times.units)


# In[12]:

# get all time steps of water level from each station
nsta = len(obs)
z = np.ones((len(jd),nsta))
for i in range(nsta):
    z[:,i] = nc['zeta'][:,obs['0-Based Index'][i]] 


# In[13]:

# make a DataFrame out of the interpolated time series at each location
zvals=pd.DataFrame(z,index=jd,columns=obs.index)


# In[14]:

# list out a few values
zvals.head()


# In[15]:

# make a new DataFrame of maximum water levels at all stations
b=pd.DataFrame(zvals.idxmax(),columns=['time of max water level (UTC)'])
# create heading for new column containing max water level
zmax_heading='zmax (%s)' % nc['zeta'].units
# Add new column to DataFrame
b[zmax_heading]=zvals.max()


# In[16]:

b


# In[17]:

# plotting at DataFrame is easy!
ax=zvals.plot(figsize=(16,4),grid=True,title=('NECOFS Forecast Water Level from %s Forecast' % model),legend=False);
# read units from dataset for ylabel
plt.ylabel(nc['zeta'].units)
# plotting the legend outside the axis is a bit tricky
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5));


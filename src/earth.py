#import spiceypy to astronomy calculations
import spiceypy
from kernel_manager import kernels_load

#import datetime to work with date data
import datetime

#import math to use math functions
import math

#TODO make it class

AU_TO_KM = 149_597_871

#spicepy needs a kernels loaded to work properly
kernels_path = ['./kernels/lsk/naif0012.tls.txt',
                './kernels/pck/gm_de431.tpc.txt',
                './kernels/spk/de440s.bsp']
kernels_load(kernels_path)

#get a today date
today = datetime.datetime.today()

#convert today to string and set midnight
today = today.strftime('%Y-%m-%dT00:00:00')

#convert UTC to ET
et_today = spiceypy.utc2et(today)


#Calculating an earth state vector and time of light's travel between
#the earth and the sun
#Using spkgeo function with parametres:
#targ = 399 - NAIF ID of the planet (The Earth in this case) that state vector is pointing
#et = et_todat - Reference time of calculations
#ref = 'ECLIPJ2000' - An Ecliptic Plane used in calculations
#obs = 10 - NAIF ID of the object (The Sun in this case) which is the beggining of state vector
earth_state_vector, earth_sun_light_time = spiceypy.spkgeo(targ=399,
    et = et_today, ref='ECLIPJ2000', obs = 10)

#Calculate earth - sun distance (km)
earth_sun_distace = math.sqrt(earth_state_vector[0]**2+earth_state_vector[1]**2+
                              earth_state_vector[2]**2)
#Convert a distance to AU
au_earth_sun_distance = earth_sun_distace/AU_TO_KM

#Calculate the orbital speed of the Earth around the Sun (km/s)
earth_sun_speed = math.sqrt(earth_state_vector[3]**2+earth_state_vector[4]**2+
                               earth_state_vector[5]**2)

#Calculate theorical orbital speed of the Earth around the Sun (km/s)
_, gm_sun = spiceypy.bodvcd(bodyid=10, item='GM', maxn=1) #GM parameter
earth_sun_speed_theory = math.sqrt(gm_sun[0]/earth_sun_distace)


print(f"Earth location in km in relation to Sun for {today}: {earth_state_vector}")
print(f"Earth distace from Sum (in AU) equals for {today}: {au_earth_sun_distance}")
print(f"The Earth orbital speed around the Sun equals for: {earth_sun_speed}")
print(f"The theoretical Earth orbital speed around the Sun equals for: {earth_sun_speed_theory} ")

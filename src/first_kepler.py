
#TO DO make plot animated
#TO DO make more docstrings about functions and class
#TO DO make class plots in another file 
#TO DO make all labels white

import datetime 
import spiceypy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

from utilities import kernels_load
from utilities import merge_plots
from utilities import prepare_dict
from utilities import NAIF_PLANETS_ID


class FirstKepler:
    def __init__(self):
        #spicepy needs a kernels loaded to work properly
        self.kernels_path = ['./kernels/lsk/naif0012.tls.txt',
                        './kernels/pck/pck00010.tpc.txt',
                        './kernels/spk/de440s.bsp']

        kernels_load(self.kernels_path)

        #Initialization of UTC time
        self.init_utc_time = datetime.datetime(year=2020, month=1, day=1,
                                        hour=0, minute=0, second=0)

        #how many days between end of calculations and initialization time
        self.days_diff = 5000
        self.end_utc_time = self.init_utc_time + datetime.timedelta(days=self.days_diff)

        #Convert dates to strings
        self.init_utc_time_str = self.init_utc_time.strftime('%Y-%m-%dT%H:%M:%S')
        self.end_utc_time_str = self.end_utc_time.strftime('%Y-%m-%dT%H:%M:%S')

        #Ephemeris time 
        self.init_et_time = spiceypy.utc2et(self.init_utc_time_str)
        self.end_et_time = spiceypy.utc2et(self.end_utc_time_str)

        #create numpy array with one day interval between start and end day
        self.time_array = np.linspace(self.init_et_time, self.end_et_time, self.days_diff) 

        #Array with all positions of solar system barycentre
        self.solar_system_barycentre_pos = []

        for time in self.time_array:
            _position, _ =spiceypy.spkgps(targ=0, et=time, ref ='ECLIPJ2000',
                                        obs = 10)
            self.solar_system_barycentre_pos.append(_position)

        #convert to numpy array
        self.solar_system_barycentre_pos_array = np.array(self.solar_system_barycentre_pos)

        #import sun radius
        _, sun_radius_arr = spiceypy.bodvcd(bodyid=10, item='RADII', maxn=3)
        self.sun_radius = sun_radius_arr[0]

        #Scalled solar system barycentre position (in Sun radii)
        self.solar_system_barycentre_pos_scalled = self.solar_system_barycentre_pos_array/self.sun_radius

        #Plotting trajectory of solar system barycentre (only needed x and y coordinates)
        self.solar_system_barycentre_pos_scalled_plane = self.solar_system_barycentre_pos_scalled[:, 0:2]

    def trajectory(self,ax1):
        plt.style.use('dark_background')

        #Begin with plotting the sun
        sun_plot = plt.Circle((0.0, 0.0), 1.0, color='yellow')
        ax1.add_artist(sun_plot)
        ax1.plot(self.solar_system_barycentre_pos_scalled_plane[:, 0], 
                self.solar_system_barycentre_pos_scalled_plane[:, 1],
                color='white')
        ax1.grid(True, linewidth=0.5, linestyle='dashed', alpha=0.7)
        ax1.set_aspect('equal')
        ax1.set_xlim(-5, 5)
        ax1.set_ylim(-5, 5)


        ax1.set_xlabel('x in the Sun radius', color='white')
        ax1.set_ylabel('y in the Sun radius', color ='white')

        ax1.set_xticklabels(self.solar_system_barycentre_pos_scalled_plane[:, 0], rotation = 45,
                            color='white')
        ax1.set_yticklabels(self.solar_system_barycentre_pos_scalled_plane[:, 1], rotation = 45,
                            color='white')
        
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

        ax1.set_title("Trajectory of the Solar System Barycentre in"
                      " relation to the Sun ", wrap=True, color='white')

        ax1.set_facecolor('navy')
    
    def __str__(self):
        #Print the starting and end times
        info = f"""\tStart day: {self.init_utc_time_str}
        End day: {self.end_utc_time_str}"""
        return info

class SolarSystem(FirstKepler):
    def __init__(self):
        super().__init__()
        #Creating a pandas' dataframe to store all crucial informations
        self.solar_system_data_frame = pd.DataFrame()

        #Creating a column with ETs in dataframe
        self.solar_system_data_frame.loc[:, 'ET'] \
        = self.time_array

        #Creating a column with UTCs in dataframe
        self.solar_system_data_frame.loc[:, 'UTC'] \
        = self.solar_system_data_frame['ET'].apply(lambda et:
            spiceypy.et2datetime(et=et).date())
        
        #Creating a column with a position of barycentre 
        #of the solar system 
        self.solar_system_data_frame.loc[:, 'barycentre_pos'] \
            = self.solar_system_barycentre_pos
        
        self.solar_system_data_frame.loc[:, 'barycentre_pos_scalled']\
            = self.solar_system_data_frame['barycentre_pos'].apply(lambda x: 
                    x / self.sun_radius)
        
        #Creating a column with a distance between barycentre
        #and sun
        self.solar_system_data_frame.loc[:, 'Barycentre_distance'] \
            = self.solar_system_data_frame['barycentre_pos_scalled'].apply(
            lambda x: np.linalg.norm(x))
    
    def plot(self, ax2):
        ax2.plot(self.solar_system_data_frame['UTC'],
                self.solar_system_data_frame['Barycentre_distance'],
                color = 'white')
        ax2.set_title(" Distance between the Sun and the Solar System Barycentre"
                      " by time", wrap=True, color='white')
        ax2.grid(True, linewidth=0.5, linestyle='dashed', alpha=0.7)
        
        ax2.set_xlabel('Time in years', color='white')
        ax2.set_ylabel('Distance in sun radius', color='white')
        ax2.set_yticklabels(self.solar_system_data_frame['Barycentre_distance'], rotation = 45,
                            color='white')
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

        ax2.set_facecolor('navy')

class PhaseAngel(SolarSystem):
    def __init__(self):
        super().__init__()
        #Adding a column of dataframe with position of another
        #planets further from The Sun than The Earth
        #Also adding a column with phase angels of planets
        #(angle between barycentrum, Sun and planet)
        
        #Choosing planets to analyze
        chosen_planets = ['Mars', 'Jupiter', 'Saturn', 'Uran']
        self.NAIF_PLANETS_ID_updated = prepare_dict(NAIF_PLANETS_ID, chosen_planets)

        for planets_name in self.NAIF_PLANETS_ID_updated.keys():
            planet_pos = f"{planets_name}_pos"
            planet_angle = f"{planets_name}_phase_ang"

            planet_id = self.NAIF_PLANETS_ID_updated[planets_name]

            self.solar_system_data_frame.loc[:, planet_pos] = \
                self.solar_system_data_frame['ET'].apply(lambda x:
                    spiceypy.spkgps(targ=planet_id,
                                    et=x,
                                    ref='ECLIPJ2000',
                                    obs=10)[0])
            self.solar_system_data_frame.loc[:, planet_angle] = \
                self.solar_system_data_frame.apply(lambda x:
                    np.degrees(spiceypy.vsep(x[planet_pos],
                                             x['barycentre_pos'])
                                )
                                ,axis=1)
    
    def plot(self):
        plt.style.use('dark_background')

        fig, axs = plt.subplots(nrows=len(self.NAIF_PLANETS_ID_updated.keys()), 
                               ncols=1,
                               sharex=True,
                               figsize=(8,20))
        
        for ax, planet_name in zip(list(axs), self.NAIF_PLANETS_ID_updated.keys()):
            ax.set_title(planet_name, color='orange')

            ax.plot(self.solar_system_data_frame['UTC'],
                self.solar_system_data_frame['Barycentre_distance'],
                color = 'white')
            

            
            ax.set_ylabel("Bar. distance in Sun Radius", rotation=90,
                          labelpad=25, fontsize=5)

            ax.set_xlim(min(self.solar_system_data_frame['UTC']), 
                        max(self.solar_system_data_frame['UTC']))
            ax.set_ylim(0, 2)

            ax_copy = ax.twinx()
            ax_copy.plot(self.solar_system_data_frame['UTC'],
                self.solar_system_data_frame[f'{planet_name}_phase_ang'],
                color = 'orange')
            
            ax_copy.invert_yaxis()
            ax_copy.set_ylim(180, 0)

            ax_copy.set_ylabel("Phase angel of planet in degrees",
                               rotation=90, labelpad=25,
                               fontsize=5, color='orange')

            ax.set_facecolor('navy')
            ax_copy.set_facecolor('navy')

            fig.set_facecolor('#1E2A4C')

            ax.grid(True, linewidth=0.5, linestyle='dashed', alpha=0.7)

            plt.subplots_adjust(hspace=15)
            
        axs[len(self.NAIF_PLANETS_ID_updated.keys()) - 1].set_xlabel('Date')
        fig.tight_layout(pad = 5.0)
        plt.show()

        
if __name__ == "__main__":
    solar_system = SolarSystem()
    merge_plots(solar_system.trajectory, solar_system.plot)
    phase_angel = PhaseAngel()
    phase_angel.plot()
    #print(phase_angel.solar_system_data_frame)

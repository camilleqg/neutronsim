# neutronsim

## Description 
Neutronsim simulates photons detected by scintillator-based neutron-event-driven detectors. The data it provides is based on observed distributions of photon characteristics utilizing event-mode neutron imaging. The purpose of this simulation is to provide large quantities of synthetic data including ground truths to effectively train neural networks that will identify single neutron events and their sources from sparse data readout.  

## Installation
Simply download the python file and move it to any folder. The .json file included here serves as a template to show what can be included, but can also be downloaded and used with the program. 

## Usage 
The simulation has two commands: simulate and display.
**Simulate** will generate the number of events that are inputted into the command line, can save this data to an excel file, and/or display it directly in the command line.  
**Display** will also generate the number of events that are inputted into the command line and will save a 2D plot with the axes of the users choice. Like simulate, it can also display the data directly in the CLI or save it to an excel file. 

### The following arguments are used for both commands:  
**--events/-e** (int): The number of events to simulate. **Required**  
**--verbose/-v** (bool): Whether to output the photon data in the terminal (True) or not (False). **Not required. Default is false**  
**--eventscale/-es** (float): Coefficient with which the distribution of number of photons per event will be scaled relative to the default (N11 scintillator). **Not required. Default is 1**  
**--noisescale/-ns** (float): Coefficient with which the distribution of number of photons due to noise will be scaled relative to the default (N11 scintillator). **Not required. Default is 1**  
**--spacesigma/-s** (float): Sigma value for gaussian distribution of photons in space. **Not required. Default is that of N11 scintillator**  
**--starttime/-st** (float): Start time for all events*. **Not required. Default is randomly generated.**  
**--startx/-sx** (float): Starting x coordinate for all events*. **Not required. Default is randomly generated.**  
**--starty/-sy** (float): Starting y coordinate for all events*. **Not required. Default is randomly generated.**  
**--datafile/-df** (str): .csv file where the photon coordinate data will be stored. **Not required. Default is None.**  
**--file/-f** (str): .json file containing all optional arguments and parameters for distributions of photon decay over time and number of photons per event. Can be read by program rather than specifying in cmd. **Not required. Default is None.**

***Important note:  
The x, y, and t coordinates are only the same for all events when they are manually chosen. When they are left to be randomly generated, each event has a different source.**

### The following arguments are only used for the display command: 
**-reveal/-r** (bool): Whether to include the source coordinate in red on the plot (True) or not (False). **Required.**  
**--pov/-pov** (str): Tells the program which axes to display on the plot. Either 'xy', 'timex', or 'timey', where the first indicated axis in the string is the x axis on the plot. **Required.**  
**--savefig/-id** (str): Filename where the plot will be saved. Either .png or .jpg. **Required.**  

```bash
# Example of command to run the project from the command line 
python neutron_sim.py simulate -e 1 -v True # This will run one event and display the output photon data in the CLI

```

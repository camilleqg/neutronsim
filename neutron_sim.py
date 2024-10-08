# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 13:51:29 2024

@author: camil
"""

import numpy as np 
import matplotlib.pyplot as plt
import textwrap
import argparse 
import json
import csv

# buncha constants 

detector_sidelength = 1e-2 # in metres 
time_window = 0.3

# import json file stuff for num_events 
def load_params(json_filename):
    '''This just loads parameters from the json file'''
    with open(json_filename, 'r') as f: 
        params = json.load(f)
    return params

# picking total number of photons 

def num_events(photons, a0 = 3426.89, b0 = -3476.32, c0 = 0.10182, sigma = 40.296, mu = 24.3823, file = None):
    '''outputs the probability of events for a given number of photons based on the best fit of the histogram'''
    if file:
        params = load_params(file) 
        a0 = params.get('a0', 3426.89)
        b0 = params.get('b0', -3476.32)
        c0 = params.get('c0', 0.10182)
        sigma = params.get('sigma', 40.296)         
        mu = params.get('mu', 24.3823)
    return 1/6*(a0*np.exp(-(photons-mu)**2 / (2*sigma**2)) + b0*np.exp(-c0*photons)) 

def total_photons(scale, file = None):
    '''guesses the total number of photons out of possible values as well as a number of events.
    from there it checks if these points appear together on the histogram. the probability of coincidence
    matches the histogram distribution. once it finds a number it likes it spits it out'''
    photonspace = np.linspace(0,255,500) # this and next two lines samples function and finds an upper limit to number of events
    eventspace = num_events(photonspace) 
    max_events = max(eventspace)
    
    min_photons = 1 # upper and lower limit of number of photons 
    max_photons = 255
    
    # evaluates the num_events function to see if the random numbers match the distribution
    num_photons_final = 0 
    while num_photons_final == 0: 
        # generates a random number of photons and random number of events based on the limits
        guess_photons = np.random.uniform(min_photons, max_photons)
        guess_events = np.random.uniform(1, max_events)
        
        if guess_events <= num_events(guess_photons, file = file): 
            num_photons_final = guess_photons
    return round(scale*num_photons_final)

# generate coordinates for one photon 
def generate_coords(mu_x, mu_y, sigma2=0.00021233045007200478): 
    ''' This function will generate a set of coordinates for x and y, based on the centre of the event (input). It will only generate one at a time
    no need for custom functions here because numpy already has a sampler for gaussian distribution'''
    num_photons = 1
    x_coord = np.random.normal(loc = mu_x, scale = sigma2, size = num_photons)
    y_coord = np.random.normal(loc = mu_y, scale = sigma2, size = num_photons)
    return x_coord[0], y_coord[0]

# generate time coordinate for one photon


def decayfit(t, a1 = 57782.4, t1 = 0.000653566, a2 = 7473.2, t2 = 0.016498, a3 = 1.28054e6, t3 = 2.87915e-05, a4 = 455714, t4 = 0.000119424, file = None): 
    ''' This function takes the time input and outputs f(x) of the best fit line of the decay'''
    if file: 
        params = load_params(file)
        a1 = params.get('a0', 57782.4) 
        t1 = params.get('t0', 0.000653566)
        a2 = params.get('a1', 7473.2)
        t2 = params.get('t1', 0.016498)
        a3 = params.get('a2', 1.28054e6)
        t3 = params.get('t2', 2.87915e-05)
        a4 = params.get('a3', 455714)
        t4 = params.get('t3', 0.000119424)
    return a1*np.exp(-t/t1) + a2*np.exp(-t/t2) + a3*np.exp(-t/t3) + a4*np.exp(-t/t4)

def generate_time(file):
    ''' Just like the photon number generator, will guess a time and number of photons, if these points
    coincide on the integral of the best fit then they are accepted and returned '''
    # event box limits 
    time_min = 0
    time_max = 0.1 # max time for a single event 
    
    # max number of photons at a time 
    max_photons = decayfit(t = 0, file = file)
    
    # loop through until we get an accepted value 
    time_final = 0 
    while time_final == 0: 
        time_guess = np.random.uniform(time_min, time_max)
        photons_guess = np.random.uniform(0, max_photons)
        if photons_guess <= decayfit(time_guess, file = file):
            time_final = time_guess 
            
    return time_final

# all together now!

def single_event(eventscale=1, noisescale = 1, spacesigma=0.00021233045007200478, start_time=-1, start_x=-1, start_y=-1, file=None):
    ''' This function will create a big list of all photons from one event'''
    ''' output format is [photons, 3], the 3 is [x,y,z]'''
    
    photons = total_photons(eventscale, file)
    photon_list = []
    ground_truth = []
    
    # generate random place and time to start
    # add random place and time to ground truth vector 
    if start_time == -1 : 
        start_time = np.random.uniform(0,time_window)
    if start_x == -1 : 
        start_x = np.random.uniform(0, detector_sidelength)
    if start_y == -1 : 
        start_y = np.random.uniform(0, detector_sidelength)
    ground_truth.append(start_x)
    ground_truth.append(start_y)
    ground_truth.append(start_time)
    # print("the true coordinates are", start_x, "and", start_y)
    # print("the true time is", start_time)
    
    for i in range(photons): 
        info = []
        x, y = generate_coords(start_x, start_y, spacesigma)
        info.append(x)
        info.append(y)
        time = generate_time(file = file) + start_time
        info.append(time)
        photon_list.append(info)
    
    noise = total_photons(noisescale)
    for i in range(noise):
        info = []
        x = np.random.uniform(0, detector_sidelength)
        y = np.random.uniform(0, detector_sidelength)
        time = np.random.uniform(0,time_window)
        info.append(x)
        info.append(y)
        info.append(time)
        photon_list.append(info)
        
    
    return photon_list, ground_truth

def noisy_event(scale=1): # this is used to generate completely random photons (just "noise") to train the model on recognizing events and non-events 
    photons = total_photons(scale)
    photon_list = []
    truth_list = []
    for i in range(photons):
      info = []
      x = np.random.uniform(0,detector_sidelength)
      y = np.random.uniform(0, detector_sidelength)
      time = np.random.uniform(0,0.1)
      info.append(x)
      info.append(y)
      info.append(time)
      photon_list.append(info)
      truth_list.append([0,0,0])
    return photon_list, truth_list
    

def sim(events, verbose = False, eventscale=1, noisescale=1, spacesigma=0.00021233045007200478, start_time=-1, start_x=-1, start_y=-1, dataSaveID = None, file=None): 
    '''This function will run the single event function events number of times and save each event to an even bigger matrix'''
    
    squeezed_events = []
    truth_list = []
    event = 0 
    if file: 
        params = load_params(file)
        verbose = params.get('verbose', False)
        eventscale = params.get('eventscale', 1)
        noisescale = params.get('noisescale', 1) 
        spacesigma = params.get('spacesigma', 0.00021233045007200478)
        start_time = params.get('start_time', -1)
        start_x = params.get('start_x', -1)
        start_y = params.get('start_y', -1)
        dataSaveID = params.get('dataSaveID', None)
       
    
    if events == 0: 
        squeezed_events, truth_list = noisy_event(noisescale)
    while event < events:
        output = single_event(eventscale=eventscale, noisescale=noisescale, spacesigma=spacesigma, start_time=start_time, start_x=start_x, start_y=start_y, file=file)
        truth_list.append(output[1])
        for i in range(len(output[0])): 
            squeezed_events.append(output[0][i])
        event +=1 
    if dataSaveID: 
        columns = ['x[px]', 'y[px]', 't[s]']
        truthsaveID = 'truth_' + dataSaveID
        with open(dataSaveID, mode = 'w', newline='') as wfile: 
            writer = csv.writer(wfile)
            writer.writerow(columns)
            writer.writerows(squeezed_events)
        with  open(truthsaveID, mode = 'w', newline = '') as wfile: 
            writer = csv.writer(wfile)
            writer.writerow(columns)
            writer.writerows(truth_list)
            
    if verbose: 
        for sublist in squeezed_events: 
            print(sublist)
        print('\n--------\n')
        for sublist in truth_list: 
            print(sublist) 
    else: 
        print("output suppressed")
    
    return squeezed_events, truth_list

def sim_disp(events, reveal, pov, saveID, eventscale=1, noisescale=1, spacesigma=0.00021233045007200478, start_time=-1, start_x=-1, start_y=-1, file=None, dataSaveID = None): 
    verbose = False
    
    if file: 
        params = load_params(file)
        verbose = params.get('verbose', False)
        eventscale = params.get('eventscale', 1)
        noisescale = params.get('noisescale', 1) 
        spacesigma = params.get('spacesigma', 0.00021233045007200478)
        start_time = params.get('start_time', -1)
        start_x = params.get('start_x', -1)
        start_y = params.get('start_y', -1)
        saveID = params.get('saveID', None)
        dataSaveID = params.get('dataSaveID', None)
        
    
    data = sim(events, verbose=verbose, eventscale=eventscale, noisescale=noisescale, spacesigma=spacesigma, start_time=start_time, start_x=start_x, start_y=start_y, file=file, dataSaveID = dataSaveID)
    photons = np.array(data[0])
    truth = np.array(data[1])
    title = 'none'
        
    if pov == 'xy': 
        plt.scatter(photons[:,0], photons[:,1])
        title = f'Y vs x view of {events} events with {eventscale}x scaled photons, {noisescale}x scaled noise, start time:  {str(start_time)}, start x: {str(start_x)}, start y: {str(start_y)}, without sources'
        plt.ylabel('y coordinates')
        plt.xlabel('x coordinates')
        if reveal: 
            plt.scatter(truth[:,0], truth[:,1], c = 'r')
            title = f'Y vs x view of {events} events with {eventscale}x scaled photons, {noisescale}x scaled noise, start time:  {str(start_time)}, start x: {str(start_x)}, start y: {str(start_y)}, with sources in red'
    elif pov == 'timex': 
        plt.scatter(photons[:,2], photons[:,0])
        title = f'X vs time view of {events} events with {eventscale}x scaled photons, {noisescale}x scaled noise, start time:  {str(start_time)}, start x: {str(start_x)}, start y: {str(start_y)}, without sources'
        plt.ylabel('x coordinates')
        plt.xlabel('Time')
        if reveal: 
            plt.scatter(truth[:,2], truth[:,0], c = 'r')
            title = f'X vs time view of {events} events with {eventscale}x scaled photons, {noisescale}x scaled noise, start time:  {str(start_time)}, start x: {str(start_x)}, start y: {str(start_y)}, with sources in red'
    elif pov == 'timey': 
        plt.scatter(photons[:,2], photons[:,1])
        title = f'Y vs time view of {events} events with {eventscale}x scaled photons, {noisescale}x scaled noise, start time:  {str(start_time)}, start x: {str(start_x)}, start y: {str(start_y)}, without sources'
        plt.ylabel('y coordinates')
        plt.xlabel('Time')
        if reveal: 
            plt.scatter(truth[:,2], truth[:,1], c = 'r')
            title = f'Y vs time view of {events} events with {eventscale}x scaled photons, {noisescale}x scaled noise, start time:  {str(start_time)}, start x: {str(start_x)}, start y: {str(start_y)}, with sources in red'
    
            
    wrapped_title = "\n".join(textwrap.wrap(title, width=60))
    plt.title(wrapped_title, fontsize=12)
    plt.tight_layout()
    plt.savefig(saveID)
    plt.close()
    
### CLI STUFF 

# top level parser
parser = argparse.ArgumentParser(description="Neutron event simulator")

# creating sub parsers for each command (functions) 
# each of these functions get their own arguments 

subparsers = parser.add_subparsers(dest="command", help = "Available commands")

# sub command 1: simulate and output events 
sim_parser = subparsers.add_parser("simulate", help = "Simulate neutron events, output results into terminal")
sim_parser.add_argument("-e", "--events", type = int, required=True, help="Number of neutron events to simulate")
sim_parser.add_argument("-v", "--verbose", type = str, default = False, help="Showing the photon data in terminal or not")
sim_parser.add_argument("-es", "--eventscale", type = float, default = 1, help = "Scaling coefficient for number of photons per event. Default value: 1")
sim_parser.add_argument("-ns", "--noisescale", type = float, default = 1, help = "Scaling coefficient for number of noise photons per event. Default value: 1")
sim_parser.add_argument("-s", "--spacesigma", type = float, default = 0.00021233045007200478, help = "Sigma of the Gaussian distribution of photons in x and y. Default value: 0.00021233045007200478")
sim_parser.add_argument("-st", "--starttime", type = float, default = -1, help = "Start time for all events. Default value is randomly generated.")
sim_parser.add_argument("-sx", "--startx", type = float, default = -1, help = "Starting x coordinate for all events. Default value is randomly generated.")
sim_parser.add_argument("-sy", "--starty", type = float, default = -1, help = "Starting y coordinate for all events. Default value is randomly generated.")
sim_parser.add_argument("-df", "--datafile", type = None, default = None, help = "Text file name for saving data. Truth file will have the same name but prefixed with truth_")
sim_parser.add_argument("-f", "--file", type = None, default = None, help = "Name of json file containing all optional arguments as well as parameters for photon decay distribution and distribution of number of photons per event.")

# sub command 2: display events
disp_parser = subparsers.add_parser("display", help = "Generate a single event and display from different povs")
disp_parser.add_argument("-e", "--events", type = int, required = True, help = "Number of neutron events to simulate") 
disp_parser.add_argument("-r", "--reveal", type = str, required = True, help = "Whether or not to display the event source(s)")
disp_parser.add_argument("-pov", "--pov", type = str, required = True, help = "Which axes to display. 'xy', 'timex', or 'timey'")
disp_parser.add_argument("-id", "--savefig", type = str, required = True, help = "png file name for saving the plots")
disp_parser.add_argument("-es", "--eventscale", type = float, default = 1, help = "Scaling coefficient for number of photons per event. Default value: 1")
disp_parser.add_argument("-ns", "--noisescale", type = float, default = 1, help = "Scaling coefficient for number of noise photons per event. Default value: 1")
disp_parser.add_argument("-s", "--spacesigma", type = float, default = 0.00021233045007200478, help = "Sigma of the Gaussian distribution of photons in x and y. Default value: 0.00021233045007200478")
disp_parser.add_argument("-st", "--starttime", type = float, default = -1, help = "Start time for all events. Default value is randomly generated.")
disp_parser.add_argument("-sx", "--startx", type = float, default = -1, help = "Starting x coordinate for all events. Default value is randomly generated.")
disp_parser.add_argument("-sy", "--starty", type = float, default = -1, help = "Starting y coordinate for all events. Default value is randomly generated.")
disp_parser.add_argument("-f", "--file", type = None, default = None, help = "Name of json file containing all optional arguments as well as parameters for photon decay distribution and distribution of number of photons per event.")
disp_parser.add_argument("-df", "--datafile", type = None, default = None, help = "Name of the file to save all the photon data. Real event source data will have the same name but begin with truth_")

# parse the arguments 
args = parser.parse_args()

# call the function based on subcommand
if args.command == "simulate": 
    sim(events=args.events, verbose=args.verbose, eventscale=args.eventscale, noisescale=args.noisescale, spacesigma=args.spacesigma, start_time=args.starttime, start_x=args.startx, start_y=args.starty, dataSaveID=args.datafile, file=args.file)
elif args.command == "display": 
    sim_disp(events=args.events, reveal=args.reveal, pov=args.pov, saveID=args.savefig, eventscale=args.eventscale, noisescale=args.noisescale, spacesigma=args.spacesigma, start_time=args.starttime, start_x=args.startx, start_y=args.starty, file=args.file, dataSaveID=args.datafile)
else: 
    parser.print_help()


















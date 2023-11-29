import zhinst.utils
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import sys
from alive_progress import alive_bar

def run_daq(device_id: str = "dev3554",
            server_host: str = "localhost",
            server_port: int = 8004,
            filename: str = "",
            run: str = "",
            noise: bool = False,
            duration: int = 300,
            amp: int = 0,
            parametric_drive: bool = False,
            external_drive: bool = False
        ):
    
    apilevel = 6
    (daq, device, _) = zhinst.utils.create_api_session(
        device_id, apilevel, server_host=server_host, server_port=server_port)
    zhinst.utils.api_server_version_check(daq)
    
    daq.set(f"/{device}/demods/0/enable", 1)
    daq.setInt(f"/{device}/demods/1/harmonic", 1) # set first harmonic on demod 2
    daq.setDouble('/dev3554/demods/0/order', 4);
    daq.setDouble('/dev3554/sigouts/0/range', 1)
    daq.setDouble('/dev3554/sigouts/0/amplitudes/1', 0)
    
    daq.setInt('/dev3554/sigouts/0/on', 0); #sig output
    daq.setInt('/dev3554/sigouts/0/enables/1', 0);  # amp output
    
    if external_drive:
        daq.setInt('/dev3554/sigouts/0/on', 1);
        daq.setInt('/dev3554/sigouts/0/enables/1', 1); 
        daq.setDouble('/dev3554/sigouts/0/amplitudes/1', amp*1e-3)
    
    if parametric_drive:
        daq.setInt('/dev3554/sigouts/0/on', 1);
        daq.setInt('/dev3554/sigouts/0/enables/1', 1); 
        daq.setInt(f"/{device}/demods/1/harmonic", 2)
        daq.setDouble('/dev3554/demods/0/order', 4);
        if amp > 1000:
            daq.setDouble('/dev3554/sigouts/0/range', 10) # increase range
        daq.setDouble('/dev3554/sigouts/0/amplitudes/1', amp*1e-3)
    
    freq = 35.38
    
    daq.setDouble('/dev3554/oscs/0/freq', freq);

    
    demod_path = f"/{device}/demods/0/sample"
    signal_paths = []
    signal_paths.append(demod_path + ".X")
    signal_paths.append(demod_path + ".Y")
    
    total_duration = duration
    module_sampling_rate = 13
    num_cols = int(np.ceil(module_sampling_rate * total_duration))
    
    daq.setDouble('/dev3554/demods/0/timeconstant', 0.07);
    daq.setDouble('/dev3554/demods/0/rate', module_sampling_rate);
    
    daq_module = daq.dataAcquisitionModule()
    
    daq_module.set("device", device)
    daq_module.set("type", 0) # acquisition type = 0 -> continuous
    daq_module.set("grid/mode", 2) # linear interpolation
    daq_module.set("count", 1)
    daq_module.set("duration", total_duration)
    daq_module.set("grid/cols", num_cols)
    daq_module.set('forcetrigger', 1)
    
    daq.setInt('/dev3554/sigouts/0/on', 1); #sig output
    daq.setInt('/dev3554/sigouts/0/enables/1', 1); 
    
    
    if noise:
        daq.setInt('/dev3554/sigouts/0/on', 1); #sig output
        daq.setInt('/dev3554/sigouts/0/add', 1) # add noise
    else:
        daq.setInt('/dev3554/sigouts/0/add', 0) # remove noise
        
    data = {}
    
    for signal_path in signal_paths:
        print("Subscribing to ", signal_path)
        daq_module.subscribe(signal_path)
        data[signal_path] = []
        
    clockbase = float(daq.getInt(f"/{device}/clockbase"))
        
    ts0 = np.nan
    read_count = 0
    
    def read_data_update_plot(data, timestamp0):
        data_read = daq_module.read(True)
        returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
        
        progress = daq_module.progress()[0]
        
        for signal_path in signal_paths:
            if signal_path.lower() in returned_signal_paths:
                for index, signal_burst in enumerate(data_read[signal_path.lower()]):
                    if np.any(np.isnan(timestamp0)):
                        timestamp0 = signal_burst["timestamp"][0,0]
                    
                    t = (signal_burst["timestamp"][0,:] - timestamp0) / clockbase
                    value = signal_burst["value"][0,:]
                    
                    num_samples = len(value)
                    dt = (signal_burst["timestamp"][0,-1]
                          - signal_burst["timestamp"][0,0]) / clockbase
                    data[signal_path].append(signal_burst)

                    if run:
                        np.savetxt(f"data\data_{signal_path[-1]}_{run}.csv",[p for p in zip(t, value)], delimiter='ü')
                        print(f"Saved data under data\data_{signal_path[-1]}_{run}.csv")
            else: pass
        
        
        return data, timestamp0
    
    print("waiting...")
    
    # time.sleep(20)
    
    print("starting measurement")
    
    daq_module.execute()
    
    # result = [];
    counter = 0;
    with alive_bar(int(total_duration*1.5)) as bar:
        while daq_module.progress() < 1.0 and not daq_module.finished():
           time.sleep(1)
           counter += 1
           bar()
    
    print(f"counter={counter}")
    data, _ = read_data_update_plot(data, ts0)
    
        
def plot(run: str):
    path = os.path.join(os.getcwd(),"data")
    dataX = np.loadtxt(os.path.join(path,f"data_X_{run}.csv"), delimiter="ü")
    dataY = np.loadtxt(os.path.join(path,f"data_Y_{run}.csv"), delimiter="ü")

    X = dataX[:,1]
    Y = dataY[:,1]

    #fig, ax = plt.subplots()
    plt.scatter(X,Y)
    plt.axis('square')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.ticklabel_format(style='sci', axis = 'both', scilimits=(0,0))
    plt.title("X and Y quadratures")
    
    plt.savefig(f"plot_{run}.png", dpi=300)

if __name__ == "__main__":

    amp = 4000
    noise = False
    external = False
    if noise:
        if external:
            run = f"noise-{amp}-external-new1"
        else:
            run = f"noise-{amp}-param-new1"
        
    else:
        if external:
            run = f"{amp}-external-new1"
        else:
            run = f"{amp}-param-new1"
            
    run = "ringup-4000-1"
        
    
    run_daq(run = run, noise = noise, duration = 90, amp = amp, parametric_drive = True)

    plot(run)

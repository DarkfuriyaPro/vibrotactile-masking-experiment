import nidaqmx
import nidaqmx.system
from nidaqmx.constants import AcquisitionType, READ_ALL_AVAILABLE

class Acc_Interface:
    def __init__(self, fs, duration):

        #system = nidaqmx.system.System.local()
        #print(system.driver_version)
        #print("There is %d devices available " % (len(system.devices)))
        #for device in system.devices:
        #    print(device.name)

        self.fs = fs
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=0, max_val=3.0)
        self.task.ai_channels.add_ai_voltage_chan("Dev1/ai1", min_val=0, max_val=3.0)
        self.task.ai_channels.add_ai_voltage_chan("Dev1/ai2", min_val=0, max_val=3.0)

        self.task.timing.cfg_samp_clk_timing(fs, sample_mode=AcquisitionType.FINITE, samps_per_chan=int(duration*fs))

    def start_recording(self):
        self.task.start()

    def obtain_data(self):
        return self.task.read(READ_ALL_AVAILABLE)
    
    def stop_recording(self):
        self.task.close()
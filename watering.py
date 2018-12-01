#!/usr/bin/python
import serial
import time
import datetime

port = '/dev/ttyACM0'
bitrate = 9600

def log_current_time():
    print(datetime.datetime.fromtimestamp(time.time()).strftime('[%Y-%m-%d %H:%M:%S]'), end=" ")

def get_current_time_str():
    return datetime.datetime.fromtimestamp(time.time()).strftime('[%Y-%m-%d %H:%M:%S]') 

class SerialController:
    def __init__(self, port='/dev/ttyACM0', bitrate=9600):
        self.port = port
        self.bitrate = bitrate
        self.ser = None

    def open(self):
        self.ser = serial.Serial(self.port, self.bitrate, timeout=1)
        
    def close(self):
        self.ser.close()
        del self.ser
        self.ser = None

    def send(self, str_content):
        self.ser.write(str_content.encode())
        last_send_time = time.time()
        while self.ser.inWaiting() <= 0:
            # make sure the signal send through 
            if time.time() - last_send_time > 1:
                self.ser.write(str_content.encode())
                last_send_time = time.time()
        log_current_time()
        print(self.ser.readline().strip().decode())
        return get_current_time_str() + ' ' + self.ser.readline().strip().decode() + '\n'

    def start(self):
        msg = self.send('1')
        log_current_time()
        print("Watering starts")
        return msg + get_current_time_str() + ' ' + "Watering starts."

    def stop(self):
        msg = self.send('1')
        log_current_time()
        print("Watering stops")
        return msg + get_current_time_str + ' ' + "Watering stops."
        

class PlantWateringAgent:
    def __init__(self, time_interval=None, log_filename='watering_log.txt'):
        self._current_time = datetime.datetime.fromtimestamp(time.time())
        self._last_watering_time = self._current_time 
        self.watering_time_interval = time_interval
        self.watering_controller = SerialController()
        self.log_filename = log_filename

    def log(self, event_str):
        with open(self.log_filename, 'a') as f:
            f.write(event_str)
            if len(event_str) > 0 and event_str[-1]!='\n':
                f.write('\n')
            elif len(event_str)==0:
                f.write(get_current_time_str+' '+'Bad logging message. Got empty string.\n')

    def run(self):
        log_current_time()
        print("Watering agent initialized.")
        self.log(get_current_time_str() + ' ' + "Watering agent initialized.")
        while True:
            self._current_time = datetime.datetime.fromtimestamp(time.time())
            if (self._current_time - self._last_watering_time).days > 1:
                self.watering_controller.open()
                msg = self.watering_controller.start()
                self.log(msg)
                time.sleep(14)
                msg = self.watering_controller.stop()
                self.log(msg)
                self.watering_controller.close()
                self._last_watering_time = datetime.datetime.fromtimestamp(time.time())
            else:
                log_current_time()
                print("Waiting ...")
            time.sleep(15)
    
if __name__ == '__main__':
    agent = PlantWateringAgent()
    agent.run()

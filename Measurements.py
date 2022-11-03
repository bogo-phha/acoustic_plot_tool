import numpy as np
import os
import ApXls as ApXls

from Toolbox import toComplex

class Measurements:
    M = []

    def __init__(self):
        pass

    def tableWidget(self):
        pass

    def addMeasurement(self, measurement):
        self.M.append(measurement)

class Measurement:
    path = None
    def __init__(self):
        self.keys = ["FR",
                "THD",
                "AOP",
                ]
        self.H = dict()

        # Further Parameters
        self.label = ""

        self.ampoffset = 0
        self.ampnormalize = False
        self.ampnormalizefreq= 0
        self.phaoffset = 0
        self.phanormalize = False
        self.phanormalizefreq= 0

        # Parse the available data
        self.parse_file()

        # Calculate the derived transfer functions
        self.calculateTransferFunctions()

    def calculateTransferFunctions(self):
        
        # if self.H["oMagRefx"] != None:
        #     pass
        #     # self.H["MagY"] = self.H["oMagy"] - self.H["oMagRefy"]
        #     # self.H["PhaY"] = self.H["oPhay"] - self.H["oPhaRefy"]
        # else:
        
        if self.ampnormalize == False:
            self.H["MagY"] = self.H["oMagY"] + self.ampoffset
        else: 
            [idx, value] = find_nearest(self.H["oMagX"], self.ampnormalizefreq)  
            self.H["MagY"] = self.H["oMagY"] - self.H["oMagY"][idx]        

        self.H["MagX"] = self.H["oMagX"] 
        self.H["PhaX"] = self.H["oPhaX"]
        self.H["PhaY"] = self.H["oPhaY"]
        self.H["AopX"] = self.H["oAopX"]
        self.H["AopY"] = self.H["oAopY"]
        self.H["ThdX"] = self.H["oThdX"]
        self.H["ThdY"] = self.H["oThdY"]
        self.H["Snr"] = self.H["oSnr"] 
        self.H["Thd"] = self.H["oThd"] 
        self.H["Sens"] = self.H["oSens"]
        

    def setDriverCalibration(self, offset):
        self.driverCalibration = offset
        self.caluclateTransferFunctions()

    def setDriverInversion(self, offset):
        self.invertDriver = offset
        self.caluclateTransferFunctions()

    def parse_file(self):
        pass

class Mic(Measurement):
    def __init__(self, path):
        self.path = path
        super().__init__()
        
    def parse_file(self):
        file = "Mic Measurement"
        data = None
        if os.path.exists(self.path + "/" + file + ".xlsx"):
            data = ApXls.MeasurementMic(self.path + "/" + file + ".xlsx")
        if os.path.exists(self.path + "/" + file + ".xls"):
            data = ApXls.MeasurementMic(self.path + "/" + file + ".xls")

        self.H["oMagX"] = data.magx
        self.H["oMagY"] = data.magy
        self.H["oPhaX"] = data.phax
        self.H["oPhaY"] = data.phay
        self.H["oAopX"] = data.aopx
        self.H["oAopY"] = data.aopy
        self.H["oThdX"] = data.thdx
        self.H["oThdY"] = data.thdy
        self.H["oSnr"] = data.snr
        self.H["oThd"] = data.thd
        self.H["oSens"] = data.sens

        # Define the additional parameters
        self.label = self.path[-60:]

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return [idx, array[idx]]
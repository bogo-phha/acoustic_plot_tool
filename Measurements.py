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
        self.keys = ["A2E",
                "A2FF1",
                "A2FF2",
                "A2FF3",
                "A2FF4",
                "A2FF5",
                "A2FF6",
                "A2FF7",
                "A2FF8",
                "A2FF9",
                "A2FF10",
                "A2FB",
                "D2E",
                "D2FB",
                "A2E(open)",
                "Passive",
                "FF1TargetEar",
                "FF2TargetEar",
                "FF3TargetEar",
                "FF4TargetEar",
                "FF5TargetEar",
                "FF6TargetEar",
                "FF7TargetEar",
                "FF8TargetEar",
                "FF9TargetEar",
                "FF10TargetEar",
                "FF1TargetFB",
                "FF2TargetFB",
                "FF3TargetFB",
                "FF4TargetFB",
                "FF5TargetFB",
                "FF6TargetFB",
                "FF7TargetFB",
                "FF8TargetFB",
                "FF9TargetFB",
                "FF10TargetFB",
                "D2E/D2FB",
                "A2E/A2FB",
                "(D2E/D2FB)/(A2E/A2FB)",
                "1/D2E",
                "1/D2FB"]
        self.H = dict()
        self.f = np.logspace(0,4,500)

        # Further Parameters
        self.label = ""

        self.driverCalibration = 0
        self.invertDriver = False

        self.driverPhase = 0
        self.FFTargetEarPhase = 0
        self.FFTargetFBPhase = 0
        self.export = False

        # Parse the available data
        self.parse_file()

        # Fill the voids
        for key in self.keys:
            try:
                a = self.H["o"+key]
            except KeyError:
                self.H["o"+key] = np.ones(np.shape(self.f))

        # Calculate the derived transfer functions
        self.caluclateTransferFunctions()

    def caluclateTransferFunctions(self):
        self.H["D2E"] = self.H["oD2E"] * 10**(self.driverCalibration/20) * np.e**( 1j * np.deg2rad(180*self.invertDriver) )
        self.H["D2FB"] = self.H["oD2FB"] * 10**(self.driverCalibration/20)* np.e**( 1j * np.deg2rad(180*self.invertDriver) )       
        self.H["A2E"] = self.H["oA2E"]
        self.H["A2E(open)"] = self.H["oA2E(open)"]
        self.H["A2FB"] = self.H["oA2FB"]
        self.H["A2FF1"] = self.H["oA2FF1"]
        self.H["A2FF2"] = self.H["oA2FF2"]
        self.H["A2FF3"] = self.H["oA2FF3"]
        self.H["A2FF4"] = self.H["oA2FF4"]
        self.H["A2FF5"] = self.H["oA2FF5"]
        self.H["A2FF6"] = self.H["oA2FF6"]
        self.H["A2FF7"] = self.H["oA2FF7"]
        self.H["A2FF8"] = self.H["oA2FF8"]
        self.H["A2FF9"] = self.H["oA2FF9"]
        self.H["A2FF10"] = self.H["oA2FF10"]
        
        
        
        self.H["FF1TargetEar"] = self.H["A2E"] / (self.H["A2FF1"] * self.H["D2E"])
        self.H["FF1TargetFB"] = self.H["A2FB"] / (self.H["A2FF1"] * self.H["D2FB"])
        self.H["FF2TargetEar"] = self.H["A2E"] / (self.H["A2FF2"] * self.H["D2E"])
        self.H["FF2TargetFB"] = self.H["A2FB"] / (self.H["A2FF2"] * self.H["D2FB"])
        self.H["FF3TargetEar"] = self.H["A2E"] / (self.H["A2FF3"] * self.H["D2E"])
        self.H["FF3TargetFB"] = self.H["A2FB"] / (self.H["A2FF3"] * self.H["D2FB"])
        self.H["FF4TargetEar"] = self.H["A2E"] / (self.H["A2FF4"] * self.H["D2E"])
        self.H["FF4TargetFB"] = self.H["A2FB"] / (self.H["A2FF4"] * self.H["D2FB"])
        self.H["FF5TargetEar"] = self.H["A2E"] / (self.H["A2FF5"] * self.H["D2E"])
        self.H["FF5TargetFB"] = self.H["A2FB"] / (self.H["A2FF5"] * self.H["D2FB"])
        self.H["FF6TargetEar"] = self.H["A2E"] / (self.H["A2FF6"] * self.H["D2E"])
        self.H["FF6TargetFB"] = self.H["A2FB"] / (self.H["A2FF6"] * self.H["D2FB"])
        self.H["FF7TargetEar"] = self.H["A2E"] / (self.H["A2FF7"] * self.H["D2E"])
        self.H["FF7TargetFB"] = self.H["A2FB"] / (self.H["A2FF7"] * self.H["D2FB"])
        self.H["FF8TargetEar"] = self.H["A2E"] / (self.H["A2FF8"] * self.H["D2E"])
        self.H["FF8TargetFB"] = self.H["A2FB"] / (self.H["A2FF8"] * self.H["D2FB"])
        self.H["FF9TargetEar"] = self.H["A2E"] / (self.H["A2FF9"] * self.H["D2E"])
        self.H["FF9TargetFB"] = self.H["A2FB"] / (self.H["A2FF9"] * self.H["D2FB"])
        self.H["FF10TargetEar"] = self.H["A2E"] / (self.H["A2FF10"] * self.H["D2E"])
        self.H["FF10TargetFB"] = self.H["A2FB"] / (self.H["A2FF10"] * self.H["D2FB"])
        
        
        self.H["Passive"] = self.H["A2E"] / self.H["A2E(open)"]
        self.H["D2E/D2FB"] = self.H["D2E"] / self.H["D2FB"]

        self.H["A2E/A2FB"] = self.H["A2E"] / self.H["A2FB"]
        self.H["(D2E/D2FB)/(A2E/A2FB)"] = (self.H["D2E"] / self.H["D2FB"]) / (self.H["A2E"] / self.H["A2FB"])

        self.H["1/D2E"] = 1/self.H["D2E"]
        self.H["1/D2FB"] = 1/self.H["D2FB"]


    def setDriverCalibration(self, offset):
        self.driverCalibration = offset
        self.caluclateTransferFunctions()

    def setDriverInversion(self, offset):
        self.invertDriver = offset
        self.caluclateTransferFunctions()

    def parse_file(self):
        pass


class FreD(Measurement):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def parse_file(self):
        data = ApXls.MeasurementSet(self.path)
        self.f = data.x
        self.H["oD2E"] = toComplex(data.Y[10], data.Y[11])
        self.H["oD2FB"] = toComplex(data.Y[6], data.Y[7])
        self.H["oD2FF"] = toComplex(data.Y[2], data.Y[3])
        self.H["oA2E"] = toComplex(data.Y[8], data.Y[9])
        self.H["oA2FB"] = toComplex(data.Y[4], data.Y[5])
        self.H["oA2FF"] = toComplex(data.Y[0], data.Y[1])

class FleX(Measurement):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def parse_file(self):
        # Parse folder
        files = ["D2E", "D2FB", "D2FF", "A2E", "A2FB", "A2FF", "A2E(open)"]
        self.f = ApXls.MeasurementSet(self.path + "/" + "D2FB.xlsx").x

        for file in files:
            if os.path.exists(self.path + "/" + file + ".xlsx"):
                data = ApXls.MeasurementSet(self.path + "/" + file + ".xlsx")
                mag = data.Y[0]
                phs = data.Y[1]
                h = toComplex(mag, phs)
                self.H["o"+file] = h
            else:
                # Fill in zeros
                self.H[file] = 1j* 1e-200 * np.ones( np.shape(self.f) )
        # Define the additional parameters
        self.label = self.path[-80:]
        
class DualFF(Measurement):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def parse_file(self):
        # Parse folder
        files = ["D2E", "D2FB", "A2E", "A2FB", "A2FF1", "A2FF2", "A2FF3", "A2FF4", "A2FF5", "A2FF6", "A2FF7", "A2FF8", "A2FF9", "A2FF10", "A2E(open)"]
        self.f = ApXls.MeasurementSet(self.path + "/" + "D2FB.xlsx").x

        for file in files:
            if os.path.exists(self.path + "/" + file + ".xlsx"):
                data = ApXls.MeasurementSet(self.path + "/" + file + ".xlsx")
                mag = data.Y[0]
                phs = data.Y[1]
                h = toComplex(mag, phs)
                self.H["o"+file] = h
            else:
                # Fill in zeros
                self.H[file] = 1j* 1e-200 * np.ones( np.shape(self.f) )
        # Define the additional parameters
        self.label = self.path[-80:]

"""
class FFAnalog(Measurement):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def parse_file(self):
        data = ApXls.MeasurementSet(self.path)
        self.f = data.x
        self.H["A2E"] = toComplex( data.Y[0], data.Y[2] )
        self.H["A2FF"] = toComplex( data.Y[1], data.Y[3] )
        self.H["D2E"] = toComplex( data.Y[4], data.Y[6] )
        self.H["D2FF"] = toComplex( data.Y[5], data.Y[7] )

class FBAnalog(Measurement):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def parse_file(self):
        data = ApXls.MeasurementSet(self.path)
        self.f = data.x
        self.H["D2E"] = toComplex( data.Y[0], data.Y[2] )
        self.H["D2FB"] = toComplex( data.Y[1], data.Y[3] )

This was some other template:
class AnotherTemplate(Measurement):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def parse_file(self):
        data = ApXls.MeasurementSet(self.path)
        self.f = data.x
        self.H["D2E"] = toComplex(data.Y[0], data.Y[1])
        self.H["A2E"] = toComplex(data.Y[2], data.Y[3])
        self.H["D2FB"] = toComplex(data.Y[4], data.Y[5])
        self.H["A2FB"] = toComplex(data.Y[6], data.Y[7])
        self.H["A2FF"] = toComplex(data.Y[8], data.Y[9])
"""

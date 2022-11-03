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
                "A2FF",
                "A2FB",
                "D2E",
                "D2FF",
                "D2FB",
                "A2E(open)",
                "Passive",
                "FFTargetEar",
                "FFTargetFB",
                "D2E/D2FB",
                "D2FB/D2FF",
                "A2E/A2FB",
                "A2FB/A2FF",
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
        self.H["D2FF"] = self.H["oD2FF"] * 10**(self.driverCalibration/20)* np.e**( 1j * np.deg2rad(180*self.invertDriver) )

        self.H["A2E"] = self.H["oA2E"]
        self.H["A2E(open)"] = self.H["oA2E(open)"]
        self.H["A2FB"] = self.H["oA2FB"]
        self.H["A2FF"] = self.H["oA2FF"]

        self.H["Passive"] = self.H["A2E"] / self.H["A2E(open)"]
        self.H["FFTargetEar"] = self.H["A2E"] / (self.H["A2FF"] * self.H["D2E"])
        self.H["FFTargetFB"] = self.H["A2FB"] / (self.H["A2FF"] * self.H["D2FB"])
        self.H["D2E/D2FB"] = self.H["D2E"] / self.H["D2FB"]
        self.H["D2FB/D2FF"] = self.H["D2FB"]/self.H["D2FF"]
        self.H["A2E/A2FB"] = self.H["A2E"] / self.H["A2FB"]
        self.H["A2FB/A2FF"] = self.H["A2FB"]/self.H["A2FF"]
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


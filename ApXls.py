import pandas as pd
import numpy as np
import os
from Measurements import find_nearest


class Measurement:
    """
    This is the base data-structure/class to represent a single measurement.
    It includes, X and Y axis, as well as their units and the name of the
    measurement.
    Also an utility method to plot the measurement is included.
    """
    x = None
    y = None
    xunit = None
    yunit = None
    title = ""

    def __init__(self, x, y, xunit, yunit, title=""):
        self.x = x
        self.y = y
        self.xunit = xunit
        self.yunit = yunit
        self.title = title

    def plot(self, ax=None, hold=True, title=None):
        """
        Plots the measurement, including correct naming of the axis.
        :param ax: You can plot on an existing axis, if provided
        :param hold: if True will surpress the matplotlib plt.show() output,
                        so you can stack multiple curves
        :param title: appears in the legend for this measurement
        """
        import matplotlib.pyplot as plt
        if ax is None:
            fig, ax = plt.subplots()
        ax.semilogx(self.x, self.y, label=self.title)
        ax.set_xlabel(self.xunit)
        ax.set_ylabel(self.yunit)
        if title is not None:
            ax.set_title(title)
        ax.grid(True)
        ax.legend()
        if not hold:
            plt.show()


class Sheet(Measurement):
    """
    This models a sheet in an ApX exported Excel file. A sheet can contain several
    measurements, listed in "channel". The "Sheet" class inherits from the basic Measurement,
    if you access the base members (x,y,xunit,yunit..) you will get the first measurement of
    that sheet.
    The other measurements you can access either by Sheet.channel[i] (returns a Measurement object)
    or directly access the raw values with capital letters: Sheet.Y[i] or Sheet.X[i]
    """
    X = None
    Y = None

    def __init__(self, data):
        """
        This constructor contains the actual xls parsing logic.
        :param data: raw xls data read from pandas' xls module
        """
        # Members for outside access
        x = None
        y = None
        xunit = None
        yunit = None
        self.X = list()
        self.Y = list()
        self.Title = list()
        self.channel = list()

        axisDir = dict()
        unit = dict()
        values = dict()
        names = dict()
        axisCount = np.shape(data)[1]

        # Parse lines and columns into their categories
        for i in range(0,axisCount):
            axisDir[i] = data[1,i]
            unit[i] = data[2,i]
            values[i] = data[3:,i]
            names[i] = data[0,2*(i//2)]
        values = np.nan_to_num(values)

        # Separate Channels
        full = False
        first = True
        for i in range(axisCount):
            if axisDir[i] == "X":
                x = values[i]
                self.X.append( x )
                self.Title.append( names[i] )
                xunit = unit[i]
            if axisDir[i] == "Y":
                y = values[i]
                self.Y.append( y )
                yunit = unit[i]
                full = True
            if full: # full means, we have found one set of x and y
                        #  completing a full measurement
                if first: # the first measurement is treated separately for easy access
                    self.x = x
                    self.y = y
                    self.xunit = xunit
                    self.yunit = yunit
                    self.title = names[i]
                    first = False
                self.channel.append( Measurement(x, y, xunit, yunit, names[i]) )
                full = False


class MeasurementSet(Measurement):
    """
    This class represents an ApX Excel file with various ways of accessing the data:
    Open a file, e.g.:
        m = MeasurementSet("ANC-Performance.xls")

    In Detail:
        m.x
        m.y
        m.xunit
        m.yunit
        m.title - data from the first measurements in the file
        m.plot() - Plots the Measurement, see class Measurement for more details

        m.sheet[i].x
        m.sheet[i].y
        ...                 - data from the first measurement of the i-th Sheet

        m.sheet[i].channel[j].x
        ...                 - data from the j-th channel of the i-th Sheet
    Or just raw data:
        m.X[i]
        m.Y[i] - All measurement data in the document indexed

        m.sheet[i].X[i]
        m.sheet[i].Y[i] - All measurement data in the i-th sheet indexed
    """
    X = None
    Y = None

    def __init__(self, file):
        self.file = file
        self.xls = pd.ExcelFile(self.file)

        self.X = list()
        self.Y = list()
        self.Title = list()

        # Proceed to analyze structure
        self.sheet = list()

        sheetsInFile = self.xls.sheet_names
        for sheet in sheetsInFile:
            data = self.xls.parse(sheet).values     # will store numpy array in data
            m = Sheet(data)                         # create sheet class with this data. Sheet class will split data into lists of X and Y values 
            for y in m.Y:                           # x&y will interate though each channel of sheet m and create a list of all y data in self.y! One measurement series (channel) can be accessed via self.y[0]
                self.Y.append(y)
            for x in m.X:
                self.X.append(x)
            self.Title.append( m.title )            # create list of all sheet titles. Title of first sheet measurement is self.Title[0]

            self.sheet.append(m)

        self.x = self.sheet[0].x
        self.y = self.sheet[0].y
        self.xunit = self.sheet[0].xunit
        self.yunit = self.sheet[0].yunit
        self.title = self.sheet[0].title


class MeasurementMic(Measurement):
    
    
    def __init__(self, file):
        self.file = file
        self.xls = pd.ExcelFile(self.file)
        self.sheets = list()
        self.mictype = None

        sheetsInFile = self.xls.sheet_names
        # Check if mictype is analog or digital

        for sheet in sheetsInFile:
            data = self.xls.parse(sheet).values     # will store numpy array in data
            self.sheets.append(data)

        if sheetsInFile[0] == "Signal to Noise Ratio":
            self.mictype = "analog"

            self.snr = self.sheets[0][3,1]
            self.magx = Sheet(self.sheets[2]).x
            self.magy = Sheet(self.sheets[2]).y
            self.phax = Sheet(self.sheets[4]).x
            self.phay = Sheet(self.sheets[4]).y
            self.thd = self.sheets[8][3,1]
            self.sens = self.sheets[6][3,1]
            self.aopx = Sheet(self.sheets[9]).X[1]
            self.aopy = Sheet(self.sheets[9]).Y[1]
            self.thdx = Sheet(self.sheets[5]).X[1]
            self.thdy = Sheet(self.sheets[5]).Y[1]

        elif sheetsInFile[0] == "RMS Level":
            self.mictype = "digital"

            self.snr = self.sheets[4][2,1]
            self.magx_dut = Sheet(self.sheets[5]).x
            self.magy_dut = Sheet(self.sheets[5]).y
            self.phax_dut = Sheet(self.sheets[6]).x
            self.phay_dut = Sheet(self.sheets[6]).y
            self.magx_ref = Sheet(self.sheets[0]).x
            self.magy_ref = Sheet(self.sheets[0]).y
            self.phax_ref = Sheet(self.sheets[1]).x
            self.phay_ref = Sheet(self.sheets[1]).y
            self.thd = self.sheets[10][2,1]
            self.sens = self.sheets[8][2,1]
            self.aopx = Sheet(self.sheets[11]).x
            self.aopy = Sheet(self.sheets[11]).y
            self.thdx = Sheet(self.sheets[7]).x
            self.thdy = Sheet(self.sheets[7]).y
            self.aopx_ref = Sheet(self.sheets[3]).x
            self.aopy_ref = Sheet(self.sheets[3]).y
            self.thdx_ref = Sheet(self.sheets[2]).x
            self.thdy_ref = Sheet(self.sheets[2]).y
        
            self.magx = self.magx_dut
            self.phax = self.phax_dut
            self.magy = self.magy_dut - self.magy_ref
            self.phay = self.phay_dut - self.phay_ref

            [idx, value] = find_nearest(self.magx, 1000)  
            self.magy = self.magy - self.magy[idx] 

            [idx, value] = find_nearest(self.phax, 1000)  
            self.phay = self.phay - self.phay[idx] 

      
        

    
    









    

import numpy as np
import matplotlib.pyplot as plt
from ParameterTable import ParameterTable
import ipywidgets as widgets
from IPython.display import display, clear_output
from tkinter import Tk, filedialog
import pandas as pd
import os


class PlotGui():
    def __init__(self, measurements):
        self.measurements = measurements
        self.table = ParameterTable(self.measurements).table
        # Widget Construction

        # I. Tab for Selection of Curve and Measurement
        self.curveSelect = widgets.SelectMultiple(
            options=self.measurements[0].keys,
            layout={'width': '500px', 'height': '250px'}
        )

        self.measurementsDict = {}
        for m in self.measurements:
            self.measurementsDict[m.label] = m

        self.measurementSelect = widgets.SelectMultiple(
            options=self.measurementsDict,
            layout={'width': '800px', 'height': '250px'})

        self.plotSelect = widgets.HBox([self.curveSelect, self.measurementSelect])

        # II. Tab for Plot Configuration (to be extended)
        self.phaseWrapSelect = widgets.Checkbox(description='Wrap phase')
        self.legendSelect = widgets.Checkbox(description='Display Legend', value=True)

        self.xLimLow = widgets.FloatLogSlider(
            value=1,
            base=10,
            min=0,  # max exponent of base
            max=4.5,  # min exponent of base
            step=0.2,  # exponent step
            description='Fmin',
            continuous_update=False,
            layout={'width': '500px'}
        )
        self.xLimHigh = widgets.FloatLogSlider(
            value=20e3,
            base=10,
            min=0,  # max exponent of base
            max=4.5,  # min exponent of base
            step=0.2,  # exponent step
            description='Fmax',
            continuous_update=False,
            layout={'width': '500px'}
        )

        self.plotTitle = widgets.Textarea(description="Plot Title:", value="Transfer Function", continuous_update=False)

        self.configSelect = widgets.VBox([self.phaseWrapSelect,
                                          self.legendSelect,
                                          self.xLimLow,
                                          self.xLimHigh,
                                          self.plotTitle], layout={'height': '250px'})

        # III. Table for editing calibrations and Labels
        self.updateButton = widgets.Button(description="Update")
        self.updateButton.on_click(self.plotTransferFunction)

        self.exportButton = widgets.Button(description="Export")
        self.exportButton.on_click(self.export)
        self.checkFFFB = widgets.Checkbox(description="FF/FB", value=True)
        self.checkEar = widgets.Checkbox(description="Ear", value=False)
        self.checkTarget = widgets.Checkbox(description="Target", value=False)


        self.buttonBox = widgets.HBox( [self.updateButton,
                                        self.exportButton,
                                        self.checkFFFB,
                                        self.checkEar,
                                        self.checkTarget])

        self.hint = widgets.Label("Hint: 180,360,540,720,900,1080,1260")

        self.tableBox = widgets.VBox([self.table, self.buttonBox, self.hint], layout={'overflow_y': 'auto'})

        # IV. Tab Widget
        tabChildren = [self.plotSelect, self.configSelect, self.tableBox]
        tab = widgets.Tab()
        tab.children = tabChildren
        tab.set_title(0, 'Measurement')
        tab.set_title(1, "Plot Config")
        tab.set_title(2, "Calibration + Export")

        # V. Put in VBox
        self.out = widgets.Output()

        self.container = widgets.VBox([tab, self.out])

        with self.out:
            clear_output(True)
            self.fig1, [self.axMagnitude, self.axPhase] = plt.subplots(nrows=2)
            self.axPhase.set_xlabel("Frequensdfsdcy in Hz")
            self.axMagnitude.set_ylabel("Amplitude in dB")
            self.axMagnitude.grid()
            self.axPhase.grid()
            self.axPhase.set_ylabel("Phase in Degrees")
            self.fig1.set_size_inches((12, 10))
            plt.show(self.fig1)
            

        self.curveSelect.observe(self.plotTransferFunction)
        self.measurementSelect.observe(self.plotTransferFunction)
        self.phaseWrapSelect.observe(self.plotTransferFunction)
        self.xLimLow.observe(self.plotTransferFunction, names='value')
        self.xLimHigh.observe(self.plotTransferFunction, names='value')
        self.plotTitle.observe(self.plotTransferFunction, names='value')
        self.legendSelect.observe(self.plotTransferFunction, names='value')

        display(self.container)

    def export(self, args):
        # Create Tk root
        root = Tk()
        # Hide the main window
        root.withdraw()
        # Raise the root to the top of all windows.
        root.call('wm', 'attributes', '.', '-topmost', True)
        # List of selected fileswill be set to b.value
        path = filedialog.askdirectory()

        for m in self.measurements:
            if m.export:
                os.mkdir(path + "/" + m.label)
                if self.checkFFFB.value:
                    self.exportTransferFunction(path + "/" + m.label + "/D2FB.xls", m.f, m.H["D2FB"], m.driverPhase)
                    self.exportTransferFunction(path + "/" + m.label + "/D2FF.xls", m.f, m.H["D2FF"], m.driverPhase)
                    self.exportTransferFunction(path + "/" + m.label + "/A2FB.xls", m.f, m.H["A2FB"], 0)
                    self.exportTransferFunction(path + "/" + m.label + "/A2FF.xls", m.f, m.H["A2FF"], 0)
                    if self.checkTarget.value:
                        self.exportTransferFunction(path + "/" + m.label + "/FFTargetFB.xls", m.f, m.H["FFTargetFB"], m.FFTargetFBPhase)
                if self.checkEar.value:
                    self.exportTransferFunction(path + "/" + m.label + "/D2E.xls", m.f, m.H["D2E"], m.driverPhase)
                    self.exportTransferFunction(path + "/" + m.label + "/A2E.xls", m.f, m.H["A2E"], 0)
                    self.exportTransferFunction(path + "/" + m.label + "/A2E(open).xls", m.f, m.H["A2E(open)"], 0)
                    if self.checkTarget.value:
                        self.exportTransferFunction(path + "/" + m.label + "/FFTargetEar.xls", m.f, m.H["FFTargetEar"], m.FFTargetEarPhase)

    def exportTransferFunction(self, path, f, H, offset):
        Hf = list(f)
        Hf.insert(0, 'Hz')
        Hf.insert(0, 'X')
        Hf.insert(0, 'Bf')

        Hm = list( 20 * np.log10( np.abs( H )))
        Hm.insert(0, 'dB')
        Hm.insert(0, 'Y')
        Hm.insert(0, 'Bf')

        Hp = list( np.rad2deg( np.unwrap( np.angle( H ) ) ) + offset )
        Hp.insert(0, 'deg')
        Hp.insert(0, 'Y')
        Hp.insert(0, 'Bf')

        d1 = {'X': Hf, 'Y': Hm}
        d2 = {'X': Hf, 'Y': Hp}
        df1 = pd.DataFrame(data=d1)
        df2 = pd.DataFrame(data=d2)

        writer = pd.ExcelWriter(path)
        df1.to_excel(writer, sheet_name="Magnitude", index=False)
        df2.to_excel(writer, sheet_name="Phase", index=False)
        writer.save()

    def plotTransferFunction(self, arg):
        if len(self.measurementSelect.value) and len(self.curveSelect.value):
            with self.out:
                clear_output(True)
                self.fig1, [self.axMagnitude, self.axPhase] = plt.subplots(nrows=2)
                self.fig1.set_size_inches((12, 10))

                measurements = self.measurementSelect.value
                curves = self.curveSelect.value

                for curve in curves:
                #curve = self.curveSelect.value[0]


                    for m in measurements:
                        H = m.H[curve]
                        self.axMagnitude.semilogx( m.f, 20*np.log10( np.abs( H )), label=m.label[-40:]+" "+curve)

                        if self.phaseWrapSelect.value:
                            phase = np.rad2deg( np.angle(H) )
                        else:
                            offset = 0
                            if curve in ["D2E", "D2FF", "D2FB"]:
                                offset = m.driverPhase
                            elif curve in ["FFTargetEar"]:
                                offset = m.FFTargetEarPhase
                            elif curve in["FFTargetFB"]:
                                offset = m.FFTargetFBPhase

                            phase = np.rad2deg( np.unwrap( np.angle( H ))) + offset

                        self.axPhase.semilogx( m.f, phase, label=m.label[-40:]+" "+curve)

                self.axMagnitude.grid(True)
                self.axMagnitude.set_ylabel("Magnitude in dB")
                self.axMagnitude.set_xlim( (self.xLimLow.value, self.xLimHigh.value) )
                self.axMagnitude.set_axisbelow(True)
                if self.legendSelect.value:
                    self.axMagnitude.legend()

                self.axPhase.set_xlim( (self.xLimLow.value, self.xLimHigh.value) )
                self.axPhase.set_ylabel("Phase in Degrees")
                self.axPhase.set_xlabel("Frequency in Hz")
                self.axPhase.legend(facecolor='white', framealpha=1)
                self.axPhase.grid()
                

                self.axMagnitude.set_title( self.plotTitle.value)

                plt.show(self.fig1)
import numpy as np
import matplotlib.pyplot as plt
from ParameterTable import ParameterTable, ParameterTable_Meas
import ipywidgets as widgets
from IPython.display import display, clear_output
from tkinter import Tk, filedialog
import pandas as pd
import os


class PlotGui():
    def __init__(self, measurements):
        self.measurements = measurements
        self.table = ParameterTable(self.measurements).table
        self.table_meas = ParameterTable_Meas(self.measurements).table

        # Widget Construction

        # I. Tab for Selection of Curve and Measurement
        self.curveSelect = widgets.Select(
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



        self.buttonBox = widgets.HBox( [self.updateButton])

        self.hint = widgets.Label("Phase Offset Hint: 180,360,540,720,900,1080,1260")

        self.tableBox = widgets.VBox([self.table, self.buttonBox, self.hint], layout={'overflow_y': 'auto'})
        self.tableBox_meas = widgets.VBox([self.table_meas], layout={'overflow_y': 'auto'})

        # IV. Tab Widget
        tabChildren = [self.plotSelect, self.configSelect, self.tableBox, self.tableBox_meas]
        tab = widgets.Tab()
        tab.children = tabChildren
        tab.set_title(0, 'Measurement')
        tab.set_title(1, "Plot Config")
        tab.set_title(2, "Calibration")
        tab.set_title(3, "Meas Values")

        # V. Put in VBox
        self.out = widgets.Output()

        self.container = widgets.VBox([tab, self.out])

        with self.out:
            clear_output(True)
            self.fig1, [self.axMagnitude, self.axPhase] = plt.subplots(nrows=2)
            self.axPhase.set_xlabel("Frequeny in Hz")
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


    def plotTransferFunction(self, arg):
        if len(self.measurementSelect.value) and len(self.curveSelect.value):
            with self.out:
                clear_output(True)
                measurements = self.measurementSelect.value
                

                # make FR plot
                if self.curveSelect.value == 'FR':
                    self.fig1, [self.axMagnitude, self.axPhase] = plt.subplots(nrows=2)
                    self.fig1.set_size_inches((12, 10))

                    for m in measurements:
                        Hamplx = m.H['MagX']
                        Hamply = m.H['MagY']
                        Hphax = m.H['PhaX']
                        Hphay = m.H['PhaY']
                        
                        self.axMagnitude.semilogx( Hamplx, Hamply, label=m.label[-40:])

                        if self.phaseWrapSelect.value:
                            phase = Hphay % 179
                        else:
                            offset = m.phaoffset
                            phase  = Hphay + offset
                        
                        self.axPhase.semilogx( Hphax, phase, label=m.label[-40:])
                    
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
                        

                    # make THD plot
                elif self.curveSelect.value == 'THD':
                    self.fig1, self.axMagnitude = plt.subplots(nrows=1)
                    self.fig1.set_size_inches((12, 10))
                    for m in measurements:
                        Hamplx = m.H['ThdX']
                        Hamply = m.H['ThdY']
                        
                        self.axMagnitude.semilogx( Hamplx, Hamply, label=m.label[-40:])
                    
                    self.axMagnitude.grid(True)
                    self.axMagnitude.set_ylabel("THD in %")
                    self.axMagnitude.set_xlim( (20, 10000) )
                    self.axMagnitude.set_ylim( (0, 1) )
                    self.axMagnitude.set_axisbelow(True)
                    if self.legendSelect.value:
                        self.axMagnitude.legend()
                    self.axPhase.set_ylabel("THD in %")
                    self.axPhase.set_xlabel("Frequency in Hz")

                        
                elif self.curveSelect.value == 'AOP':
                    self.fig1, self.axMagnitude = plt.subplots(nrows=1)
                    self.fig1.set_size_inches((12, 10))
                    for m in measurements:
                        Hamplx = m.H['AopX']
                        Hamply = m.H['AopY']
                        
                        self.axMagnitude.plot( Hamplx, Hamply, label=m.label[-40:])
                    
                    self.axMagnitude.grid(True)
                    self.axMagnitude.set_xlabel("Frequency in Hz")
                    self.axMagnitude.set_ylabel("THD in %")
                    self.axMagnitude.set_xlim( (60, 130) )
                    self.axMagnitude.set_ylim( (0, 20) )
                    self.axMagnitude.set_axisbelow(True)
                    if self.legendSelect.value:
                        self.axMagnitude.legend()
                    
                plt.show(self.fig1)

                    

                        

                    

           

                
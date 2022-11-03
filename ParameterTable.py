import ipysheet

class ParameterTable():
    def __init__(self, measurements):
        self.measurements = measurements
        self.table = ipysheet.sheet(rows=len(measurements),
                               columns=7,
                               column_headers=["Label",
                                               "Amp Offset",
                                               "Amp Normalize",
                                               "Amp Normalize Freq",
                                               "Phase Offset",
                                               "Phase Normalize",
                                               "Phase Normalize Freq"],
                               row_headers=False)
        self.rows = []
        self.cells = []

        for i in range(len(self.measurements)):
            columns = {}
            cell_label = ipysheet.cell(i, 0, self.measurements[i].label)
            cell_label.observe(self.onChange, 'value')
            columns["Label"] = cell_label
            self.cells.append(cell_label)

            cell_ampoffset = ipysheet.cell(i, 1, self.measurements[i].ampoffset)
            cell_ampoffset.observe(self.onChange, 'value')
            columns["Amp Offset"] = cell_ampoffset
            self.cells.append(cell_ampoffset)

            cell_ampnormalize = ipysheet.cell(i, 2, self.measurements[i].ampnormalize)
            cell_ampnormalize.observe(self.onChange, 'value')
            columns["Amp Norm"] = cell_ampnormalize
            self.cells.append(cell_ampnormalize) 

            cell_ampnormalizefreq = ipysheet.cell(i, 3, self.measurements[i].ampnormalizefreq)
            cell_ampnormalizefreq.observe(self.onChange, 'value')
            columns["Amp Norm Freq"] = cell_ampnormalizefreq
            self.cells.append(cell_ampnormalizefreq)

            cell_phaoffset = ipysheet.cell(i, 4, self.measurements[i].phaoffset)
            cell_phaoffset.observe(self.onChange, 'value')
            columns["Phase Offset"] = cell_phaoffset
            self.cells.append(cell_phaoffset)

            cell_phanormalize = ipysheet.cell(i, 5, self.measurements[i].phanormalize)
            cell_phanormalize.observe(self.onChange, 'value')
            columns["Phase Norm"] = cell_phanormalize
            self.cells.append(cell_phanormalize)

            cell_phanormalizefreq = ipysheet.cell(i, 6, self.measurements[i].phanormalizefreq)
            cell_phanormalizefreq.observe(self.onChange, 'value')
            columns["Phase Norm Freq"] = cell_phanormalizefreq
            self.cells.append(cell_phanormalizefreq)

            self.rows.append(columns)

    def onChange(self, change):
        for i in range(len(self.measurements)):
            self.measurements[i].label = self.rows[i]["Label"].value

            self.measurements[i].ampoffset = self.rows[i]["Amp Offset"].value 
            self.measurements[i].ampnormalize = self.rows[i]["Amp Norm"].value
            self.measurements[i].ampnormalizefreq = self.rows[i]["Amp Norm Freq"].value
            self.measurements[i].phaoffset = self.rows[i]["Phase Offset"].value
            self.measurements[i].phanormalize     = self.rows[i]["Phase Norm"].value
            self.measurements[i].phanormalizefreq = self.rows[i]["Phase Norm Freq"].value
            self.measurements[i].calculateTransferFunctions()
            
class ParameterTable_Meas():
    def __init__(self, measurements):
        self.measurements = measurements
        self.table = ipysheet.sheet(rows=len(measurements),
                               columns=4,
                               column_headers=["-Mic-",
                                               "SNR",
                                               "Sensitivity",
                                               "THD"
                                               ],
                               row_headers=False)

        for i in range(len(self.measurements)):

            cell_Label = ipysheet.cell(i, 0, self.measurements[i].label[-60:])
            cell_Snr = ipysheet.cell(i, 1, self.measurements[i].H["oSnr"])
            cell_Sens = ipysheet.cell(i, 2, self.measurements[i].H["oSens"])
            cell_Thd = ipysheet.cell(i, 3, self.measurements[i].H["oThd"])

    

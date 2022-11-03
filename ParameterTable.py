import ipysheet

class ParameterTable():
    def __init__(self, measurements):
        self.measurements = measurements
        self.table = ipysheet.sheet(rows=len(measurements),
                               columns=7,
                               column_headers=["Label",
                                               "Driver Calibration",
                                               "Invert Driver",
                                               "Driver Phase",
                                               "FF Target Ear Phase",
                                               "FF Target FB Phase",
                                               "Export"],
                               row_headers=False)
        self.rows = []
        self.cells = []

        for i in range(len(self.measurements)):
            columns = {}
            cell_label = ipysheet.cell(i, 0, self.measurements[i].label)
            cell_label.observe(self.onChange, 'value')
            columns["Label"] = cell_label
            self.cells.append(cell_label)

            cell_driver = ipysheet.cell(i, 1, self.measurements[i].driverCalibration)
            cell_driver.observe(self.onChange, 'value')
            columns["Driver Calibration"] = cell_driver
            self.cells.append(cell_driver)

            cell_driver_invert = ipysheet.cell(i, 2, self.measurements[i].invertDriver)
            cell_driver_invert.observe(self.onChange, 'value')
            columns["Invert Driver"] = cell_driver_invert
            self.cells.append(cell_driver_invert)

            cell_driver_phase = ipysheet.cell(i, 3, self.measurements[i].driverPhase)
            cell_driver_phase.observe(self.onChange, 'value')
            columns["Driver Phase"] = cell_driver_phase
            self.cells.append(cell_driver_phase)

            cell_FFTargetEarPhase = ipysheet.cell(i, 4, self.measurements[i].FFTargetEarPhase)
            cell_FFTargetEarPhase.observe(self.onChange, 'value')
            columns["FF Target Ear Phase"] = cell_FFTargetEarPhase
            self.cells.append(cell_FFTargetEarPhase)

            cell_FFTargetFBPhase = ipysheet.cell(i, 5, self.measurements[i].FFTargetFBPhase)
            cell_FFTargetFBPhase.observe(self.onChange, 'value')
            columns["FF Target FB Phase"] = cell_FFTargetFBPhase
            self.cells.append(cell_FFTargetFBPhase)

            cell_export = ipysheet.cell(i, 6, self.measurements[i].export)
            cell_export.observe(self.onChange, 'value')
            columns["Export"] = cell_export
            self.cells.append(cell_export)

            self.rows.append(columns)

    def onChange(self, change):
        for i in range(len(self.measurements)):
            self.measurements[i].label = self.rows[i]["Label"].value

            self.measurements[i].setDriverCalibration( self.rows[i]["Driver Calibration"].value )
            self.measurements[i].setDriverInversion( self.rows[i]["Invert Driver"].value)

            self.measurements[i].driverPhase = self.rows[i]["Driver Phase"].value
            self.measurements[i].FFTargetEarPhase = self.rows[i]["FF Target Ear Phase"].value
            self.measurements[i].FFTargetFBPhase = self.rows[i]["FF Target FB Phase"].value

            self.measurements[i].export = self.rows[i]["Export"].value

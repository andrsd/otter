import vtk
from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.viz.PropsBase import PropsBase


class FileProps(PropsBase):
    """
    Properties page to display when root is selected
    """

    IDX_NAME = 0
    IDX_COLOR = 1
    IDX_ID = 2

    def __init__(self, reader, parent=None):
        super().__init__(parent)
        self._title.setText("File properties")
        self._reader = reader
        self._block_actors = {}

        self._colors = [
            QtGui.QColor(156, 207, 237),
            QtGui.QColor(165, 165, 165),
            QtGui.QColor(60, 97, 180),
            QtGui.QColor(234, 234, 234),
            QtGui.QColor(197, 226, 243),
            QtGui.QColor(127, 127, 127),
            QtGui.QColor(250, 182, 0)
        ]

        self.setupWidgets()
        self.buildVtkActor()

    def getVtkActor(self):
        return list(self._block_actors.values())

    def setupWidgets(self):
        self._file_name = QtWidgets.QLineEdit(self._reader.getFileName())
        self._file_name.setReadOnly(True)
        self._layout.addWidget(self._file_name)
        self._setupVariableWidget()
        self._setupBlocksWidget()
        self._layout.addStretch()

        self._variable.currentIndexChanged.connect(self.onVariableChanged)

    def _setupVariableWidget(self):
        var_info = self._reader.getVariableInfo()

        self._variable = QtWidgets.QComboBox()
        self._variable.addItem("Block colors", None)
        for vi in var_info:
            self._variable.addItem(vi.name, vi)
        self._layout.addWidget(self._variable)

    def _setupBlocksWidget(self):
        self._lbl_blocks = QtWidgets.QLabel("Blocks")
        self._layout.addWidget(self._lbl_blocks)
        self._block_model = QtGui.QStandardItemModel()
        self._block_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._block_model.itemChanged.connect(self.onBlockChanged)
        self._blocks = QtWidgets.QTreeView()
        self._blocks.setFixedHeight(200)
        self._blocks.setRootIsDecorated(False)
        self._blocks.setModel(self._block_model)
        self._blocks.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._blocks.setColumnWidth(0, 200)
        self._blocks.setColumnWidth(1, 20)
        self._blocks.setColumnWidth(2, 50)
        self._layout.addWidget(self._blocks)

    def _addBlock(self, row, binfo, clr_idx):
        si_name = QtGui.QStandardItem()
        si_name.setText(binfo.name)
        si_name.setCheckable(True)
        si_name.setCheckState(QtCore.Qt.Checked)
        si_name.setData(binfo)
        self._block_model.setItem(row, self.IDX_NAME, si_name)

        si_clr = QtGui.QStandardItem()
        si_clr.setText('\u25a0')
        qcolor = self._colors[clr_idx]
        si_clr.setForeground(QtGui.QBrush(qcolor))
        si_clr.setData(clr_idx)
        self._block_model.setItem(row, self.IDX_COLOR, si_clr)

        si_id = QtGui.QStandardItem()
        si_id.setText(str(binfo.number))
        self._block_model.setItem(row, self.IDX_ID, si_id)

    def _buildVtkBlocksActor(self, binfo):
        if binfo.multiblock_index is not None:
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(self._reader.getVtkOutputPort())
            eb.AddIndex(binfo.multiblock_index)
            eb.Update()

            geometry = vtk.vtkCompositeDataGeometryFilter()
            geometry.SetInputConnection(0, eb.GetOutputPort(0))
            geometry.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(geometry.GetOutputPort())
        else:
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputConnection(0, self._reader.getVtkOutputPort())
            mapper.ScalarVisibilityOff()

        mapper.InterpolateScalarsBeforeMappingOn()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.VisibilityOn()

        return actor

    def buildVtkActor(self):
        actors = []

        blocks = self._reader.getBlocks()
        for index, binfo in enumerate(blocks):
            clr_idx = index % len(self._colors)
            qcolor = self._colors[clr_idx]
            clr = [
                qcolor.redF(),
                qcolor.greenF(),
                qcolor.blueF()
            ]

            actor = self._buildVtkBlocksActor(binfo)
            property = actor.GetProperty()
            property.SetColor(clr)
            actors.append(actor)
            self._block_actors[binfo.number] = actor

            row = self._block_model.rowCount()
            self._addBlock(row, binfo, clr_idx)

    def onBlockChanged(self, item):
        if item.column() == self.IDX_NAME:
            visible = item.checkState() == QtCore.Qt.Checked
            binfo = item.data()
            actor = self._block_actors[binfo.number]
            actor.SetVisibility(visible)

    def onVariableChanged(self, index):
        vinfo = self._variable.itemData(index)
        if vinfo is None:
            for bnum, actor in self._block_actors.items():
                mapper = actor.GetMapper()
                mapper.ScalarVisibilityOff()
        else:
            for actor in self._block_actors.values():
                mapper = actor.GetMapper()
                mapper.ScalarVisibilityOn()
                mapper.SelectColorArray(vinfo.name)
                mapper.UseLookupTableScalarRangeOn()
                if vinfo.object_type == vtk.vtkExodusIIReader.NODAL:
                    mapper.SetScalarModeToUsePointFieldData()
                elif vinfo.object_type == vtk.vtkExodusIIReader.ELEM_BLOCK:
                    mapper.SetScalarModeToUseCellFieldData()
                mapper.InterpolateScalarsBeforeMappingOn()

import vtk
from PyQt5.QtWidgets import QLineEdit, QComboBox, QLabel, QTreeView, \
    QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem, QBrush
from otter.plugins.viz.PropsBase import PropsBase
from otter.plugins.common.Reader import Reader


class FileProps(PropsBase):
    """
    Properties page to display when file is selected
    """

    IDX_NAME = 0
    IDX_COLOR = 1
    IDX_ID = 2

    def __init__(self, reader, parent):
        super().__init__(parent)
        self._reader = reader
        self._block_actors = {}
        self._vtk_extract_block = {}

        self._colors = [
            QColor(156, 207, 237),
            QColor(165, 165, 165),
            QColor(60, 97, 180),
            QColor(234, 234, 234),
            QColor(197, 226, 243),
            QColor(127, 127, 127),
            QColor(250, 182, 0)
        ]

        self.setupWidgets()
        self.buildVtkActor()
        self.onVariableChanged(self._variable.currentIndex())

    def getVtkActor(self):
        return list(self._block_actors.values())

    def setupWidgets(self):
        self._file_name = QLineEdit(self._reader.getFileName())
        self._file_name.setReadOnly(True)
        self._layout.addWidget(self._file_name)
        self._setupVariableWidget()
        self._setupBlocksWidget()
        self._layout.addStretch()

        self._variable.currentIndexChanged.connect(self.onVariableChanged)

    def _setupVariableWidget(self):
        var_info = self._reader.getVariableInfo()

        self._variable = QComboBox()
        for vi in var_info:
            self._variable.addItem(vi.name, vi)
        self._variable.addItem("Block colors", None)
        self._layout.addWidget(self._variable)

    def _setupBlocksWidget(self):
        self._lbl_blocks = QLabel("Blocks")
        self._layout.addWidget(self._lbl_blocks)
        self._block_model = QStandardItemModel()
        self._block_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._block_model.itemChanged.connect(self.onBlockChanged)
        self._blocks = QTreeView()
        self._blocks.setFixedHeight(200)
        self._blocks.setRootIsDecorated(False)
        self._blocks.setModel(self._block_model)
        self._blocks.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._blocks.setColumnWidth(0, 200)
        self._blocks.setColumnWidth(1, 20)
        self._blocks.setColumnWidth(2, 50)
        self._layout.addWidget(self._blocks)

    def _addBlock(self, row, binfo, clr_idx):
        si_name = QStandardItem()
        si_name.setText(binfo.name)
        si_name.setCheckable(True)
        si_name.setCheckState(Qt.Checked)
        si_name.setData(binfo)
        self._block_model.setItem(row, self.IDX_NAME, si_name)

        si_clr = QStandardItem()
        si_clr.setText('\u25a0')
        qcolor = self._colors[clr_idx]
        si_clr.setForeground(QBrush(qcolor))
        si_clr.setData(clr_idx)
        self._block_model.setItem(row, self.IDX_COLOR, si_clr)

        si_id = QStandardItem()
        si_id.setText(str(binfo.number))
        self._block_model.setItem(row, self.IDX_ID, si_id)

    def _buildVtkBlocksActor(self, binfo):
        if binfo.multiblock_index is not None:
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(self._reader.getVtkOutputPort())
            eb.AddIndex(binfo.multiblock_index)
            eb.Update()
            self._vtk_extract_block[binfo.number] = eb

            geometry = vtk.vtkCompositeDataGeometryFilter()
            geometry.SetInputConnection(0, eb.GetOutputPort(0))
            geometry.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(geometry.GetOutputPort())
        else:
            self._vtk_extract_block[binfo.number] = None

            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputConnection(0, self._reader.getVtkOutputPort())
            mapper.ScalarVisibilityOff()

        mapper.InterpolateScalarsBeforeMappingOn()
        mapper.SetLookupTable(self._vtk_lut)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.VisibilityOn()
        self._block_actors[binfo.number] = actor

        return actor

    def buildVtkActor(self):
        self._buildLookupTable()

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

            row = self._block_model.rowCount()
            self._addBlock(row, binfo, clr_idx)

    def _buildLookupTable(self):
        self._vtk_lut = vtk.vtkLookupTable()
        self._vtk_lut.SetTableRange(0, 1)
        self._vtk_lut.SetHueRange(2. / 3., 0)
        self._vtk_lut.SetSaturationRange(1, 1)
        self._vtk_lut.SetValueRange(1, 1)
        self._vtk_lut.SetNumberOfColors(256)
        self._vtk_lut.Build()

    def getLookupTable(self):
        return self._vtk_lut

    def onBlockChanged(self, item):
        if item.column() == self.IDX_NAME:
            visible = item.checkState() == Qt.Checked
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
            range = self._getVariableValuesRange(vinfo)
            for actor in self._block_actors.values():
                mapper = actor.GetMapper()
                mapper.ScalarVisibilityOn()
                mapper.SelectColorArray(vinfo.name)
                if vinfo.object_type == Reader.VAR_NODAL:
                    mapper.SetScalarModeToUsePointFieldData()
                elif vinfo.object_type == Reader.VAR_CELL:
                    mapper.SetScalarModeToUseCellFieldData()
                mapper.InterpolateScalarsBeforeMappingOn()
                mapper.SetColorModeToMapScalars()
                mapper.SetScalarRange(range)

    def _getVariableValuesRange(self, vinfo):
        # NOTE: IDK if the data obtained via mapper.GetInputAsDataSet()
        # contains the full data set (i.e. interior values in 3D) or just
        # surface values (in 2D this is good)
        range = [None, None]
        for actor in self._block_actors.values():
            mapper = actor.GetMapper()
            data_set = mapper.GetInputAsDataSet()
            data = None
            if vinfo.object_type == Reader.VAR_NODAL:
                data = data_set.GetPointData()
            elif vinfo.object_type == Reader.VAR_CELL:
                data = data_set.GetCellData()
            if data is not None:
                r = data.GetScalars(vinfo.name).GetRange()
                range = self._expandRange(range, r)
        return range

    def _expandRange(self, range, r):
        if range[0] is None or r[0] < range[0]:
            range[0] = r[0]
        if range[1] is None or r[1] > range[1]:
            range[1] = r[1]
        return range

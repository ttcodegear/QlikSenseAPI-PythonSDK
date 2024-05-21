import math #, asyncio, time
from qlik_sdk import (Config, AuthType, Qlik)
from qlik_sdk.apis.Qix import (
  FieldValue,
  GenericObjectProperties,
  NxInfo,
  ListObjectDef,
  HyperCubeDef,
  NxDimension,
  NxMeasure,
  NxInlineDimensionDef,
  NxInlineMeasureDef,
  FieldAttributes,
  SortCriteria,
  ValueExpr,
  NxPage
)

host = "https://xxxx.yy.qlikcloud.com"
api_key = "eyJhbGc...."
config = Config(host=host, auth_type=AuthType.APIKey, api_key=api_key)
qlik = Qlik(config)

appid = '72a3da4b-1093-4c4c-840d-1ee44fbcbb91'
app = qlik.apps.get(appid)
app.open(qNoData = False)
try:
  field = app.get_field('支店名')
  select_ok = field.select_values([FieldValue(qText = '関東支店'), FieldValue(qText = '関西支店')])
  #print(select_ok)

  listobject_def = GenericObjectProperties(
    qInfo = NxInfo(
      qType = 'my-list-object'
    ),
    qListObjectDef = ListObjectDef(
      qDef = NxInlineDimensionDef(
        qFieldDefs = ["支店名"],
        qFieldLabels = ["支店名"],
        qSortCriterias = [SortCriteria(qSortByLoadOrder = 1)]
      ),
      qFrequencyMode = "NX_FREQUENCY_VALUE",
      qShowAlternatives = True
    )
  )
  lo_hypercube = app.create_session_object(listobject_def)
  lo_layout = lo_hypercube.get_layout()
  lo_width = lo_layout.qListObject.qSize.qcx
  lo_height = 1 if lo_width==0 else math.floor(10000 / lo_width)
  lo_layout.qListObject.qDataPages = []
  def getAllList(w: int, h: int, lr: int) -> None:
    requestPage = [NxPage(qTop=lr, qLeft=0, qWidth=w, qHeight=h)]
    dataPages = lo_hypercube.get_list_object_data('/qListObjectDef', requestPage)
    lo_layout.qListObject.qDataPages.append(dataPages[0])
    n = len(dataPages[0].qMatrix)
    if lr + n >= lo_layout.qListObject.qSize.qcy:
      renderingList()
      return
    getAllList(w, h, lr + n)
  def renderingList() -> None:
    hc = lo_layout.qListObject
    allListPages = hc.qDataPages
    for p in allListPages:
      for r in range(len(p.qMatrix)):
        for c in range(len(p.qMatrix[r])):
          cell = p.qMatrix[r][c]
          field_data = str(cell.qElemNumber) + ','
          if cell.qState=='S':
            field_data += '(Selected)'
          if cell.qElemNumber == -2:
            field_data += '-'
          elif cell.qNum is not None and not cell.qNum == 'NaN':
            field_data += str(cell.qNum)
          elif cell.qText is not None:
            field_data += cell.qText
          else:
            field_data += ''
          print(field_data)
    return
  # Register an event listener for change events
  def listobjectChanged() -> None:
    print('listobject has beed changed.')
    #lo_layout = lo_hypercube.get_layout()
    #lo_layout.qListObject.qDataPages = []
    #getAllList(lo_width, lo_height, 0)
    return
  lo_hypercube.on(
    event_name = 'changed',
    listener = listobjectChanged
  )
  getAllList(lo_width, lo_height, 0)

  hypercube_def = GenericObjectProperties(
    qInfo = NxInfo(
      qType = 'my-straight-hypercube'
    ),
    qHyperCubeDef = HyperCubeDef(
      qDimensions = [NxDimension(
        qDef = NxInlineDimensionDef(
          qFieldDefs = ["営業員名"],
          qFieldLabels = ["営業員名"]
        ),
        qNullSuppression = True
      )],
      qMeasures = [NxMeasure(
        qDef = NxInlineMeasureDef(
          qDef = 'Sum([販売価格])',
          qLabel = '実績',
          qNumFormat = FieldAttributes(qType = "MONEY", qUseThou = 1, qThou = ',')
        ),
        qSortBy = SortCriteria(
          qSortByState = 0,
          qSortByFrequency = 0,
          qSortByNumeric = -1, # ソート: 0=無し, 1=昇順, -1=降順
          qSortByAscii = 0,
          qSortByLoadOrder = 0,
          qSortByExpression = 0,
          qExpression = ValueExpr(qv = ' ')
        )
      )],
      qSuppressZero = False,
      qSuppressMissing = False,
      qMode = "DATA_MODE_STRAIGHT",
      qInterColumnSortOrder = [1,0], # ソート順: 1=実績, 0=営業員名
      qStateName = "$"
    )
  )
  hc_hypercube = app.create_session_object(hypercube_def)
  hc_layout = hc_hypercube.get_layout()
  hc_width = hc_layout.qHyperCube.qSize.qcx
  hc_height = 1 if hc_width==0 else math.floor(10000 / hc_width)
  hc_layout.qHyperCube.qDataPages = []
  def getAllData(w: int, h: int, lr: int) -> None:
    requestPage = [NxPage(qTop=lr, qLeft=0, qWidth=w, qHeight=h)]
    dataPages = hc_hypercube.get_hyper_cube_data('/qHyperCubeDef', requestPage)
    hc_layout.qHyperCube.qDataPages.append(dataPages[0])
    n = len(dataPages[0].qMatrix)
    if lr + n >= hc_layout.qHyperCube.qSize.qcy:
      renderingHyperCube()
      return
    getAllData(w, h, lr + n)
  def renderingHyperCube() -> None:
    hc = hc_layout.qHyperCube
    allListPages = hc.qDataPages
    for p in allListPages:
      for r in range(len(p.qMatrix)):
        for c in range(len(p.qMatrix[r])):
          cell = p.qMatrix[r][c]
          field_data = ''
          if cell.qElemNumber == -2:
            field_data += '-'
          elif cell.qText is not None:
            field_data += cell.qText
          elif cell.qNum is not None:
            field_data += str(cell.qNum)
          else:
            field_data += ''
          print(field_data)
    return
  # Register an event listener for change events
  def hypercubeChanged() -> None:
    print('hypercube has beed changed.')
    #hc_layout = hc_hypercube.get_layout()
    #hc_layout.qHyperCube.qDataPages = []
    #getAllList(hc_width, hc_height, 0)
    return
  hc_hypercube.on(
    event_name = 'changed',
    listener = hypercubeChanged
  )
  getAllData(hc_width, hc_height, 0)

  #testok = field.select_values([FieldValue(qText = '関東支店')])
  #print(testok)
  #time.sleep(10)
except Exception as e:
  print(e)
finally:
  app.close()

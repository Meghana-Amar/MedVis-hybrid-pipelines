import vtk


def Aneurysm():
  #test
  #print vtk.vtkVersion().GetVTKVersion()
  print("start test")
  #reader = vtk.vtkDICOMImageReader()
  #reader.SetFileName(r"image_0")
  reader = vtk.vtkXMLImageDataReader()
  reader.SetFileName(r"aneurysm.vti")
  reader.Update()
  
  data = reader.GetOutput()
  maths = vtk.vtkImageMathematics()
  maths.SetInputConnection(reader.GetOutputPort())
  maths.SetConstantC(1024)
  maths.SetOperationToAddConstant()
  maths.Update()
  m = maths.GetOutput()
  range = m.GetScalarRange()
  print (range)
  unsg = vtk.vtkImageShiftScale()
  unsg.SetInputConnection(maths.GetOutputPort())
  unsg.SetOutputScalarTypeToUnsignedShort()
  unsg.Update()
  
#------------ 1D transfer function ----------------------------------------------------
  otf = vtk.vtkPiecewiseFunction() #opacity
  ctf = vtk.vtkColorTransferFunction() #colours
  gtf = vtk.vtkPiecewiseFunction() #gradient
#opacities
  otf.RemoveAllPoints()
  otf.AddPoint(range[0]+100, 0.0)
  otf.AddPoint((range[0]+range[1])/2, 0.3)
  otf.AddPoint(range[1], 1.0)

#colours
#https://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html#aa3bd656f032908593e89f749796ed786
  ctf.RemoveAllPoints()
  ctf.AddRGBPoint(range[0], 1, 1, 0)
  ctf.AddRGBPoint(1250, 0.65, 0.7, 1.0)  
  ctf.AddRGBPoint(range[1], 0, 0, 1)
#gradients
  gtf.RemoveAllPoints()
  gtf.AddPoint(range[0], 0.0)
  gtf.AddPoint((range[0]+range[1])/2, 0.8)
  gtf.AddPoint(range[1], 1)
#-----------------------------------------------------------------------------------------
#contourBone
  contourBone = vtk.vtkMarchingCubes()
  contourBone.SetInput(reader.GetOutput())
  contourBone.ComputeNormalsOn()
  contourBone.SetValue(0,ctx.field("Iso").value)
  geoVolumeBone = vtk.vtkGeometryFilter()
  geoVolumeBone.SetInput(contourBone.GetOutput())
  geoBoneMapper = vtk.vtkPolyDataMapper()
  geoBoneMapper.SetInput(geoVolumeBone.GetOutput())
  geoBoneMapper.ScalarVisibilityOff()
#-------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------
  propVolume = vtk.vtkVolumeProperty()
  propVolume.ShadeOn()
  propVolume.SetColor(ctf)
  propVolume.SetScalarOpacity(otf)
  propVolume.SetGradientOpacity(gtf) #enable gradient
  propVolume.SetInterpolationTypeToLinear()
  prop = vtk.vtkProperty()
  prop.SetColor(0.5,0.5,0.5)
  prop.SetEdgeVisibility(1)
  prop.SetLineWidth(5)
  rayCast = vtk.vtkVolumeRayCastCompositeFunction()
  rayCast.SetCompositeMethodToInterpolateFirst()
#rayCast.SetCompositeMethodToClassifyFirst()
  rayCast2 = vtk.vtkVolumeRayCastIsosurfaceFunction()
  rayCast2.SetIsoValue(1500)
  rayCast3 = vtk.vtkVolumeRayCastMIPFunction()
  mapperVolume = vtk.vtkVolumeRayCastMapper()
  mapperVolume.SetVolumeRayCastFunction(rayCast3)
  mapperVolume.SetInputConnection(unsg.GetOutputPort()) 

  actorBone = vtk.vtkLODActor()
  actorBone.SetNumberOfCloudPoints(1000000)
  actorBone.SetMapper(geoBoneMapper)
  actorBone.GetProperty().SetColor(ctx.field("color").value)

  actorVolume = vtk.vtkVolume()
  actorVolume.SetMapper(mapperVolume)
  actorVolume.SetProperty(propVolume)
  planeWidget = vtk.vtkImagePlaneWidget()
  planeWidget.SetInput(reader.GetOutput()) 
  planeWidget.SetPlaneOrientationToXAxes()
  planeWidget.SetSliceIndex(reader.GetOutput().GetDimensions()[0]/2)
  planeWidget.TextureVisibilityOff()
#planeWidget.SetSliceIndex(200)
#planeWidget.SetOrigin(0.0,0.0,0.0)
#planeWidget.SetSlicePosition(200)
  print(reader.GetOutput().GetDimensions())
  print("index: "+str(planeWidget.GetSliceIndex()))
  print("pos: "+str(planeWidget.GetSlicePosition()))
  planeWidget1 = vtk.vtkImagePlaneWidget()
  planeWidget1.SetInput(reader.GetOutput()) 
  planeWidget1.SetPlaneOrientationToYAxes()
  planeWidget1.SetSliceIndex(reader.GetOutput().GetDimensions()[0]/2)
  planeWidget1.TextureVisibilityOff()
#planeWidget.SetSliceIndex(200)
#planeWidget.SetOrigin(0.0,0.0,0.0)
#planeWidget.SetSlicePosition(200)
  print(reader.GetOutput().GetDimensions())
  print("index: "+str(planeWidget1.GetSliceIndex()))
  print("pos: "+str(planeWidget1.GetSlicePosition()))
  planeWidget2 = vtk.vtkImagePlaneWidget()
  planeWidget2.SetInput(reader.GetOutput()) 
  planeWidget2.SetPlaneOrientationToZAxes()
  planeWidget2.SetSliceIndex(reader.GetOutput().GetDimensions()[0]/2)
  planeWidget2.TextureVisibilityOff()
#planeWidget.SetSliceIndex(200)
#planeWidget.SetOrigin(0.0,0.0,0.0)
#planeWidget.SetSlicePosition(200)
  print(reader.GetOutput().GetDimensions())
  print("index: "+str(planeWidget2.GetSliceIndex()))
  print("pos: "+str(planeWidget2.GetSlicePosition()))
#rendering
  renderer = vtk.vtkRenderer()
  renderWindow = vtk.vtkRenderWindow()
  renderWindow.AddRenderer(renderer)

  
  silhouette = vtk.vtkPolyDataSilhouette()
  silhouette.SetInput(geoVolumeBone.GetOutput())
  silhouette.SetCamera(renderer.GetActiveCamera())
  silhouette.SetEnableFeatureAngle(0)
  silhouette.SetBorderEdges(True)
  silhouette.BorderEdgesOn()

  silhouetteMapper = vtk.vtkPolyDataMapper()
  silhouetteMapper.SetInput(silhouette.GetOutput())
  silhouetteMapper.ScalarVisibilityOff()

  actorSilhouette = vtk.vtkLODActor()
  actorSilhouette.SetProperty(prop)
  actorSilhouette.SetMapper(silhouetteMapper)


  renderer.AddActor(actorVolume)
  renderer.AddActor(actorBone)
  renderer.AddActor(actorSilhouette)
  renderer.ResetCamera()
  renderer.GetActiveCamera().Azimuth(30)
  renderer.GetActiveCamera().Elevation(30)
  renderer.GetActiveCamera().Dolly(1.5)
  iren = vtk.vtkRenderWindowInteractor()
  iren.SetRenderWindow(renderWindow)
  iren.Initialize()
  planeWidget.SetInteractor(iren)# render window interactor
  planeWidget.PlaceWidget()
  planeWidget.On()
  planeWidget1.SetInteractor(iren)# render window interactor
  planeWidget1.PlaceWidget()
  planeWidget1.On()
  planeWidget2.SetInteractor(iren)# render window interactor
  planeWidget2.PlaceWidget()
  planeWidget2.On()
  renderWindow.Render()
  iren.Start()

def changeColor(fld):
  polydataActor=renderer.AddActor("actorBone")
  polydataActor.GetProperty().SetColor(fld.value)
  actorBone.setObject(polydataActor)
  
def changeIso(fld):
  contourBone.SetValue(0,ctx.field("Iso").value)


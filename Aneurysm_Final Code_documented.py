# This is the python script to generate a visualisation in the rendering window
# by the combination of 3 different visualisation pipelines - Surface Rendering using
# Marching Cubes algorithm, Direct Volume Rendering using MIP compositing function
# and Silhouette based non photorealisitc rendering. To give more anatomical context to 
# the users anatomical planes have been added to the rendering window which gives the users
# information about the location and the orientation of an object of interest in the rendering
# This code also enables the users to interactively select the color of the iso-surface 
# to make the visualisation more appealing to them and they can select different iso-surface 
# values as well.


import vtk


def Aneurysm():

# Code module to read the input data 
  print("start test")
  reader = vtk.vtkXMLImageDataReader()
  reader.SetFileName(r"aneurysm.vti")
  reader.Update()
  
# Reading the input data file, performing mathematical shift to make the data values positive and updating the image  
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
# Code moduole used to make compute the iso-surface using the marching cubes algorithm
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
# Code module used to generate the 3D module and set the properties of the volume to be rendered
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

# Creating the actor which would render the iso-surface using Marching Cube Algorithm in the renderer
  actorBone = vtk.vtkLODActor()
  actorBone.SetNumberOfCloudPoints(1000000)
  actorBone.SetMapper(geoBoneMapper)
  actorBone.GetProperty().SetColor(ctx.field("color").value)
# Creating the actor which would render the volume using MIP compositing function in the renderer
  actorVolume = vtk.vtkVolume()
  actorVolume.SetMapper(mapperVolume)
  actorVolume.SetProperty(propVolume)
  
  
# Generation of the anatomical axis to improve the imformation content of the rendering  
  planeWidget = vtk.vtkImagePlaneWidget()
  planeWidget.SetInput(reader.GetOutput()) 
  planeWidget.SetPlaneOrientationToXAxes()
  planeWidget.SetSliceIndex(reader.GetOutput().GetDimensions()[0]/2)
  planeWidget.TextureVisibilityOff()
  print(reader.GetOutput().GetDimensions())
  print("index: "+str(planeWidget.GetSliceIndex()))
  print("pos: "+str(planeWidget.GetSlicePosition()))
  planeWidget1 = vtk.vtkImagePlaneWidget()
  planeWidget1.SetInput(reader.GetOutput()) 
  planeWidget1.SetPlaneOrientationToYAxes()
  planeWidget1.SetSliceIndex(reader.GetOutput().GetDimensions()[0]/2)
  planeWidget1.TextureVisibilityOff()
  print(reader.GetOutput().GetDimensions())
  print("index: "+str(planeWidget1.GetSliceIndex()))
  print("pos: "+str(planeWidget1.GetSlicePosition()))
  planeWidget2 = vtk.vtkImagePlaneWidget()
  planeWidget2.SetInput(reader.GetOutput()) 
  planeWidget2.SetPlaneOrientationToZAxes()
  planeWidget2.SetSliceIndex(reader.GetOutput().GetDimensions()[0]/2)
  planeWidget2.TextureVisibilityOff()
  print(reader.GetOutput().GetDimensions())
  print("index: "+str(planeWidget2.GetSliceIndex()))
  print("pos: "+str(planeWidget2.GetSlicePosition()))


# Creating an object renderer in which the final rendering is to be done
  renderer = vtk.vtkRenderer()
  renderWindow = vtk.vtkRenderWindow()
  renderWindow.AddRenderer(renderer)

# Creating Silhoeutte based non photorealistic visualisation  
  silhouette = vtk.vtkPolyDataSilhouette()
  silhouette.SetInput(geoVolumeBone.GetOutput())
  silhouette.SetCamera(renderer.GetActiveCamera())
  silhouette.SetEnableFeatureAngle(0)
  silhouette.SetBorderEdges(True)
  silhouette.BorderEdgesOn()

# Mapping the Silhouette polydata 
  silhouetteMapper = vtk.vtkPolyDataMapper()
  silhouetteMapper.SetInput(silhouette.GetOutput())
  silhouetteMapper.ScalarVisibilityOff()

# Creating an actor to represent the rendering of the silhouette in the final rendering window
  actorSilhouette = vtk.vtkLODActor()
  actorSilhouette.SetProperty(prop)
  actorSilhouette.SetMapper(silhouetteMapper)

# adding actors and the anatomical axis to the final rendering window
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

# Making a function to enbale the user to interactively change the color of the surface rendering
def changeColor(fld):
  polydataActor=renderer.AddActor("actorBone")
  polydataActor.GetProperty().SetColor(fld.value)
  actorBone.setObject(polydataActor)
  
# Making a function which enables the user to interactively change the iso-surface a user wants to view  
def changeIso(fld):
  contourBone.SetValue(0,ctx.field("Iso").value)


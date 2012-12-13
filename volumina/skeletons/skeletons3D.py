import vtk

from numpy import asarray as A
from volumina.skeletons.frustum import cut

class Skeletons3D:
    def __init__(self, skeletons, view3D):
        self._skeletons = skeletons
        self._view3D = view3D       
        
        self._node2view = dict()
        self._edge2view = dict()
       
    def _cubeBoundsFromNode(self, cube, node):
        cube.SetBounds(node.pos[0]-node.shape[0]/2.0, node.pos[0]+node.shape[0]/2.0, \
                       node.pos[1]-node.shape[1]/2.0, node.pos[1]+node.shape[1]/2.0, \
                       node.pos[2]-node.shape[2]/2.0, node.pos[2]+node.shape[2]/2.0)
        
    def update(self):
        for n in self._skeletons._nodes:
            if n not in self._node2view:
                cube = vtk.vtkCubeSource()
                cubeMapper = vtk.vtkPolyDataMapper()
                cubeMapper.SetInputConnection(cube.GetOutputPort())
                cubeActor = vtk.vtkActor()
                cubeActor.SetMapper(cubeMapper)
                #cubeActor.GetProperty().SetRepresentationToWireframe()
                #cubeActor.GetProperty().SetColor(*color)
                self._view3D.qvtk.renderer.AddActor(cubeActor)
                self._node2view[n] = (cube, cubeActor)
            
            cube, cubeActor = self._node2view[n]
            
            self._cubeBoundsFromNode(cube, n)
            if n.isSelected():
                cubeActor.GetProperty().SetColor(0,1,0)
            else:
                cubeActor.GetProperty().SetColor(0,0,0)
        
        for e in self._skeletons._edges:
            if e not in self._edge2view:
                '''
                print "add edge", e
                source = vtk.vtkLineSource()
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(source.GetOutputPort())
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(0,0,0)
                self._view3D.qvtk.renderer.AddActor(actor)
                self._edge2view[e] = source
                '''
                
                pointsSource = vtk.vtkProgrammableSource()
                
                def makePoints():
                    c1 = self._node2view[e[0]][0]
                    c2 = self._node2view[e[1]][0]
                    l = A(c2.GetCenter()) - A(c1.GetCenter())
                    p1 = cut(c1, l)
                    p2 = cut(c2, l)
                    thePoints = p1+p2
        
                    points = vtk.vtkPoints()
                    for pt in thePoints:
                        points.InsertNextPoint(*pt)
                    
                    pointsSource.GetPolyDataOutput().SetPoints(points)
                
                pointsSource.SetExecuteMethod(makePoints) 
                
                delaunay = vtk.vtkDelaunay3D()
                delaunay.SetInputConnection(pointsSource.GetOutputPort())
                
                surfaceFilter = vtk.vtkDataSetSurfaceFilter()
                surfaceFilter.SetInputConnection(delaunay.GetOutputPort()) 
                
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(surfaceFilter.GetOutputPort())
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor((0,0,1))
                self._view3D.qvtk.renderer.AddActor(actor)
                
                self._edge2view[e] = pointsSource
           
            pointsSource = self._edge2view[e]
            pointsSource.Modified()
        
        self._view3D.qvtk.update()
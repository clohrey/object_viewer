import numpy as np
import math
from file_parser import read_obj

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

posX, posY = 0.0, 0.0
vertex_buffer_object = None

DEFAULT_COLOR = (0.2, 0.8, 0.4, 0.0)
WIDTH, HEIGHT = 500, 500

RED = (1.0, 0.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0, 0.0)
YELLOW = (1.0, 1.0, 0.0, 0.0)
BLACK = (0.0, 0.0, 0.0, 0.0)
WHITE = (1.0, 1.0, 1.0, 0.0)

center = None
field_of_view = 45.0
near = 0.1
far = 100.0
display_mode = 's'
projection_mode = 'p'
light = None
data_for_vbo = None
scale_factor = 0
model_color = BLACK

start_p = None
# https://docs.scipy.org/doc/numpy-1.12.0/reference/generated/numpy.identity.html
act_ori = np.identity(4)
angle = 0
axis = [0, 0, 1]
do_rotation = False
zoomFactor, zoomMin, zoomMax = 1.0, 0.5, 10.0


def generate_vbo_data(geo_vertices, vertex_normals, faces):
    data = []

    for face in faces:
        if not vertex_normals:
            normal = calculate_normal(geo_vertices, face)
        for vertex in face:
            v = vertex[0]
            vn = vertex[2]
            if vertex_normals:
                data.append(geo_vertices[v] + vertex_normals[vn])
            else:
                data.append(np.append(np.array(geo_vertices[v]), normal))
    return data


def calculate_normal(geo_vertices, face):
    a = geo_vertices[face[0][0]]
    b = geo_vertices[face[1][0]]
    c = geo_vertices[face[2][0]]
    return np.cross(np.subtract(b, a), np.subtract(c, a))


"""
if normals == []:
    noNormals = True
    for p in vertices:
        normals.append([0,0,0])

    #Normalen pro Face berechnen
    for face in faces:
        i, j, k = int(face[0])-1, int(face[1])-1,int(face[2])-1
        x = array(vertices[j]) - array(vertices[i])
        y = array(vertices[k]) - array(vertices[i])
        n = cross(x, y)

        normals[i] = [x + y for x, y in zip(normals[i], n)]
        normals[j] = [x + y for x, y in zip(normals[j], n)]
        normals[k] = [x + y for x, y in zip(normals[k], n)]
"""


def init_gl():
    global field_of_view, near, far, projection_mode
    aspect_ratio = float(WIDTH) / HEIGHT

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glClearColor(*WHITE)

    # https://www.opengl.org/discussion_boards/showthread.php/133880-Diference-between-GL_MODELVIEW-and-GL_PROJECTION
    # The projection matrix defines the properties of the camera that views the objects
    # in the world coordinate frame. Here you typically set the zoom factor, aspect ratio
    # and the near and far clipping planes.
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(field_of_view / zoomFactor, aspect_ratio, near, far)

    # https://www.opengl.org/discussion_boards/showthread.php/133880-Diference-between-GL_MODELVIEW-and-GL_PROJECTION
    # The modelview matrix defines how your objects are transformed
    # (meaning translation,rotation and scaling) in your world coordinate frame
    glMatrixMode(GL_MODELVIEW)
    glutPostRedisplay()


def init_geometry():
    # TODO: Nochmal drüber schauen!
    global vertex_buffer_object, scale_factor, center, light, data_for_vbo
    geo_vertices, vertex_normals, faces = read_obj(sys.argv[1])

    bounding_box = [list(map(min, zip(*geo_vertices))), list(map(max, zip(*geo_vertices)))]
    scale_factor = 2.0 / max([(x[1] - x[0]) for x in zip(*bounding_box)])
    center = [(x[0] + x[1]) / 2.0 for x in zip(*bounding_box)]
    light = [bounding_box[1][0] * 2, bounding_box[1][1] * 3, bounding_box[1][2] / 2]

    data_for_vbo = generate_vbo_data(geo_vertices, vertex_normals, faces)
    vertex_buffer_object = vbo.VBO(np.array(data_for_vbo, 'f'))


def display():
    """
    Zeichnet nacheinander jedes Frame
    Quelle: https://wiki.delphigl.com/
    """
    global data_for_vbo, vertex_buffer_object, center, display_mode
    # ModelView-Matrix-Modus aktivieren
    glMatrixMode(GL_MODELVIEW)

    # Leert die Buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Ersetzt die aktuelle Matrix durch die Einheitsmatrix
    glLoadIdentity()

    # Erstellt eine Betrachtungsmatrix aus einem Betrachterpunkt(CenterX, CenterY, CenterZ)
    gluLookAt(-2, 0, 4, 0, 0, 0, 0, 1, 0)

    # Vertex Buffer Object rendern
    vertex_buffer_object.bind()

    # Werte aus Folie 193
    # config zum Lesen der Vertices und Pointer auf VBO's bzw. Normalen
    glVertexPointer(3, GL_FLOAT, 24, vertex_buffer_object)
    glNormalPointer(GL_FLOAT, 24, vertex_buffer_object + 12)

    # Bewegt den Koordinatenursprung in den Punkt(posX, posY, 0.0)
    glTranslate(posX, posY, 0.0)

    matrix = act_ori * rotate(angle, axis)
    glMultMatrixf(matrix.tolist())

    # Folie 193, Verzerrung bzw. Spiegelung der Koordinatensystems
    glScale(scale_factor, scale_factor, scale_factor)
    glTranslate(-center[0], -center[1], -center[2])

    # Setzt Farbe des anzuzeigenden Objektes
    glColor(model_color)

    if display_mode == 's':
        # Folie 193
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        # Wenn aktiviert werden Tiefenvergleiche getätigt
        # und der Tiefenpuffer (z-Buffer) aktualisiert.
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glCullFace(GL_BACK)
        glLight(GL_LIGHT0, GL_POSITION, light)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(data_for_vbo))
    elif display_mode == 'w':
        # Polygon-Netz
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_NORMALIZE)
        glDisable(GL_COLOR_MATERIAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        # https://wiki.delphigl.com/index.php/glDrawArrays
        glDrawArrays(GL_TRIANGLES, 0, len(data_for_vbo))

    vertex_buffer_object.unbind()
    # Back zu Front Buffer swappen für Anzeige
    glutSwapBuffers()


def key_events(key, filler1, filler2):
    global display_mode, model_color

    key = key.decode("utf-8")

    if key == 'w':
        if glutGetModifiers() == GLUT_ACTIVE_ALT:
            glClearColor(*WHITE)
        else:
            model_color = WHITE
        glutPostRedisplay()

    if key == 'd':
        if display_mode == 's':
            display_mode = 'w'
            glutPostRedisplay()
        elif display_mode == 'w':
            display_mode = 's'
            glutPostRedisplay()


def mouse_button_pressed(button, state, x, y):
    # https://www.opengl.org/resources/libraries/glut/spec3/node50.html
    # Folie 195
    global start_p, act_ori, angle, do_rotation
    r = min(WIDTH, HEIGHT)/2.0

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            do_rotation = True
            start_p = project_on_sphere(x, y, r)
        if state == GLUT_UP:
            do_rotation = False
            act_ori = act_ori*rotate(angle, axis)


def mouse_moved(x, y):
    global angle, axis, scale_factor, start_p
    if do_rotation:
        r = min(WIDTH, HEIGHT)/2.0
        move_p = project_on_sphere(x, y, r)
        # TODO: Hier eventuell nochmal checken ob start_p == move_p
        angle = math.acos(np.dot(start_p, move_p))
        axis = np.cross(start_p, move_p)
        glutPostRedisplay()


def project_on_sphere(x, y, r):
    # Arcball-Rotation Folie 195
    x, y = x - WIDTH / 2.0, HEIGHT / 2.0 - y
    a = min(r * r, x * x + y * y)
    z = math.sqrt(r * r - a)
    l = math.sqrt(x * x + y * y + z * z)
    return x/l, y/l, z/l


def rotate(angle, axis):
    # TODO: Hier vlt direkt auf global angle, axis zugreifen?
    # Rotationsberechnung Folie 195
    c, mc = math.cos(angle), 1 - math.cos(angle)
    s = math.sin(angle)
    l = math.sqrt(np.dot(np.array(axis), np.array(axis)))
    x, y, z = np.array(axis)/l
    r = np.matrix(
        [[x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
         [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
         [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
         [0, 0, 0, 1]])
    return r.transpose()





















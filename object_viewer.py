import numpy as np
import math
from file_parser import read_obj

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

pos_x, pos_y = 0.0, 0.0
vertex_buffer_object = None

DEFAULT_COLOR = (0.2, 0.8, 0.4, 0.0)
WIDTH, HEIGHT = 500, 500

RED = (1.0, 0.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0, 0.0)
YELLOW = (1.0, 1.0, 0.0, 0.0)
BLACK = (0.0, 0.0, 0.0, 0.0)
WHITE = (1.0, 1.0, 1.0, 0.0)
model_color = WHITE
shadow_color = (0.05, 0.05, 0.05, 0.0)
background_color = WHITE

center = None
light = None
data_for_vbo = None
start_p = None

field_of_view = 45.0
near = 0.1
far = 100.0
# https://docs.scipy.org/doc/numpy-1.12.0/reference/generated/numpy.identity.html
act_ori = np.identity(4)
angle = 0
axis = [0, 0, 1]
zoom_factor, zoom_min, zoom_max = 1.0, 0.5, 10.0
scale_factor = 0

display_mode = 's'
projection_mode = 'p'
rotation_mode = False
shadow_mode = True
resize_mode = False
shifting_mode = False
zooming_mode = False

old_pos_x, old_pos_y = None, None

bounding_box = []


def normalize(a):
    div = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
    if div:
        a[0] = a[0] / div
        a[1] = a[1] / div
        a[2] = a[2] / div
    return a


def generate_vbo_data(geo_vertices, vertex_normals, faces):
    data = []

    if not vertex_normals:
        [vertex_normals.append([0, 0, 0]) for x in geo_vertices]
        vertex_normals = calculate_normals(geo_vertices, faces, vertex_normals)
        for i in range(len(faces)):
            for f in faces[i]:
                data.append(geo_vertices[f[0]] + normalize(vertex_normals[f[0]]))
        return data
    else:
        for face in faces:
            for vertex in face:
                v = vertex[0]
                vn = vertex[2]
                data.append(geo_vertices[v] + vertex_normals[vn])
        return data


def calculate_normals(geo_vertices, faces, vertex_normals):
    for face in faces:
        a, b, c = int(face[0][0]), int(face[1][0]), int(face[2][0])
        x = np.array(geo_vertices[b]) - np.array(geo_vertices[a])
        y = np.array(geo_vertices[c]) - np.array(geo_vertices[a])
        normal = np.cross(x, y)

        vertex_normals[a] = [x + y for x, y in zip(vertex_normals[a], normal)]
        vertex_normals[b] = [x + y for x, y in zip(vertex_normals[b], normal)]
        vertex_normals[c] = [x + y for x, y in zip(vertex_normals[c], normal)]
    return vertex_normals


def init_gl():
    global field_of_view, near, far, projection_mode

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glClearColor(*background_color)

    change_projection()


def init_geometry():
    global vertex_buffer_object, scale_factor, center, light, data_for_vbo, bounding_box
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

    glClearColor(*background_color)

    # Ersetzt die aktuelle Matrix durch die Einheitsmatrix
    glLoadIdentity()

    # Erstellt eine Betrachtungsmatrix aus einem Betrachterpunkt(CenterX, CenterY, CenterZ)
    gluLookAt(0, 0, 4, 0, 0, 0, 0, 1.0, 0)

    # Vertex Buffer Object rendern
    vertex_buffer_object.bind()

    # Werte aus Folie 193
    # config zum Lesen der Vertices und Pointer auf VBO's bzw. Normalen
    glVertexPointer(3, GL_FLOAT, 24, vertex_buffer_object)
    glNormalPointer(GL_FLOAT, 24, vertex_buffer_object + 12)

    # Bewegt den Koordinatenursprung in den Punkt(posX, posY, 0.0)
    glTranslatef(pos_x, pos_y, 0.0)

    matrix = act_ori * rotate()
    glMultMatrixf(matrix.tolist())

    # Folie 193, Verzerrung bzw. Spiegelung der Koordinatensystems
    glScalef(scale_factor, scale_factor, scale_factor)
    glTranslatef(-center[0], -center[1], -center[2])

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
        # https://wiki.delphigl.com/index.php/glCullFace
        # legt fest welche Flächen mittels Backface Culling
        # vom Zeichnen ausgeschlossen werden sollen.
        glCullFace(GL_BACK)
        glLight(GL_LIGHT0, GL_POSITION, light)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDrawArrays(GL_TRIANGLES, 0, len(data_for_vbo))
        if shadow_mode:
            shadow()
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
        if shadow_mode:
            shadow()

    vertex_buffer_object.unbind()
    # Back zu Front Buffer swappen für Anzeige
    glutSwapBuffers()


def key_events(key, filler1, filler2):
    global display_mode, model_color, shadow_mode, background_color, projection_mode

    key = key.decode("utf-8")

    if key == 'w':
        model_color = WHITE

    if key == 's':
        model_color = BLACK

    if key == 'd':
        if display_mode == 's':
            display_mode = 'w'
        elif display_mode == 'w':
            display_mode = 's'

    if key == 'o':
        projection_mode = 'o'
        change_projection()

    if key == 'p':
        projection_mode = 'p'
        change_projection()

    if key == 'h':
        shadow_mode ^= 1

    if key == 'r':
        model_color = RED

    if key == 'g':
        model_color = YELLOW

    if key == 'b':
        model_color = BLUE

    if key == 'S':
        background_color = BLACK

    if key == 'W':
        background_color = WHITE

    if key == 'R':
        background_color = RED

    if key == 'B':
        background_color = BLUE

    if key == 'G':
        background_color = YELLOW

    glutPostRedisplay()


def mouse_button_pressed(button, state, x, y):
    # https://www.opengl.org/resources/libraries/glut/spec3/node50.html
    # Folie 195
    global start_p, act_ori, angle, rotation_mode, shifting_mode, zooming_mode, old_pos_x, old_pos_y

    if state == GLUT_UP:
        old_pos_x = None
        old_pos_y = None

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            r = min(WIDTH, HEIGHT) / 2.0
            rotation_mode = True
            start_p = project_on_sphere(x, y, r)
        if state == GLUT_UP:
            act_ori = act_ori * rotate()
            rotation_mode = False
            angle = 0

    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            shifting_mode = True
        if state == GLUT_UP:
            shifting_mode = False

    if button == GLUT_MIDDLE_BUTTON:
        if state == GLUT_DOWN:
            zooming_mode = True
        if state == GLUT_UP:
            zooming_mode = False


def mouse_moved(x, y):
    global angle, axis, scale_factor, shifting_mode, start_p
    global pos_x, pos_y, old_pos_x, old_pos_y, zoom_factor, zoom_min, zoom_max
    delta_x = 0
    delta_y = 0

    if rotation_mode:
        r = min(WIDTH, HEIGHT) / 2.0
        move_p = project_on_sphere(x, y, r)
        if start_p == move_p:
            return
        angle = math.acos(np.dot(start_p, move_p))
        axis = np.cross(start_p, move_p)
        glutPostRedisplay()

    if old_pos_x:
        delta_x = x - old_pos_x
    if old_pos_y:
        delta_y = y - old_pos_y

    # Setzt neue PosX PosY für display()
    if shifting_mode:
        scale = float(WIDTH) / 2.0
        if delta_x:
            pos_x += delta_x / scale
        if delta_y:
            pos_y -= delta_y / scale
        glutPostRedisplay()

    if zooming_mode:
        z_scale = float(HEIGHT) / 10
        if delta_y != 0:
            zoom_factor -= (delta_y / z_scale)
            if zoom_factor < zoom_min:
                zoom_factor = zoom_min
            if zoom_factor > zoom_max:
                zoom_factor = zoom_max
            change_projection()

    old_pos_x = x
    old_pos_y = y


def project_on_sphere(x, y, r):
    # Arcball-Rotation Folie 195
    x = x - WIDTH / 2.0
    y = HEIGHT / 2.0 - y
    a = min(r * r, x * x + y * y)
    z = math.sqrt(r * r - a)
    l = math.sqrt(x * x + y * y + z * z)
    return x/l, y/l, z/l


def rotate():
    # Rotationsberechnung Folie 195
    global angle, axis
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


def shadow():
    global bounding_box, shadow_color, data_for_vbo
    # Arbeitsblatt 7
    glPushMatrix()  # Aktuellen Zustand merken
    p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0 / light[1], 0, 0, 1.0, 0, 0, 0, 0, 0]
    glTranslatef(light[0], light[1], light[2])
    glTranslatef(0.0, bounding_box[0][1], 0.0)
    glMultMatrixf(p)  # Projektion berechnen
    glTranslatef(0.0, -bounding_box[0][1], 0.0)
    glTranslatef(-light[0], -light[1], -light[2])
    glColor(*shadow_color)
    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
    glDisable(GL_COLOR_MATERIAL)
    glDisable(GL_NORMALIZE)
    glDrawArrays(GL_TRIANGLES, 0, len(data_for_vbo))
    glPopMatrix()  # Zustand wiederherstellen


def change_projection():
    global field_of_view, near, far
    aspect_ratio = float(WIDTH) / HEIGHT

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Wechsel zwischen orthogonaler und perspektivischer Projektion
    if projection_mode == 'o':
        # Folie 154
        glOrtho(
            -1.0 * aspect_ratio / zoom_factor,
            1.0 * aspect_ratio / zoom_factor,
            -1.0 / zoom_factor, 1.0 / zoom_factor,
            -10.0,
            10.0
                )
    elif projection_mode == 'p':
        gluPerspective(field_of_view / zoom_factor, aspect_ratio, near, far)

    glMatrixMode(GL_MODELVIEW)
    glutPostRedisplay()


def reshape(width, height):
    # Folie 166
    global WIDTH, HEIGHT

    if height == 0:
        height = 1
    WIDTH, HEIGHT = width, height
    glViewport(0, 0, int(width), int(height))
    change_projection()

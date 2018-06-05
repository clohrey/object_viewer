

def read_obj(path):
    """
    Reads and formats .obj files
    :param path:
    :return vertices, normals, faces in a list, read from object file:
    """
    geo_vertices = []
    vertex_normals = []
    faces = []

    for line in open(path):
        line = line.split()
        if line:
            if line[0] == 'v':
                geo_vertices.append(map(float, line[1:]))
            elif line[0] == 'vn':
                vertex_normals.append(map(float, line[1:]))
            elif line[0] == 'f':
                face = []
                """
                Nochmal ueberarbeiten!
                """
                for vertex_string in line[1:]:
                    vertex_list = vertex_string.split("/")
                    v = int(vertex_list[0]) - 1
                    t = -1
                    n = -1
                    if len(vertex_list) > 1 and vertex_list[1]:
                        t = int(vertex_list[1]) - 1
                    if len(vertex_list) > 2 and vertex_list[2]:
                        n = int(vertex_list[2]) - 1
                    face.append([v, t, n])
                faces.append(face)
    return geo_vertices, vertex_normals, faces

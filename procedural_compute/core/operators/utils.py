def _get_color_or_random(index, colors):
    if index < len(colors):
        return colors[index]
    return [random.random() for i in range(3)]


def _get_value_or_random(index, values):
    if index < len(values):
        return values[index]
    return random.random()


def _get_or_create_color_layer(mesh):
    return mesh.vertex_colors.get("Col") or mesh.vertex_colors.new()


def is_exploded(obj):
    mesh = obj.data
    n_vertices_expected = sum([p.loop_total for p in mesh.polygons])
    return n_vertices_expected == len(mesh.vertices)


def explode_polygons_to_mesh(obj, force=False):
    """ Explode all of the polygons to separate polygons without any linking
    vertices.  This is required for coloring the faces with vertex colors.
    """
    if (not force) and is_exploded(obj):
        print("Mesh is already exploded.  Not exploding faces.  Set kwarg force=True to bypass this.")
        return None

    print(f"Exploding faces on mesh for object: {obj.name}")
    vertices = []
    faces = []
    # Construct a new set of vertices and faces
    for poly in obj.data.polygons:
        face_start_index = len(vertices)
        # Add the vertices to the global list
        for vi in poly.vertices:
            vertices.append(obj.data.vertices[vi].co.to_tuple())
        # The face is just a straight range of these vertices
        faces.append([vi + face_start_index for vi in range(len(poly.vertices))])
    # Remove the original mesh
    obj.data.clear_geometry()
    # Add in the new vertices and faces
    obj.data.from_pydata(vertices, [], faces)


def color_polygons(obj, values = [], alpha=1.0, try_explode=True, force_explode=False):
    """ Color the polygons of an object on a colorscale
    NOTE: Use a ColorRamp in the ShadingEditor (nodes) to generate a colormap
    """
    mesh = obj.data

    # Check the number of faces match the number of values provided
    n_faces = len(mesh.polygons)
    if not len(values) == n_faces:
        raise ValueError("len(values) is not equal to number of faces")

    # Ensure the object is exploded into separate polygons (no common vertices)
    if try_explode:
        explode_polygons_to_mesh(obj, force=force_explode)

    # Create the color layer if it doesn't exist
    color_layer = _get_or_create_color_layer(mesh)
    # Color the polygons
    for polygon in mesh.polygons:
        # Get the color to use
        #value = _get_value_or_random(polygon.index, values)
        value = values[polygon.index]
        # Set the color for the vertices from the face color
        for vi in polygon.vertices:
            color_layer.data[vi].color = (value, value, value, alpha)


def print_poly_colors(obj):
    color_layer = obj.data.vertex_colors["Col"]
    for poly in obj.data.polygons:
        vertex_indices = [i for i in poly.vertices]
        print(f"POLYGON: {poly.index}: {vertex_indices}")
        for vi in poly.vertices:
            color_values = [i for i in color_layer.data[vi].color]
            print(f" - {vi}: {color_values}")

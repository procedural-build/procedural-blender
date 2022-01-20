import bpy


def drawCollectionTemplateList(layout, base, collection):
    """ Draws a UI TemplateList for a generic Blender collection type
    """
    row = layout.row()
    row.template_list("UI_UL_list", "custom", base, collection, base, "active_" + collection + "_index", rows=2)
    col = row.column(align=True)
    oType = getBaseObjType(base)

    bPath = base.path_from_id()
    if "[" in bPath:
        (p1, p2) = bPath.split("[")
        p2 = p2.split("]")[1]
        bPath = p1 + p2

    col.operator("scene.collectionops", icon='ZOOM_IN', text="").command = oType + "." + bPath + "." + collection + ".add"
    col.operator("scene.collectionops", icon='ZOOM_OUT', text="").command = oType + "." + bPath + "." + collection + ".remove"
    return None
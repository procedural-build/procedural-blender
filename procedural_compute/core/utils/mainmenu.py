import bpy

modulesList = ["ODS_Studio_SUN", "ODS_Studio_RAD", "ODS_Studio_CFD", "ODS_Studio_FDS", "ODS_Studio_EP", "ODS_Studio_LCA"]
menuList = ["SunPath", "Radiance", "CFD", "FDS", "Energy", "LCA"]


def makeTuple(s):
    return (s, s, s)


def get_items_list():
    items_list = []
    for m in range(len(modulesList)):
        module = modulesList[m]
        if module in bpy.context.preferences.addons.keys():
            #print("FOUND: ",module)
            items_list += [makeTuple(menuList[m])]
    return items_list


def add(module):
    items_list = get_items_list()
    #print("ADDING %s MODULE"%(module))
    m = modulesList.index(module)
    if not makeTuple(menuList[m]) in items_list:
        items_list += [makeTuple(menuList[m])]
    update_mainmenu(items_list)


def remove(module):
    #print("REMOVING %s MODULE"%(module))
    m = modulesList.index(module)
    items_list.remove(makeTuple(menuList[m]))
    update_mainmenu(items_list)

def mainmenu_loaded():
    from procedural_compute.core.properties import BM_SCENE_ODS
    return len(BM_SCENE_ODS.__annotations__['mainMenu'].keywords['items']) > 0

def update_mainmenu(items_list):
    if len(items_list) == 0:
        bpy.types.BM_SCENE_ODS.mainMenu = bpy.props.EnumProperty(
            name="mainMenu",
            items=items_list,
            description="ODS menu categories"
        )
    else:
        bpy.types.BM_SCENE_ODS.mainMenu = bpy.props.EnumProperty(
            name="mainMenu",
            items=items_list,
            description="ODS menu categories",
            default=items_list[0][0]
        )

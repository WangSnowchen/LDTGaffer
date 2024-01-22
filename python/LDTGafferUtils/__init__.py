import IECore
import Gaffer
import GafferScene
import GafferUI
import imath
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

import os

def registerAnnotation( menu):
    scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
    script = scriptWindow.scriptNode()
    mainWindow = GafferUI.ScriptWindow.acquire( script )

    selected = script.selection()
    if selected.size():
        current_annotation = Gaffer.Metadata.value(selected[0], "annotation:user:text")
        initial_text = current_annotation if current_annotation else ""
        d = GafferUI.TextInputDialogue( initialText=initial_text, title="Annotation", confirmLabel="Set" )
        c = GafferUI.ColorChooserDialogue( title="Select Color", color=imath.Color3f( 1 ) , cancelLabel="Cancel", confirmLabel="OK" )
        text = d.waitForText( parentWindow =  mainWindow )
        color = c.waitForColor( parentWindow =  mainWindow )
        for node in selected:
            if text:
                Gaffer.Metadata.registerValue(node, "annotation:user:text", text)
                Gaffer.Metadata.registerValue( node, 'annotation:user:color', imath.Color3f(color) )
            else:
                Gaffer.Metadata.deregisterValue(node, "annotation:user:text")
                Gaffer.Metadata.registerValue( node, 'annotation:user:color', imath.Color3f(color) )

def registerEditScopeIncludeInNavigationMenu( menu):
    scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
    script = scriptWindow.scriptNode()
    mainWindow = GafferUI.ScriptWindow.acquire( script )

    selected = script.selection()
    if selected.size():
        current_editScopeProcessorType = Gaffer.Metadata.value(selected[0], "editScope:includeInNavigationMenu")
        d = GafferUI.TextInputDialogue( initialText="LDT", title="Annotation", confirmLabel="Set" )
        text = d.waitForText( parentWindow =  mainWindow )
        for node in selected:
            if text:
                Gaffer.Metadata.registerValue(node, "editScope:includeInNavigationMenu", text)
            else:
                Gaffer.Metadata.deregisterValue(node, "editScope:includeInNavigationMenu")

def openThisFile_GRF( menu ):
    scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
    script = scriptWindow.scriptNode()
    FileName = script["fileName"].getValue()
    FileName = os.path.dirname(FileName)
    subprocess.run(['xdg-open', FileName])


def export_extension( menu ) :
	scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
	script = scriptWindow.scriptNode()
	path, bookmarks = GafferUI.FileMenu.__pathAndBookmarks( scriptWindow )

	dialogue = GafferUI.PathChooserDialogue( path, title="Save script", confirmLabel="Save", leaf=True, bookmarks=bookmarks )
	path = dialogue.waitForPath( parentWindow = scriptWindow )

	if not path :
		return

	path = str( path )

	script["fileName"].setValue( path )
	with GafferUI.ErrorDialogue.ErrorHandler( title = "Error Saving File", parentWindow = scriptWindow ) :

		scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
		Gaffer.ExtensionAlgo.exportExtension(
			os.path.splitext(os.path.basename(path))[0],	#PackageName
			script.selection(),							   	#Nodelist
			path
		)

def get_selected(single=True):
    selected_nodes = root.selection()
    if single:
        if len(selected_nodes) == 1:
            return selected_nodes[0]
        else:
            raise Exception(
                "Zero or More than 1 node selected"
            )
    else:
        return selected_nodes


class AttributesSearch():
    """
    Traverse the scene, and get a list of unique attribute values
    with the paths where they were found as:
        {'attr_value':['/obj1','obj2']}
    """

    attributes = {}

    def __init__(self, scene, path, object_attribute):
        """
        Traverse the scene, to get a list of unique attr values and its paths.
        {'attr_value':['/obj1','obj2']}

        Args:
            scene (node out plug): node out plug
            path (str): where to start the search as in "/"
            object_attribute (str): attribute name, for ie: "surfacing_project"
        """
        self.traverse_scene(scene, path, object_attribute)

    def traverse_scene(self, scene, path, object_attribute):
        """Traverse the scene recursively add add attr found to the list."""
        try:
            attribute_value = str(scene.attributes(path)[object_attribute])
            if attribute_value not in self.attributes.keys():
                self.attributes[attribute_value] = []
            self.attributes[attribute_value].append(path)
        except:
            pass
        for childName in scene.childNames(path):
            self.traverse_scene(scene, os.path.join(
                path, str(childName)), object_attribute)

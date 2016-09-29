#Author-
#Description-Copy Paste Components and bodies between documents.
# Author-Patrick Rainsberry
# Description-Directly publish to copyPaste

# Referenced heavily from: https://github.com/boboman/Octonomous/blob/master/Octonomous.py


import adsk.core, traceback
import adsk.fusion

from os.path import expanduser
import os

handlers = []

resultFilename = ''


# Creates directory and returns file name for settings file
def getFileName():

    # Get Home directory
    home = expanduser("~")
    home += '/copyPaste/'
    
    # Create if doesn't exist
    if not os.path.exists(home):
        os.makedirs(home)
    
    # Create file name in this path
    copyPasteFileName = home  + 'copyPaste.step'
    return copyPasteFileName


# Export an STL file of selection to local temp directory
def exportFile(tempComponent, filename):

    # Get the ExportManager from the active design.
    app = adsk.core.Application.get()
    design = app.activeProduct
    exportMgr = design.exportManager
    
    # Create export options for STL export    
    stepOptions = exportMgr.createSTEPExportOptions(filename, tempComponent)

    
    # Execute Export command
    exportMgr.execute(stepOptions)
    
    return filename

def getTempComponent(tempBodies):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    tempOccurance = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create()) 
    
    for body in tempBodies:
        body.copyToComponent(tempOccurance)
            
    return tempOccurance         
                
def pasteBodies(filename, pasteComponent):

    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
        
    # Get import manager
    importManager = app.importManager
    stpFileName = filename
    stpOptions = importManager.createSTEPImportOptions(stpFileName)
    
    temp2Occurence = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create()) 
    # Import step file to root component
    importManager.importToTarget(stpOptions, temp2Occurence.component)
    
    base_ = pasteComponent.features.baseFeatures.add()
    
    if base_.startEdit():
    
        for body in temp2Occurence.component.occurrences.item(0).component.bRepBodies:
            pasteComponent.bRepBodies.add(body, base_)
        base_.finishEdit()  
    
    temp2Occurence.deleteMe()
        
# Get the current values of the command inputs.
def getCopyInputs(inputs):
    try:
    
        selection_input = inputs.itemById('copySelectionInput')
        count = selection_input.selectionCount
        tempBodies = adsk.core.ObjectCollection.create()
    
        for i in range(0, count):
            body = selection_input.selection(i).entity
            tempBodies.add(body)
    
        return tempBodies
    except:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def getPasteInputs(inputs):
    
    try: 
        selection_input = inputs.itemById('pasteSelectionInput')
        pasteComponent = selection_input.selection(0).entity
        
        if pasteComponent.objectType == adsk.fusion.Occurrence.classType():
            pasteComponent = pasteComponent.component
 
        return pasteComponent
        
    except:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Define the event handler for when the copyPaste command is executed 
class FusionCopyExecutedEventHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        ui = []
        try:
            global resultFilename
            app = adsk.core.Application.get()
            ui  = app.userInterface

            # Get the inputs.
            inputs = args.command.commandInputs
            tempBodies = getCopyInputs(inputs)
            filename = getFileName()
            tempOccurance = getTempComponent(tempBodies)
            
            # Export the selected file as a step to temp directory            
            resultFilename = exportFile(tempOccurance.component, filename)
            tempOccurance.deleteMe()
            

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Define the event handler for when the copyPaste command is run by the user.
class FusionCopyCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        ui = []
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface

            # Connect to the command executed event.
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            onExecute = FusionCopyExecutedEventHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

            # Define the inputs.
            inputs = cmd.commandInputs
            

            selectionInput = inputs.addSelectionInput('copySelectionInput', 'Selection', 'Select the component to copy' )
#            selectionInput.addSelectionFilter('Occurrences')
#            selectionInput.addSelectionFilter('RootComponents')
            selectionInput.addSelectionFilter('SolidBodies')
            selectionInput.setSelectionLimits(0);
            
            cmd.commandCategoryName = 'fusionCopy'
            cmd.setDialogInitialSize(500, 300)
            cmd.setDialogMinimumSize(300, 300)

            cmd.okButtonText = 'Ok'
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Define the event handler for when the copyPaste command is executed 
class FusionPasteExecutedEventHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        ui = []
        try:
            global resultFilename
            app = adsk.core.Application.get()
            ui  = app.userInterface

            # Get the inputs.
            inputs = args.command.commandInputs
            pasteComponent = getPasteInputs(inputs)
            filename = getFileName()
            pasteBodies(filename, pasteComponent)
            


        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Define the event handler for when the copyPaste command is run by the user.
class FusionPasteCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        ui = []
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface

            # Connect to the command executed event.
            cmd = args.command
            cmd.isExecutedWhenPreEmpted = False
            
            onExecute = FusionPasteExecutedEventHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

            # Define the inputs.
            inputs = cmd.commandInputs
            

            selectionInput = inputs.addSelectionInput('pasteSelectionInput', 'Selection', 'Select the component to copy' )
            selectionInput.addSelectionFilter('Occurrences')
#            selectionInput.addSelectionFilter('RootComponents')
#            selectionInput.addSelectionFilter('SolidBodies')
            selectionInput.setSelectionLimits(1);
            
            cmd.commandCategoryName = 'fusionPaste'
            cmd.setDialogInitialSize(500, 300)
            cmd.setDialogMinimumSize(300, 300)

            cmd.okButtonText = 'Ok'
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
# Main Definition
def run(context):
    ui = None

    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        if ui.commandDefinitions.itemById('CopyButtonID'):
            ui.commandDefinitions.itemById('CopyButtonID').deleteMe()
            
        if ui.commandDefinitions.itemById('PasteButtonID'):
            ui.commandDefinitions.itemById('PasteButtonID').deleteMe()

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        FusionPasteButtonDef = cmdDefs.addButtonDefinition('PasteButtonID', 'Paste Bodies', 'tooltip', './resources')
        onPasteCreated = FusionPasteCreatedEventHandler()
        FusionPasteButtonDef.commandCreated.add(onPasteCreated)
        handlers.append(onPasteCreated)

        FusionCopyButtonDef = cmdDefs.addButtonDefinition('CopyButtonID', 'Copy Bodies', 'tooltip', './resources')
        onCopyCreated = FusionCopyCreatedEventHandler()
        FusionCopyButtonDef.commandCreated.add(onCopyCreated)
        handlers.append(onCopyCreated)
        
        # Find the "ADD-INS" panel for the solid and the surface workspaces.
        solidPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        surfacePanel = ui.allToolbarPanels.itemById('SurfaceScriptsAddinsPanel')
        
        # Add a button for the "Request Quotes" command into both panels.
        buttonControl1 = solidPanel.controls.addCommand(FusionCopyButtonDef, '', False)
        buttonControl2 = surfacePanel.controls.addCommand(FusionCopyButtonDef, '', False)
        buttonControl3 = solidPanel.controls.addCommand(FusionPasteButtonDef, '', False)
        buttonControl4 = surfacePanel.controls.addCommand(FusionPasteButtonDef, '', False)
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        if ui.commandDefinitions.itemById('CopyButtonID'):
            ui.commandDefinitions.itemById('CopyButtonID').deleteMe()
        if ui.commandDefinitions.itemById('PasteButtonID'):
            ui.commandDefinitions.itemById('PasteButtonID').deleteMe()   

        # Find the controls in the solid and surface panels and delete them.
        solidPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = solidPanel.controls.itemById('CopyButtonID')
        if cntrl:
            cntrl.deleteMe()
        cntrl = solidPanel.controls.itemById('PasteButtonID')
        if cntrl:
            cntrl.deleteMe()
        
        surfacePanel = ui.allToolbarPanels.itemById('SurfaceScriptsAddinsPanel')
        cntrl = surfacePanel.controls.itemById('PasteButtonID')
        if cntrl:
            cntrl.deleteMe()
        cntrl = surfacePanel.controls.itemById('CopyButtonID')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

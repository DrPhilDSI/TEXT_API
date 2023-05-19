# Author-
# Description-

import datetime
import time
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

SKETCH_NAME = 'Texty mc textface'

# current date

DATE = datetime.date.today()


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        rootComp = design.rootComponent
        sketch = rootComp.sketches.itemByName(SKETCH_NAME)

        if sketch is not None:
            sketch_Text = sketch.sketchTexts.item(0)
            sketch_Text.text = str(DATE)

        doc = app.activeDocument
        products = doc.products
        product = products.itemByProductType('CAMProductType')
        cam = adsk.cam.CAM.cast(product)

        setup = cam.setups.item(0)
        operations = setup.operations
        operation = operations.itemByName('Engrave Date')
        future = cam.generateToolpath(operation)

        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = False
        progress.show('Toolpath Generation Progress',
                      'Generating Toolpaths', 0, 10)

        numOps = future.numberOfOperations

        #  create and show the progress dialog while the toolpaths are being generated.
        progress = ui.createProgressDialog()
        progress.isCancelButtonShown = False
        progress.show('Toolpath Generation Progress',
                      'Generating Toolpaths', 0, 10)

        # Enter a loop to wait while the toolpaths are being generated and update
        # the progress dialog.
        while not future.isGenerationCompleted:
            # since toolpaths are calculated in parallel, loop the progress bar while the toolpaths
            # are being generated but none are yet complete.
            n = 0
            start = time.time()
            while future.numberOfCompleted == 0:
                # increment the progess value every .125 seconds.
                if time.time() - start > .125:
                    start = time.time()
                    n += 1
                    progress.progressValue = n
                    adsk.doEvents()
                if n > 10:
                    n = 0

            # The first toolpath has finished computing so now display better
            # information in the progress dialog.

            # set the progress bar value to the number of completed toolpaths
            progress.progressValue = future.numberOfCompleted

            # set the progress bar max to the number of operations to be completed.
            progress.maximumValue = numOps

            # set the message for the progress dialog to track the progress value and the total number of operations to be completed.
            progress.message = 'Generating %v of %m' + ' Toolpaths'
            adsk.doEvents()

        progress.hide()

        ws = ui.workspaces.itemById('CAMEnvironment')
        ws.activate()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

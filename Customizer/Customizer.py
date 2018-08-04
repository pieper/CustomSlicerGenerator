import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

#
# Customizer
#

class Customizer(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Customizer" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Customizer"]
    self.parent.dependencies = []
    self.parent.hidden = True
    self.parent.contributors = ["Steve Pieper (Isomics, Inc.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is a custom entry point for the Customizer custom build of slicer.  It was automatically generated as part of the creation of this package with the CustomSlicerGenerator.
    """
    self.parent.acknowledgementText = """
    This project is funded by R01DE024450 University of Michigan Quantification Of 3d Bony Changes In Temporomandibular Joint Osteoarthritis.
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

    # Trigger the Customizer dialog to be shown when application has started up
    if not slicer.app.commandOptions().noMainWindow :
      self.logic = CustomizerLogic()
      slicer.app.connect("startupCompleted()", self.showCustomizerWelcome)


  def showCustomizerWelcome(self):


    title = "Customizer"

    if slicer.app.platform.startswith('linux') and not self.logic.pathsAreSet():
       if self.logic.currentAdditionalModulePaths() != []:
         text = "Warning: your Slicer installation configuration will be overwritten to allow the installation and use of @CUSTOM_APP_NAME@.\n\nClick Ok to continue installation or Cancel to preserve your current state"
         choice = qt.QMessageBox.warning(slicer.util.mainWindow(), title, text, qt.QMessageBox.Ok|qt.QMessageBox.Cancel)
         if choice == qt.QMessageBox.Cancel:
           text = "@CUSTOM_APP_NAME@ is not correctly configured.  Some operations will be be possible."
           qt.QMessageBox.information(slicer.util.mainWindow(), title, text)
           return
       self.logic.setRequiredPaths()
       settings = qt.QSettings(slicer.app.slicerRevisionUserSettingsFilePath, qt.QSettings.IniFormat)
       settings.setValue("Extensions/ManagerEnabled", "false")
       if slicer.app.os is not "macos":
         executableDir,executableFileName = os.path.split(slicer.app.launcherExecutableFilePath)
         extensionsPath = os.path.join(executableDir, "Extensions-" + str(slicer.app.repositoryRevision))
         settings.setValue("Extensions/InstallPath",extensionsPath)


    restart = False
    settings = slicer.app.userSettings()
    if settings.value("Modules/HomeModule") != "AstroVolume" :
      restart = True
    settings.setValue("Modules/HomeModule", "AstroVolume")
    settings.setValue("Modules/FavoriteModules", ("AstroWelcome", "AstroSampleData", "AstroVolume", "SlicerAstroData", "AstroStatistics",  "AstroSmoothing", "SegmentEditor", "AstroMasking", "AstroProfiles", "AstroMomentMaps", "AstroPVSlice", "AstroPVDiagram", "AstroModeling"))
    title = "Customizer"
    text = "Welcome to @CUSTOM_APP_NAME@!"
    if "@CUSTOM_VERSION_NUMBER@" != "":
      text +="\n\nVersion: @CUSTOM_VERSION_NUMBER@"
    if "@CUSTOM_WELCOME_MESSAGE@" != "":
      text +="\n\n@CUSTOM_WELCOME_MESSAGE@"
    if restart:
      text +="\n\n The Customizer has configurated SlicerAstro, please restart!"

    qt.QMessageBox.information(slicer.util.mainWindow(), title, text)


#
# CustomizerWidget
#

class CustomizerWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Nothing...


    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

#
# CustomizerLogic
#

class CustomizerLogic(ScriptedLoadableModuleLogic):
  """ To implement the customization process
  """

  def currentAdditionalModulePaths(self):
    revisionSettings = slicer.app.revisionUserSettings()
    currentPaths = revisionSettings.value('Modules/AdditionalPaths')
    if not currentPaths: currentPaths = []
    return currentPaths

  def requiredAdditionalModulePaths(self):
    """Generate the list of absolute paths
    required to run the extensions related
    to this custom slicer"""
    requiredPaths = []
    for relPath in @CUSTOM_REL_PATHS@:
      absPath = os.path.join(
                  slicer.app.slicerHome,
                  "@CUSTOM_APP_NAME@"+"-Extensions",
                  relPath)
      requiredPaths.append(absPath)
    return requiredPaths

  def pathsAreSet(self):
    """returns the current list of module paths"""
    currentPaths = self.currentAdditionalModulePaths()
    requiredPaths = self.requiredAdditionalModulePaths()
    for requiredPath in requiredPaths:
      if not requiredPath in currentPaths:
        return False
    return True

  def setRequiredPaths(self):
    """sets the required module paths"""
    revisionSettings = slicer.app.revisionUserSettings()
    requiredPaths = self.requiredAdditionalModulePaths()
    revisionSettings.setValue('Modules/AdditionalPaths', requiredPaths)
    revisionSettings.beginWriteArray('PYTHONPATH')
    index = 0
    for requiredPath in requiredPaths:
        revisionSettings.setArrayIndex(index)
        revisionSettings.setValue('path', requiredPath)
        index += 1
    revisionSettings.endArray()

  def loadCustomExtensions(self,depth=1):
    """TODO: this does not actually load the modules
    correctly.  May not be possible to load shared libraries
    and CLIs with this method"""
    factory = slicer.app.moduleManager().factoryManager()
    loadedModules = factory.instantiatedModuleNames()

    newModules = []
    failedModules = []
    for relPath in @CUSTOM_REL_PATHS@:
      absPath = os.path.join(
                  slicer.app.slicerHome,
                  "@CUSTOM_APP_NAME@"+"-Extensions",
                  relPath)
      print("Looking for modules in: " + absPath)
      modules = ModuleInfo.findModules(absPath,depth)
      print("Found custom modules: " + str(modules))
      candidates = [m for m in modules if m.key not in loadedModules]
      print("These are candidates: " + str(candidates))
      for candidate in candidates:
        factory.registerModule(qt.QFileInfo(candidate.path))
        if not factory.isRegistered(candidate.key):
          failedModules.append(candidate.key)
        else:
          newModules.append(candidate.key)
      if len(failedModules):
        title = "Customizer"
        text = "Warning: the following custom modules failed to load:\n\n"
        text += str(failedModules)
        qt.QMessageBox.warning(slicer.util.mainWindow(), title, text)
      else:
        print("Loaded all new modules correctly!")
        print("New modules are: " + str(newModules))


  def customize(self):
    # TODO: set module paths to include all the extensions
    # that are in the application directory

    factory = slicer.app.moduleManager().factoryManager()

    return True

  def verifyCustomConfiguration(self):
    # TODO: test that all modules listed in the config.json file
    # are loaded
    return True


class CustomizerTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Customizer1()

  def test_Customizer1(self):
    """ Test that the customization has worked correctly.
    """

    self.delayDisplay("Starting the test",50)
    #
    # verify each of the modules in the ModulesToKeep list
    #
    logic = CustomizerLogic()
    self.assertTrue( logic.verifyCustomConfiguration() )
    self.delayDisplay('Test passed!')

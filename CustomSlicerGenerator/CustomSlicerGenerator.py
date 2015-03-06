import os
import unittest
import shutil
import json
import fnmatch
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

#
# CustomSlicerGenerator
#

class CustomSlicerGenerator(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "CustomSlicerGenerator"
    self.parent.categories = ["Developer Tools"]
    self.parent.dependencies = []
    self.parent.contributors = ["Steve Pieper (Isomics, Inc.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This module can be used to generate a new slicer application package that
    includes a subset of the modules in the currently running slicer.

    This module is controlled by a configuration file in JSON format.  The simplest config file to create a completely stripped Slicer would be { "TargetAppName" : "SlicerNULL", "ModulesToKeep" : [] }  See the module source code for more useful examples.

    Entire contents of extensions are always included based on the premise
    that if you did not want them in your custom Slicer you would not
    have them installed.
    """
    self.parent.acknowledgementText = """
    This project is funded by R01DE024450 University of Michigan Quantification Of 3d Bony Changes In Temporomandibular Joint Osteoarthritis.

    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# CustomSlicerGeneratorWidget
#

class CustomSlicerGeneratorWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Configuration Selection
    #
    self.configPathEdit = ctk.ctkPathLineEdit()
    self.configPathEdit.toolTip = "A json file in the format described in the help tab above."
    parametersFormLayout.addRow('Config File', self.configPathEdit)

    self.targetDirectoryButton = ctk.ctkDirectoryButton()
    self.targetDirectoryButton.directory = slicer.app.temporaryPath
    self.targetDirectoryButton.toolTip = "Where you want the customized Slicer application to be created.  By default it is the current Slicer temporary directory."
    parametersFormLayout.addRow('Target Directory', self.targetDirectoryButton)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Generate")
    self.applyButton.toolTip = "Generate the Custom Slicer."
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)

    # Possible use for error messages
    self.message = qt.QErrorMessage()
    self.message.setWindowTitle("CustomSlicerGenerator")

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def onApplyButton(self):
    configPath = self.configPathEdit.currentPath
    targetDirectoryPath = self.targetDirectoryButton.directory
    if configPath == "" or targetDirectoryPath == "":
      message = qt.QErrorMessage()
      message.setWindowTitle("CustomSlicerGenerator")
      message.showMessage("Must select config file and and otuput path")
    logic = CustomSlicerGeneratorLogic()
    result,detail = logic.generate(configPath, targetDirectoryPath)
    if result == "AppExists":
      answer = qt.QMessageBox().question(
        slicer.app.activeWindow(),
        "Target Exists",
        "The application directory exists.  \n\n%s\n\nClick Ok to overwrite." % detail,
        qt.QMessageBox.Ok | qt.QMessageBox.Cancel)
      if answer == qt.QMessageBox.Ok:
        result,detail = logic.generate(configPath, targetDirectoryPath,force=True)
    print(result)
    if result != "Ok":
      self.message.showMessage(result)
    else:
      qt.QDesktopServices().openUrl(qt.QUrl('file://'+targetDirectoryPath))

#
# CustomSlicerGeneratorLogic
#

class CustomSlicerGeneratorLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def isExtensionFile(self,filePath):
    """true if file is in a place where slicer keeps extensions"""
    return fnmatch.fnmatch(filePath,"*/Extensions-*")

  def isModuleFile(self,filePath):
    """true if file is in a place where slicer keeps module files"""
    fullVersion = slicer.app.applicationVersion
    version = fullVersion[0:fullVersion.rfind('.')]
    libPattern = "*/lib/Slicer-"+version+"/*-modules/*"
    return fnmatch.fnmatch(filePath,libPattern)

  def checkFilePath(self,config,filePath):
    """Use platform-specific custom knowledge of the Slicer directory
    layout to decide if a file is part of a module that we don't
    want to include."""

    # reject cruft
    if filePath.endswith('.pyc'):
      return False
    # accept extensions anid non-module files
    if self.isExtensionFile(filePath):
      return True
    if not self.isModuleFile(filePath):
      return True

    fileName = os.path.split(filePath)[-1]
    parentDirectory = os.path.split(filePath)[-2]

    # reject anything specifically excluded
    for moduleName in config['ModulesToSkip']:
      modulePattern = '*'+moduleName+'*'
      if fnmatch.fnmatch(fileName, modulePattern) or \
         fnmatch.fnmatch(parentDirectory, modulePattern):
        return False

    # accept anything specifically included
    for moduleName in config['ModulesToKeep']:
      modulePattern = '*'+moduleName+'*'
      if fnmatch.fnmatch(fileName, modulePattern) or \
         fnmatch.fnmatch(parentDirectory, modulePattern):
        return True

    # reject anything not specifically mentioned
    return False

  def log(self,fp,message):
    print(message)
    fp.write(message + "\n")
    
  def loggedCopy(self,fp,source,target,config):
    """Handles copy and keeps log.  Note it maps the app name too"""
    sourcePath,sourceFileName = os.path.split(source)
    if os.path.isdir(target):
      targetPath = target
    else:
      targetPath,targetFileName = os.path.split(target)
    if sourceFileName == "Slicer": target = os.path.join(targetPath, config['TargetAppName'])
    if sourceFileName == "Slicer.exe": target = os.path.join(targetPath, config['TargetAppName'] + ".exe")
    if sourceFileName == "SlicerLauncherSettings.ini": target = os.path.join(targetPath, config['TargetAppName'] + "LauncherSettings.ini")
    print('copy ', source, target)
    fp.write('copy \n' + source + '\n to \n->' + target + "\n")
    if os.path.isdir(source):
      shutil.copytree(source, target)
    else:
      shutil.copy(source, target)

  def generate(self,configPath,targetDirectoryPath,force=False,fileCountLimit=-1):
    """Performs the actual deed of making a custom application directory"""

    # get the config information
    try:
      # TODO: get config from a url (e.g. gist)
      configFP = open(configPath, 'r')
      configJSON = configFP.read()
      try:
        config = json.JSONDecoder().decode(configJSON)
      except ValueError:
        return "Could not parse json in config file.  If you don't see an obvious error in the file, try an on-line validator such as jsonlint.com."
      configFP.close()
    except Exception, e:
      print(e)
      return str(e)

    # determine and confirm target directory
    targetAppDirectory = config['TargetAppName']
    if slicer.app.platform.startswith('macosx'):
      targetAppDirectory += ".app"
    targetAppPath = os.path.join(targetDirectoryPath,targetAppDirectory)
    if os.path.exists(targetAppPath):
      if force:
        shutil.rmtree(targetAppPath)
      else:
        return ("AppExists", targetAppPath)

    self.delayDisplay('Generating...', 50)

    if slicer.app.platform.startswith('macosx'):
      slicerDirectory = os.path.join(slicer.app.slicerHome, "../")
    else:
      slicerDirectory = slicer.app.slicerHome

    if slicerDirectory[-1] != "/":
      slicerDirectory = slicerDirectory + "/"


    # copy files selectively according to config
    logFP = open(os.path.join(targetDirectoryPath,targetAppDirectory+".log.txt"), "w")
    skippedFileList = []
    fileList = []
    for root, subFolders, files in os.walk(slicerDirectory):
      if fileCountLimit > 0 and len(fileList) > fileCountLimit:
        return ("stopped", "Stopping after %d files" % fileCountLimit)
      for fileName in files:
        filePath = os.path.join(root,fileName)
        print('considering ', filePath)
        fileList.append(filePath)
        if self.checkFilePath(config,filePath):
          sourcePath = filePath[len(slicerDirectory):] # strip common dir
          print('sourcePath ', sourcePath)
          targetFilePath = os.path.join(targetAppPath,sourcePath)
          print('targetAppPath ', targetAppPath)
          print('targetFilePath ', targetFilePath)
          # targetDir = os.path.join(os.path.split(targetFilePath)[:-1])[0]
          targetDir = os.path.dirname(targetFilePath)
          print('targetDir ', targetDir)
          try:
            # creates all directories, raises an error if it already exists
            os.makedirs(targetDir)
          except OSError:
            pass # not a problem if directories already exist
          self.loggedCopy(logFP, filePath, targetDir, config)
        else:
          self.log(logFP, 'skip ' + filePath)
          skippedFileList.append(filePath)

    # copy the configuration into the target directory
    self.loggedCopy(logFP, configPath, targetAppPath, config)

    # for custom targets, decide if we are going beside the app (windows/linux)
    # or inside the app (mac)
    interDirectory = ""
    if slicer.app.platform.startswith('macosx'):
      interDirectory = "Contents"

    # copy all directories in the module path into
    # a special CustomExtensions directory, which
    # will be added to the settings by the Customizer
    customExtensionsPath = os.path.join(
                            targetAppPath,
                            interDirectory,
                            config['TargetAppName'] + "-Extensions")
    customExtensionRelativePaths = []
    os.makedirs(customExtensionsPath)
    revisionSettings = slicer.app.revisionUserSettings()
    paths = revisionSettings.value('Modules/AdditionalPaths')
    if not paths: paths = []
    for path in paths:
      sourcePath = None
      targetPath = None
      extIndex = path.find("Extensions-")
      if extIndex != -1:
        extStartIndex = 1+path.find('/', extIndex)
        if extStartIndex != 0:
          extEndIndex = path.find('/', extStartIndex)
          if extEndIndex != -1:
            sourcePath = path[:extEndIndex]
            targetRelativePath = path[extStartIndex:extEndIndex]
            targetRelativeSearchPath = path[extStartIndex:]
            targetPath = os.path.join(customExtensionsPath, targetRelativePath)
            customExtensionRelativePaths.append(targetRelativeSearchPath)
      if sourcePath and targetPath:
        if not os.path.isdir(targetPath):
          self.loggedCopy(logFP, sourcePath, targetPath, config)
      else:
        self.log(logFP, "Could not find extension paths for " + path)


    # make a custom version of the Customizer module
    customizerPath = os.path.join(
                      os.path.dirname(slicer.modules.customslicergenerator.path),
                      "../Customizer/Customizer.py")
    fp = open(customizerPath)
    moduleSource = fp.read()
    fp.close()
    targetCustomizerModuleName = config['TargetAppName'] + "Customizer" 
    moduleSource = moduleSource.replace("Customizer", targetCustomizerModuleName)
    moduleSource = moduleSource.replace("@CUSTOM_APP_NAME@", config['TargetAppName'])
    moduleSource = moduleSource.replace("@CUSTOM_REL_PATHS@", str(customExtensionRelativePaths))
    targetPath = os.path.join(
                  targetAppPath,
                  interDirectory,
                  "lib/Slicer-%d.%d" % (slicer.app.majorVersion, slicer.app.minorVersion),
                  "qt-scripted-modules",
                  targetCustomizerModuleName + ".py")
    fp = open(targetPath, "w")
    fp.write(moduleSource)
    fp.close()


    # fix the name of the app executable
    if slicer.app.platform.startswith('macosx'):
      sourceAppReal = os.path.join(slicerDirectory, "Contents/MacOS/Slicer")
      targetAppRealPath = os.path.join(targetDirectoryPath, targetAppDirectory, "Contents/MacOS/")
      targetAppReal = os.path.join(targetAppRealPath, config['TargetAppName'])
    elif slicer.app.platform.startswith('win'):
      sourceAppReal = os.path.join(slicerDirectory, "bin/SlicerApp-real.exe")
      targetAppExecutable = config['TargetAppName'] + "App-real.exe"
      targetAppRealPath = os.path.join(targetDirectoryPath, targetAppDirectory, "bin")
      targetAppReal = os.path.join(targetAppRealPath, targetAppExecutable)
    else:
      sourceAppReal = os.path.join(slicerDirectory, "bin/SlicerApp-real")
      targetAppExecutable = config['TargetAppName'] + "App-real"
      targetAppRealPath = os.path.join(targetDirectoryPath, targetAppDirectory, "bin")
      targetAppReal = os.path.join(targetAppRealPath, targetAppExecutable)
    # move the app to the right spot
    try:
      # creates all directories, raises an error if it already exists
      os.makedirs(targetAppRealPath)
    except OSError:
      pass # not a problem if directories already exist
    print('copy ', sourceAppReal, targetAppReal)
    logFP.write('copy '+ sourceAppReal + " to " + targetAppReal)
    shutil.copy(sourceAppReal, targetAppReal)

    # fix the metadata file to launch the new executable name
    targetAppName = config['TargetAppName']
    if slicer.app.platform.startswith('win'):
      targetAppName += ".exe"
    if slicer.app.platform.startswith('macosx'):
      # change the plist file
      targetSettingsPath = os.path.join(targetDirectoryPath, targetAppDirectory, "Contents/Info.plist")
      settings = qt.QSettings(targetSettingsPath, qt.QSettings.NativeFormat)
      settings.setValue("CFBundleExecutable", config['TargetAppName'])
    else:
      targetSettingsPath = os.path.join(targetDirectoryPath, targetAppDirectory, "bin/SlicerLauncherSettings.ini")
      settings = qt.QSettings(targetSettingsPath, qt.QSettings.IniFormat)
      settings.setValue("Application/path", "<APPLAUNCHER_DIR>/./bin/"+targetAppExecutable)
    settings.sync()

    logFP.close()
    return ("Ok", "")

class CustomSlicerGeneratorTest(ScriptedLoadableModuleTest):
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
    self.test_CustomSlicerGenerator1()

  def test_CustomSlicerGenerator1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    logic = CustomSlicerGeneratorLogic()

    modulePaths = (
      "/Applications/Slicer-4.4.0.app/Contents/lib/Slicer-4.4/cli-modules/AddScalarVolumes",
      "/Applications/Slicer-4.4.0.app/Contents/Extensions-23774/SPHARM-PDM/lib/Slicer-4.4/cli-modules/SpharmTool",
      "/Applications/Slicer-4.4.0.app/Contents/lib/Slicer-4.4/qt-scripted-modules/DICOMLib/DICOMProcesses.py",
    )
    for modulePath in modulePaths:
      self.delayDisplay(modulePath, 50)
      self.assertTrue(logic.isModuleFile(modulePath))

    self.delayDisplay("Starting the test", 50)

    # set up our config path
    modulePath = os.path.dirname(slicer.modules.customslicergenerator.path)
    configPath = os.path.join(modulePath, "sample.config.json")
    slicer.modules.CustomSlicerGeneratorWidget.configPathEdit.currentPath = configPath

    slicer.modules.CustomSlicerGeneratorWidget.onApplyButton()

    self.delayDisplay("Worked!")

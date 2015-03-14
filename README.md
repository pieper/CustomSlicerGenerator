# What?
Work in progress: a tool to generate a custom version of 3D Slicer (http://slicer.org)

# Who?
This is intended for developers working on application-specific versions of 3D Slicer.  Use of this tool requires some knowledge of the layout of the Slicer application (but not a lot if you aren't planning anything fancy).

This work was supported by the National Institute of Dental & Craniofacial Research and the National Institute of Biomedical Imaging and Bioengineering under Award Number R01DE024450.  See [the DCBIA website](https://sites.google.com/a/umich.edu/dentistry-image-computing/) for more information.

# When?
This project arose during the [2015 Winter Project Week](http://www.na-mic.org/Wiki/index.php/2015_Winter_Project_Week).  The background of this work is described here:
http://www.slicer.org/slicerWiki/index.php/Documentation/Labs/CustomSlicerGenerator.


# How?
* Clone this repository
* Get-or-create a release build of Slicer.  This works best with a build after March 5, 2015 (that is, Slicer code that includes [this change](https://github.com/Slicer/Slicer/commit/454fed0f5f2f8ea18269f2bfdfc4733326c4c6d7) and [this fix](https://github.com/Slicer/Slicer/commit/567055d01a362cfd23653f1a56b92869c2998a14) so it will have independent settings for the original Slicer and your CustomSlicer)
* Start Slicer with a command something like:
```sh
./Slicer --additional-module-paths ./CustomSlicerGenerator/CustomSlicerGenerator
```
* The CustomSlicerGenerator Module will be available and it allows you to select two things:
 * A config.json file like [this one](https://github.com/pieper/CustomSlicerGenerator/blob/master/CustomSlicerGenerator/sample.config.json).  
 * An output directory where your CustomSlicer will be created.


* The fields of the config.json file currently include:
   * TargetAppName - the name of the output, such as SlicerCMF
   * ModulesToKeep - a list of the modules that should be included.  These will be matched with a pattern `*ModuleName*` in order to match the file and directory name conventions of a Slicer distribution.  Any modules *not* listed here will not be copied to your CustomSlicer.
   * ModulesToSkip - because the filenames are matched with wildcards, there can be ambiguity between, say, the DICOM module and the CreateDICOMSeries module, so you can explicityly list modules you don't want to include.

* Any Extensions that you have installed on your Slicer will be bundled automatically into your CustomSlicer.
* A Customizer module will be included in your CustomSlicer that is used to set the extension path settings when users first run your CustomSlicer (currently requires a one-time restart of the CustomSlicer for the extensions to be recognized).
* You should zip up your CustomSlicer and give it a unique version number (typically by appending the date) to faciliate debugging.

# Does it really work?
Yes!

The CustomSlicerGenerator was used to create SlicerCMF for use at a [dental research training workshop](http://www.na-mic.org/Wiki/index.php/Construction_and_Superimposition_of_3D_Surface_Models_IADR_2015) on March 11, 2015.

A Mac and Windows version are [available in this folder on midas](http://slicer.kitware.com/midas3/folder/2717) for anyone to inspect and test.  Linux works too, but wasn't needed for this workshop.

# What else should I keep in mind?
Think carefully about becoming a software distributor - it's more than just creating an executable and putting it on a web site.  It means that people will be coming to you with questions and suggestions, sometimes complaints, and sometimes praise.  It also means you need to consider the licenses of anything you distribute; [Slicer's license](http://slicer.org/pages/LicenseText) allows you to use and redistribute the code anyway you want, but not everybody is that generous.  Also remember that people will be trusting you with their precious data, so be careful.

# Issues?
Only extensions and modules that are inside the Slicer application are considered.  If you have custom modules that aren't extensions, you can install them into the application directory tree.  Scripts are easy, just put them in, for example, lib/Slicer-4.4/qt-scripted-modules.  If you have C++ modules you will need to build them in release mode (probably you will want to build your own Slicer application distribution too).  For almost all purposes it's probably preferable to make these into regular Slicer extensions so that all the build and test work is done by the factory machines for all platforms.  The main reason someone might build their own Slicer release as a base for a CustomSlicer is if they don't want to make their work public.

# Next steps?
The current state of the CustomSlicerGenerator was enough for our SlicerCMF purposes.  There are other ideas listed [on the Slicer labs page](http://www.slicer.org/slicerWiki/index.php/Documentation/Labs/CustomSlicerGenerator) but they aren't hot-button issues so probably won't happen until/unless someone finds them important enough to work on.




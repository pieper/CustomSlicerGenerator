cmake_minimum_required(VERSION 2.8.9)

project(CustomSlicerGenerator)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://www.example.com/Slicer/Extensions/CustomSlicerGenerator")
set(EXTENSION_CATEGORY "Developer Tools")
set(EXTENSION_CONTRIBUTORS "Steve Pieper (Isomics, Inc.)")
set(EXTENSION_DESCRIPTION "This is used to create a new Slicer package containing a selected subset of modules.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/CustomSlicerGenerator.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/CustomSlicerGenerator/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CustomSlicerGenerator)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})

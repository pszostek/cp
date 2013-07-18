CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE "DEBUG")
  #SET(CMAKE_BUILD_TYPE "RELEASE")
  #SET(CMAKE_BUILD_TYPE "RELWITHDEBINFO")
  #SET(CMAKE_BUILD_TYPE "MINSIZEREL")
ENDIF()

#FIND_PACKAGE(Boost 1.45.0)
#IF(Boost_FOUND)
#  INCLUDE_DIRECTORIES("${Boost_INCLUDE_DIRS}" "/usr/include/python2.6")
#  SET(Boost_USE_STATIC_LIBS OFF)
#  SET(Boost_USE_MULTITHREADED ON)
#  SET(Boost_USE_STATIC_RUNTIME OFF)
#  FIND_PACKAGE(Boost 1.45.0 COMPONENTS python)
#
#  ADD_LIBRARY(demangle SHARED demangle.cxx)
#  TARGET_LINK_LIBRARIES(demangle ${Boost_LIBRARIES})
#ELSEIF(NOT Boost_FOUND)
#  MESSAGE(FATAL_ERROR "Unable to find correct Boost version. Did you set BOOST_ROOT?")
#ENDIF()


find_package(Boost 1.45.0 COMPONENTS python REQUIRED)
message("Include dirs of boost: " ${Boost_INCLUDE_DIRS} )
message("Libs of boost: " ${Boost_LIBRARIES} )

find_package(PythonLibs REQUIRED)
message("Include dirs of Python: " ${PYTHON_INCLUDE_DIRS} )
message("Libs of Python: " ${PYTHON_LIBRARIES} )

include_directories(
    ${Boost_INCLUDE_DIRS}
    ${PYTHON_INCLUDE_DIRS}  # <-------
)

add_library(demangle SHARED demangle.cxx)

target_link_libraries(demangle
    ${Boost_LIBRARIES}
    ${PYTHON_LIBRARIES} # <------
)


IF(CMAKE_COMPILER_IS_GNUCXX)
  ADD_DEFINITIONS("-Wall")
ELSE()
  MESSAGE(FATAL_ERROR "CMakeLists.txt has not been tested/written for your compiler.")
ENDIF()

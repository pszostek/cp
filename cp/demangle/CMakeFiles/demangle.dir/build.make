# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /usr/bin/ccmake

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/paszoste/addr2line/demangle

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/paszoste/addr2line/demangle

# Include any dependencies generated for this target.
include CMakeFiles/demangle.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/demangle.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/demangle.dir/flags.make

CMakeFiles/demangle.dir/demangle.cxx.o: CMakeFiles/demangle.dir/flags.make
CMakeFiles/demangle.dir/demangle.cxx.o: demangle.cxx
	$(CMAKE_COMMAND) -E cmake_progress_report /home/paszoste/addr2line/demangle/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/demangle.dir/demangle.cxx.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/demangle.dir/demangle.cxx.o -c /home/paszoste/addr2line/demangle/demangle.cxx

CMakeFiles/demangle.dir/demangle.cxx.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/demangle.dir/demangle.cxx.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/paszoste/addr2line/demangle/demangle.cxx > CMakeFiles/demangle.dir/demangle.cxx.i

CMakeFiles/demangle.dir/demangle.cxx.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/demangle.dir/demangle.cxx.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/paszoste/addr2line/demangle/demangle.cxx -o CMakeFiles/demangle.dir/demangle.cxx.s

CMakeFiles/demangle.dir/demangle.cxx.o.requires:
.PHONY : CMakeFiles/demangle.dir/demangle.cxx.o.requires

CMakeFiles/demangle.dir/demangle.cxx.o.provides: CMakeFiles/demangle.dir/demangle.cxx.o.requires
	$(MAKE) -f CMakeFiles/demangle.dir/build.make CMakeFiles/demangle.dir/demangle.cxx.o.provides.build
.PHONY : CMakeFiles/demangle.dir/demangle.cxx.o.provides

CMakeFiles/demangle.dir/demangle.cxx.o.provides.build: CMakeFiles/demangle.dir/demangle.cxx.o

# Object files for target demangle
demangle_OBJECTS = \
"CMakeFiles/demangle.dir/demangle.cxx.o"

# External object files for target demangle
demangle_EXTERNAL_OBJECTS =

libdemangle.so: CMakeFiles/demangle.dir/demangle.cxx.o
libdemangle.so: CMakeFiles/demangle.dir/build.make
libdemangle.so: /usr/lib/libboost_python.so
libdemangle.so: /usr/lib/x86_64-linux-gnu/libpython3.3m.so
libdemangle.so: CMakeFiles/demangle.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX shared library libdemangle.so"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/demangle.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/demangle.dir/build: libdemangle.so
.PHONY : CMakeFiles/demangle.dir/build

CMakeFiles/demangle.dir/requires: CMakeFiles/demangle.dir/demangle.cxx.o.requires
.PHONY : CMakeFiles/demangle.dir/requires

CMakeFiles/demangle.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/demangle.dir/cmake_clean.cmake
.PHONY : CMakeFiles/demangle.dir/clean

CMakeFiles/demangle.dir/depend:
	cd /home/paszoste/addr2line/demangle && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/paszoste/addr2line/demangle /home/paszoste/addr2line/demangle /home/paszoste/addr2line/demangle /home/paszoste/addr2line/demangle /home/paszoste/addr2line/demangle/CMakeFiles/demangle.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/demangle.dir/depend


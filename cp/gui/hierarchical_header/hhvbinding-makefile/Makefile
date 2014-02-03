LIBFOO_DIR = ${PWD}/../libhhv
LIBS = -I/usr/local/include/PySide -I/usr/local/include/python2.7 -I/usr/local/include/python2.7 -I/usr/local/include/shiboken/  /usr/lib/x86_64-linux-gnu/libpython2.7.so -L/usr/local/lib \
  -L$(LIBFOO_DIR) -lhhv -lpyside-python2.7 -lshiboken-python2.7
CXXFLAGS = -I/usr/share/qt4/mkspecs/linux-g++ -I. \
   -I/usr/include/python2.7/ \
   -I$(LIBFOO_DIR) \
   -I$(pwd)/hhv \
   -I$(pkg-config --variable=includedir pyside)/QtCore/ \
   -I/usr/include/PySide/QtUiTools/ \
   -I/usr/include/qt4/QtUiTools/ \
   -I/usr/local/include/PySide/QtXmlPatterns/ \
   -I/usr/include/PySide/QtXml \
   -I/usr/include/PySide/QtUiTools/ \
   -I/home/paszoste/cp/cp/gui/pyside/PySide/ \
   -I/usr/include/PySide/QtTest \
   -I/usr/include/PySide/QtOpenGL/ \
   -I/usr/include/PySide/QtHelp/ \
   -I/usr/include/qt4/Qt/ \
   -I/usr/include/qt4/QtNetwork/ \
   -I/usr/local/include/PySide/QtNetwork/ \
   -I/usr/local/include/PySide/QtDeclarative/ \
   -I/usr/local/include/PySide/QtGui/ \
   -I/usr/include/qt4/QtGui \
   -I/usr/include/qt4 \
   -I/usr/include/qt4/QtCore/ \
   -I/usr/include/shiboken/ \
   -I/usr/include/PySide/QtCore/ \
   -I/usr/local/include/PySide/
 
QT4TYPESYSTEM_DIR = `pkg-config pyside --variable=typesystemdir`
QT4HEADER_DIRS = /usr/include/qt4
PYSIDE_PYTHONPATH = `pkg-config --variable=pythonpath PySide`
PYTHON_INTERPRETER = `pkg-config --variable=python_interpreter shiboken`
 
all: hhv.so ../libhhv/libhhv.so
shiboken_crap := hhv/hierarchicalheaderview_wrapper.cpp hhv/hierarchicalheaderview_wrapper.h hhv/hhv_module_wrapper.cpp hhv/hhv_python.h 

hhv.so: ${shiboken_crap}
	g++ -c hhv/hierarchicalheaderview_wrapper.cpp hhv/hhv_module_wrapper.cpp  -Wall -fPIC $(CXXFLAGS) 
	g++ hierarchicalheaderview_wrapper.o hhv_module_wrapper.o $(LIBS) -fPIC -shared -Wl,-soname,hhv.so -o hhv.so
 
${shiboken_crap}: global.h typesystem_hhv.xml
	shiboken --generatorSet=shiboken \
  global.h \
  --include-paths=$(LIBFOO_DIR):$(QT4HEADER_DIRS):/usr/include \
  --typesystem-paths=.:$(QT4TYPESYSTEM_DIR) \
  --output-directory=. \
  typesystem_hhv.xml

../libhhv/libhhv.so: ../libhhv/HierarchicalHeaderView.h ../libhhv/HierarchicalHeaderView.cpp
	make -C ../libhhv all
 
test:
	LD_LIBRARY_PATH=$(LIBFOO_DIR):$(LD_LIBRARY_PATH) PYTHONPATH=$(PYSIDE_PYTHONPATH):$(PYTHONPATH) $(PYTHON_INTERPRETER) -c \
  "from PySide import QtCore, QtGui;from PySide.QtGui import *;from PySide.QtCore import *; import hhv; m = hhv.HierarchicalHeaderView(QtCore.Qt.Horizontal);"
 
clean:
	rm -rf *.o *.so *.?pp *.log *.log hhv/*
	make -C ../libhhv clean



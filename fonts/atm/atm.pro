CONFIG += c++11 link_pkgconfig
TEMPLATE += app
TARGET = atm
QT += core gui
QT += widgets
DEPENDPATH += .
PKGCONFIG = harfbuzz freetype2
SOURCES += main.cpp

#!/bin/bash

echo "PyQDA will be copied to the directory /usr/share/pyshared"
echo "An icon file will be copied to the directory /usr/share/pixmaps"
echo "A clickable icon to start Py3QDA will be created"
echo "These actions require owner (sudo) permission"

sudo cp -r Py3QDA /usr/share/pyshared/Py3QDA
sudo cp Py3QDA/PyQDA.png /usr/share/pixmaps
cp Py3QDAdesktop Py3QDA.desktop
sudo chmod a+x Py3QDA.desktop

echo "Completed"
echo "\n"
echo "Double click the icon to start Py3QDA"
echo "\n"
echo "To remove Py3QDA type the following in the terminal:"
echo "sudo rm -R /usr/share/pyshared/Py3QDA"
echo "sudo rm /usr/share/pixmaps/PyQDA.png"

#!/bin/bash

echo "PyQDA will be copied to the directory /usr/share/pyshared"
echo "An icon file will be copied to the directory /usr/share/pixmaps"
echo "A clickable icon to start PyQDA will be created"
echo "These actions require owner (sudo) permission"

sudo cp -r PyQDA /usr/share/pyshared/PyQDA
sudo cp PyQDA/PyQDA.png /usr/share/pixmaps
cp PyQDAdesktop PyQDA.desktop
sudo chmod a+x PyQDA.desktop

echo "Completed"
echo "\n"
echo "Double click the icon to start PyQDA"
echo "You can put the icon into the Unity Launcher, you can move it to the desktop. Do not delete it. If deleted you will have to run the install.sh script again to get it back."
echo "\n"
echo "To remove PyQDA type the following in the terminal:"
echo "sudo rm -R /usr/share/pyshared/PyQDA"
echo "sudo rm /usr/share/pixmaps/PyQDA.png"

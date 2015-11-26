===========
PyQDA
===========

PyQDA is a qualitative data analysis application. It uses the same Sqlite database format as used by RQDA allowing you to open your RQDA projects in PyQDA, and vice versa. For details of RQDA see http://rqda.r-forge.r-project.org/

PyQDA projects are stored in an Sqlite database. Text files can be typed in manually or loaded from txt, odt, docx and pdf files. See Issues below. Codes can be assigned to text and grouped into categories. Various types of reports can be produced including network graphs, coding frequencies and several ways to query the database.

Example files are included to allow you to work through the Help documents. These files are ID1.docx, ID2.odt, transcript.txt and attributes.csv.

INSTALLATION
============

METHOD 1:
This method wil create an executable PyQDA icon on Ubuntu/Debian. You will see a PyQDA icon appear in the PyQDA folder. Double-click this to start PyQDA. This icon can be moved to the Desktop or into the Unity Launcher (on Ubuntu).
Extract the tar.gz folder.
Open a terminal and type the following to install PyQDA::

    # Move to the extracted PyQDA folder.
    # This assumes the folder is in your Downloads folder.

    cd Downloads/PyQDA-0.1.0

    # Run the install.sh file. The install process will ask for your permission to install PyQDA.

    ./install.sh


METHOD 2:

Extract the tar.gz folder.
Open a terminal and type the following to start PyQDA. Of course replace path to directory with the actual file path::

    python /pathtodirectory/PyQDA.py

If you are using Windows you can double-click the PyQDA.py file to start PyQDA.

Dependencies
=========

Required

* Python 2.7. PyQDA has been developed using Python 2.7

* PyQt

Optional

* PyPdf to allow importing of pdf text

* igraph to view network graphs of codes and categories

Issues
=========

* Testing has only been performed on Ubuntu and CrunchBang using English
  character sets.

* I did have some problems with decoding some Unicode characters and have put in
  a few workarounds for these. Maybe another programmer can give some advice for
  improvements.

* Text loaded with PyPdf is not formatted at all. This includes no paragraph
  separations.

* I have tried to implement most of PEP8 with help from Ninja-IDE :) However I
  did not restrict my coding to 80 character lines.

For the future
=========

* I would have liked to implement an inter-rater agreement statistic but did not
  know how to do this.

* I would like to develop the capacity to assign codes to images and image
  portions.

License
=========

PyQDA is distributed under the MIT LICENSE.


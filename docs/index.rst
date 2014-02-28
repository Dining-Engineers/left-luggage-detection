.. Left Luggage Detection documentation master file, created by
   sphinx-quickstart on Fri Feb 21 11:10:52 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================================
Welcome to Left Luggage Detection's documentation!
==================================================

**Authors:**
    - *Andrea Rizzo*, andrearizzo[at]outlook.com

    - *Matteo Bruni*, matteo.bruni[at]gmail.com

*Abstract*
------------------
This wiki describes the method used to detect abandoned items in a 
public space.
Today, video surveillance is used airports, train stations and public 
spaces where it is essential guarantee a high security level.
The video stream is obtained through the use of a Kinect device. 
The the RGB (*intensity*) and depth video streams are analyzed 
independently. From each stream we obtain a set of proposal, i.e. left 
luggage item, that are combined in the final step of our pipeline.

Contents
--------

   .. :doc:`docs`

.. toctree::
   :maxdepth: 3

   report
   docs
   usage
   dependencies
   dataset
   LICENSE

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


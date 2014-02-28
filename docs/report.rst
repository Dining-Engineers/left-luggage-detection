=======================
Left luggage detection
=======================

This wiki describes the method used to detect abandoned items in a 
public space.
Today, video surveillance is used airports, train stations and public 
spaces where it is essential guarantee a high security level.
The video stream is obtained through the use of a Kinect device. 
The the RGB (*intensity*) and depth video streams are analyzed 
independently. From each stream we obtain a set of proposal, i.e. left 
luggage item, that are combined in the final step of our pipeline.


.. toctree::
   :maxdepth: 2

   report/introduction
   report/approach
   report/background_models
   report/combination





Introduction
------------------

In this section we briefly describe the proposed approach.

*Image data:* we use the Kinect device. Kinect sensor is a horizontal 
bar connected to a small 
base with a motorized pivot. The major device features are RGB camera 
and depth sensor. 
The device has a USB2 interface and the resolution of the RGB camera is 
:math:`640 \times 480` with 8 bit quantization. The depth camera instead 
has a resolution  of :math:`640 \times 480` with 11 bit quantization.

*Pipeline:* our detection pipeline analyzes the RGB (*intensity*) and 
depth video streams independently. 
This means that the RGB left object proposals are found without considering the depth data and 
the depth proposals are found without considering the RGB data. 
Both sets of proposal are combined later in a processing stage. 
The independent processing warranted because the RGB video stream is 
defined everywhere, 
i.e. for each pixel of a stream frame the intensity value is defined, 
but it is liable to 
photometric variations. Instead the depth video stream is not defined 
everywhere. The depth value 
is only available for the image regions that are close enough to the device. Also for black objects 
the sensor can't measure the depth value.

By using the two video streams a background models for depth and 
RGB are computed. 
To extract left luggage proposals the spatial changes over time are accumulated in an image aggregator. For the depth 
aggregator we provide more 
than one method to accumulate the depth changes. If the aggregator exceeds a threshold is segmented 
with a bounding box and we mark the spatial region as left item proposal. The depth and intensity 
proposal are compared using the PASCAL criterion. 
The bounding boxes that satisfy the criterion are considered 
left objects.
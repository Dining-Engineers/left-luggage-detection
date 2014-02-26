===============
Left luggage detection
===============

**Authors:**
    - *Andrea Rizzo*, andrearizzo[at]outlook.com

    - *Matteo Bruni*, matteo.bruni[at]gmail.com

*Abstract*
------------------
This wiki describes the method used to detect abandoned items in a public space.
Today, video surveillance is used airports, train stations and public spaces where it is essential guarantee a high security level.
The video stream is obtained by a Kinect.....


Introduction
------------------

Approach
------------------
In this section we briefly describe the proposed approach.

*Image data:* we use the Kinect device. Kinect sensor is a horizontal bar connected to a small base with a motorized pivot. The major device features are RGB camera and depth sensor. The device has a USB2 interface and the resolution of the RGB camera is 
:math:`640 \times 480` with 8 bit quantization instead the depth camera resolution is :math:`640 \times 480` with 11 bit quantization.

*Pipeline:* our detection pipeline analyzes the RGB (*intensity*) and depth video streams independently. This means that the RGB left object proposals are found without consider the depth data and the depth proposals are found without consider the RGB data. Both sets of proposal are combined in a later processing stage. The independent processing warranted because the RGB video stream is defined everywhere, i.e. for each pixel of a stream frame the intensity value is defined, but as one it is liable to photometric variations. Instead the depth video stream is not defined everywhere. The depth value is only available for the image regions that are close enough to the device. Also for black objects the sensor can't measure the depth value.
By using the two video stream a background model for depth and a background model for RGB are computed. The spatial changes are accumulated in an aggregator. For the depth aggregator we provide more than one method to accumulate the spatial changes. If the aggregator exceeds a threshold is segmented with a bounding box and we mark the spatial region as left item proposal. The depth and intensity proposal are compared using the overlapping criterion. The bounding boxes that match the selection criteria are considered left objects.

Background modeling
--------------------
In this section we describe the methods used to model the background. Then we describe the methods used to accumulate the spatial changes and how the aggregators are processed to extract the proposals.

Depth background model and proposal
````````````````````````````````````
The depth background model is computed by using the higher-resolution (11-bit) depth matrix because we want to do computations with the depth. The method used to model the background is the accumulate running average. At time :math:`t` the model is updated with the following function:

:math:`model_{t} = (1-\alpha) \cdot model_{t-1} + \alpha \cdot frame_{t}`

where the coefficient :math:`\alpha` is the learning rate. For a proper background modelling we have to detect the holes in depth map, i.e. the pixels where the sensor didn't measure the depth. The value of these pixels is :math:`2^{11}-1`. Then the foreground is extracted.
Since the depth image is very noisy, applying an opening is suggested.

To extract the proposal, we accumulate the spatial changes in depth. The methods provided are three.

Image accumulator
^^^^^^^^^^^^^^^^^^
The first method is a simple **image accumulator** and it is quicker than the other methods. By using a matrix with the same size of depth frame, the pixels that are in current foreground are incremented by an unit value. Instead the pixels that were in the foreground but now are not in current foreground the correspondent entries are decremented. To generate a proposal from the accumulator we consider only the entry that have a number of observations above a threshold. The proposals are extracted by using [#note1]_. The proposals with area less than 50 pixels are not considered.

Bounding box accumulator
^^^^^^^^^^^^^^^^^^^^^^^^^
The **bounding box accumulator** method is slower than *image accumulator* but is more accurate. The proposals are generated as in the previous method by using the mask of current foreground. So the current set of bounding box are compared with the set of accumulated bounding box. We consider two bounding box similar if the distance between two centers and the area ratio are under a threshold. For each bounding box that has a match the correspondent entries in the accumulator are updated with the new spatial coordinates and the counter are incremented by an unit value. For each bounding box that hasn't a match it's temporarily stored in the accumulator with counter set to 1. For each bounding box in the accumulator that hasn't a match the correspondent count are decrement. To generate a proposal from the accumulator we consider only the bounding boxes that have a number of observations above a threshold. Note that if more than one bounding box match with a bounding box in the accumulator it considers the first match found.
	
Best bounding box accumulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The **best bounding box accumulator** method is the slowest. It's works as the previous method but if more than one bounding box match with a bounding box in the accumulator it updates the accumulator by using the best match found.

Intensity background model and proposal
````````````````````````````````````````
The intensity background model is computed by using the method of Zivkovic et al [#note2]_.

.. image:: img/example1.png
   :height: 480
   :width: 640
   :scale: 80
   :alt: alternate text in do lo mette?

|
|



overlapping criterion:

:math:`r = \frac{area \left(B_{curr} \cap B_{acc} \right)}{area \left(B_{curr} \cup B_{acc} \right)}`


.. [#note1] Suzuki, S. and Abe, K., Topological Structural Analysis of Digitized Binary Images by Border Following. CVGIP 30 1, pp 32-46 (1985).

.. [#note2] Z. Zivkovic and F. van der Heijden. Efficient adaptive density estimation per image pixel for the task of background subraction. Pattern Recogn. Lett., 27(7):773–780, May 2006.
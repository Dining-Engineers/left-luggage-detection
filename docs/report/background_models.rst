=======================
Background modeling
=======================

In this section we describe the methods used to model the background. 
Then we describe the methods used to accumulate the spatial changes and how the aggregators 
are processed to extract the proposals.


Depth background model and proposals
-------------------------------------
The depth background model is computed by using the higher-resolution (11-bit) depth matrix 
because we want to do computations with the depth. The method used to model the background is the 
accumulate running average. At time :math:`t` the model is updated with the following function:

:math:`model_{t} = (1-\alpha) \cdot model_{t-1} + \alpha \cdot frame_{t}`

where the coefficient :math:`\alpha` is the learning rate. For a proper background modelling we 
have to detect the holes in depth map, i.e. the pixels where the sensor didn't measure the depth. 
The value of these pixels is :math:`2^{11}-1`. Then the foreground is extracted.
Since the depth image is very noisy, applying an opening is suggested.

To extract the proposal, we accumulate the spatial changes in depth. The methods provided are three.


Image accumulator
^^^^^^^^^^^^^^^^^^

The first method is a simple **image accumulator** and it is quicker than the other methods. 
By using a matrix with the same size of depth frame, the pixels that are in current foreground 
are incremented by an unit value. Instead the pixels that were in the foreground but now are not 
in current foreground the correspondent entries are decremented. To generate a proposal from 
the accumulator we consider only the entry that have a number of observations above a threshold. 
The proposals are extracted by using [#note1]_. 
The proposals with area less than 50 pixels are not considered.


Bounding box accumulator
^^^^^^^^^^^^^^^^^^^^^^^^^

The **bounding box accumulator** method is slower than *image accumulator* but is more accurate. The 
proposals are generated as in the previous method by using the mask of current foreground. So the 
current set of bounding box are compared with the set of accumulated bounding box. We consider 
two bounding box similar if the distance between two centers and the area ratio are under a threshold. 
For each bounding box that has a match the correspondent entries in the accumulator are updated with 
the new spatial coordinates and the counter are incremented by an unit value. For each bounding box 
that hasn't a match it's temporarily stored in the accumulator with counter set to 1. 
For each bounding box in the accumulator that hasn't a match the correspondent count are decrement. 
To generate a proposal from the accumulator we consider only the bounding boxes that have a number 
of observations 
above a threshold. Note that if more than one bounding box match with a bounding box in the accumulator 
it considers the first match found.
	
Best bounding box accumulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The **best bounding box accumulator** method is the slowest. It's works as the previous method but if 
more than one bounding box match with a bounding box in the accumulator it updates the accumulator by 
using the best match found.


Intensity background model and proposals
````````````````````````````````````````

The intensity background model is computed by using the method of Zivkovic et al [#note2]_. 
The intensity-based proposal are generated with the dual foregrouonds model of Porikli et al. [#note3]_. 


Porikli method
^^^^^^^^^^^^^^^^^^

Briefly the Porikli method aims to detect an abandoned item. Instead of using a single background 
approaches the Prikli methods use two backgrounds: long-term background :math:`B_{L}` and short-term 
background :math:`B_{S}`. To compute both backgrounds the method of Zivkovic is used. For long-term 
background the learning rate :math:`\alpha_{L}` is lower than the learning rate :math:`\alpha_{S}` used 
to compute the short-term background. Therefore the :math:`B_{L}` is more resistant against the temporary 
changes. In contrast, the :math:`B_{S}` adapts to the underlying distribution faster and the changes in 
the scene are blended more rapidly.
For each frame of video stream, the long and short term foregrounds 
are extracted by substracting from the current frame the background models :math:`B_{L}` and :math:`B_{S}`.
So we obtain a long-term foreground mask :math:`F_{L}` and a short-term foreground mask :math:`F_{S}`.
Let :math:`I \left(x,y\right)` be a pixel of the current frame, we have four cases:

 1. if :math:`F_{L}\left(x,y\right)=1` and :math:`F_{S}\left(x,y\right)=1` then the pixel correspond 
 to a moving object;

 2. if :math:`F_{L}\left(x,y\right)=1` and :math:`F_{S}\left(x,y\right)=0` then the pixel correspond 
 to a **temporarily static object**;

 3. if :math:`F_{L}\left(x,y\right)=0` and :math:`F_{S}\left(x,y\right)=1` then the pixel correspond 
 to scene of background that was accluded before;

 4. if :math:`F_{L}\left(x,y\right)=0` and :math:`F_{S}\left(x,y\right)=0` then the pixel is a 
 background pixel for both backgrounds model.

By using the :math:`F_{L}` and :math:`F_{S}` an image aggregator is computed. To each pixel correspond 
an entry in the image aggregator. If a pixel is in :math:`F_{L}` but is not in :math:`F_{S}` the 
correspond entry in the image aggregator is increment. Otherwise the image aggregator is decremented.



.. [#note1] Suzuki, S. and Abe, K., Topological Structural Analysis of Digitized Binary Images by Border Following. CVGIP 30 1, pp 32-46 (1985).
.. [#note2] Z. Zivkovic and F. van der Heijden. Efficient adaptive density estimation per image pixel for the task of background subraction. Pattern Recogn. Lett., 27(7):773–780, May 2006.
.. [#note3] F. Porikli, Y. Ivanov, and T. Haga. Robust abandoned object detection using dual foregrounds. EURASIP J. Adv. Signal Process, 2008, Jan. 2008. 2, 3, 5


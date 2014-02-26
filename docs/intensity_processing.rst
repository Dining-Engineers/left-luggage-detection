Intensity Processing
====================

The intensity module contains classes that hide some of all the repeated
code associated with processing intensity data. The main component
is the :class:`.IntensityProcessing` class, which is used to process
continuously retrieved data from the kinect.
The background model used in this class is obtained through
Zivkovic method: Adaptive Gaussian Mixture Model.
The extraction of the foreground pixels proposals is obtained via the
:meth:`.IntensityProcessing.compute_foreground_masks`.
The bounding boxes proposals are extracted using :meth:`.IntensityProcessing.extract_proposal_bbox`
from an aggregator build using Porikli's method via :meth:`.IntensityProcessing.update_detection_aggregator`.


Usage Example
-------------

If code already exists to retrieve the data extracting the bounding boxes proposals can be reduced to as little as the following:

.. code-block:: python

        # get next video frame
        rgb.current_frame = cam.get_image()
        while True:
            # get rgb dual background (long and short sensitivity)
            # N.B. background is black (0) and foreground white (1)
            rgb.compute_foreground_masks(rgb.current_frame)

            # update rgb aggregator
            rgb.update_detection_aggregator()

            # extract bounding box proposals
            rgb_proposal_bbox = rgb.extract_proposal_bbox()



IntensityProcessing class
-------------------------

.. automodule:: intensity_processing
    :members:
    :undoc-members:
    :show-inheritance:

Depth Processing
================

The depth module contains classes that hide some of all the repeated
code associated with processing depth data. The main component
is the :class:`.DepthProcessing` class, which is used to process
continuously retrieved data from the kinect.
The background model used in this class is obtained through running average via
the method :meth:`.DepthProcessing.update_background_model`

Usage Example
-------------

If code already exists to retrieve the data extracting the bounding boxes proposals can be reduced to as little as the following:

.. code-block:: python

    # DepthProcessing instance
    depth = DepthProcessing(IMAGE_SHAPE)

    while True:
        # retrieve the depth information
        depth.current_frame = cam.get_depth_matrix()
        if first_run:
            # in first run moving average start from first frame
            depth.background_model = depth.current_frame.astype(depth.background_model.dtype)
            first_run = False

        # get depth background
        depth.update_background_model(depth.current_frame)

        # get depth foreground
        depth.extract_foreground_mask_from_run_avg(depth.current_frame)

        # apply opening to remove noise
        depth.foreground_mask = bg_models.apply_opening(depth.foreground_mask,
                                                        BG_OPEN_KSIZE,
                                                        cv2.MORPH_ELLIPSE)

        depth_proposal_bbox = depth.extract_proposal_bbox(depth.ACCUMULATOR)


DepthProcessing class
---------------------

.. automodule:: depth_processing
    :members:
    :show-inheritance:

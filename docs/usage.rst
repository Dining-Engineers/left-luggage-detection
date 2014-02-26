=====
Usage
=====


To use our application you can simply launch the main application via:

.. code-block:: console

    python left-luggage-detection.py


.. note::

    make sure your kinect is connected to your pc **and** the power supply otherwise you'll only be able to control the
    motor and not the video stream


Offline Usage
-------------

You can also test this application using registered video via Fakenect library which is included in Openkinect.

To record a video:

.. code-block:: console

    mkdir directory_record
    record directory_record


To use a recorded video you need to specify two environment variables: ``LD_PRELOAD`` and ``FAKENECT_PATH``:

.. code-block:: console

    LD_PRELOAD="/usr/local/lib64/fakenect/libfreenect.so" FAKENECT_PATH="video/path" python left-luggage-detection.py
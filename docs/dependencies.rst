====================
Project Dependencies
====================

You need to have the following libs/programs installed:


1. OpenKinect
-------------

Home page: http://openkinect.org/wiki/Main_Page

Source Code: https://github.com/OpenKinect/libfreenect

Dependencies
````````````

Manual Build on Linux: for compiling, you need to have the following libs/programs installed:

    * cmake
    * libusb-1.0-0
    * libusb-1.0-0-dev
    * pkg-config
    * libglut3
    * libglut3-dev

APT users: (Works on Ubuntu 10.10)

.. code-block:: console

    sudo apt-get install cmake libglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev

For Ubuntu 13.04, use this instead (replaced libglut3 with freeglut3):

.. code-block:: console

    sudo apt-get install cmake freeglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev


The python wrapper also need:

.. code-block:: console

    sudo apt-get install cython python-dev python-numpy


Manual Build
````````````

Download last libfreenect version from github and compile with CMAKE:

.. code-block:: console

    git clone git://github.com/OpenKinect/libfreenect.git
    cd libfreenect
    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    sudo ldconfig /usr/local/lib64/

To test if the library is correctly installed use:

.. code-block:: console

   sudo glview

To install the Python wrapper

.. code-block:: console

    cd libfreenect/wrappers/python
    sudo python setup.py install

To use Kinect as a non-root user do the following:

.. code-block:: console

    sudo adduser $USER video

2. OpenCV
---------

To install OpenCV you can use the following script

.. code-block:: console

    wget https://raw.github.com/jayrambhia/Install-OpenCV/master/Ubuntu/opencv_latest.sh
    chmod +x opencv_latest.sh
    ./opencv_latest.sh

.. note::
    If you want cuda support add WITH_CUDA=ON in the cmake section if the above script


3. Pygame
---------

To display the video stream we use pygame so you'll need:

.. code-block:: console

    sudo apt-get install python-pygame


4. Optional
-----------

SimpleCV (optional)
```````````````````

If you decide to use SimpleCV class to display the video stream install SimpleCV from: http://simplecv.org/download


cProfile
````````

To run memory and speed benchmark of the application

.. code-block:: console

    sudo apt-get install pythontracer

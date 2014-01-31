#from OpenGL.GL import GL_ARRAY_BUFFER, GL_DYNAMIC_DRAW, glFlush
from OpenGL.GL import *
from OpenGL.arrays import vbo


import sys
import numpy

import cv
import freenect
import frame_convert

import timing
timings = timing.Timing()


import Image

class Kinect(object):
    def __init__(self):
        #set up initial conditions
        pos = numpy.ndarray((640*480*4, 1), dtype=numpy.float32)
        self.pos_vbo = vbo.VBO(data=pos, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
        self.pos_vbo.bind()
        #same shit, different toilet
        self.col_vbo = vbo.VBO(data=pos, usage=GL_DYNAMIC_DRAW, target=GL_ARRAY_BUFFER)
        self.col_vbo.bind()


    def get_depth(self):
        if len(freenect.sync_get_depth()) > 0:
            depth = freenect.sync_get_depth()[0]
            #numpy.clip(depth, 0, 2**10 - 1, depth)
            #depth >>= 2
            #print depth[0][0]
            return depth.astype(numpy.float32)/2048.

            #print "return from get depth"
            #return numpy.array(depth, dtype=numpy.float32)
            #return frame_convert.pretty_depth_cv(freenect.sync_get_depth()[0])
        return None

    def get_video(self):
        if len(freenect.sync_get_video()) > 0:
            rgb = freenect.sync_get_video()[0]
            rgb = rgb[:, :, ::-1]  # RGB -> BGR
            return rgb.astype(numpy.int8)
            #return frame_convert.video_cv(freenect.sync_get_video()[0])
        return None

    def get_particles(self):
        depth = self.get_depth()
        rgb = self.get_video()
        #print "d.depth", depth.depth
        #print "d.channels", depth.nChannels

        #print "rgb.depth", rgb.depth
        #print "rgb.channels", rgb.nChannels


        #print "rgb im.depth", rgb.depth
        #dnp = numpy.fromstring(depth.tostring(), dtype=numpy.int8, count=depth.width*depth.height*depth.nChannels)
        #rgbnp = numpy.fromstring(rgb.tostring(), dtype=numpy.int8, count=rgb.width*rgb.height*rgb.nChannels)
        return rgb, depth
    
        #TODO: Get the depth as float between 0 and 1 instead of int between 0 and 255
        #di = Image.fromstring("L", cv.GetSize(depth), depth.tostring())
        #rgbi = Image.fromstring("RGB", cv.GetSize(rgb), rgb.tostring())
        #di.show()
        #rgbi.show()
        #return numpy.array(rgbi, dtype=numpy.int8), numpy.array(di, dtype=numpy.float32)





import pyopencl as cl
class CL(object):
    def __init__(self, *args, **kwargs):
        self.clinit()
        self.loadProgram("calibrate.cl")

        self.timings = timings

    
    def load_images(self, rgb, depth):
        cl.enqueue_write_buffer(self.queue, self.rgb_cl, rgb)
        cl.enqueue_write_buffer(self.queue, self.depth_cl, depth)
        self.queue.finish()


    def loadData(self, pos_vbo, col_vbo):
        mf = cl.mem_flags
        self.pos_vbo = pos_vbo
        self.col_vbo = col_vbo

        self.pos = pos_vbo.data
        self.col = col_vbo.data

        #Setup vertex buffer objects and share them with OpenCL as GLBuffers
        self.pos_vbo.bind()
        self.pos_cl = cl.GLBuffer(self.ctx, mf.READ_WRITE, int(self.pos_vbo.buffers[0]))
        self.col_vbo.bind()
        self.col_cl = cl.GLBuffer(self.ctx, mf.READ_WRITE, int(self.col_vbo.buffers[0]))

        #pure OpenCL arrays
        #self.vel_cl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=vel)
        #self.pos_gen_cl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.pos)
        #self.vel_gen_cl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=self.vel)
        self.queue.finish()

        self.imsize = 640*480
        self.num = self.imsize
        dempty = numpy.ndarray((self.imsize, 1), dtype=numpy.float32)
        rgbempty = numpy.ndarray((self.imsize, 3), dtype=numpy.dtype('b'))

        #ptd: 485.377991, 7.568644, 0.013969, 0.000000, 11.347664, -474.452148, 0.024067, 0.000000, -312.743378, -279.984619, -0.999613, 0.000000, -8.489457, 2.428294, 0.009412, 1.000000, 
        #iptd: 0.001845, -0.000000, -0.000000, 0.000000, 0.000000, -0.001848, -0.000000, 0.000000, -0.575108, 0.489076, -1.000000, 0.000000, 0.000000, -0.000000, -0.000000, 1.000000, 
        #temp values from calibrated kinect using librgbd calibration from Nicolas Burrus
        ptd = numpy.array([485.377991, 7.568644, 0.013969, 0.000000, 
                           11.347664, -474.452148, 0.024067, 0.000000, 
                           -312.743378, -279.984619, -0.999613, 0.000000, 
                           -8.489457, 2.428294, 0.009412, 1.000000], 
                           dtype=numpy.float32)


        iptd = numpy.array([0.001845, -0.000000, -0.000000, 0.000000, 
                            0.000000, -0.001848, -0.000000, 0.000000, 
                            -0.575108, 0.489076, -1.000000, 0.000000, 
                            0.000000, -0.000000, -0.000000, 1.000000], dtype=numpy.float32)
        
        ptd = numpy.reshape(ptd, (4,4), order='C')
        #ptd = ptd.T
        iptd = numpy.reshape(iptd, (4,4), order='C')
        #iptd = iptd.T

        mf = cl.mem_flags
        self.depth_cl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=dempty)
        self.rgb_cl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=rgbempty)
        
        self.pt_cl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=ptd)
        self.ipt_cl = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=iptd)
        
        self.queue.finish()
        # set up the list of GL objects to share with opencl
        self.gl_objects = [self.pos_cl, self.col_cl]
        
    @timings
    def execute(self, sub_intervals):
        cl.enqueue_acquire_gl_objects(self.queue, self.gl_objects)

        global_size = (self.num,)
        local_size = None

        # set up the Kernel argument list
        w = numpy.int32(640)
        h = numpy.int32(480)
        kernelargs = (self.pos_cl, 
                      self.col_cl, 
                      self.depth_cl,
                      self.rgb_cl, 
                      self.pt_cl, 
                      self.ipt_cl, 
                      w,
                      h)

    
        for i in xrange(0, sub_intervals):
            self.program.project(self.queue, global_size, local_size, *(kernelargs))

        #pos = numpy.ndarray((self.imsize*4, 1), dtype=numpy.float32)
        #cl.enqueue_read_buffer(self.queue, self.pos_cl, pos).wait()
        #for i in xrange(0, 100, 4):
        #    print pos[i], pos[i+1], pos[i+2], pos[i+3]

        cl.enqueue_release_gl_objects(self.queue, self.gl_objects)
        self.queue.finish()
 

    def clinit(self):
        plats = cl.get_platforms()
        from pyopencl.tools import get_gl_sharing_context_properties
        import sys 
        if sys.platform == "darwin":
            self.ctx = cl.Context(properties=get_gl_sharing_context_properties(),
                             devices=[])
        else:
            self.ctx = cl.Context(properties=[
                (cl.context_properties.PLATFORM, plats[0])]
                + get_gl_sharing_context_properties(), devices=None)
                
        self.queue = cl.CommandQueue(self.ctx)

    def loadProgram(self, filename):
        #read in the OpenCL source file as a string
        f = open(filename, 'r')
        fstr = "".join(f.readlines())
        #print fstr
        #create the program
        self.program = cl.Program(self.ctx, fstr).build()


    def render(self):
        
        glEnable(GL_POINT_SMOOTH)
        glPointSize(2)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #setup the VBOs
        self.col_vbo.bind()
        glColorPointer(4, GL_FLOAT, 0, self.col_vbo)

        self.pos_vbo.bind()
        glVertexPointer(4, GL_FLOAT, 0, self.pos_vbo)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        #draw the VBOs
        glDrawArrays(GL_POINTS, 0, self.num)

        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        glDisable(GL_BLEND)
     


### python ile goruntu isleme bolge buyutme(regiongrowing) yapan kod
#### test icin ####
import Image,os


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enque(self, item):
        self.items.insert(0, item)

    def deque(self):
        return self.items.pop()

    def qsize(self):
        return len(self.items)
    
    def isInside(self, item):
        return item in self.items
        



def regiongrow(image, epsilon, start_point):

    Q = Queue()
    s = []
    
    x = start_point[0]
    y = start_point[1]
    
    image = image.convert("L")
    Q.enque((x, y))

    while not Q.isEmpty():

        t = Q.deque()
        x = t[0]
        y = t[1]
        
        if x < image.size[0]-1 and \
           abs(  image.getpixel( (x + 1 , y) ) - image.getpixel( (x , y) )  ) <= epsilon :

            if not Q.isInside( (x + 1 , y) ) and not (x + 1 , y) in s:
                Q.enque( (x + 1 , y) )

                
        if x > 0 and \
           abs(  image.getpixel( (x - 1 , y) ) - image.getpixel( (x , y) )  ) <= epsilon:

            if not Q.isInside( (x - 1 , y) ) and not (x - 1 , y) in s:
                Q.enque( (x - 1 , y) )

                     
        if y < (image.size[1] - 1) and \
           abs(  image.getpixel( (x , y + 1) ) - image.getpixel( (x , y) )  ) <= epsilon:

            if not Q.isInside( (x, y + 1) ) and not (x , y + 1) in s:
                Q.enque( (x , y + 1) )

                    
        if y > 0 and \
           abs(  image.getpixel( (x , y - 1) ) - image.getpixel( (x , y) )  ) <= epsilon:

            if not Q.isInside( (x , y - 1) ) and not (x , y - 1) in s:
                Q.enque( (x , y - 1) )


        if t not in s:
            s.append( t )

            
    image.load()
    putpixel = image.im.putpixel
    
    for i in range ( image.size[0] ):
        for j in range ( image.size[1] ):
            putpixel( (i , j) , 0 )

    for i in s:
        putpixel(i , 150)
        
    output=raw_input("enter save fle name : ")
    image.thumbnail( (image.size[0] , image.size[1]) , Image.ANTIALIAS )
    image.save(output + ".JPEG" , "JPEG")


i= Image.open("TEST.PNG")
epsilon = 23
seed = (130, 15)
regiongrow(i, epsilon, seed)
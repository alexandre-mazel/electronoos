from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio

def runLoopOscHandler(world, ip = "127.0.0.1", port = 8002):
    
    def filter_handler(address, *args):
        print(f"filter_handler:{address}: {args}")
        
        if "_labels" in address:
            # it's a label  => following values are name of values
            # eg: /global/label ["nom de la premiere valeur", "nom de la deuxieme valeur", ...]
            print("It's a label...")
            real_address = address.replace("_labels", "")
            world.receiveLabels(real_address,args)
            return
        world.receiveValues(address,args)
    # filter_handler - end
    
    def filter_handler_list(address, *args):
        print(f"filter_handler_list:{address}: {args}")
        world.receiveList(address,args)
        
    # filter_handler - end


    dispatcher = Dispatcher()
    dispatcher.map("/global", filter_handler)
    dispatcher.map("/global_labels", filter_handler)
    dispatcher.map("/u1", filter_handler)
    dispatcher.map("/u2", filter_handler)
    dispatcher.map("/src", filter_handler_list)
    dispatcher.map("/dst", filter_handler_list)
    dispatcher.map("/src_frame", filter_handler_list)
    dispatcher.map("/dst_frame", filter_handler_list)

    async def loop(world):
        """Example main loop that only runs for 10 iterations before finishing"""
        while 1:
            #~ print(f"Loop...")
            await asyncio.sleep(0.04) # 25fps
            bQuit = world.handleInput()
            world.update()
            if bQuit:
                break
            world.render()


    async def init_main(world):
        print("Running OSC Server on %s:%s" % (ip,port))
        server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
        transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

        await loop(world)  # Enter main loop of program

        transport.close()  # Clean up serve endpoint


    asyncio.run(init_main(world))
    
# runLoopOscHandler - end
    
    
import pygame as pg

successes, failures = pg.init()
print("INF: pygame int: %s successes and %s failure(s)" % (successes, failures))

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0) 
blue = (0, 0, 255)

fontTitleViewer = pg.font.SysFont('Arial', 16)
fontScaleViewer = pg.font.SysFont('Arial', 11)
fontListViewerBig = pg.font.SysFont('Arial', 15)
fontListViewerSmall = pg.font.SysFont('Arial', 11)

def smart(n):
    """
    convert to string in a compact form
    """
    units = [
                    [1024*1024*1024*1024, "T"],
                    [1024*1024*1024, "G"],
                    [1024*1024, "M"],
                    [1024, "k"],
                ]
    for mul,unit in units:
        if n > mul:
            return "%.1f %s" % (n/mul,unit)
    if isinstance(n,int):
        return "%s" % n
    return "%.2f" % n
    

class ValueViewer:
    """
    An oscilloscope like to view a value over time
    """
    def __init__(self,x=10,y=10,w=200,h=100,title="Value"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.color = (255,244,255)
        self.text_surface = fontTitleViewer.render(self.title, True, self.color)
        self.values  = []
    
    def setTitle(self, s ):
        self.title = s
        self.text_surface = fontTitleViewer.render(self.title, True, self.color)
        
    def update(self,rVal):
        self.values.append(rVal)
        
    def render(self, surf):
        bVerbose = 1
        bVerbose = 0
        
        color = self.color
        x,y = self.x,self.y
        x2 = self.x+self.w
        y2 = self.y+self.h
        th = 1 # thickness of the line
        htitle=24
        titlemargin = 4
        softcolor = (64,64,64)
        fillcolor = (40,128,40)
        pg.draw.rect(surf,softcolor,(x,y,self.w,htitle),0)
        pg.draw.line(surf,color,(x,y),(x2,y),width=th)
        pg.draw.line(surf,color,(x,y+htitle),(x2,y+htitle),width=th)
        pg.draw.line(surf,color,(x,y),(x,y2),width=th)
        pg.draw.line(surf,color,(x,y2),(x2,y2),width=th)
        pg.draw.line(surf,color,(x2,y),(x2,y2),width=th) 
        surf.blit(self.text_surface, (x+titlemargin,y+titlemargin))
        
        if bVerbose: print("ValueViewer.render: title: '%s', value: %s" % (self.title,self.values))
        
        if len(self.values)<1:
            return
            
        if len(self.values) >= self.w-1:
            self.values = self.values[-(self.w-1):]
            
        hutil = (self.h-htitle)-5 # 5 for a bit of margin around max
        
        # variable finishing by pixels are exprimed in pixels from the center of the graph (ycenter_pixels)
        
        ycenter_pixels = y+htitle+4+hutil//2 # hauteur de trace du milieu du graph en pixel
        maxval = max(self.values)
        minval = min(self.values)
        variationmax = maxval-minval
        offset = minval + variationmax / 2.  # average value (we will offset the graph so this value will be rendered at the center of the graph)
 
        if variationmax > 0:
            zoomy = (hutil/variationmax)*0.5
        else:
            # minval == maxval
            if minval == 0:
                zoomy = 1
            else:
                zoomy = abs((hutil/minval))*0.4 # it should take only half the screen with the zero visible
                offset = 0 # we want to see the zero
                
        offset_pixels = -int(offset*zoomy)
        offset_pixels = 0 # pas la peine de calculer l'offset car il est deja inclus dans le calcul
            
            
        if bVerbose: print("DBG: ValueViewer: title: %s, min: %.2f, max: %.2f, variationmax:%.2f, zoomy: %.2f, offset: %.2f, offset_pixels: %.2f" % (self.title,minval, maxval, variationmax,zoomy,offset,offset_pixels) )
        
        x += 1 # small decayt
        for i,val in enumerate(self.values):
            xv = i
            val_pixels = int((val-offset)*zoomy)
            if bVerbose: print("DBG: val: %s, val_pixels: %s, ycenter_pixels: %s" % (val,val_pixels,ycenter_pixels))
            
            yzero_pixels = int((0-offset)*zoomy)
            if bVerbose: print("DBG: yzero_pixels: %s" % (yzero_pixels))
            
            y_rendered = ycenter_pixels-val_pixels #+offset_pixels
            if bVerbose: print("DBG: y_rendered: %s" % (y_rendered))
            
            
            # fill to zero
            yfill_rendered = ycenter_pixels-yzero_pixels
            if yfill_rendered != y_rendered:
                if yfill_rendered>y2:
                    yfill_rendered = y2
                if yfill_rendered<y+htitle+1:
                    yfill_rendered = y+htitle+1
                
                if yfill_rendered<y_rendered:
                    y_rendered -= 1
                else:
                    y_rendered += 1
                pg.draw.line(surf, fillcolor, (x+xv, yfill_rendered), (x+xv, y_rendered) )
                
            # render zero line
            if abs(yzero_pixels)<=hutil/2:
                yzero_rendered = ycenter_pixels-yzero_pixels #+offset_pixels
                if bVerbose: print("DBG: yzero_rendered: %s" % (yzero_rendered))
                surf.set_at((x+xv, yzero_rendered), softcolor)
                
            # render value
            surf.set_at((x+xv, y_rendered), color) # just one point
    
        if 1:
            # write scales
            s = "%.2g" % maxval #  "+%.2g" is nice also
            scale = fontScaleViewer.render(s, True, self.color)
            surf.blit(scale, (x+titlemargin,y+titlemargin+22))
            s = "%.2g" % minval
            scale = fontScaleViewer.render(s, True, self.color)
            surf.blit(scale, (x+titlemargin,y+self.h-15))
            
#class ValueViewer - end
            
class ListViewer:
    """
    Render a list of information and values
    """
    def __init__(self,x=10,y=10,w=300,h=100,title="Value"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.htitle = 24
        self.xOffColumn0 = 0
        self.xOffColumn1 = 200
        self.xOffColumn2 = 240
        self.color = (255,244,255)
        self.text_surface = fontTitleViewer.render(self.title, True, self.color)
        self.values  = []
        self.numSort = 2 # wich colum to use for sort
        self.bSortReverse = True
    
    def setTitle(self, s ):
        self.title = s
        
    def update(self,rVal):
        self.values = rVal
        
    def reactToClick(self,click_pos):
        """
        return True if click has been handled
        """
        x,y = click_pos
        if x<self.x or x>self.x+self.w:
            return False
        if y<self.y or y>self.y+self.h:
            return False
        offsety = y-self.y
        nClickOnColumn = -1
        if offsety < self.htitle:
            offsetx = x-self.x
            if offsetx < self.xOffColumn1:
                nClickOnColumn = 0
            elif offsetx < self.xOffColumn2:
                nClickOnColumn = 1
            else:
                nClickOnColumn = 2  
        if nClickOnColumn != -1:
            if nClickOnColumn != self.numSort:
                self.numSort = nClickOnColumn
                self.bSortReverse = True
            else:
                self.bSortReverse = not self.bSortReverse
            
        
    def render(self, surf):
        bVerbose = 1
        bVerbose = 0
        
        color = self.color
        x,y = self.x,self.y
        x2 = self.x+self.w
        y2 = self.y+self.h
        
        th = 1 # thickness of the line
        htitle=self.htitle
        titlemargin = 4
        softcolor = (64,64,64)
        fillcolor = (40,128,40)
        pg.draw.rect(surf,softcolor,(x,y,self.w,htitle),0)
        pg.draw.line(surf,color,(x,y),(x2,y),width=th)
        pg.draw.line(surf,color,(x,y+htitle),(x2,y+htitle),width=th)
        pg.draw.line(surf,color,(x,y),(x,y2),width=th)
        pg.draw.line(surf,color,(x,y2),(x2,y2),width=th)
        pg.draw.line(surf,color,(x2,y),(x2,y2),width=th) 
        surf.blit(self.text_surface, (x+titlemargin,y+titlemargin))
        
        if len(self.values) < 20:
            fontToUse = fontListViewerBig
            hfont = 17
        else:
            fontToUse = fontListViewerSmall
            hfont = 11
        
        if 1:
            # render sort sign
            self.xSort = (self.xOffColumn0 + self.xOffColumn1 ) //2
            if self.numSort == 1:
                self.xSort = self.xOffColumn1
            elif self.numSort == 2:
                self.xSort = self.xOffColumn2
                
            #pg.draw.rect(surf,fillcolor,(x+self.xSort+10,y+8,10,10),0)
            if self.bSortReverse: dir=6
            else: dir = -6
                
            pg.draw.polygon(surf,fillcolor,( (x+self.xSort+10,y+12),(x+self.xSort+10+10,y+12),(x+self.xSort+10+5,y+12+dir) ),0)
        
        if bVerbose: print("ListViewer.render: title: '%s', value: %s" % (self.title,self.values))
        
        if len(self.values)<1:
            return
            
            
        hutil = (self.h-htitle)-5 # 5 for a bit of margin around max
        
        # variable finishing by pixels are exprimed in pixels from the center of the graph (ycenter_pixels)
        
            
        if bVerbose: print("DBG: ListViewer: title: %s, values: %s" % (self.title, str(self.values)))

        vSorted = sorted(self.values,key=lambda x:x[self.numSort], reverse=self.bSortReverse)
        
        for i, v in enumerate(vSorted):
            xv = i
            lib = v[0]
            cpt = v[1]
            vol = v[2]
            s = "%s" % lib
            yline = i*hfont
            if yline>=self.h-htitle-10:
                break
            if bVerbose: print( "DBG: ListViewer: i: %d, lib: %s" % (i,lib))
            libr = fontToUse.render(s, True, self.color)
            surf.blit(libr, (x+titlemargin+self.xOffColumn0,y+htitle+yline))
            
            s = "%s" % cpt
            libr = fontToUse.render(s, True, self.color)
            surf.blit(libr, (x+titlemargin+self.xOffColumn1,y+htitle+yline))
            
            s = smart(vol)
            libr = fontToUse.render(s, True, self.color)
            surf.blit(libr, (x+titlemargin+self.xOffColumn2,y+htitle+yline))

            
#class ValueViewer - end


class Object:
    def __init__(self,x=10,y=10,w=32,h=32):
        self.x = w
        self.y = y
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0

# class Object - end

class World:
    def __init__(self):
        w = 1380
        h = 1024
        if 0:
            # reduce screen to see debug
            w = 640
            h = 480
        self.screen = pg.display.set_mode((w,h))
        self.clock = pg.time.Clock()
        self.fps = 60  # Frames per second.
        
        self.square = Object()
        self.square.img = pg.Surface((self.square.w, self.square.h))
        self.square.img.fill(white)
        self.square.x = 0
        self.square.y = 0
        self.square.vx = 5
        self.square.vy = 0
        
        self.keypressed={} # will store current keyboard pressed
        
        self.vviewers = {} # key => ValueViewer
        
        self.lviewers = {} # key => ListViewer
        
        
    def handleInput(self):
        """
        Analyse user command
        return True if user want to quit
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
                
            if event.type == pg.KEYDOWN:     
                print("DBG: key '%s' pressed" % event.key )
                self.keypressed[event.key] = 1
                
            if event.type == pg.KEYUP:
                self.keypressed[event.key] = 0
                
                    
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                for k,v in self.lviewers.items():
                    v.reactToClick(pos)
                
        for key, bPressed in self.keypressed.items():
            if bPressed:
                if key == pg.K_a or key == pg.K_UP:
                    #~ self.square.y -= 1
                    self.square.vy -= 1
                elif key == pg.K_q or key == pg.K_DOWN:
                    self.square.y += 1
                elif key == pg.K_ESCAPE:
                    return True
                    
        return False
        
    def receiveValues(self,strName, values):
        """
        for each tag strName, receive a list of values, each of them will be added to one ValueViewer
        """
        
        print("DBG: receiveValues: '%s': %s" % (strName,values) )
        #self.vviewers[0].update(values[0])
        for i,v in enumerate(values):
            key = strName + "_" + ("%02d"%i)
            try:
                self.vviewers[key].update(v)
            except KeyError as err:
                x = (len(self.vviewers)%5)*200
                y = (len(self.vviewers)//5)*100
                self.vviewers[key] = ValueViewer(x=x,y=y,title=key)
                self.vviewers[key].update(v)
                
    def receiveLabels( self, strName, labels):
        #~ print("DBG: receiveLabels: '%s': %s" % (strName,labels) )
        #self.vviewers[0].update(values[0])
        for i,s in enumerate(labels):
            key = strName + "_" + ("%02d"%i)
            #~ print("DBG: receiveLabels: %s => %s" % (key,s))
            try:
                self.vviewers[key].setTitle(s)
            except KeyError as err:
                x = (len(self.vviewers)%5)*200
                y = (len(self.vviewers)//5)*100
                self.vviewers[key] = ValueViewer(x=x,y=y,title=s)
                
    def receiveList( self, strName, values):
        """
        receive stat relative to one type of information strName
        - values is a list of [nbr_event, sum data]
        """
            
        print("DBG: receiveList: '%s': %s" % (strName,values) )
        
        key = strName
        try:
            self.lviewers[key].update(values)
        except KeyError as err:
            x = (len(self.lviewers)%5)*300
            y = 400-(len(self.lviewers)//5)*100
            self.lviewers[key] = ListViewer(x=x,y=y,title=key,h=600)
            self.lviewers[key].update(values)
    
    def update(self):
        """
        Update internal state of the world
        """
        
        self.clock.tick(self.fps)
        
        self.square.x += self.square.vx
        self.square.y += self.square.vy
        
        self.square.vy += 0.2
        
        # out of screen test
        if      (self.square.vx > 0 and self.square.x + self.square.w > self.screen.get_width()) \
            or (self.square.vx < 0 and self.square.x < 0) \
            :
            self.square.vx *= -1
            
        if self.square.y < 0: 
            self.square.y = 0
        if self.square.vy > 0 and self.square.y + self.square.h> self.screen.get_height(): 
            self.square.y = self.screen.get_height()-self.square.h
            self.square.vx *=0.9
            self.square.vy *= -0.7
            if abs(self.square.vy)<1.:
                self.square.vy = 0
            if abs(self.square.vx)<0.2:
                self.square.vx = 0
                
    def render(self):
        """
        Show a representation of the world to the user
        """
        self.screen.fill(black)
        self.screen.blit(self.square.img, [self.square.x,self.square.y,self.square.x+self.square.w,
                                                                                                self.square.y+self.square.h] )
                                                                                                
        #~ self.screen.set_at((100, 300), (255,255,233)) 
        #~ self.screen.set_at((110, 300), (255,255,233)) 
        
        for k,v in self.vviewers.items():
            v.render(self.screen)
            
        for k,v in self.lviewers.items():
            v.render(self.screen)
        
        
        pg.display.update()  # or pg.display.flip()
        
# class World - end

if __name__ == "__main__":
    world = World()
    runLoopOscHandler(world)

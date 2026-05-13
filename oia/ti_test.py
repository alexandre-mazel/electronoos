class polyscr:
  w, h, w0, h0, x0, y0 = 0, 0, 0, 0, 0, 0
  # get_pixel(x, y)
  # set_pixel(x, y, color(r8, g8, b8))
  show_screen = lambda self: None
  need_show_screen = False
  # color mode :
  # 0: (R8, G8, B8)
  # 1: int RGB-565
  color_mode = 0

  def color(self, r, g=0, b=0):
    if isinstance(r, tuple) or isinstance(r,list):
      r, g, b = r[0], r[1], r[2]
    return self.color_mode == 0 and (r,g,b) or r<<11 | g<<5 | b

  def __init__(self):

    try: # TI-Nspire Ndless
      from nsp import Texture as myscr
      self.w, self.h = 320, 240
      myscr = myscr(self.w, self.h, None)
      self.get_pixel = myscr.getPx
      self.set_pixel = myscr.setPx
      self.show_screen = myscr.display
      self.need_show_screen = True
      self.color_mode = 1

    except:

      try: # TI-83/84 CE
        import ti_graphics as myscr
        self.get_pixel = myscr.getPixel
        self.set_pixel = myscr.setPixel

      except ImportError:

        try: # Casio USB Power Graphic 3
          import casioplot as myscr
          self.show_screen = myscr.show_screen
          self.need_show_screen = True

        except ImportError: # NumWorks
          import kandinsky as myscr

        self.get_pixel = myscr.get_pixel
        self.set_pixel = myscr.set_pixel

    # detect readable pixel array
    if self.w <= 0:

      def _can_get_pixel(x, y):
        c = self.get_pixel(x, y)
        if c == self.color(0, 0, 0):
          self.set_pixel(x, y, self.color(255,0,0))
          c = self.get_pixel(x, y)
        return c is not None and c != self.color(0, 0, 0)

      self.w, self.h, dw, dh = 0, 0, 1, 1
      while dw or dh:
        if not _can_get_pixel(self.w - (dw == 0),self.h - (dh == 0)):
          if _can_get_pixel(self.w,self.h-1): dh = 0
          elif _can_get_pixel(self.w-1,self.h): dw = 0
          else: dw, dh = 0, 0
        self.w += dw;  self.h += dh

    # detect writable pixel array
    # remove top status bar

    def _can_set_pixel(x, y):

      def _invert_color(r, g=0, b=0):
        if isinstance(r, tuple) or isinstance(r,list):
          r, g, b = r[0], r[1], r[2]
        return self.color(~r & 0xFF, ~g & 0xFF, ~b & 0xFF)

      c = self.get_pixel(x, y)
      self.set_pixel(x, y, _invert_color(c))
      return c != self.get_pixel(x, y)

    self.w0, self.h0 = self.w, self.h
    while not _can_set_pixel(0, self.y0):
      self.y0 += 1; self.h0 -= 1
      
# class polyscr - end


#from polyscr import *

scr = polyscr()

def hsv2c(h,s,v):
  c=v*s
  x,m,k=c*(1-abs((h%(2/3))*3-1)),v-c,(h*3)//1
  return (round(255*(m+x*(k%3==1)+c*(k%5==0))),round(255*(m+c*(k==1 or k==2)+x*(k%3==0))),round(255*(m+x*(k%3==2)+c*(k==3 or k==4))))

def grad(x,y,w,h):
  for i in range(w):
    for j in range(h):
      c=hsv2c(2*j/(h-1),i>=w//2 and 1 or i/(w//2-1),i<w//2 and 1 or (w-1-i)/((w-w//2)-1))
      scr.set_pixel(x+i,y+j,c)
      
    

grad(scr.x0, scr.y0, scr.w0, scr.h0)
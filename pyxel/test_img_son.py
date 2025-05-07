import pyxel

class App:
    def __init__(self):
        pyxel.init(128, 128, title="Nuit du Code")
        self.x = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            
        self.x = (self.x + 1) % pyxel.width


    def draw(self):
        pyxel.cls(0)
        pyxel.rect(self.x, 0, 8, 18, 15) # x, y, w, h, color
         
    def run(self):
        pyxel.run(self.update, self.draw)
         
app = App()
app.run()
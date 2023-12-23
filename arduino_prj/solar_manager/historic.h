#ifndef HISTORIC_H
#define HISTORIC_H

class Historic
{
  // a class to store values and be able to draw them on a display (oled or ...)
  public:
    Historic( int w ); // historic: nbr of value to memorize
    void append( int v );

    // x and y: left bottom corner of the graphic
    // hmax: height maximum for the graph
    void drawGraphicOled( int x, int y, void * pOledObject, int hmax = 32 );

  private:
    int * values_;
    int w_; // size max
    int n_; // current values
};

#endif // HISTORIC_H
#ifndef HISTORIC_H
#define HISTORIC_H

class Historic
{
  // a class to store values and be able to draw them on a display (oled or ...)
  public:
    Historic(int w); // historic: nbr of value to memorize
    void append(int v);

    void sendToOled(int x, int y, void * pOledObject);

  private:
    int * values_;
    int w_; // size max
    int n_; // current values
};

#endif // HISTORIC_H
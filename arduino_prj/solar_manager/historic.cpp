#include "historic.h"

Historic::Historic(int w)
{
  w_ = w;
  values_ = (int*)malloc(w_*sizeofint));
  n_ = 0;
}

void Historic::append(int v)
{
  if(n_+1>=w_)
  {
    // eat one value
    --n_;
    memcpy(values_,values_+1,n_);
  }
  values_[n_] = v;
  ++n_;
}
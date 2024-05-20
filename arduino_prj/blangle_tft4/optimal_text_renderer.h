// Optimal Text Renderer
// for a tft, erase only the changing portion of a text (erasing only usefull background)

#ifndef OPTIMAL_TEXT_RENDERER_H
#define OPTIMAL_TEXT_RENDERER_H


class MCUFRIEND_kbv;

class OptimalTextRenderer {
    public:
        OptimalTextRenderer(int colorBackground, int colorText, int nSizeText, int x, int y, int nNbrCharMax = 16 );
        ~OptimalTextRenderer();

        void render( MCUFRIEND_kbv * pTft, const char * txt, int bForceRedrawAll = 0 );

    private:
      int colorBackground_;
      int colorText_;
      int nSizeText_;
      int x_;
      int y_;
      int nNbrCharMax_;
      char * lastRenderedText_;


}; // class OpimalTextRenderer

#endif // OPTIMAL_TEXT_RENDERER_H
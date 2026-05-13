/*
 * Didier : july 2020
 * Alexandre: fev 2024
 * Very Ligth Serial Cmd Parser 
 * usage:
 *  readLine(): returns pstr  or NULL
 *  separators: ' ' ',' ':' '='
 *  getString(); returns pstr or NULL 
 *  getFloat();  returns float or NAN
 *  getValue(); parses name:number ; name is given by valueName; returns float or Nan
 */

 #include <Arduino.h>

class SerialParser 
{
  public:

    SerialParser();

    char* readLine(); // return NULL when no more line in buffer

    // all following functions return next data in the flow

    int nextField();

    char* getStr();
    float getFloat();
    float getValue();

  private:
    int       writeIndex_;
    int       readIndex_;
    boolean   eol_;
    char*     valueName_;

    char      bufferW_[512];
 
};

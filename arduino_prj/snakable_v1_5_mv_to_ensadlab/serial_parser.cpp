#include "serial_parser.h"

SerialParser::SerialParser()
  : writeIndex_ (0)
  , readIndex_ (0)
  , eol_ (true)
{
  valueName_ = NULL;
  bufferW_[0]=0;
}

char* SerialParser::readLine()
{      
  eol_ = true;
  while( Serial.available() ){
    char c = Serial.read();
    if( c<32 ){
      bufferW_[writeIndex_]=0;
      writeIndex_ = 0;
      readIndex_ = 0;
      eol_ = false;
      //for(int i=0)i<bufIndex;
      return bufferW_;        
    }
    else if( writeIndex_ < 255 ){
      bufferW_[writeIndex_++] = c;
      bufferW_[writeIndex_] = 0;
    }
  }
  return NULL;
}

int SerialParser::nextField()
{
  char c = bufferW_[readIndex_];
  while( (c==' ')||( c==',' )||( c==':' )||( c=='=' )  ){
    c = bufferW_[++readIndex_];
  }
  return readIndex_;
}

char* SerialParser::getStr()
{
  int idx = nextField();
  char c = bufferW_[readIndex_];
  while( (c>' ') && ( c!=',' ) && ( c!=':' ) && ( c!='=' )  ){
    c = bufferW_[++readIndex_];    
  }
  bufferW_[readIndex_]=0;
  eol_ = (c < 32); //endofLine
  if(!eol_) //not eol
    readIndex_++;
      
  return &bufferW_[idx];
}

float SerialParser::getFloat()
{
  char* pstr = getStr();
  if( (*pstr>='-')&&(*pstr<='9') ) 
    return atof( pstr); //return 0 if not a number
  return NAN;
}

float SerialParser::getValue()
{ //name = this.valueName;
  char* pstr = getStr();
  if( (*pstr>='-')&&(*pstr<='9') ){ //isNum
    valueName_ = NULL;
    return atof( pstr);   
  }
  valueName_ = pstr;
  return getFloat();    
}


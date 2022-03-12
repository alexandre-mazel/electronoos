@ echo off
rem cf push.bat
IF "%1"=="" (
  @cd /D %PUSH_DIR%
) ELSE (
rem try to enable a "pop 2 "that will jump to POP_DIR2, works but the cd doesnt execute!

  setlocal enableDelayedExpansion
  set varname=PUSH_DIR%1
  set pathdir=!%varname%!
rem endlocal enableDelayedExpansion
  rem echo changing...
  rem (cmd /c cd %pathdir%)
  
  (changedir %pathdir%)
)

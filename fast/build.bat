@echo off
rem Build the solver with MSVC (run from any prompt; sets up the compiler env).
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
cd /d "%~dp0"
cl /nologo /O2 /std:c++17 /EHsc /openmp:llvm /arch:AVX2 ca_quotient.cpp /Fe:ca_quotient.exe

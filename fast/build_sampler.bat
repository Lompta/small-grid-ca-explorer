@echo off
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
cd /d "%~dp0"
cl /nologo /O2 /std:c++17 /EHsc /openmp:llvm /arch:AVX2 sample_runs.cpp /Fe:sample_runs.exe

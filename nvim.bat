@setlocal
@pushd %~dp0
@%~dp0\nvim.py %*
@if not [%errorlevel%]==[1] goto :end

@%~dp0\bin\nvim-qt.exe %*
@del %~dp0\nvim.txt

:end
@popd


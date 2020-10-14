@setlocal
@pushd %~dp0
:: @if not exist servername.txt goto nvimqt
@%~dp0\nvim.py %*
@if not [%errorlevel%]==[1] goto :end

@:nvimqt
@%~dp0\bin\nvim-qt.exe %*
:: @time /t >> %~dp0\servername.log
:: @type %~dp0\servername.txt >> %~dp0\servername.log
@del %~dp0\nvim.txt

:end
@popd


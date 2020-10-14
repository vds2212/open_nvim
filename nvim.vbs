ReDim arrCmd(WScript.Arguments.Count + 1)
arrCmd(0) = "cmd /c C:\Softs\Neovim\nvim.bat"

For i = 0 To WScript.Arguments.Count - 1
    Arg = WScript.Arguments(i)
    'WScript.Echo WScript.Arguments(i)
    If InStr(Arg, " ") > 0 Then Arg = """" & Arg & """"
    arrCmd(i + 1) = Arg
Next

Dim strCmd
strCmd  = Join(arrCmd)

Set oShell = CreateObject("WScript.Shell")
oShell.Run strCmd, 0, true

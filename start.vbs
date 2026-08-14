Option Explicit
' ASCII-only. WSH cannot compile UTF-8 .vbs files.
Dim fso, sh, dir, cmd
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = dir

Function Ok(line)
  Ok = (sh.Run("cmd /c " & line & " >NUL 2>NUL", 0, True) = 0)
End Function

cmd = ""
If Ok("pyw -3 -c ""import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)""") Then
  cmd = "pyw -3 server.py"
ElseIf Ok("pythonw -c ""import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)""") Then
  cmd = "pythonw server.py"
ElseIf Ok("py -3 -c ""import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)""") Then
  cmd = "py -3 server.py"
ElseIf Ok("python -c ""import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)""") Then
  cmd = "python server.py"
End If

If cmd = "" Then
  MsgBox "Python 3.12+ not found. Install official Python and check Add python.exe to PATH.", 16, "Console"
  WScript.Quit 127
End If

sh.Run "cmd /c " & cmd, 0, False

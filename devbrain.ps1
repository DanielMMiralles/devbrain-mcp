$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& py -3.12 -u "$ScriptDir\src\devbrain_cli.py" @args

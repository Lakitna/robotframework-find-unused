Output "/app/docs/gif/files/files.gif"

Set Shell "bash"
Set FontSize 18
Set Width 1000
Set Height 600
Set Padding 20
Set Margin 0
Set CursorBlink false

Hide
    Type "pip install -r requirements.txt --editable /app"
    Enter
    Wait

    Type "clear"
    Enter
Show

Type "robotunused files"
Sleep 200ms
Enter
Wait
Sleep 7s

Type "robotunused files --show-count"
Sleep 1200ms
Enter
Wait
Sleep 8s

Type "robotunused files --show-tree"
Sleep 1200ms
Enter
Wait
Sleep 8s

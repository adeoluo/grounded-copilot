# Records docs/demo/ask.gif from a real run: `vhs docs/demo/ask.tape` from the repo root.
Output docs/demo/ask.gif
Set Shell "bash"
Set FontSize 15
Set Width 1300
Set Height 460
Set Padding 18
Set Theme "Catppuccin Mocha"
Set TypingSpeed 22ms

Hide
Type `export PS1='$ ' && uv sync -q && source .venv/bin/activate && clear` Enter
Sleep 10s
Show
Type `python -m grounded_copilot ask "What is the deepest ocean?"` Enter
Sleep 2.5s
Type `python -m grounded_copilot ask "Who painted the Mona Lisa?"` Enter
Sleep 2.5s
Type `python -m grounded_copilot ask "Why is Mars called the red planet?"` Enter
Sleep 3s

# online_chess

Chess is one of the oldest and most popular board games. It is played by two opponents on a checkered board with specially designed pieces of contrasting colours, commonly white and black. The objective of the game is to capture the opponent's king.

With Online_chess game, we can play this chess game online together

### Start Game:

Make sure you have the tkmacosx module and the tkinter module or you can download it by:

```bash
pip install tkmacosx
pip install tk
```

Clone repository
```bash
git clone git@github.com:OnesNT/online_chess.git
```
Run server:
```bash
cd online_chess
git checkout dev1
python3 server.py
```

Run game:
```bash
cd online_chess
git checkout dev1
python3 main.py
```

### Play game: 

<img width="1194" alt="Screen Shot 2022-12-03 at 20 49 07" src="https://user-images.githubusercontent.com/113534334/205454725-da016e74-ae05-41fa-8637-548b983e74d5.png">

At first, we need to fill in Server address and Server Port, if you leaves the blank, it will be default connect ,so don't need to fill anything otherwise you can fill address 0.0.0.0:4000 to connect to server.

Then fill your username to easily found by your opponent. If you leaves the blank, it will default your name as "Guess N-th" , which N is the ordinal numbers login to the server

<img width="1194" alt="Screen Shot 2022-12-03 at 21 01 07" src="https://user-images.githubusercontent.com/113534334/205455196-025e5da0-4ff1-49b1-b8d9-a3e5ea26d45d.png">

After filling anything, you will need to find your opponent, if you enter the correct opponent's name, game will match you to your opponent you are finding. If you leaves the blank then there will be random opponent for you




https://user-images.githubusercontent.com/113534334/205457833-1d9c7963-6829-4180-9dea-880a296e0dc1.mp4




As you see, if A and B play a game online, every move made by A then board B is also updated and vice versa

### Extra features:

+ Texting to your opponent while playing
+ If there is a winner there will be a result board and the game is over
+ Support for multiple game sessions at the same time






# Protocol

The regular workflow is:

* acquiring a user
* sending `READY` signal to the server
* waiting for all the users to be ready
* starting the game
* server sends the game details to the clients
* clients send the changes in the paddles position 
* when the game is over, server sends `GAMEOVER` signal

When game is over, the users should send `READY` signal one more time in
order to start another game.

## Acquiring User

Right after the connection is established the server sends a message to
the client notifying it if the user was successfully acquired.

```
< OK            # if a user was successfully acquired
< SERVER_FULL   # if the server is full, all the users are already acquired
```

## Before Game is Started

The server waits for the `READY` signals from both users. Till then it
sends no information to the users.

The client `READY` signal looks like this:

```
> READY
```

As soon as the server got the both `READY` signals, it begins the game.

## Game Details

The server sends the state of the game in the following format:

```
< STATE
< {"you": {"pos": 0}, "opponent": {"pos": 0}, "ball": {"pos": {"x": 0, y: "0"}}}
```

## User Actions

User can move its paddle up or down. Correspoding commands are:

```
> UP
> DOWN
```

## End of the Game

If one of the user missed the ball, the game is stopped and the
information about the result is being sent to the users:

```
< GAMEOVER
< {"status": "loser", "score": {"you": 0, "opponent": 1}}
```

After that the server switches to the waiting mode and waits for the
`READY` signals from the users.

## The Example of the Connection

```
< OK
> READY
< STATE
< {"you": {"pos": 0}, "opponent": {"pos": 0}, "ball": {"pos": {"x": 0, y: "0"}}}
< ...
< ...
> UP
> UP
< STATE
< {"you": {"pos": 50}, "opponent": {"pos": -30}, "ball": {"pos": {"x": 100, y: "20"}}}
< ...
< GAMEOVER
< {"status": "loser", "score": {"you": 0, "opponent": 1}}
```

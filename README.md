# chatserv

**CSEE 4119, HW 3**: Javier Llaca Ojinaga (jl3960)

A TCP chat application written in python.

## Protocol

### Authentication

#### Username

Once the connection is established between the server and the client, the
client sends a username to the client. The server then considers the following cases:

- The username is valid: the server responds with `password` and we proceed
  with password authentication.
- The username is invalid: the server responds with `register`. If the client
  responds with `y`, the server responds with `password`, waiting until the
  client sends two lines with the same password. Otherwise, the server responds
  with `username` and we restart username authentication.
- The user is already connected: the server responds with `connected` and we
  restart user authentication.
- The user has been blocked at this IP address: the server responds with
  `blocked:x`, where x is the number of seconds left for the block on logins
  for this user from this IP address to be lifted.


#### Password

The client sends the password corresponding to the authenticated username. If
this fails three times, the server sends the number of seconds during which
logins for this user from this IP address will be blocked.

### Chatting

Once the user is logged in, the server sends newline-separated messages from
the user's message queue followed by a line with the string `DONE`. The client
then sends a command string and the server responds accordingly. This process
(emptying the message queue and processing a command) is repeated until the
user enters the command `logout`, upon which the server logs the user out and
terminates the connection with the client.

## Commands

- `who`: Display users curently online
- `last <minutes>`: Display users online in the last number of minutes
- `broadcast <message>`: Send message to all users
- `send <user> <message>`: Send message to user
- `send (<user> ... <user>) <message>`: Send message to group of users
- `logout`: Logout from chat server
- `fetch`: Fetch messages in message queue.

### Error-handling

#### Send to invalid usernames

If the users argument for the send command includes invalid usernames, the
server will respond with `send:x`, where `x` is a comma-separated list of
invalid usernames.

#### Invalid commands or arguments

If a command or its arguments are invalid, the server will responds with
`error:command:x` and `error:args:x`, respectively, where `x` is the command.

#### Timeouts

If at any moment the client receives the string `timeout`, it means that the
client has exceeded the time during which it may be inactive. This is defined
in seconds by the `TIME_OUT` environment variable where the server is run.

## Server Program

The server program implements the protocol defined above.

### Extra-features

#### New user registration

If the username entered upon login is invalid, it is possible to register a new
username. Once the new username is validated (after entering a password and
verifying it, the username-password combination is appended to the
`user_pass.txt` file.

#### Offline messaging

Since each user has a dedicated message queue, it is possible to send messages
to users who are not currently online. That is, user A sends a message to user
B who is online, and whenever user B logs in, the server will dump any messages
that were stored in user B's message queue.

## Client Program

The client program provides a convenient interface for communicating with the
server while following the protocol defined above. There are a few things to be noted:

- During authentication, empty strings are ignored. That is, the client will
  prompt the user for strings until their input is non-empty.
- In the command loop, if the user enters either the empty string or the `help`
  command, which displays a list of valid commands and their usage, the client
  will by default send the `fetch` command to the server.

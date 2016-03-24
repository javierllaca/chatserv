# chatserv

**CSEE 4119, HW 3**: Javier Llaca Ojinaga (jl3960)

A TCP chat application written in python.

## Protocol

### Authentication

#### Username

Once the connection is established between the server and the client, the
client sends a username to the client. The server then considers the following cases:

- The username is valid: the server responds with 'password' and we proceed
  with password authentication.
- The username is invalid: the server responds with 'register'. If the client
  responds with 'y', the server responds with 'password', waiting until the
  client sends two lines with the same password. Otherwise, the server responds
  with 'username' and we restart username authentication.
- The user is already connected: the server responds with 'connected' and we
  restart user authentication.
- The user has been blocked at this IP address: the server responds with
  'blocked:x', where x is the number of seconds left for the block on logins
  for this user from this IP address to be lifted.


#### Password

The client sends the password corresponding to the authenticated username. If
this fails three times, the server sends the number of seconds during which
logins for this user from this IP address will be blocked.

### Chatting

Once the user is logged in, the client sends a command string, which the server
parses and responds to accordingly. The following

### Error-handling

#### Send to invalid usernames

#### Commands

Command strings can yield two errors: invalid commands and invalid arguments.

#### Timeouts

If at any moment the client receives the string 'timeout', it means that the
client has exceeded the time during which it may be inactive. This is defined
in seconds by the `TIME_OUT` environment variable where the server is run.

## Server Program

hello

### Extra-features

#### New user registration

hello

#### Offline messaging

Each user has a thread-safe message queue, which is used by the server to enqueue messages

## Client Program

hello

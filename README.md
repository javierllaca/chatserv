# chatserv

*CSEE 4119, HW 3*
*Name*: Javier Llaca Ojinaga
*UNI*: jl3960


A TCP chat application written in python. The server and client programs adhere
to the protocol defined below:

## Protocol

### Authentication

Once the connection is established between the server and the client, the
client sends a username to the client. The server then considers the following cases:

- The username is valid
- The username is invalid
- The user is already active
- The user has been blocked at this IP address

### Chatting

### Error-handling

#### Send to invalid usernames

#### Commands

adsf

#### Timeouts

If at any moment the client receives the string 'timeout', it means that the
client has exceeded the time during which it may be inactive. This is defined
in seconds by the `TIME_OUT` environment variable where the server is run.


## Extra-features

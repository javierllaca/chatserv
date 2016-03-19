import re

COMMAND_TOKEN_REGEX = re.compile(r'\(.*\)|\'.*\'|\S+')

def parse_command(command_string):
    tokens = [match.group(0) for match in COMMAND_TOKEN_REGEX.finditer(command_string)]
    if not tokens:
        return False
    command, args = tokens[0], tokens[1:]
    for i in range(len(args)):
        if args[i][0] == '(' and args[i][-1] == ')':
            args[i] = re.split('\s+', args[i][1:-1])
        elif args[i][0] == '\'' and args[i][-1] == '\'':
            args[i] = args[i][1:-1]
    return command, args

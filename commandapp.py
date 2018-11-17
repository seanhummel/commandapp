"""
    CommandApp is a set of classes for setting up a command line app,
    which has multiple levels.  For instance if you were to make a source control
    app, which has "checkin" and "checkout" commands.  You would want the commands
    to have separate commands, each of which had it's own command line options.

    When making an app, you want to use CommandApp, and add elements to it.  So the hierarchy looks like:

        CommandApp
            CommandMenuNode
                CommandOptionHandler
                CommandOptionHandler
                CommandOptionHandler
            CommandOptionHandler
            CommandOptionHandler
            CommandMenuNode
                CommandMenuNode
                    CommandOptionHandler

    This simple diagram gives you an idea of what sort of command hierarchy you can put in place.

"""
import inspect
import json
import os

import columnizer
import pyargs

"""
    Use CommandMenuNode when you want to create a node which doesn't necessarily execute anything, 
    but it is used as a named portion of the menu system.  So that you can have multiple levels
    of commands in a hierarchy.  You can add CommandMenuNodes, and CommandOptionHandlers to the
    CommandMenuNode.  
    Don't use this as the root, instead used the CommandApp, which handles the app level stuff.
"""


class CommandMenuNode:
    def __init__(self, command_name, description = "", remainder_description = ""):
        self.remainder = remainder_description
        self.description = description
        self.command_name = command_name
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

    def print_menu(self):
        rows = []
        for cmd in self.commands:
            rows.append([cmd.command_name, cmd.description])

        print columnizer.indent(rows, hasHeader = False, separateRows = False,
                                delim = "   ",
                                wrapfunc = lambda x: columnizer.wrap_onspace_strict(x, 40))

    def parse_args(self, args):
        if len(args) == 0:
            self.print_menu()
            return 0
        else:
            found_cmd = None
            for cmd in self.commands:
                if cmd.command_name.lower() == args[0].lower():
                    found_cmd = cmd
                    break
            if found_cmd is not None:
                args.pop(0)
                return cmd.parse_args(args)
            print "Could not find the command '%s' " % args[0]
            return -1


"""
    CommandOptionHandler, this type of handler allows you to add "options" for the 
    argument parser, when the "setup" method is called.   You should inherit this
    and implement setup() and handle_command().  
"""


class CommandOptionHandler(pyargs.PyArgs):
    def __init__(self, command_name, description = "", remainder_description = ""):
        pyargs.PyArgs.__init__(self)
        self.remainder_description = remainder_description
        self.description = description
        self.command_name = command_name
        self.setup()

    def setup(self):
        """Do all your add_options here."""
        raise NotImplementedError()
        pass

    def handle_command(self, options, remainders):
        """When this is called, you should execute your code for this command."""
        raise NotImplementedError()
        pass

    def parse_args(self, args):
        if len(args) == 0:
            self.print_menu()
            return 0

        options, remainders = self.parse(args)
        return self.handle_command(options, remainders)

    def print_menu(self):
        appname = os.path.split(inspect.stack()[-1][1])[-1]
        print "%s [options] %s" % (appname, self.remainder_description)
        print "-" * 40
        pyargs.PyArgs.print_menu(self)
        return 0


"""
    Use a CommandOptionApp to when you want an App which is specifically a single command,
    which has options.
"""


class CommandOptionApp(CommandOptionHandler):
    def __init__(self, command_name, description = "", remainder_description = ""):
        CommandOptionHandler.__init__(command_name, description, remainder_description)

    def setup(self):
        pass

    def handle_command(self, options, remainders):
        pass


"""
    Use a CommandApp when you want to make an app which contains multiple commands.  
    You can add either CommandMenuNode or CommandOptionHandler to the app.  These can 
    then be accessed via the command line.
"""


class CommandApp(CommandMenuNode):
    def __init__(self, description = ""):
        CommandMenuNode.__init__(self, "")
        self.description = description
        self.commands = []

    def parse_args(self, args):
        appname = os.path.split(inspect.stack()[-1][1])[-1]
        if len(args) == 0:
            print "%s %s" % (appname, self.description)
            print "-" * 40
            self.print_menu()
        else:
            return CommandMenuNode.parse_args(self, args)


"""
    Testing stuff
"""


class CommandPrettyCommand(CommandOptionHandler):
    def __init__(self):
        CommandOptionHandler.__init__(self, "pretty", "This command is meant to look pretty.",
                                      "remainders description here.")

    def setup(self):
        self.add_option(pyargs.PyArgsOption(shortname = "a", longname = "address",
                                            description = "address for the the users, perhaps their real names as well."))
        self.add_option(
            pyargs.PyArgsOption(shortname = "b", longname = "bloodtype",
                                allowedvalues = ["a", "b", "a+", "a-", "ab+", "ab-", "o", "o+", "o-"],
                                description = "bloodtype of the users."))

    def handle_command(self, options, remainders):
        print "This CommandPrettyCommand:"
        print "options:"
        print json.dumps(options, indent = 4)
        return 0


if __name__ == "__main__":
    app = CommandApp("This is a simple taste of a command line app.")
    handler = CommandMenuNode("a", "does things that a's do.")
    handler2 = CommandMenuNode("b", "what does a b do anyway?")
    handler3 = CommandMenuNode("delete", "does what delete does.")
    handler4 = CommandMenuNode("level4", "skips to level4")
    handler5 = CommandMenuNode("level5", "skips to level4")
    handler6 = CommandPrettyCommand()

    app.add_command(handler)
    app.add_command(handler2)
    app.add_command(handler3)
    handler3.add_command(handler4)
    handler3.add_command(handler5)
    handler5.add_command(handler6)
    app.parse_args(["delete", "level5", "pretty"])  # ["delete", "level5", "pretty", "-a", "--bloodtype=a"])

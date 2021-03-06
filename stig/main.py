# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
# http://www.gnu.org/licenses/gpl-3.0.txt

# Remove python from process name when running inside tmux
import os
if 'TMUX' in os.environ:
    try:
        from setproctitle import setproctitle
    except ImportError:
        pass
    else:
        from . import __appname__
        setproctitle(__appname__)


import sys
import asyncio
aioloop = asyncio.get_event_loop()


from . import cliopts
from . import logging
cliargs, clicmds = cliopts.parse()


logging.setup(debugmods=cliargs['debug'], filepath=cliargs['debug_file'])
logging.redirect_level('INFO', sys.stdout)
log = logging.make_logger()


from . import settings
cfg = settings.Settings()
settings.init_defaults(cfg)

def _log_cfg_change(setting):
    msg = '{} = {!s}'.format(setting.name, setting)
    if setting.value == setting.default:
        msg += ' (default)'
    log.debug(msg)
cfg.on_change(_log_cfg_change)


from .helpmgr import HelpManager
helpmgr = HelpManager()
helpmgr.settings = cfg


from .client import API
srvapi = API(host=cfg['connect.host'].value,
             port=cfg['connect.port'].value,
             path=cfg['connect.path'].value,
             user=cfg['connect.user'].value,
             password=cfg['connect.password'].value,
             tls=cfg['connect.tls'].value,
             interval=cfg['tui.poll'].value,
             loop=aioloop)
srvapi.rpc.enabled = False
srvapi.bandwidth_unit = cfg['unit.bandwidth'].value
srvapi.bandwidth_prefix = cfg['unitprefix.bandwidth'].value
srvapi.size_unit = cfg['unit.size'].value
srvapi.size_prefix = cfg['unitprefix.size'].value

settings.init_server_defaults(cfg, srvapi.settings)


from .commands import CommandManager
cmdmgr = CommandManager(loop=aioloop)
cmdmgr.resources.update(aioloop=aioloop,
                        srvapi=srvapi,
                        cfg=cfg,
                        helpmgr=helpmgr)
helpmgr.commands = cmdmgr
cmdmgr.load_cmds_from_module(
    'stig.commands.cli', 'stig.commands.tui',
)

def _pre_run_hook(cmdline):
    # Change command before it is executed

    # If there is '-h' or '--help' in the arguments, replace it with 'help
    # <cmd>'.  This is dirty but easier than forcing argparse to ignore all
    # other arguments without calling sys.exit().
    if '-h' in cmdline or '--help' in cmdline:
        cmdcls = cmdmgr.get_cmdcls(cmdline[0], interface='ANY')
        if cmdcls is not None:
            if cmdcls.name != 'tab':
                return ['help', cmdcls.name]
            else:
                # 'tab ls -h' is a little trickier because both 'tab' and 'ls'
                # can have arbitrary additional arguments which we must remove.
                #
                # Find first argument to 'tab' that is also a valid command
                # name.  Preserve all arguments before that.
                tab_args = []
                for arg in cmdline[1:]:
                    if cmdmgr.get_cmdcls(arg, interface='ANY') is not None:
                        return ['tab'] + tab_args + ['help', arg]
                    else:
                        tab_args.append(arg)
                return ['help', 'tab']
    return cmdline
cmdmgr.pre_run_hook = _pre_run_hook



def run():
    from .commands.guess_ui import (guess_ui, UIGuessError)
    from .commands import CmdError
    from . import hooks

    # Read commands from rc file
    rclines = ()
    if not cliargs['norcfile']:
        from .settings import rcfile
        from .settings.defaults import DEFAULT_RCFILE
        try:
            rclines = rcfile.read(cliargs['rcfile'] or DEFAULT_RCFILE)
        except rcfile.RcFileError as e:
            log.error('Loading rc file failed: {}'.format(e))
            sys.exit(1)

    # Decide if we run as a TUI or CLI
    if cliargs['tui']:
        cmdmgr.active_interface = 'tui'
    elif cliargs['notui']:
        cmdmgr.active_interface = 'cli'
    else:
        try:
            cmdmgr.active_interface = guess_ui(clicmds, cmdmgr, cfg)
        except UIGuessError as e:
            log.error('Unable to guess user interface')
            log.error('Provide one of these options: --tui/-t or --no-tui/-T')
            sys.exit(1)
        except CmdError as e:
            log.error(e)
            sys.exit(1)

    def run_commands():
        for cmdline in rclines:
            success = cmdmgr.run_sync(cmdline, on_error=log.error)
            # Ignored commands return None, which we consider a success here
            # because TUI commands like 'tab' in the rc file should have no
            # effect at all when in CLI mode.
            if success is False:
                return False

        # Exit if CLI commands fail
        if clicmds:
            if cmdmgr.active_interface == 'cli':
                # CLI commands (e.g. 'ls') will block indefinitely unless we enable now.
                srvapi.rpc.enabled = True

            success = cmdmgr.run_sync(clicmds, on_error=log.error)
            if not success:
                return False

        # Now that potential connect.* settings are made either via rc file or
        # command line arguments, we can allow any requests to go through.
        srvapi.rpc.enabled = True

        return True

    # Run commands either in CLI or TUI mode
    if cmdmgr.active_interface == 'cli':
        # Exit when pipe is closed (e.g. `stig help | head -1`)
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

        try:
            if not run_commands():
                sys.exit(1)
        except KeyboardInterrupt:
            log.debug('Caught SIGINT')

    elif cmdmgr.active_interface == 'tui':
        from .tui import main as tui
        cmdmgr.resources.update(tui=tui)
        if not tui.run(run_commands):
            sys.exit(1)

    _cancel_unfinished_tasks()

    # # Closing the event loop raises "RuntimeError: Event loop is closed" (not
    # # always) when a `run_in_executor` command (i.e. a thread) is cancelled.
    # # https://github.com/python/asyncio/issues/258
    # aioloop.close()

def _cancel_unfinished_tasks():
    pending = (task for task in asyncio.Task.all_tasks() if not task.done())
    for task in pending:
        log.debug('Cancelling pending task: %r', task)
        task.cancel()
        try:
            log.debug('Finishing pending task: %r', task)
            aioloop.run_until_complete(task)
        except asyncio.CancelledError:
            pass

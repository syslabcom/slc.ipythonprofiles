c = get_config()
c.InteractiveShellApp.ignore_old_config=True
c.TerminalIPythonApp.exec_lines = [ "import zdebug" ]
#import sys, os
#mypath = os.path.abspath('/'.join(os.path.abspath(__file__).split('/')[:-1]))
#c.TerminalIPythonApp.exec_lines = [ "import sys", "sys.path.append('%s')" % mypath, "import zdebug" ]

'''
Created on Nov 21, 2016

@author: Thomas
'''
import sys
from autologging import logged
import pinject
from pinject import copy_args_to_public_fields
import readline
import os
from subprocess import Popen, PIPE, call
import shutil

@logged
class Run(object):
    def __init__(self):
        import e3_io
        self.configManager = e3_io.ConfigManager()
        self.tapManager = e3_io.TapManager()
        self.projectManager = e3_io.ProjectManager()
        pass
    def run(self):
        pass
    def executeCommand(self, input, command):
        config = self.configManager.get_config()
        if command != None:
            #try:
                command.run()
                self.projectManager.append_project_history(input, command)
                if command.get_output():
                    for output in command.get_output():
                        print output
                
                if command.get_output_files():
                    tapId = self.tapManager.get_current_tap_id_and_name()
                    if not os.path.isdir(os.path.join("e3_data", tapId, input)):
                        os.makedirs(os.path.join("e3_data", tapId, input))
                    for outputFile in command.get_output_files():
                        shutil.copy(outputFile, os.path.join("e3_data", tapId, input))
                
                if config['showOutputFileLocation'] and command.get_output_files():
                    print "Files:"
                    for outputFile in command.get_output_files():
                        print outputFile
                if command.get_execute_output():
                    with open(os.devnull, 'w') as devnull:
                        for execute in command.get_execute_output():
                            if execute == 'Exit':
                                sys.exit()
                            else:
                                p = Popen(execute, stdout=devnull, stderr=devnull, shell=True)
            #except Exception as e:
            #    print "Something went wrong: " + str(e)
        else:
            print "Unrecognized command"
    
@logged
class OneShot(Run):
    @copy_args_to_public_fields
    def __init__(self, commandProvider):
        Run.__init__(self)
    def run(self):
        input = ' '.join(sys.argv[1:])
        input = input.replace('\\', '')
        command = self.commandProvider.provide(input)
        self.executeCommand(input, command)
        
@logged 
class Interactive(Run):
    @copy_args_to_public_fields
    def __init__(self, commandProvider):
        Run.__init__(self)
    def run(self):
        current_tap = self.tapManager.get_current_tap()
        if current_tap is None:
            import e3_io
            e3_io.reset()
        
        current_tap = self.tapManager.get_current_tap()
        if current_tap:
            print "Tap: %s" % self.tapManager.get_tap_id_and_name_and_status(current_tap)
        else:
            print "Tap: None"
        while True:
            input = raw_input('e3 > ')
            command = self.commandProvider.provide(input)
            self.executeCommand(input, command)
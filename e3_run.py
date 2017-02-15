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
import yaml
import e3_io

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
                
                tap = self.tapManager.get_current_tap()
                tapId = self.tapManager.get_current_tap_id_and_name()
                runDir = os.path.join(e3_io.get_working_dir(), "_".join(tapId.split()), "_".join(input.split()))
                runDirOutputFiles = []
                if command.get_output_files():
                    if not os.path.isdir(runDir):
                        os.makedirs(runDir)
                    
                    tapDir = os.path.abspath(os.path.join(runDir, os.pardir))
                    with open(os.path.join(tapDir, "input.txt"), 'w+') as i:
                        i.write(tap.get_cleantax())
                    with open(os.path.join(tapDir, "config.txt"), 'w+') as cfg:
                        cfg.write("isCoverage: " + str(tap.isCoverage))
                        cfg.write("isSiblingDisjointness: " + str(tap.isSiblingDisjointness))
                        cfg.write("regions: " + tap.regions)
                        yaml.dump(config, cfg, default_flow_style=False)
                        
                    for outputFile in command.get_output_files():
                        newName = input
                        if(len(command.get_output_files()) > 1):
                            newName = os.path.basename(outputFile)
                            if ".cleantax" in newName:
                                newName = newName.replace(".cleantax", input)
                            else:
                                newName = input + "_" + newName
                        newName = "_".join(newName.split())
                        if not newName.endswith("." + config['imageFormat']):
                            newName = newName  + "." + config['imageFormat']
                        newFile = os.path.join(runDir, newName)
                        shutil.copy(outputFile, newFile)
                        runDirOutputFiles.append(newFile)
                        
                        newExecuteOutput = []
                        for execute in command.get_execute_output():
                            if outputFile in execute:
                                execute = execute.replace(outputFile, newFile)
                            newExecuteOutput.append(execute)
                        command.executeOutput = newExecuteOutput
                            
                if config['showOutputFileLocation'] and command.get_output_files():
                    print "Files:"
                    for outputFile in runDirOutputFiles:
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
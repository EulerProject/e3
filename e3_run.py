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
import time

@logged
class Run(object):
    def __init__(self):
        import e3_io
        self.configManager = e3_io.ConfigManager()
        self.tapManager = e3_io.TapManager()
        self.projectManager = e3_io.ProjectManager()
        self.graphCreator = e3_io.GraphCreator()
        pass
    def run(self):
        pass
    def add_to_history(self, input, command, tapBeforeExecution, tapAfterExecution):
        import e3_command
        import e3_model
        if isinstance(command, e3_command.Euler2Command):
            srcNode = tapBeforeExecution.get_id()#e3_model.TapHistoryNode(tapBeforeExecution.get_id(), { })
            dstNode = tapBeforeExecution.get_id() + "/" +input#e3_model.Euler2CommandHistoryNode(tapBeforeExecution.get_id(), input, { "output" : '; '.join(command.get_output()) })
            self.tapManager.add_history_node(dstNode, { "output" : '; '.join(command.get_output()) })
            self.tapManager.add_history_edge(srcNode, dstNode, { "command" : input, "startTime": command.startTime, "endTime" : command.endTime })
        if isinstance(command, e3_command.ModelCommand):
            srcNode = tapBeforeExecution.get_id() #e3_model.TapHistoryNode(tapBeforeExecution.get_id(), { })
            dstNode = tapAfterExecution.get_id() #e3_model.TapHistoryNode(tapAfterExecution.get_id(), { })
            self.tapManager.add_history_edge(srcNode, dstNode, { "command" : input, "startTime": command.startTime, "endTime" : command.endTime })
            
    def create_cwd_command_output(self, input, command, tapAfterExecution):
        config = self.configManager.get_config()
        tapId = self.tapManager.get_tap_name(tapAfterExecution.get_id())
        import e3_io
        e3DataDir = e3_io.get_working_dir()
        tapDir = os.path.join(e3DataDir, "_".join(tapId.split()))
        runDir = os.path.join(e3DataDir, "_".join(tapId.split()), "_".join(input.split()))
        
        import e3_command
        if isinstance(command, e3_command.Euler2Command):
            runDirOutputFiles = []
            if command.get_output_files():
                if not os.path.isdir(runDir):
                    os.makedirs(runDir)
                with open(os.path.join(runDir, "config.txt"), 'w+') as cfg:
                    cfg.write("isCoverage: " + str(tapAfterExecution.isCoverage) + "\n")
                    cfg.write("isSiblingDisjointness: " + str(tapAfterExecution.isSiblingDisjointness) + "\n")
                    cfg.write("regions: " + tapAfterExecution.regions + "\n")
                    cfg.write("\n")
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
                    #indexHtml = [
                    #    "<li><a href=" + os.path.basename(runDirOutputFile) + ">" + os.path.basename(runDirOutputFile) + "</a></br>"
                    #    for runDirOutputFile in runDirOutputFiles]
                    #indexHtml.insert(0, "<li><a href=\"config.txt\">config.txt</a></br>")
                    #with open(os.path.join(runDir, 'index.html'), 'w') as indexFile:
                    #    indexFile.write('\n'.join(indexHtml))
                    
                    newExecuteOutput = []
                    for execute in command.get_execute_output():
                        if outputFile in execute:
                            execute = execute.replace(outputFile, newFile)
                        newExecuteOutput.append(execute)
                    command.executeOutput = newExecuteOutput
                
        import e3_command
        if isinstance(command, e3_command.ModelCommand) or isinstance(command, e3_command.Euler2Command):
            if not os.path.isdir(tapDir):
                os.makedirs(tapDir)
            with open(os.path.join(tapDir, "input.txt"), 'w+') as i:
                i.write(tapAfterExecution.get_cleantax())
                
            self.graphCreator.create_history_graph(e3DataDir)
            self.graphCreator.create_tap_graph(tapDir)
                    
    def process_execute_result(self, command):
        if command.get_output():
            for output in command.get_output():
                print output
        
        config = self.configManager.get_config()
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
    
    def executeCommand(self, input, command):
        if command != None:
            try:
                tapBeforeExecution = self.tapManager.get_current_tap()
                command.startTime = time.time()
                command.run()
                command.endTime = time.time()
                tapAfterExecution = self.tapManager.get_current_tap()
                self.add_to_history(input, command, tapBeforeExecution, tapAfterExecution)
                self.projectManager.append_project_history(input, command)
                self.create_cwd_command_output(input, command, tapAfterExecution)
                self.process_execute_result(command)
            except Exception as e:
               print "Something went wrong: " + str(e)
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
        try:
            command = self.commandProvider.provide(input)
            self.executeCommand(input, command)
        except Exception as e:
            print str(e)
        
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
            print "Tap: %s" % self.tapManager.get_tap_name_and_status(current_tap.get_id())
        else:
            print "Tap: None"
        while True:
            input = raw_input('e3 > ')
            #try:
            command = self.commandProvider.provide(input)
            self.executeCommand(input, command)
            #except Exception as e:
            #    print str(e)
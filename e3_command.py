'''
@author: Thomas
'''
from autologging import logged
from pinject import copy_args_to_public_fields
import e3_io
#from e3_io import set_name, get_tap_from_cleantax, get_tap, store_tap, set_current_tap, get_config, get_tap_id_and_name, get_names, clear_names
from subprocess import Popen, PIPE, call
import os
import e3_parse
import e3_validation
import e3_model
import git
    
@logged
class Command(object):
    @copy_args_to_public_fields
    def __init__(self):
        self.config = e3_io.get_config()
        self.output = []
        self.outputFiles = []
        self.executeOutput = []
        pass
    def run(self):
        self.__log.debug("run %s" % self.__class__.__name__)
    def get_output(self):
        return self.output
    def get_execute_output(self):
        return self.executeOutput
    def get_output_files(self):
        return self.outputFiles
    
@logged
class MiscCommand(Command):
    @copy_args_to_public_fields
    def __init__(self):
        Command.__init__(self)
    def run(self):
        Command.run(self)
                    
class Euler2Command(Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Command.__init__(self)
        
        self.alignUncertaintyReductionInputCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --ur'
        self.alignExtractInputCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner}  -e {regions} {disjointness} {coverage} --xia'
        self.alignArtRemCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner}  -e {regions} {disjointness} {coverage} --artRem'
        self.alignFoundInOneCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --fourinone'
        self.alignCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage}'
        self.alignConsistencyCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --consistency'
        self.alignMaxNCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} -n {maxN}'
        self.alignRepairCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --repair={repairMethod}'
        self.showIVCommand = '{euler2Executable} show iv {cleantaxFile} -o {outputDir} {imageFormat}';
        self.showPWCommand = '{euler2Executable} show -o {outputDir} pw {imageFormat}'
        self.showInconLatCommand = '{euler2Executable} show -o {outputDir} inconLat {imageFormat}'
        self.showFourInOneCommand = '{euler2Executable} show -o {outputDir} fourinone {imageFormat}'
        self.showSummaryCommand = '{euler2Executable} show -o {outputDir} sv {imageFormat}'
        self.showAmbLatCommand = '{euler2Executable} show -o {outputDir} ambLat {imageFormat}'
        self.euler2Executable = self.config['euler2Executable']
        self.reasoner = self.config['reasoner']
        self.imageViewer = self.config['imageViewer']
        self.maxPossibleWorldsToShow = self.config['maxPossibleWorldsToShow']
        self.imageFormat = self.config['imageFormat']
        self.repairMethod = self.config['repairMethod']
        self.isCoverage = self.tap.isCoverage
        self.isSiblingDisjointness = self.tap.isSiblingDisjointness
        self.regions = self.tap.regions
        self.defaultIsSiblingDisjointness = self.config['defaultIsSiblingDisjointness']
        self.defaultIsCoverage = self.config['defaultIsCoverage']
        self.defaultRegions = self.config['defaultRegions']
        self.tapId = self.tap.get_id()
        self.cleantaxFile = e3_io.get_cleantax_file(self.tap)
        self.outputDir = e3_io.get_tap_dir(self.tapId)
        self.name = self.__class__.__name__
        self.e2InputDir = e3_io.get_0_input_dir(self.tap)
        self.e2AspInputDir = e3_io.get_1_asp_input_dir(self.tap)
        self.e2AspOutputDir = e3_io.get_2_asp_output_dir(self.tap)
        self.e2MirDir = e3_io.get_3_mir_dir(self.tap)
        self.e2PWsDir = e3_io.get_4_pws_dir(self.tap)
        self.e2AggregatesDir = e3_io.get_5_aggregates_dir(self.tap)
        self.e2LatticesDir = e3_io.get_6_lattices_dir(self.tap)
        self.isConsistent = True
        if not hasattr(self, 'maxN'):
            self.maxN = None
    def run(self):
        Command.run(self)
    def run_euler(self, command):
        # add parameters to the command that are relevant to avoid re-runs (i.e. all tap relevant data + maxN + ...?)
        # by at the same time keeping the file name minimal
        coverage = "" if self.isCoverage else "--disablecov"
        disjointness = "" if self.isSiblingDisjointness else "--disablesib"
        imageFormat = "--svg" if self.imageFormat == "svg" else ""
        command = command.format(euler2Executable = '{euler2Executable}', 
                cleantaxFile = '{cleantaxFile}', outputDir = '{outputDir}', 
                #imageFormat = '{imageFormat}', 
                #reasoner = '{reasoner}', 
                repairMethod = self.repairMethod,  maxN = self.maxN, regions = self.regions, coverage = coverage, 
                disjointness = disjointness, imageFormat = imageFormat, reasoner = self.reasoner)
        stdoutFile = os.path.join(self.outputDir, '%s.stdout' % command)
        stderrFile = os.path.join(self.outputDir, '%s.stderr' % command)
        returnCodeFile = os.path.join(self.outputDir, '%s.returncode' % command)
        if os.path.isfile(stdoutFile) and os.path.isfile(stderrFile) and os.path.isfile(returnCodeFile):
            with open(stdoutFile,'r') as f:
                stdout = f.read()
            with open(stderrFile,'r') as f:
                stderr = f.read()
            with open(returnCodeFile,'r') as f:
                returnCode = f.read()
            if "Input is inconsistent" in stdout:
                self.isConsistent = False
            if returnCode and stderr:
                print stderr.rstrip()
            return stdout, stderr, returnCode
        # add remaining parameters
        command = command.format(euler2Executable = self.euler2Executable, 
                cleantaxFile = self.cleantaxFile, outputDir = self.outputDir, imageFormat = self.imageFormat, 
                maxN = self.maxN, reasoner = self.reasoner);
        with open(stdoutFile, 'w+') as out:
            with open(stderrFile, 'w+') as err:
                with open(returnCodeFile, 'w+') as rc:
                    #print command
                    p = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
                    stdout, stderr = p.communicate()
                    #print stdout
                    #print stderr
                    if p.returncode and stderr:
                        print stderr.rstrip()
                    if "Input is inconsistent" in stdout:
                        self.isConsistent = False
                    out.write(stdout)
                    err.write(stderr)
                    rc.write('%s' % p.returncode)
                    if os.path.isfile('report.csv'):
                        os.remove('report.csv')
                    return stdout, stderr, p.returncode
    def is_consistent(self):
        return self.isConsistent
    def get_possible_worlds(self):
        possibleWorlds = []
        with open(os.path.join(self.e2AspOutputDir, '.cleantax.pw'), 'r') as f:
            currentWorld = ""
            for line in f:
                if len(line.strip()) == 0:
                    if len(currentWorld) > 0:
                        possibleWorlds.append(currentWorld.rstrip())
                        currentWorld = ""
                else:
                    if not len(line.strip()) == 0:
                        currentWorld += line
            if len(currentWorld) > 0:
                possibleWorlds.append(currentWorld.rstrip())
        return possibleWorlds
    
class ModelCommand(Command):
    @copy_args_to_public_fields                 
    def __init__(self):
        Command.__init__(self)
    def run(self):
        Command.run(self)    
              
class SetConfig(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, key, value):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        config = e3_io.get_config()
        if not self.key in config:
            self.output.append("Configuration parameter " + self.key + " does not exist.")
            return 
        if type(config[self.key]) is bool:
            self.value = True if not (self.value == 'false' or self.value == 'False') else False
        if type(config[self.key]) is int:
            self.value = int(self.value)
        if type(config[self.key]) is str:
            self.value = str(self.value)
        config[self.key] = self.value
        e3_io.store_config(config)
        self.output.append("Configuration updated: " + self.key + " = " + str(self.value))

class PrintConfig(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        config = e3_io.get_config()
        for key in config:
            self.output.append("{key} = {value}".format(key = key, value = config[key])) 
          
@logged 
class Reset(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        e3_io.reset()
        tap = e3_io.get_current_tap()
        self.output.append("Reset successful")
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(tap))
         
@logged
class SetGitCredentials(MiscCommand):        
    @copy_args_to_public_fields
    def __init__(self, host, user, password):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        e3_io.set_git_credencials(self.host, self.user, self.password)
        self.output.append("git credentials set successfully")
        
@logged
class GitPull(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = e3_io.get_config()
        g = git.Git(e3_io.get_e3_dir())
        try:
            g.status()
            g.pull()
        except git.exc.GitCommandError as e:
            e3_io.clean_e3_dir()
            g.clone(config['gitRepository'], e3_io.get_e3_dir())
        self.output.append("Pulled successfully")
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(e3_io.get_current_tap()))

@logged
class GitPush(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, message):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = e3_io.get_config()
        try:
            g = git.Git(e3_io.get_e3_dir())
            try:
                g.status()
            except git.exc.GitCommandError as e:
                g.init() # can already have a .git folder
                g.remote("add", "origin", config['gitRepository']) # can already have an "origin"
            g.fetch() # may not be able to if remote is bogus url
            g.add(".")
            g.commit("-m", self.message) #could in theory have empty message
            g.push("--all")
            self.output.append("Pushed successfully")
        except git.exc.GitCommandError as e:
            self.output.append(str(e))
         
@logged 
class Bye(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        self.output.append("See you soon!")
        self.executeOutput.append("Exit")
        
@logged 
class Help(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        for commandParser in e3_parse.commandParsers:
            help = commandParser.get_help()
            if help:
                self.output.append('-------------------')
                self.output.append(commandParser.get_help())
                
@logged
class NameTap(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, name):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        e3_io.set_name(self.name, self.tap);
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
                
class PrintNames(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        names = e3_io.get_names()
        if names:
            self.output.append('\n'.join(names))
        else:
            self.output.append('No names stored.')
    
#class ClearNames(MiscCommand):
#    @copy_args_to_public_fields
#    def __init__(self):
#        MiscCommand.__init__(self)
#    def run(self):
#        MiscCommand.run(self)
#        e3_io.clear_names()
#        self.output.append("Names are cleared")
    
class PrintTap(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        self.output.append(self.tap.__str__())
    
class PrintTaxonomies(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        for taxonomy in self.tap.taxonomies:
            indices = ['']
            for x in range(1, len(taxonomy)):
                indices.append(str(x) + ". ")
            taxonomyLines = [x + y for x, y in zip(indices, taxonomy)]
            self.output.append('\n'.join(taxonomyLines))
            
class PrintArticulations(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)        
        indices = ['']
        for x in range(1, len(self.tap.articulations)):
            indices.append(str(x) + ". ")
        articulationLines = [x + y for x, y in zip(indices, self.tap.articulations)]
        self.output.append('\n'.join(articulationLines))
    
@logged
class CreateProject(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        if e3_io.exists_project(self.name):
            self.output.append('A project with name ' + self.name + ' already exists')
            return
        e3_io.create_project(self.name)
        e3_io.set_history(self.name, "")
        e3_io.set_current_project(self.name)

@logged
class OpenProject(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        if not e3_io.exists_project(self.name):
            self.output.append('A project with name ' + self.name + ' does not exist')
            return
        e3_io.set_current_project(self.name)

@logged
class PrintProjectHistory(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, commandProvider):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        name = e3_io.get_current_project()
        if not name:
            self.output.append('No project open')
            return
        if not e3_io.exists_project(name):
            self.output.append('Project has been removed')
            return
        with open(e3_io.get_history_file(name), 'r') as historyFile:
            for i, line in enumerate(historyFile):
                line = line.rstrip()
                uuidPart = line.split(' ', 1)[0]
                commandPart = line.split(' ', 1)[1]
                command = self.commandProvider.provide(commandPart)
                if isinstance(command, ModelCommand):
                    self.output.append(str(i) + ". [Tap] " + commandPart + " (" + uuidPart + ")")
                elif isinstance(command, Euler2Command):
                    self.output.append(str(i) + ". [Reasoning] " + commandPart + " (" + uuidPart + ")")
                elif isinstance(command, MiscCommand):
                    self.output.append(str(i) + ". [Misc] " + commandPart + " (" + uuidPart + ")")
                    
@logged
class RemoveProjectHistory(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, commandProvider, index):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        name = e3_io.get_current_project()
        if not name:
            self.output.append('No project open')
            return
        if not e3_io.exists_project(name):
            self.output.append('Project has been removed')
            return
        lines = []
        with open(e3_io.get_project_history(name), 'r') as historyFile:
            lines = historyFile.readlines()
            if self.index >= len(lines) or self.index < 0:
                self.output.append("This is not a valid index")
            line = lines[self.index]
            newLines = list(lines)
            command = self.commandProvider.provide(line)
            if isinstance(command, ModelCommand):
                for i in range(self.index, len(lines)):
                    del newLines[self.index]
            else:
                del newLines[self.index]
        e3_io.set_history(name, ''.join(newLines))
    
@logged
class CloseProject(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        e3_io.set_current_project(None) 
    
@logged
class ClearProjects(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        e3_io.clear_projects()
        e3_io.set_current_project(None) 
    
@logged
class RemoveProject(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        if e3_io.get_current_project() == self.name:
            e3_io.set_current_project(None)
        e3_io.remove_project(self.name)
        
@logged
class PrintProjects(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        projects = e3_io.get_projects()
        if projects:
            self.output.append('\n'.join(projects))
        else:
            self.output.append('No projects stored.')
            
@logged 
class LoadTap(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, cleantaxFile):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        try:
            tap = e3_io.get_tap_from_cleantax_file(self.cleantaxFile)
            e3_io.set_current_tap(tap)
            e3_io.store_tap(tap)
            self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(tap))
        except IOError as e:
            self.output.append("File not found.")
            return
        except e3_validation.ValidationException as e:
            self.output.append(str(e))

@logged 
class ClearTap(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        config = e3_io.get_config()
        tap = e3_model.Tap(config['defaultIsCoverage'], config['defaultIsSiblingDisjointness'], config['defaultRegions'], [], [])
        e3_io.set_current_tap(tap)
        e3_io.store_tap(tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(tap))

class AddChildren(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, taxonomyId, children):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        if self.tap.has_taxonomy(self.taxonomyId) is None:
            self.output.append("Taxonomy with id " + self.taxonomyId + " not found.")
            return
        
        parts = self.children[1:-1].split()
        if len(parts) <= 1:
            self.output.append("Taxonomy line with one <= 1 node is not valid.")
            return
        
        try:
            self.tap.add_children(self.taxonomyId, parts[0], parts[1:])
        except e3_validation.ValidationException as e:
            self.output.append(str(e))
            return
        
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))

class RemoveChildren(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, taxonomyId, children, recursive):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        if self.tap.has_taxonomy(self.taxonomyId) is None:
            self.output.append("Taxonomy with id " + self.taxonomyId + " not found.")
            return
        
        parts = self.children[1:-1].split()
        if len(parts) <= 1:
            self.output.append("Taxonomy line with one <= 1 node is not valid.")
            return
        
        try:
            self.tap.remove_children(self.taxonomyId, parts[0], parts[1:], self.recursive)
        except e3_validation.ValidationException as e:
            self.output.append(str(e))
            return
        
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))

class AddTaxonomy(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id, name):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if self.tap.has_taxonomy(self.id):
            self.output.append("Taxonomy with id: " + self.id + " already exists")
        taxonomy = self.tap.add_taxonomy(e3_model.Taxonomy(self.id, self.name))
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))

class RemoveTaxonomy(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if not self.tap.has_taxonomy(self.id):
            self.output.append("Taxonomy with id " + self.id + " does not exist")
            return
        taxonomy = self.tap.remove_taxonomy(self.id)
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
            
class ClearTaxonomy(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if not self.tap.has_taxonomy(self.id):
            self.output.append("Taxonomy with id " + self.id + " does not exist")
            return
        taxonomy = self.tap.clear_taxonomy(self.id)
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
                    
class ClearArticulations(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tap.articulations = []
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
            
class SetTaxonomyInfo(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id, newId, newName):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tap.set_taxonomy_info(self.id, self.newId, self.newName)
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
        
@logged
class AddArticulation(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, articulation):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        articulation = None
        for validRelation in e3_model.relations:
            split = " " + validRelation + " "
            if split in self.articulation:
                parts = self.articulation.split(split)
                left = parts[0].split()
                right = parts[1].split()
                articulation = e3_model.Articulation(left, right, validRelation)
                break
        
 
        if articulation is  None:
            self.output.append("Not a valid articulation. No valid relation found.")
        else:
            try:
                e3_validation.validate_new_articulation(articulation, self.tap)
            except e3_validation.ValidationException as e:
                self.output.append(str(e))
                return
            
            self.tap.add_articulation(articulation)        
            e3_io.set_current_tap(self.tap)
            e3_io.store_tap(self.tap)
            self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))

@logged
class RemoveArticulation(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, articulationIndex):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if self.articulationIndex > len(self.tap.articulations) or self.articulationIndex < 1:
            self.output.append("This is not a valid index")
            return
        self.tap.remove_articulation(self.articulationIndex)
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
    
class UseTap(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        e3_io.set_current_tap(self.tap)
        if self.tap:
            self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
            
@logged
class SetCoverage(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, value):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tap.isCoverage = self.value
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))

@logged 
class SetRegions(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, value):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if self.value == "mnpw" or self.value == "mncb" or self.value == "mnve" or self.value == "vrpw" or self.value == "vrve":
            self.tap.regions = self.value
            e3_io.set_current_tap(self.tap)
            e3_io.store_tap(self.tap)
            self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
        else:
            self.output.append("This is not a valid region")

@logged 
class SetSiblingDisjointness(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, value):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tap.isSiblingDisjointness = self.value
        e3_io.set_current_tap(self.tap)
        e3_io.store_tap(self.tap)
        self.output.append("Tap: " + e3_io.get_tap_id_and_name_and_status(self.tap))
    
@logged 
class GraphWorlds(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)
        if not self.is_consistent():
            self.output.append("The tap is inconsistent")
            return
        
        stdout, stderr, returnCode = self.run_euler(self.showPWCommand)
        possibleWorldsCount = len(self.get_possible_worlds())
        if possibleWorldsCount == 0:
            self.output.append("There are no possible worlds.")
        elif possibleWorldsCount <= self.maxPossibleWorldsToShow:
            self.output.append("There are {count} possible worlds. I show them all to you.".format(
                count = possibleWorldsCount))
        else:
            self.output.append("There are {count} possible worlds. I will only show {maxCount} of them to you.".format(
                count = possibleWorldsCount, maxCount = self.maxPossibleWorldsToShow))
        
        self.executeOutput = []
        openCount = 0
        for filename in os.listdir(self.e2PWsDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2PWsDir, filename)
                self.outputFiles.append(file)
                if openCount < self.maxPossibleWorldsToShow:
                    openCount += 1
                    self.executeOutput.append(self.imageViewer.format(file = file))
                
@logged 
class IsConsistent(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        
        if self.is_consistent():
            self.output.append("yes")
        else:
            self.output.append("no")
    
@logged 
class MoreWorldsThan(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap, more):
        Euler2Command.__init__(self, tap)
        self.maxN = self.more + 1 #adapt from "more than" to "more than equals"
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        stdout, stderr, returnCode = self.run_euler(self.alignMaxNCommand)
        if not self.is_consistent():
            self.output.append("Cannot determine if there are more than {more} worlds. The tap is not consistent".format(more = self.more))
            return
               
        possibleWorldsCount = len(self.get_possible_worlds())
        if possibleWorldsCount < self.maxN:
            self.output.append("There are less than or equal to {more} possible worlds. There are {count}.".format(
                more = self.more, count = possibleWorldsCount))
        else:
            self.output.append("There are more than {more} possible worlds.".format(
                more = self.more))
            
@logged 
class PrintFix(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        stdout, stderr, returnCode = self.run_euler(self.alignRepairCommand)
        if self.is_consistent():
            self.output.append("The tap is not inconsistent. I have nothing to show.")
            return
        self.output.append("Suggested repair options")
        for line in stdout.splitlines():
            if line.startswith('Repair option'):
                self.output.append(line.rstrip())
            if line.startswith('Possible world'):
                self.output = []
                self.output.append("The tap is not inconsistent. There is nothing to fix.")
                return
                           
@logged
class GraphInconsistency(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return       
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)
        if self.is_consistent():
            self.output.append("The tap is not inconsistent. I have nothing to show.")
            return
        
        stdout, stderr, returnCode = self.run_euler(self.showInconLatCommand)
        self.output.append("Take a look at the graph")
        self.executeOutput = []
        for filename in os.listdir(self.e2LatticesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2LatticesDir, filename)
                self.executeOutput.append(self.imageViewer.format(file = file)) 
                self.outputFiles.append(file)
            
@logged
class PrintWorlds(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)        
        if not self.is_consistent():
            self.output.append("The tap is inconsistent")
            return
        
        possibleWorlds = self.get_possible_worlds()
        possibleWorldsCount = len(possibleWorlds)
        if possibleWorldsCount == 0:
            self.output.append("There are no possible worlds.")
        elif possibleWorldsCount <= self.maxPossibleWorldsToShow:
            self.output.append("There are {count} possible worlds. I show them all to you.".format(
                count = len(possibleWorlds)))
        else:
            self.output.append("There are {count} possible worlds. I will only show {maxCount} of them to you.".format(
                count = len(possibleWorlds), maxCount = self.maxPossibleWorldsToShow))
        for world in possibleWorlds:
            self.output.append(world)
      
@logged 
class GraphTap(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        stdout, stderr, returnCode = self.run_euler(self.showIVCommand)
        self.output.append("Take a look at the graph")
        self.executeOutput = []
        for filename in os.listdir(self.e2InputDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2InputDir, filename)
                self.executeOutput.append(self.imageViewer.format(file = file))
                self.outputFiles.append(file)
@logged 
class GraphFourInOne(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        stdout, stderr, returnCode = self.run_euler(self.alignFoundInOneCommand)
        stdout, stderr, returnCode = self.run_euler(self.showFourInOneCommand)
        #if "This is a consistent example, no 4-in-1 lattice generated" in stdout:
            #self.output.append("The tap is consistent")
            #return
        
        self.output.append("Take a look at the graph")
        self.executeOutput = []
        for filename in os.listdir(self.e2LatticesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2LatticesDir, filename)
                self.executeOutput.append(self.imageViewer.format(file = file))
                self.outputFiles.append(file)
@logged 
class GraphSummary(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)
        if not self.is_consistent():
            self.output.append("The tap is inconsistent")
            return
        stdout, stderr, returnCode = self.run_euler(self.showPWCommand)
        stdout, stderr, returnCode = self.run_euler(self.showSummaryCommand)
        self.output.append("Take a look at the graph")
        self.executeOutput = []
        for filename in os.listdir(self.e2AggregatesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2AggregatesDir, filename)
                self.executeOutput.append(self.imageViewer.format(file = file))
                self.outputFiles.append(file)
@logged
class GraphAmbiguity(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status())
            return
        
        self.maxN = 2
        stdout, stderr, returnCode = self.run_euler(self.alignMaxNCommand)
        if not self.is_consistent():
            self.output.append("The tap is inconsistent")
            return
        
        possibleWorldsCount = len(self.get_possible_worlds())
        if possibleWorldsCount == self.maxN:
            self.output.append("The tap is ambiguous. There is more than one possible worlds")
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignArtRemCommand)
        stdout, stderr, returnCode = self.run_euler(self.showAmbLatCommand)
        if "No MUS generated for this example" in stdout:
            self.output.append("The tap is not valid for graph ambiguity")
            return
        self.output.append("Take a look at the graph")
        self.executeOutput = []
        for filename in os.listdir(self.e2LatticesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2LatticesDir, filename)
                self.executeOutput.append(self.imageViewer.format(file = file))
                self.outputFiles.append(file)
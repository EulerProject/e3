'''
@author: Thomas
'''
from autologging import logged
from pinject import copy_args_to_public_fields
from subprocess import Popen, PIPE, call
import os
import shutil
import yaml

@logged
class Command(object):
    @copy_args_to_public_fields
    def __init__(self):
        import e3_io
        self.tapManager = e3_io.TapManager()
        self.configManager = e3_io.ConfigManager()
        self.output = []
        self.outputFiles = []
        self.executeOutput = []
        self.startTime = None
        self.endTime = None
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
        self.showInconLatFullCommand = '{euler2Executable} show -o {outputDir} inconLat {imageFormat} --full'
        self.showInconLatReducedCommand = '{euler2Executable} show -o {outputDir} inconLat {imageFormat} --reduced'
        self.showFourInOneCommand = '{euler2Executable} show -o {outputDir} fourinone {imageFormat}'
        self.showSummaryCommand = '{euler2Executable} show -o {outputDir} sv {imageFormat}'
        self.showAmbLatCommand = '{euler2Executable} show -o {outputDir} ambLat {imageFormat}'
        config = self.configManager.get_config()
        self.euler2Executable = config['environment']['euler2Executable']
        self.reasoner = config['reasoning']['reasoner']
        self.imageViewer = config['environment']['imageViewer']
        self.maxPossibleWorldsToShow = config['cli behavior']['maxPossibleWorldsToShow']
        self.imageFormat = config['cli behavior']['imageFormat']
        self.repairMethod = config['reasoning']['repairMethod']
        self.isCoverage = self.tap.isCoverage
        self.isSiblingDisjointness = self.tap.isSiblingDisjointness
        self.regions = self.tap.regions
        self.defaultIsSiblingDisjointness = config['reasoning']['defaultIsSiblingDisjointness']
        self.defaultIsCoverage = config['reasoning']['defaultIsCoverage']
        self.defaultRegions = config['reasoning']['defaultRegions']
        self.tapId = self.tap.get_id()
        self.cleantaxFile = self.tapManager.get_cleantax_file(self.tapId)
        self.outputDir = self.tapManager.get_tap_dir(self.tapId)
        self.name = self.__class__.__name__
        self.e2InputDir = self.tapManager.get_0_input_dir(self.tapId)
        self.e2AspInputDir = self.tapManager.get_1_asp_input_dir(self.tapId)
        self.e2AspOutputDir = self.tapManager.get_2_asp_output_dir(self.tapId)
        self.e2MirDir = self.tapManager.get_3_mir_dir(self.tapId)
        self.e2PWsDir = self.tapManager.get_4_pws_dir(self.tapId)
        self.e2AggregatesDir = self.tapManager.get_5_aggregates_dir(self.tapId)
        self.e2LatticesDir = self.tapManager.get_6_lattices_dir(self.tapId)
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
        with open(os.path.join(self.e2AspOutputDir, 'cleantax.pw'), 'r') as f:
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
        config = self.configManager.get_config()
        oldValue = None
        for firstLevelKey in config:
            if self.key in config[firstLevelKey]:
                oldValue = config[firstLevelKey][self.key]
                break
        
        if oldValue is None:
            self.output.append("Configuration parameter " + self.key + " does not exist.")
            return 
        
        if type(oldValue) is bool:
            self.value = True if not (self.value == 'false' or self.value == 'False') else False
        if type(oldValue) is int:
            self.value = int(self.value)
        if type(oldValue) is str:
            self.value = str(self.value)
            
        config[firstLevelKey][self.key] = self.value
        self.configManager.store_config(config)
        self.output.append("Configuration updated: " + self.key + " = " + str(self.value))

class PrintConfig(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        import e3_io
        print e3_io.ordered_yaml_dump(config, Dumper=yaml.SafeDumper, default_flow_style=False)
          
@logged 
class Reset(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        import e3_io
        e3_io.reset()
        self.output.append("Reset successful")
        self.output.append("Tap: " + self.tapManager.get_current_tap_name_and_status())

@logged 
class ResetConfig(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        import e3_io
        self.configManager.store_config(self.configManager.get_default_config())
        self.output.append("Reset config successfully")

@logged 
class ClearHistory(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        self.tapManager.clear_history()
        self.output.append("Cleared history successfully")

@logged 
class Clear(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        import e3_io
        e3_io.clear()
        self.output.append("Clear successful")
        self.output.append("Tap: " + self.tapManager.get_current_tap_name_and_status())
         
@logged
class ShowHistory(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        import e3_io
        self.executeOutput.append(config['environment']['htmlViewer'].format(file = os.path.join(e3_io.get_working_dir(), "index.html")))
@logged
class SetGitCredentials(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, host, user, password):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        import e3_io
        e3_io.set_git_credencials(self.host, self.user, self.password)
        self.output.append("git credentials set successfully")

@logged
class GitCachePull(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        import git
        import e3_io
        g = git.Git(e3_io.get_e3_dir())
        try:
            g.status()
            g.pull()
        except git.exc.GitCommandError as e:
            e3_io.clean_e3_dir()
            g.clone(config['sharing']['cacheGitRepo'], e3_io.get_e3_dir())
        self.output.append("Pulled successfully")
        self.output.append("Tap: " + self.tapManager.get_current_tap_name_and_status())
        
@logged
class GitPull(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        import git
        import e3_io
        g = git.Git(e3_io.get_e3_data_git_dir())
        try:
            g.status()
            g.pull()
        except git.exc.GitCommandError as e:
            e3_io.clean_e3_data_git_dir()
            g.clone(config['sharing']['workspaceGitRepo'], e3_io.get_e3_data_git_dir())
            
        targetDir = os.path.join(e3_io.get_e3_data_git_dir(), self.name)
        if not os.path.isdir(targetDir):
            self.output.append("Pulled successfully but " + self.name + " not found in the repository.")
            return
        if os.path.isdir(e3_io.get_working_dir()):
            shutil.rmtree(e3_io.get_working_dir())
        shutil.copytree(targetDir, e3_io.get_working_dir())
        self.output.append("Pulled successfully")

@logged
class GitPush(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name, message):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
            
        import git
        import e3_io
        try:
            g = git.Git(e3_io.get_e3_data_git_dir())
            try:
                g.status()
            except git.exc.GitCommandError as e:
                g.init() # can already have a .git folder
                g.remote("add", "origin", config['sharing']['workspaceGitRepo']) # can already have an "origin"
            g.pull("origin", "master") # may not be able to if remote is invalid url
            
            targetDir = os.path.join(e3_io.get_e3_data_git_dir(), self.name)
            if os.path.isdir(targetDir):
                shutil.rmtree(targetDir)
            shutil.copytree(e3_io.get_working_dir(), targetDir)
            g.add(".")
            try: 
                g.commit("-m", self.message) #could fail if nothing to commit anymore locally, but push missing
            except git.exc.GitCommandError as e:
                self.output.append(str(e))
            #could in theory have empty message 
            g.push("--all")
            self.output.append("Pushed successfully")
        except git.exc.GitCommandError as e:
            self.output.append(str(e))

@logged
class GitCachePush(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, message):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        import git
        import e3_io
        try:
            g = git.Git(e3_io.get_e3_dir())
            try:
                g.status()
            except git.exc.GitCommandError as e:
                g.init() # can already have a .git folder
                g.remote("add", "origin", config['sharing']['cacheGitRepo']) # can already have an "origin"
            g.fetch() # may not be able to if remote is invalid url
            g.add(".")
            try: 
                g.commit("-m", self.message) #could fail if nothing to commit anymore locally, but push missing
            except git.exc.GitCommandError as e:
                self.output.append(str(e))
            #could in theory have empty message 
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
        import e3_parse
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
        self.tapManager.set_name(self.name, self.tap.get_id());
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
                
class PrintNames(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        names = self.tapManager.get_names()
        if names:
            self.output.append('\n'.join(names))
        else:
            self.output.append('No names stored.')
    
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
            self.output.append(taxonomy.__str__() + "\n")
            
class PrintArticulations(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        indices = []
        for x in range(1, len(self.tap.articulations) + 1):
            indices.append(str(x) + ". ")
        articulationLines = [x + y for x, y in zip(indices, [a.__str__() for a in self.tap.articulations])]
        self.output.append('\n'.join(articulationLines))

@logged 
class LoadTap(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, cleantaxFile):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        import e3_validation
        try:
            import e3_io
            tap = e3_io.CleantaxReader().get_tap_from_cleantax_file(self.cleantaxFile)
            self.tapManager.set_current_tap(tap)
            self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(tap.get_id()))
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
        currentTap = self.tapManager.get_current_tap()
        config = ConfigManager().get_config()
        import e3_model
        tap = e3_model.Tap(config['defaultIsCoverage'], config['defaultIsSiblingDisjointness'], config['defaultRegions'], [], [])
        self.tapManager.set_current_tap(tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(currentTap.get_id()))

class AddChildren(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, taxonomyId, children):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        parts = self.children[1:-1].split()
        if len(parts) <= 1:
            self.output.append("Taxonomy line with one <= 1 node is not valid.")
            return
        
        import e3_validation
        try:
            self.tap.add_children(self.taxonomyId, parts[0], parts[1:])
            self.tapManager.set_current_tap(self.tap)
        except ValueError as e:
            self.output.append(str(e))
            return
        except e3_validation.ValidationException as e:
            self.output.append(str(e))
            return
        
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

class RemoveChildren(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, taxonomyId, children, recursive):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        parts = self.children[1:-1].split()
        if len(parts) <= 1:
            self.output.append("Taxonomy line with one <= 1 node is not valid.")
            return
        
        import e3_validation
        try:
            self.tap.remove_children(self.taxonomyId, parts[0], parts[1:], self.recursive)
            self.tapManager.set_current_tap(self.tap)
        except ValueError as e:
            self.output.append(str(e))
            return
        except e3_validation.ValidationException as e:
            self.output.append(str(e))
            return
        
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

class AddTaxonomy(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id, name):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if self.tap.has_taxonomy(self.id):
            self.output.append("Taxonomy with id: " + self.id + " already exists")
            
        self.tap.add_taxonomy(e3_model.Taxonomy(self.id, self.name))
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

class RemoveTaxonomy(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if not self.tap.has_taxonomy(self.id):
            self.output.append("Taxonomy with id " + self.id + " does not exist")
            return
        self.tap.remove_taxonomy(self.id)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
            
class ClearTaxonomy(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if not self.tap.has_taxonomy(self.id):
            self.output.append("Taxonomy with id " + self.id + " does not exist")
            return
        self.tap.clear_taxonomy(self.id)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
                    
class ClearArticulations(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tap.articulations = []
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
            
class SetTaxonomyInfo(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id, newId, newName):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tap.set_taxonomy_info(self.id, self.newId, self.newName)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
        
@logged
class AddArticulation(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, articulationLine):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        import e3_io
        articulation = e3_io.CleantaxReader().get_articulation_from_cleantax(self.articulationLine)
        if articulation is  None:
            self.output.append("Not a valid articulation. No valid relation found.")
        else:
            import e3_validation
            if e3_validation.ModelValidator().is_valid_new_articulation(articulation, self.tap):
                self.tap.add_articulation(articulation)
                self.tapManager.set_current_tap(self.tap)
                self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
            else:
                self.output.append("This articulation already exists: " + newArticulation)

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
        #self.tapManager.remove_articulation(self.input, self.tap, self.articulationIndex)
        self.tap.remove_articulation(self.articulationIndex)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
    
class UseTap(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tapManager.set_current_tap(self.tap)
        if self.tap:
            self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
            
@logged
class SetCoverage(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, value):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        self.tap.isCoverage = self.value
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

@logged 
class SetRegions(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, value):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if self.value == "mnpw" or self.value == "mncb" or self.value == "mnve" or self.value == "vrpw" or self.value == "vrve":
            self.tap.regions = self.value
            self.tapManager.set_current_tap(self.tap)
            self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
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
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
    
@logged 
class GraphWorlds(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        if not self.is_consistent():
            self.output.append("The tap is inconsistent. I have nothing to show")
            return
            
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return 0
        
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        if not self.is_consistent():
            self.output.append("Cannot determine if there are more than {more} worlds. The tap is not consistent".format(more = self.more))
        
        stdout, stderr, returnCode = self.run_euler(self.alignMaxNCommand)
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        if self.is_consistent():
            self.output.append("The tap is not inconsistent. I have nothing to show.")
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignRepairCommand)
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
    def __init__(self, tap, type):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return 
                
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        if self.is_consistent():
            self.output.append("The tap is not inconsistent. I have nothing to show.")
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)
        if self.type == "reduced":
            stdout, stderr, returnCode = self.run_euler(self.showInconLatReducedCommand)
        elif self.type == "full":
            stdout, stderr, returnCode = self.run_euler(self.showInconLatFullCommand)
        else:
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        if not self.is_consistent():
            self.output.append("The tap is inconsistent. I have nothing to show.")
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        # This can be executed on consistent and inconsistent taps!
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        if not self.is_consistent():
            self.output.append("The tap is inconsistent. I have nothing to show.")
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignCommand)
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
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        stdout, stderr, returnCode = self.run_euler(self.alignConsistencyCommand)
        if not self.is_consistent():
            self.output.append("The tap is inconsistent. I have nothing to show.")
            return
        
        self.maxN = 2
        stdout, stderr, returnCode = self.run_euler(self.alignMaxNCommand)
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
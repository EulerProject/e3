'''
@author: Thomas
'''
from autologging import logged
from pinject import copy_args_to_public_fields
from subprocess import Popen, PIPE, call
import os
import shutil
from ruamel import yaml
import re
from collections import OrderedDict
import csv
from ruamel.yaml.scalarstring import SingleQuotedScalarString, DoubleQuotedScalarString

@logged
class Command(object):
    @copy_args_to_public_fields
    def __init__(self):
        import e3_io
        self.tapManager = e3_io.TapManager()
        self.configManager = e3_io.ConfigManager()
        import e3_io
        self.graphCreator = e3_io.GraphCreator()
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

class Euler2(object):
    alignUncertaintyReductionInputCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --ur'
    alignExtractInputCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner}  -e {regions} {disjointness} {coverage} --xia'
    alignArtRemCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner}  -e {regions} {disjointness} {coverage} --artRem'
    alignFourInOneCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --fourinone'
    alignCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage}'
    alignConsistencyCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --consistency'
    alignMaxNCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} -n {maxN}'
    alignRepairCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --repair={repairMethod}'
    alignRepairHSTCommand = '{euler2Executable} align {cleantaxFile} -o {outputDir} -r {reasoner} -e {regions} {disjointness} {coverage} --repair=HST'
    showIVCommand = '{euler2Executable} show iv {cleantaxFile} -o {outputDir} {imageFormat}';
    showPWCommand = '{euler2Executable} show -o {outputDir} pw {imageFormat}'
    showInconLatCommand = '{euler2Executable} show -o {outputDir} inconLat {imageFormat}'
    showInconLatFullCommand = '{euler2Executable} show -o {outputDir} inconLat {imageFormat} --full'
    showInconLatReducedCommand = '{euler2Executable} show -o {outputDir} inconLat {imageFormat} --reduced'
    showFourInOneCommand = '{euler2Executable} show -o {outputDir} fourinone {imageFormat}'
    showSummaryCommand = '{euler2Executable} show -o {outputDir} sv {imageFormat}'
    showAmbLatCommand = '{euler2Executable} show -o {outputDir} ambLat {imageFormat}'
    commandStyles = OrderedDict()
    commandStyles[showIVCommand] = []
    commandStyles[showIVCommand].append("input")
    commandStyles[showIVCommand].append("singletoninput")
    commandStyles[showIVCommand].append("map")
    commandStyles[showIVCommand].append("ncs")
    commandStyles[showPWCommand] = []
    commandStyles[showPWCommand].append("rcg")
    commandStyles[showPWCommand].append("zoomin")
    commandStyles[showPWCommand].append("map")
    commandStyles[showPWCommand].append("ncs")
    commandStyles[showSummaryCommand] = []
    commandStyles[showSummaryCommand].append("aggregate")
    commandStyles[showSummaryCommand].append("cluster")
    commandStyles[showSummaryCommand].append("map")
    commandStyles[showSummaryCommand].append("ncs")
    commandStyles[showAmbLatCommand] = []
    commandStyles[showAmbLatCommand].append("map")
    commandStyles[showAmbLatCommand].append("ncs")
    commandStyles[showFourInOneCommand] = []
    commandStyles[showFourInOneCommand].append("map")
    commandStyles[showFourInOneCommand].append("ncs")
    commandStyles[showInconLatCommand] = []
    commandStyles[showInconLatCommand].append("map")
    commandStyles[showInconLatCommand].append("ncs")
    #not clear what "map" and "ncs" styles are used for hence added for all show commands
    
    @copy_args_to_public_fields
    def __init__(self, tap):    
        import e3_io
        configManager = e3_io.ConfigManager()
        tapManager = e3_io.TapManager()    
        config = configManager.get_config()
        self.style = configManager.get_style()
        self.euler2Executable = config['environment']['euler2Executable']
        self.reasoner = config['reasoning']['reasoner']
        self.imageFormat = config['cli behavior']['imageFormat']
        self.repairMethod = config['reasoning']['fixMethod']
        self.isCoverage = self.tap.isCoverage
        self.isSiblingDisjointness = self.tap.isSiblingDisjointness
        self.regions = self.tap.regions
        self.tapId = self.tap.get_id()
        self.cleantaxFile = tapManager.get_cleantax_file(self.tapId)
        self.tapDir = tapManager.get_tap_dir(self.tapId)
        self.e2InputDir = os.path.join(self.tapDir, "{uniqueParameteredRun}", "0-Input")
        self.e2AspInputDir = os.path.join(self.tapDir, "{uniqueParameteredRun}", "1-ASP-input-code")
        self.e2AspOutputDir = os.path.join(self.tapDir, "{uniqueParameteredRun}", "2-ASP-output")
        self.e2MirDir = os.path.join(self.tapDir, "{uniqueParameteredRun}", "3-MIR")
        self.e2PWsDir = os.path.join(self.tapDir, "{uniqueParameteredRun}", "4-PWs")
        self.e2AggregatesDir = os.path.join(self.tapDir, "{uniqueParameteredRun}", "5-Aggregates")
        self.e2LatticesDir = os.path.join(self.tapDir, "{uniqueParameteredRun}", "6-Lattices")
        self.isConsistent = True
        if not hasattr(self, 'maxN'):
            self.maxN = None
    def run(self, command):
        # add parameters to the command that are relevant to avoid re-runs (i.e. all tap relevant data + maxN + ...?)
        # by at the same time keeping the file name minimal
        coverage = "" if self.isCoverage else "--disablecov"
        disjointness = "" if self.isSiblingDisjointness else "--disablesib"
        imageFormat = "--svg" if self.imageFormat == "svg" else ""
        
        uniqueParameteredRun = "{reasoner} {regions} {coverage} {disjointness} {maxN} {repairMethod} {imageFormat}"
        uniqueParameteredRun = uniqueParameteredRun.format(reasoner = self.reasoner, regions = self.regions, coverage = coverage, 
                          disjointness = disjointness, maxN = self.maxN, repairMethod = self.repairMethod, 
                          imageFormat = imageFormat)
        uniqueParameteredRun = '_'.join(uniqueParameteredRun.split())
        outputDir = os.path.join(self.tapDir, uniqueParameteredRun)
        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)
        self.e2InputDir = self.e2InputDir.format(uniqueParameteredRun = uniqueParameteredRun)
        self.e2AspInputDir = self.e2AspInputDir.format(uniqueParameteredRun = uniqueParameteredRun)
        self.e2AspOutputDir = self.e2AspOutputDir.format(uniqueParameteredRun = uniqueParameteredRun)
        self.e2MirDir = self.e2MirDir.format(uniqueParameteredRun = uniqueParameteredRun)
        self.e2PWsDir = self.e2PWsDir.format(uniqueParameteredRun = uniqueParameteredRun)
        self.e2AggregatesDir = self.e2AggregatesDir.format(uniqueParameteredRun = uniqueParameteredRun)
        self.e2LatticesDir = self.e2LatticesDir.format(uniqueParameteredRun = uniqueParameteredRun)
        
        uniqueCommand = command.format(euler2Executable = '{euler2Executable}', 
                cleantaxFile = '{cleantaxFile}', outputDir = '{outputDir}', 
                #imageFormat = '{imageFormat}', 
                #reasoner = '{reasoner}', 
                repairMethod = self.repairMethod, maxN = self.maxN, regions = self.regions, coverage = coverage, 
                disjointness = disjointness, imageFormat = imageFormat, reasoner = self.reasoner)
        uniqueCommand = ' '.join(uniqueCommand.split())
        stdoutFile = os.path.join(outputDir, '%s.stdout' % uniqueCommand)
        stderrFile = os.path.join(outputDir, '%s.stderr' % uniqueCommand)
        returnCodeFile = os.path.join(outputDir, '%s.returncode' % uniqueCommand)
        styleFile = os.path.join(outputDir, '%s.styles' % uniqueCommand)
        currentCommandStyle = OrderedDict()
        if command in Euler2.commandStyles and Euler2.commandStyles[command]:
            for style in Euler2.commandStyles[command]:
                currentCommandStyle[style] = self.style[style]
        import e3_io
        if os.path.isfile(stdoutFile) and os.path.isfile(stderrFile) and os.path.isfile(returnCodeFile) and os.path.isfile(styleFile):
            refreshCommandForced = False
            if command in Euler2.commandStyles and Euler2.commandStyles[command]:
                with open(styleFile, 'r') as f:
                    previousStyle = yaml.load(f, Loader=yaml.RoundTripLoader, preserve_quotes=True)
                if currentCommandStyle != previousStyle:
                    refreshCommandForced = True
            if not refreshCommandForced:
                with open(stdoutFile, 'r') as f:
                    self.stdout = f.read()
                with open(stderrFile, 'r') as f:
                    self.stderr = f.read()
                with open(returnCodeFile, 'r') as f:
                    self.returnCode = f.read()
                if "Input is inconsistent" in self.stdout:
                    self.isConsistent = False
                if self.returnCode and self.stderr:
                    print self.stderr.rstrip()
                return self.stdout, self.stderr, self.returnCode
        
        stylesheetsDir = os.path.join(outputDir, "stylesheets")
        e3_io.mkdirs_ignore_existing(stylesheetsDir)
        for key in self.style:
            with open(os.path.join(stylesheetsDir, key + "style_src.yaml"), "w") as src:
                yaml.dump(self.style[key], src, Dumper=yaml.RoundTripDumper, default_flow_style=False)
            #to conform to the expectation of Euler's y2d that the stylesheet yaml files require an extra identation (see default-stylesheets)
            with open(os.path.join(stylesheetsDir, key + "style_src.yaml"), "r") as src:
                with open(os.path.join(stylesheetsDir, key + "style.yaml"), "w") as fileExpectedFormat:
                   for line in src:
                       fileExpectedFormat.write('  ' + line)
            os.remove(os.path.join(stylesheetsDir, key + "style_src.yaml"))
            
         # add remaining parameters
        effectiveCommand = uniqueCommand.format(euler2Executable = self.euler2Executable, 
                cleantaxFile = self.cleantaxFile, outputDir = outputDir, imageFormat = self.imageFormat, 
                maxN = self.maxN, reasoner = self.reasoner);
        with open(stdoutFile, 'w+') as out:
            with open(stderrFile, 'w+') as err:
                with open(returnCodeFile, 'w+') as rc:
                    with open(styleFile, 'w+') as s:
                        #print effectiveCommand
                        #print outputDir
                        p = Popen(effectiveCommand, stdout=PIPE, stderr=PIPE, shell=True, cwd = outputDir)
                        self.stdout, self.stderr = p.communicate()
                        #print self.stdout
                        #print self.stderr
                        if p.returncode and self.stderr:
                            print self.stderr.rstrip()
                        if "Input is inconsistent" in self.stdout:
                            self.isConsistent = False
                        out.write(self.stdout)
                        err.write(self.stderr)
                        rc.write('%s' % p.returncode)
                        yaml.dump(currentCommandStyle, s, Dumper=yaml.RoundTripDumper, default_flow_style=False)
                        #if os.path.isfile('report.csv'):
                        #    os.remove('report.csv') not needed with Popen(..cwd=)
                        self.returncode = p.returncode
                        return self.stdout, self.stderr, self.returncode
    def is_consistent(self):
        return self.isConsistent
    def get_world_yaml(self):
        for filename in os.listdir(self.e2PWsDir):
            if filename.startswith("cleantax_0_") and filename.endswith(".yaml"):
                with open(os.path.join(self.e2PWsDir, filename), "r") as f:
                    return yaml.load(f)
    def get_worlds(self):
        worlds = []
        worldStart = False
        world = []
        for line in self.stdout.splitlines():
            if len(line.strip()) == 0:
                continue
            if line.startswith('Possible world'):
                if worldStart:
                    worlds.append(world)
                worldStart = True
                world = []
            elif worldStart:
                line = line.strip()[1:-1]
                line = line.split(", ")
                for a in line:
                    a = a.replace("\"!\"", " disjoint ")
                    a = a.replace("\"=\"", " equals ")
                    a = a.replace("\"<\"", " is_included_in ")
                    a = a.replace("\">\"", " includes ")
                    a = a.replace("\"><\"", " overlaps ")
                    world.append(a)
        if world:
            worlds.append(world)
        return worlds
    
    def get_world_count(self):
        return len(self.get_worlds())
    def get_maximal_articulation_sets(self):
        sets = []
        for filename in os.listdir(self.e2InputDir):
            if filename.startswith("cleantax-alt"):
                set = []
                file = os.path.join(self.e2InputDir, filename)
                import e3_io
                tap = e3_io.CleantaxReader().get_tap_from_cleantax_file(file)
                for a in tap.articulations:
                    set.append(a.__str__()[1:-1]);
                sets.append(set)
        return sets
    
    def get_unique_articulation_sets(self):
        uniqueArtSets = []
        for line in self.stdout.splitlines():
            if line.startswith('Min articulation subset that makes unique PW'):
                uniqueArtSet = []
                articulationsLine = line.split('[')[1]
                articulations = re.compile(":|,|]").split(articulationsLine)
                for i, articulation in enumerate(articulations):
                    if i%2 == 1:
                        uniqueArtSet.append(articulation.strip())
                uniqueArtSets.append(uniqueArtSet)
        return uniqueArtSets
    
    #['1.B is_included_in 2.B', '1.A equals 2.A', '1.G equals 2.G', '1.C 1.D lsum 2.C', '1.F equals 2.F', '1.E equals 2.E'] ['1.B is_included_in 2.B', '1.H equals 2.H', '1.A equals 2.A', '1.G equals 2.G', '1.C 1.D lsum 2.C', '1.E equals 2.E'] 
    def get_maximal_ambiguity_sets(self):
        for line in self.stdout.splitlines():
            if line.startswith('MAA'):
                uniqueArtSets = []
                articulationSets = re.compile("\] \[|\[|\]").split(line)[1:-1]
                for articulationSet in articulationSets:
                    uniqueArtSet = []
                    for i, articulation in enumerate(articulationSet.split(", ")):
                        uniqueArtSet.append(articulation.strip()[1:-1])
                    uniqueArtSets.append(uniqueArtSet)
                return uniqueArtSets


    def get_maximal_consistency_sets(self):
        for line in self.stdout.splitlines():
            if line.startswith('MCS'):
                uniqueArtSets = []
                articulationSets = re.compile("\] \[|\[|\]").split(line)[1:-1]
                for articulationSet in articulationSets:
                    uniqueArtSet = []
                    for i, articulation in enumerate(articulationSet.split(", ")):
                        uniqueArtSet.append(articulation.strip()[1:-1])
                    uniqueArtSets.append(uniqueArtSet)
                return uniqueArtSets
    
    def get_minimal_inconsistency_sets(self):
        for line in self.stdout.splitlines():
            if line.startswith('MIS'):
                uniqueArtSets = []
                articulationSets = re.compile("\] \[|\[|\]").split(line)[1:-1]
                for articulationSet in articulationSets:
                    uniqueArtSet = []
                    for i, articulation in enumerate(articulationSet.split(", ")):
                        uniqueArtSet.append(articulation.strip()[1:-1])
                    uniqueArtSets.append(uniqueArtSet)
                return uniqueArtSets
    
    def get_minimal_uniqueness_sets(self):
        for line in self.stdout.splitlines():
            if line.startswith('MUS'):
                uniqueArtSets = []
                articulationSets = re.compile("\] \[|\[|\]").split(line)[1:-1]
                for articulationSet in articulationSets:
                    uniqueArtSet = []
                    for i, articulation in enumerate(articulationSet.split(", ")):
                        uniqueArtSet.append(articulation.strip()[1:-1])
                    uniqueArtSets.append(uniqueArtSet)
                return uniqueArtSets
    
    def get_input_graphs(self):
        files = []
        for filename in os.listdir(self.e2InputDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2InputDir, filename)
                files.append(file)
        return files
    def get_world_graphs(self):
        files = []
        for filename in os.listdir(self.e2PWsDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2PWsDir, filename)
                files.append(file)
        return files
    def get_world_graphs_count(self):
        return len(self.get_world_graphs())
    def get_fix_option_sets(self):
        sets = []
        for line in self.stdout.splitlines():
            if line.startswith('Repair option'):
                set = []
                articulations = line.split("[")[1].strip()[:-1]
                for a in articulations.split(" , "):
                    set.append(a)
                sets.append(set)
            if line.startswith('Possible world'):
                return []
        return sets
    def get_mir(self):
        mir = []
        mirFile = os.path.join(self.e2MirDir, "cleantax_mir.csv")
        if os.path.isfile(mirFile):
            with open(mirFile, 'r') as f:
                lines = f.read().split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        elements = line.split(",")
                        newElements = []
                        collectSet = []
                        insideSet = False
                        for e in elements:
                            if not e.startswith("{") and not e.endswith("}") and not insideSet:
                                newElements.append(e)
                            else:
                                collectSet.append(e.replace("{", "").replace("}", "").strip())
                                if e.startswith("{"):
                                    insideSet = True
                                if e.endswith("}"):
                                    insideSet = False
                                    newElements.append(','.join(collectSet))
                                    
                        import e3_model
                        relations = []
                        if "," in newElements[1]:
                            relations = newElements[1].split(',')
                        else:
                            relations.append(newElements[1])
                        
                        for relation in relations:
                            if relation == "!": relation = "disjoint"
                            if relation == "=": relation = "equals"
                            if relation == "<": relation = "is_included_in"
                            if relation == ">": relation = "includes"
                            if relation == "><": relation = "overlaps"
                            
                            leftNodes = []
                            leftNodes.append(newElements[0])
                            rightNodes = []
                            rightNodes.append(newElements[2])
                            a = e3_model.Articulation(leftNodes, rightNodes, relation)
                            mir.append({ 
                                "type": newElements[3],
                                "articulation": a
                            })
        return mir
    def get_inconsistency_lattice_graphs(self, type):
        graphs = []
        for filename in os.listdir(self.e2LatticesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2LatticesDir, filename)
                if type == "full":
                    if "_fulllat" in filename:
                        graphs.append(file)
                elif type == "reduced":
                    if "_lat" in filename:
                        graphs.append(file)
                else:
                    graphs.append(file)
        return graphs
    def get_four_in_one_lattice_graphs(self):
        graphs = []
        for filename in os.listdir(self.e2LatticesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2LatticesDir, filename)
                graphs.append(file)
        return graphs
    def get_summary_graphs(self):
        graphs = []
        for filename in os.listdir(self.e2AggregatesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2AggregatesDir, filename)
                graphs.append(file)
        return graphs
    def get_ambiguity_lattice_graphs(self):
        graphs = []
        for filename in os.listdir(self.e2LatticesDir):
            if filename.endswith(".%s" % self.imageFormat):
                file = os.path.join(self.e2LatticesDir, filename)
                graphs.append(file)
        return graphs
    
    
class Euler2Command(Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Command.__init__(self)
        config = self.configManager.get_config()
        self.imageViewer = config['environment']['imageViewer']
        self.maxWorldsToShow = config['cli behavior']['maxWorldsToShow']
    def run(self):
        Command.run(self)

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
        existsKey = False
        for firstLevelKey in config:
            if self.key in config[firstLevelKey]:
                oldValue = config[firstLevelKey][self.key]
                existsKey = True
                break
        
        if not existsKey:
            self.output.append("Configuration parameter " + self.key + " does not exist.")
            return 
        
        if type(oldValue) is bool:
            self.value = True if not (self.value == 'false' or self.value == 'False') else False
        elif type(oldValue) is int:
            self.value = int(self.value)
        elif type(oldValue) is str:
            self.value = str(self.value)
        if type(oldValue) is DoubleQuotedScalarString:
            self.value = DoubleQuotedScalarString(self.value)
        if type(oldValue) is SingleQuotedScalarString:
            self.value = SingleQuotedScalarString(self.value)
            
        config[firstLevelKey][self.key] = self.value
        self.configManager.store_config(config)
        self.output.append("Configuration updated: " + self.key + " = " + str(self.value))
        
class SetStyle(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, key, value):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        style = self.configManager.get_style()
        
        keys = self.key.split("/")
        currentDict = style
        pastKey = "/"
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                break
            if key in currentDict:
                currentDict = currentDict[key]
                pastKey += key + "/"
            else:
                self.output.append("Style parameter " + key + " does not exist in " + pastKey)
                return
        
        oldValue = currentDict[keys[i]]
        if type(oldValue) is bool:
            self.value = True if not (self.value == 'false' or self.value == 'False') else False
        if type(oldValue) is int:
            self.value = int(self.value)
        if type(oldValue) is str:
            self.value = str(self.value)
        if type(oldValue) is DoubleQuotedScalarString:
            self.value = DoubleQuotedScalarString(self.value)
        if type(oldValue) is SingleQuotedScalarString:
            self.value = SingleQuotedScalarString(self.value)
        currentDict[keys[i]] = self.value
        self.configManager.store_style(style)
        self.output.append("Configuration updated: " + self.key + " = " + str(self.value))

class PrintConfig(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        print yaml.dump(config, Dumper=yaml.RoundTripDumper, default_flow_style=False)
        
class PrintStyle(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        style = self.configManager.get_style()
        print yaml.dump(style, Dumper=yaml.RoundTripDumper, default_flow_style=False)
          
@logged 
class Reset(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
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
class ResetStyle(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        import e3_io
        self.configManager.store_style(self.configManager.get_default_style())
        self.output.append("Reset style successfully")

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
class GitStatePull(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        repo = config['sharing']['stateGitRepo']
        if repo == None or not repo.strip() :
            self.output.append("Configuration value stateGitRepo is not set.")
            return
        
        import git
        import e3_io
        gitDir = os.path.join(e3_io.get_e3_git_dir(), 
                              "_".join(re.compile("\W+").split(repo)))
        if not os.path.isdir(gitDir):
            os.mkdir(gitDir)
        g = git.Git(gitDir)
        try:
            g.status()
            g.pull()
        except git.exc.GitCommandError as e:
            e3_io.clean_e3_git_dir()
            g.clone(repo, e3_io.get_e3_git_dir())
        
        targetDir = os.path.join(gitDir, os.path.join(*(self.name.split("/"))))
        if not os.path.isdir(targetDir):
            self.output.append("Pulled successfully but " + self.name + " not found in the repository.")
            return
        if os.path.isdir(e3_io.get_e3_dir()):
            shutil.rmtree(e3_io.get_e3_dir())
        shutil.copytree(targetDir, e3_io.get_e3_dir())
        self.output.append("Pulled successfully")
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
        
@logged
class GitPull(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name):
        MiscCommand.__init__(self)
        pass
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        repo = config['sharing']['workspaceGitRepo']
        if repo == None or not repo.strip() :
            self.output.append("Configuration value workspaceGitRepo is not set.")
            return
        
        import git
        import e3_io
        gitDir = os.path.join(e3_io.get_e3_data_git_dir(), 
                              "_".join(re.compile("\W+").split(repo)))
        if not os.path.isdir(gitDir):
            os.mkdir(gitDir)
        g = git.Git(gitDir)
        try:
            g.status()
            g.pull()
        except git.exc.GitCommandError as e:
            e3_io.clean_e3_data_git_dir()
            g.clone(repo, e3_io.get_e3_data_git_dir())
            
        targetDir = os.path.join(gitDir, os.path.join(*(self.name.split("/"))))
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
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        repo = config['sharing']['workspaceGitRepo']
        if repo == None or not repo.strip() :
            self.output.append("Configuration value workspaceGitRepo is not set.")
            return
        
        import git
        import e3_io
        try:
            gitDir = os.path.join(e3_io.get_e3_data_git_dir(), 
                                  "_".join(re.compile("\W+").split(repo)))
            if not os.path.isdir(gitDir):
                os.mkdir(gitDir)
            g = git.Git(gitDir)
            try:
                g.status()
            except git.exc.GitCommandError as e:
                g.init() # can already have a .git folder
                g.remote("add", "origin", repo) # can already have an "origin"
            g.pull("origin", "master") # may not be able to if remote is invalid url
            
            targetDir = os.path.join(gitDir, os.path.join(*(self.name.split("/"))))
            if os.path.isdir(targetDir):
                shutil.rmtree(targetDir)
            import e3_io
            e3_io.mkdirs_ignore_existing(os.path.abspath(os.path.join(targetDir, os.path.pardir)))
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
class GitStatePush(MiscCommand):
    @copy_args_to_public_fields
    def __init__(self, name, message):
        MiscCommand.__init__(self)
    def run(self):
        MiscCommand.run(self)
        config = self.configManager.get_config()
        repo = config['sharing']['stateGitRepo']
        if repo == None or not repo.strip() :
            self.output.append("Configuration value stateGitRepo is not set.")
            return
        
        import git
        import e3_io
        try:
            gitDir = os.path.join(e3_io.get_e3_git_dir(), 
                      "_".join(re.compile("\W+").split(repo)))
            if not os.path.isdir(gitDir):
                os.mkdir(gitDir)
            g = git.Git(gitDir)
            try:
                g.status()
            except git.exc.GitCommandError as e:
                g.init() # can already have a .git folder
                g.remote("add", "origin", repo) # can already have an "origin"
            g.pull("origin", "master") # may not be able to if remote is invalid url
            
            targetDir = os.path.join(gitDir, os.path.join(*(self.name.split("/"))))
            if os.path.isdir(targetDir):
                shutil.rmtree(targetDir)
            import e3_io
            e3_io.mkdirs_ignore_existing(os.path.abspath(os.path.join(targetDir, os.pardir)))
            shutil.copytree(e3_io.get_e3_dir(), targetDir)
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

class AddConcepts(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, taxonomyId, children):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        parts = self.children[1:-1].split()
        #1 part will add concept as root
        #if len(parts) <= 1:
        #    self.output.append("Taxonomy line with <= 1 nodes is invalid.")
        #    return
        
        import e3_validation
        try:
            if len(parts) == 1:
                self.tap.add_node(self.taxonomyId, parts[0])
            elif len(parts) > 1:
                self.tap.add_children(self.taxonomyId, parts[0], parts[1:])
            self.tapManager.set_current_tap(self.tap)
            self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
        except ValueError as e:
            self.output.append(str(e))
            return
        except e3_validation.ValidationException as e:
            self.output.append(str(e))
            return


class RemoveConcepts(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, taxonomyId, children, recursive):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        parts = self.children[1:-1].split()
        #1 part will remove concept as root
        #if len(parts) <= 1:
        #    self.output.append("Taxonomy line with <= 1 nodes is invalid.")
        #    return
        
        import e3_validation
        try:
            if len(parts) == 1:
                self.tap.remove_node(self.taxonomyId, parts[0])
            elif len(parts) > 1:
                self.tap.remove_children(self.taxonomyId, parts[0], parts[1:], self.recursive)
            self.tapManager.set_current_tap(self.tap)
            self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
        except ValueError as e:
            self.output.append(str(e))
            return
        except e3_validation.ValidationException as e:
            self.output.append(str(e))
            return

class AddTaxonomy(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, id, name):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if self.tap.has_taxonomy(self.id):
            self.output.append("Taxonomy with id: " + self.id + " already exists")
            
        import e3_model
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
        self.articulationLine = "[" + self.articulationLine + "]"
        articulation = e3_io.CleantaxReader().get_articulation_from_cleantax(self.articulationLine)
        if articulation is  None:
            self.output.append("This is not a valid articulation.")
        else:
            import e3_validation
            if e3_validation.ModelValidator().is_valid_new_articulation(articulation, self.tap):
                self.tap.add_articulation(articulation)
                self.tapManager.set_current_tap(self.tap)
                self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
            else:
                self.output.append("This articulation already exists: " + self.articulationLine)

@logged
class RemoveArticulationByIndex(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, articulationIndex):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if self.articulationIndex > len(self.tap.articulations) or self.articulationIndex < 1:
            self.output.append("This is not a valid index.")
            return
        self.tap.remove_articulation_by_index(self.articulationIndex)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))
    
@logged
class RemoveArticulation(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, articulationLine):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        
        import e3_io
        articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + self.articulationLine + "]")
        if articulation is  None:
            self.output.append("This is not a valid articulation: " + self.articulationLine)
        else:
            if not self.tap.contains_articulation(articulation):
                self.output.append("The tap does not contain the articulation: " + self.articulationLine)
                return
            self.tap.remove_articulation(articulation)
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
            self.output.append("This is not a valid region.")

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

def get_taxonomy_from_world_yaml(tap, worldYaml):
    srcTaxonomiesIds = []
    srcTaxonomiesNames = []
    for taxonomy in tap.taxonomies:
        srcTaxonomiesIds.append(taxonomy.id)
        srcTaxonomiesNames.append(taxonomy.name)
    import e3_model
    taxonomy = e3_model.Taxonomy('-'.join(srcTaxonomiesIds), '-'.join(srcTaxonomiesNames))
    for key in worldYaml:
        #if "concept" in worldYaml[key]:
            #node    
            #groups.add(wordYaml[key]['group'])
        if "label" in worldYaml[key]:
            #edge
            src = worldYaml[key]['s']
            src = src.replace('\\n', '-')
            target = worldYaml[key]['t']
            target = target.replace('\\n', '-')
            children = []
            children.append(src)
            taxonomy.add_children(target, children)
    return taxonomy

@logged
class RenameConcept(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, taxonomyId, oldName, newName):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        if not self.tap.has_taxonomy(self.taxonomyId):
            self.output.append("Taxonomy with id " + self.taxonomyId + " not found.")
        taxonomy = self.tap.get_taxonomy(self.taxonomyId)
        if not taxonomy.contains_node(self.oldName):
            self.output.append("Taxonomy with id " + self.taxonomyId + " does not contain a concept with name " + self.oldName)
        if taxonomy.contains_node(self.newName):
            self.output.append("Taxonomy with id " + self.taxonomyId + " already contains a concept with name " + self.newName)
        self.tap.rename_concept(self.taxonomyId, self.oldName, self.newName)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

@logged
class CreateTapFromWorlds(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, srcTaps):
        ModelCommand.__init__(self)
    def run(self):
        ModelCommand.run(self)
        createdTap = self.tapManager.get_default_tap()
        for srcTap in self.srcTaps:
            srcTapName = self.tapManager.get_tap_name(srcTap.get_id())
            unique, align = is_unique(srcTap)
            self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir)
            if unique:
                align = Euler2(srcTap)
                stdout, stderr, returnCode = align.run(Euler2.alignCommand)
                showPW = Euler2(srcTap)
                stdout, stderr, returnCode = showPW.run(Euler2.showPWCommand)
                worldYaml = align.get_world_yaml()
                if worldYaml is None:
                    self.output.append("Cannot find unique world of tap " + srcTapName)
                    return
                taxonomy = get_taxonomy_from_world_yaml(srcTap, worldYaml)
                createdTap.add_taxonomy(taxonomy)
            else:
                self.output.append("Tap " + srcTapName + " is not unique.")
                return
        self.tapManager.set_current_tap(createdTap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(createdTap.get_id()))
            
def is_consistent(tap):
    alignConsistency = Euler2(tap)
    stdout, stderr, returnCode = alignConsistency.run(Euler2.alignConsistencyCommand)
    return alignConsistency.is_consistent()
    
def is_unique(tap):
    alignMaxN = Euler2(tap)
    alignMaxN.maxN = 2
    stdout, stderr, returnCode = alignMaxN.run(Euler2.alignMaxNCommand)
    worldCount = alignMaxN.get_world_count()
    return worldCount == 1, alignMaxN

@logged 
class GraphWorlds(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap, maxWorlds):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if self.maxWorlds is not None and self.maxWorlds <= 0:
            self.output.append("Can only produce a positive number of worlds.")
            return
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        if self.maxWorlds is not None:
            alignMaxN = Euler2(self.tap)
            alignMaxN.maxN = self.maxWorlds
            stdout, stderr, returnCode = self.run_euler(Euler2.alignMaxNCommand)
            self.outputFiles.append(self.graphCreator.create_mir_graph(alignMaxN.get_mir(), alignMaxN.e2MirDir))
        else:
            align = Euler2(self.tap)
            stdout, stderr, returnCode = align.run(Euler2.alignCommand)
            self.outputFiles.append(self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir))
        
        showPW = Euler2(self.tap)
        showPW.maxN = self.maxWorlds
        stdout, stderr, returnCode = showPW.run(Euler2.showPWCommand)
        worldCount = showPW.get_world_graphs_count()
        if worldCount == 0:
            self.output.append("There are no worlds.")
        else:
            self.output.append("{count} worlds have been produced.".format(
                count = worldCount))
        self.executeOutput = []
        openCount = 0
        for f in showPW.get_world_graphs():
            self.outputFiles.append(f)
            if openCount < self.maxWorldsToShow:
                openCount += 1
                self.executeOutput.append(self.imageViewer.format(file = f))
                    
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
        if is_consistent(self.tap):
            self.output.append("Yes.")
        else:
            self.output.append("No")
            
@logged
class IsAmbiguous(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("No, the tap is inconsistent.")
        unique, align = is_unique(self.tap)
        self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir)
        if unique:
            self.output.append("No.")
        else:
            self.output.append("Yes.")
@logged
class IsUnique(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return 0
        if not is_consistent(self.tap):
            self.output.append("No, the tap is inconsistent.")
        unique, align = is_unique(self.tap)
        self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir)
        if unique:
            self.output.append("Yes.")
        else:
            self.output.append("No.")
            
@logged 
class MoreWorldsThan(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap, more):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return 0
        if not is_consistent(self.tap):
            self.output.append("Cannot determine if there are more than {more} worlds. The tap is not consistent".format(more = self.more))
        
        alignMaxN = Euler2(self.tap)
        alignMaxN.maxN = self.more + 1 #adapt from "more than" to "more than equals"
        stdout, stderr, returnCode = alignMaxN.run(Euler2.alignMaxNCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignMaxN.get_mir(), alignMaxN.e2MirDir))
        worldCount = alignMaxN.get_world_count()
        if alignMaxN.maxN >= 2 and worldCount == 1:
            self.output.append("There is exactly one world. The tap is unique.")
        elif worldCount < alignMaxN.maxN:
            if alignMaxN.maxN == 1:
                self.output.append("The tap must be inconsistent. There are no worlds. Something may have gone wrong.")
            else:
                self.output.append("There are less than or equal to {more} worlds. In fact, there are {count}. The tap is ambiguous.".format(
                    more = self.more, count = worldCount))
        else:
            if alignMaxN.maxN == 1:
                self.output.append("There are more than {more} worlds. It is still unclear is the tap is ambiguous or unique.".format(
                    more = self.more))
            else:
                self.output.append("There are more than {more} worlds. The tap is ambiguous.".format(
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
        if is_consistent(self.tap):
            self.output.append("The tap is consistent. Nothing has been produced.")
            return
        
        alignRepair = Euler2(self.tap)
        stdout, stderr, returnCode = alignRepair.run(Euler2.alignRepairCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignRepair.get_mir(), alignRepair.e2MirDir))
        fixOptionSets = alignRepair.get_fix_option_sets()
        if fixOptionSets:
            self.output.append("Remove any of the following sets of articulations:")
            for i, set in enumerate(fixOptionSets):
                self.output.append(str(i + 1) + ".\n" + ', '.join(set) + "\n")
        else:
            self.output.append("The tap is consistent. Nothing has been produced.")

@logged 
class UseFix(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, setId):
        ModelCommand.__init__(self)
        self.setId = setId - 1
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if is_consistent(self.tap):
            self.output.append("The tap is consistent. Nothing has been produced.")
            return
        
        alignRepair = Euler2(self.tap)
        stdout, stderr, returnCode = alignRepair.run(Euler2.alignRepairCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignRepair.get_mir(), alignRepair.e2MirDir))
        fixOptionSets = alignRepair.get_fix_option_sets()
        if not fixOptionSets:
            self.output.append("No fixes available.")
        if self.setId < 0 or self.setId >= len(fixOptionSets):
           self.output.append("Invalid fix set id.")
           return
       
        import e3_io
        for a in fixOptionSets[self.setId]:
            articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
            self.tap.remove_articulation(articulation)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

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
        if is_consistent(self.tap):
            self.output.append("The tap is consistent. Nothing has been produced.")
            return
        
        alignRepairHST = Euler2(self.tap)
        stdout, stderr, returnCode = alignRepairHST.run(Euler2.alignRepairHSTCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignRepairHST.get_mir(), alignRepairHST.e2MirDir))
        if self.type == "reduced":
            showInconLatReduced = Euler2(self.tap)
            stdout, stderr, returnCode = showInconLatReduced.run(Euler2.showInconLatReducedCommand)
            graphs = showInconLatReduced.get_inconsistency_lattice_graphs(self.type)
        elif self.type == "full":
            showInconLatFull = Euler2(self.tap)
            stdout, stderr, returnCode = showInconLatFull.run(Euler2.showInconLatFullCommand)
            graphs = showInconLatFull.get_inconsistency_lattice_graphs(self.type)
        else:
            showInconLat = Euler2(self.tap)
            stdout, stderr, returnCode = showInconLat.run(Euler2.showInconLatCommand)
            graphs = showInconLat.get_inconsistency_lattice_graphs(self.type)
        
        self.output.append("Take a look at the produced graph.")
        self.executeOutput = []
        for f in graphs:
            self.executeOutput.append(self.imageViewer.format(file = f)) 
            self.outputFiles.append(f)
        
@logged
class PrintWorlds(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap, maxWorlds):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if self.maxWorlds is not None and self.maxWorlds <= 0:
            self.output.append("Can only produce a positive number of worlds.")
            return
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        if self.maxWorlds is not None:
            alignMaxN = Euler2(self.tap)
            alignMaxN.maxN = self.maxWorlds
            stdout, stderr, returnCode = alignMaxN.run(Euler2.alignMaxNCommand)
            self.outputFiles.append(self.graphCreator.create_mir_graph(alignMaxN.get_mir(), alignMaxN.e2MirDir))
            worlds = alignMaxN.get_worlds()
            worldCount = alignMaxN.get_world_count()
        else:
            align = Euler2(self.tap)
            stdout, stderr, returnCode = align.run(Euler2.alignCommand)
            self.outputFiles.append(self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir))
            worlds = align.get_worlds()
            worldCount = align.get_world_count()
        if worldCount == 0:
            self.output.append("There are no worlds.")
        else:
            self.output.append("{count} worlds have been produced.".format(
                count = worldCount))
        for i, world in enumerate(worlds):
            if i + 1 <= self.maxWorldsToShow:
                self.output.append("\n" + str(i + 1) + ". World")
                self.output.extend(world)
            else: break
            
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
        showIV = Euler2(self.tap)
        stdout, stderr, returnCode = showIV.run(Euler2.showIVCommand)
        self.output.append("Take a look at the produced graph.")
        self.executeOutput = []
        for f in showIV.get_input_graphs():
            self.executeOutput.append(self.imageViewer.format(file = f))
            self.outputFiles.append(f)
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
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        showFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = showFourInOne.run(Euler2.showFourInOneCommand)
        #if "This is a consistent example, no 4-in-1 lattice generated" in stdout:
            #self.output.append("The tap is consistent")
            #return
        
        self.output.append("Take a look at the produced graph.")
        self.executeOutput = []
        for f in showFourInOne.get_four_in_one_lattice_graphs():
            self.executeOutput.append(self.imageViewer.format(file = f))
            self.outputFiles.append(f)
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
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        align = Euler2(self.tap)
        stdout, stderr, returnCode = align.run(Euler2.alignCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir))
        showPW = Euler2(self.tap)
        stdout, stderr, returnCode = showPW.run(Euler2.showPWCommand)
        showSummary = Euler2(self.tap)
        stdout, stderr, returnCode = showSummary.run(Euler2.showSummaryCommand)
        self.output.append("Take a look at the produced graph.")
        self.executeOutput = []
        for f in showSummary.get_summary_graphs():
            self.executeOutput.append(self.imageViewer.format(file = f))
            self.outputFiles.append(f)
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
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        alignMaxN = Euler2(self.tap)
        alignMaxN.maxN = 2
        stdout, stderr, returnCode = alignMaxN.run(Euler2.alignMaxNCommand)
        worldCount = alignMaxN.get_world_count()
        if worldCount == alignMaxN.maxN:
            self.output.append("The tap is ambiguous. Nothing has been produced.")
            return
        
        alignArtRem = Euler2(self.tap)
        stdout, stderr, returnCode = alignArtRem.run(Euler2.alignArtRemCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignArtRem.get_mir(), alignArtRem.e2MirDir))
        showAmbLat = Euler2(self.tap)
        stdout, stderr, returnCode = showAmbLat.run(Euler2.showAmbLatCommand)
        if "No MUS generated for this example" in stdout:
            self.output.append("The tap is not valid for graph ambiguity. Nothing has been produced.")
            return
        
        self.output.append("Take a look at the produced graph.")
        self.executeOutput = []
        for f in showAmbLat.get_ambiguity_lattice_graphs():
            self.executeOutput.append(self.imageViewer.format(file = f))
            self.outputFiles.append(f)

@logged
class PrintMinimalArticulations(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        alignMaxN = Euler2(self.tap)
        alignMaxN.maxN = 2
        stdout, stderr, returnCode = alignMaxN.run(Euler2.alignMaxNCommand)
        worldCount = alignMaxN.get_world_count()
        if worldCount != 1:
            self.output.append("The tap is ambiguous. Nothing has been produced.")
            return
        
        alignArtRem = Euler2(self.tap)
        alignArtRem.maxN = 2
        stdout, stderr, returnCode = alignArtRem.run(Euler2.alignArtRemCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignArtRem.get_mir(), alignArtRem.e2MirDir))
        
        uniqueArticulationSets = alignArtRem.get_unique_articulation_sets()
        for i, set in enumerate(uniqueArticulationSets):
            self.output.append(str(i + 1) + ".\n" + ', '.join(set) + "\n")

@logged
class UseMinimalArticulations(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, minimalArticulationSetId):
        ModelCommand.__init__(self)
        self.minimalArticulationSetId = minimalArticulationSetId - 1
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        alignMaxN = Euler2(self.tap)
        alignMaxN.maxN = 2
        stdout, stderr, returnCode = alignMaxN.run(Euler2.alignMaxNCommand)
        worldCount = alignMaxN.get_world_count()
        if worldCount != 1:
            self.output.append("The tap is ambiguous. Nothing has been produced.")
            return
        
        alignArtRem = Euler2(self.tap)
        alignArtRem.maxN = 2
        stdout, stderr, returnCode = alignArtRem.run(Euler2.alignArtRemCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignArtRem.get_mir(), alignArtRem.e2MirDir))
        uniqueArticulationSets = alignArtRem.get_unique_articulation_sets()
        if self.minimalArticulationSetId < 0 or self.minimalArticulationSetId >= len(uniqueArticulationSets):
           self.output.append("Invalid minimal articulation set id.")
           return
        
        import e3_io
        self.tap.articulations = []
        for a in uniqueArticulationSets[self.minimalArticulationSetId]:
            articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
            self.tap.add_articulation(articulation)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

@logged
class PrintMaximalArticulations(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        alignExtractInput = Euler2(self.tap)
        stdout, stderr, returnCode = alignExtractInput.run(Euler2.alignExtractInputCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignExtractInput.get_mir(), alignExtractInput.e2MirDir))
        for i, set in enumerate(alignExtractInput.get_maximal_articulation_sets()):
            self.output.append(str(i + 1) + ". Set\n" + '\n'.join(set) + "\n")
            
@logged
class UseMaximalArticulations(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, maximalArticulationSetId):
        ModelCommand.__init__(self)
        self.maximalArticulationSetId = maximalArticulationSetId - 1
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        alignExtractInput = Euler2(self.tap)
        stdout, stderr, returnCode = alignExtractInput.run(Euler2.alignExtractInputCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignExtractInput.get_mir(), alignExtractInput.e2MirDir))
        maximalArticulationSets = alignExtractInput.get_maximal_articulation_sets()
        if self.maximalArticulationSetId < 0 or self.maximalArticulationSetId >= len(maximalArticulationSets):
           self.output.append("Invalid maximal articulation set id.")
           return
        
        import e3_io
        self.tap.articulations = []
        for a in maximalArticulationSets[self.maximalArticulationSetId]:
            articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
            self.tap.add_articulation(articulation)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

@logged
class UseWorld(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, worldId):
        ModelCommand.__init__(self)
        if worldId is not None:
            self.worldId = worldId - 1
        else:
            self.worldId = worldId
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("The tap is inconsistent. Nothing has been produced.")
            return
        
        if self.worldId is None and not unique(self.tap):
            self.output.append("The tap is not unique.")
            return
        else:
            if self.worldId is None:
                self.worldId = 0
            align = Euler2(self.tap)
            stdout, stderr, returnCode = align.run(Euler2.alignCommand)
            self.outputFiles.append(self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir))
            worlds = align.get_worlds()
            if self.worldId < 0 or self.worldId >= len(worlds):
               self.output.append("Invalid world id.")
               return
            world = worlds[self.worldId]
            
            import e3_io
            self.tap.articulations = []
            for a in world:
                articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
                self.tap.add_articulation(articulation)
            self.tapManager.set_current_tap(self.tap)
            self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

@logged
class PrintMinimalUniqueness(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_minimal_uniqueness_sets()
        for i, set in enumerate(sets):
            self.output.append(str(i + 1) + ". Set\n" + '\n'.join(set) + "\n")
        if not sets:
            self.output.append("Minimal uniqueness is empty.")

@logged
class UseMinimalUniqueness(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, setId):
        ModelCommand.__init__(self)
        self.setId = setId - 1
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_minimal_uniqueness_sets()
        if not sets:
            self.output.append("Minimal uniqueness is empty.")
        if self.setId < 0 or self.setId >= len(sets):
           self.output.append("Invalid minimal uniqueness set id.")
           return
       
        import e3_io
        self.tap.articulations = []
        for a in sets[self.setId]:
            articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
            self.tap.add_articulation(articulation)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

            
@logged
class PrintMinimalInconsistency(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_minimal_inconsistency_sets()
        for i, set in enumerate(sets):
            self.output.append(str(i + 1) + ". Set\n" + '\n'.join(set) + "\n")
        if not sets:
            self.output.append("Minimal inconsistency is empty.")

@logged
class UseMinimalInconsistency(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, setId):
        ModelCommand.__init__(self)
        self.setId = setId - 1
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_minimal_inconsistency_sets()
        if not sets:
            self.output.append("Minimal inconsistency is empty.")
        if self.setId < 0 or self.setId >= len(sets):
           self.output.append("Invalid minimal inconsistency set id.")
           return
       
        import e3_io
        self.tap.articulations = []
        for a in sets[self.setId]:
            articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
            self.tap.add_articulation(articulation)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

            
@logged
class PrintMaximalConsistency(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_maximal_consistency_sets()
        for i, set in enumerate(sets):
            self.output.append(str(i + 1) + ". Set\n" + '\n'.join(set) + "\n")
        if not sets:
            self.output.append("Maximal consistency is empty.")

@logged
class UseMaximalConsistency(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, setId):
        ModelCommand.__init__(self)
        self.setId = setId - 1
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_maximal_consistency_sets()
        if not sets:
            self.output.append("Maximal consistency is empty.")
        if self.setId < 0 or self.setId >= len(sets):
           self.output.append("Invalid maximal consistency set id.")
           return
       
        import e3_io
        self.tap.articulations = []
        for a in sets[self.setId]:
            articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
            self.tap.add_articulation(articulation)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

@logged
class PrintMaximalAmbiguity(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_maximal_ambiguity_sets()
        for i, set in enumerate(sets):
            self.output.append(str(i + 1) + ". Set\n" + '\n'.join(set) + "\n")
        if not sets:
            self.output.append("Maximal ambiguity is empty.")

@logged
class UseMaximalAmbiguity(ModelCommand):
    @copy_args_to_public_fields
    def __init__(self, tap, setId):
        ModelCommand.__init__(self)
        self.setId = setId - 1
    def run(self):
        ModelCommand.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        
        alignFourInOne = Euler2(self.tap)
        stdout, stderr, returnCode = alignFourInOne.run(Euler2.alignFourInOneCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(alignFourInOne.get_mir(), alignFourInOne.e2MirDir))
        sets = alignFourInOne.get_maximal_ambiguity_sets()
        if not sets:
            self.output.append("Maximal ambiguity is empty.")
        if self.setId < 0 or self.setId >= len(sets):
           self.output.append("Invalid maximal ambiguity set id.")
           return
       
        import e3_io
        self.tap.articulations = []
        for a in sets[self.setId]:
            articulation = e3_io.CleantaxReader().get_articulation_from_cleantax("[" + a + "]")
            self.tap.add_articulation(articulation)
        self.tapManager.set_current_tap(self.tap)
        self.output.append("Tap: " + self.tapManager.get_tap_name_and_status(self.tap.get_id()))

@logged
class IsTrue(Euler2Command):
    @copy_args_to_public_fields
    def __init__(self, tap, articulationLine):
        Euler2Command.__init__(self, tap)
    def run(self):
        Euler2Command.run(self)
        if not self.tap.is_euler_ready():
            self.output.append("The tap is not ready: " + self.tap.get_status_message())
            return
        if not is_consistent(self.tap):
            self.output.append("No. (The tap is inconsistent, nothing will be true)")
            return
        
        align = Euler2(self.tap)
        stdout, stderr, returnCode = align.run(Euler2.alignCommand)
        self.outputFiles.append(self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir))
        worldCount = align.get_world_count()
        
        self.articulationLine = "[" + self.articulationLine + "]"
        import e3_io
        articulation = e3_io.CleantaxReader().get_articulation_from_cleantax(self.articulationLine)
        if articulation is  None:
            self.output.append("This is not a valid articulation.")
        else:
            import e3_validation
            if e3_validation.ModelValidator().is_valid_new_articulation(articulation, self.tap):
                self.tap.add_articulation(articulation)
            self.tapManager.store_tap(self.tap)
            if not is_consistent(self.tap):
                self.output.append("No.")
                return
            align = Euler2(self.tap)
            stdout, stderr, returnCode = align.run(Euler2.alignCommand)
            self.outputFiles.append(self.graphCreator.create_mir_graph(align.get_mir(), align.e2MirDir))
            worldCount = align.get_world_count()
            if worldCount == worldCount:
                self.output.append("Yes.")
            else:
                self.output.append("No.")
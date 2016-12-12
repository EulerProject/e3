'''
Created on Nov 22, 2016

@author: Thomas
'''
from autologging import logged
from pinject import copy_args_to_public_fields
import e3_command
import e3_io

@logged               
class CommandParser(object):
    @copy_args_to_public_fields
    def __init__(self, pattern):
        import re
        self.re = re.compile(pattern, re.IGNORECASE)
        self.config = e3_io.get_config()
        pass
    def is_command(self, input):
        return self.re.match(input)
    def get_command(self, input):
        pass
    def get_help(self):
        pass

@logged
class ResetParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^reset$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.Reset()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "reset\t\t\t\t\t\t\tResets e3 to factory settings"
    
@logged
class CreateProjectParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^create project (\S*)$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.CreateProject(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "create project <name>\t\t\t\t\tCreates a project with <name> including managable command history"
    
@logged
class OpenProjectParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^open project (\S*)$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.OpenProject(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "open project <name>\t\t\t\t\tOpens an existing project with <name>"
        
@logged
class PrintProjectHistoryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print project history$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.PrintProjectHistory(CommandProvider())
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print project history\t\t\t\t\tPrint the project's command history"
        
@logged
class RemoveProjectHistoryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^remove project history (\d+)$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.RemoveProjectHistory(CommandProvider(), int(match.group(1)))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove project history <index>\t\t\t\tRemove command with <index> and all dependent commands from the project's command history"
        
@logged
class CloseProjectParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^close project$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.CloseProject()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "close project\t\t\t\t\t\tClose the current project"
@logged
class RemoveProjectParser(CommandParser):    
    def __init__(self):
        CommandParser.__init__(self, '^remove project (\S*)$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.RemoveProject(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove project <name>\t\t\t\t\tRemove the project with <name>"
    
@logged
class PrintProjectsParser(CommandParser):    
    def __init__(self):
        CommandParser.__init__(self, '^print projects$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.PrintProjects()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print projects\t\t\t\t\t\tPrint an overview of the existing projects"
    
@logged
class ClearProjectsParser(CommandParser):    
    def __init__(self):
        CommandParser.__init__(self, '^clear projects')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.ClearProjects()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear projects\t\t\t\t\t\tClears all the projects"
    
@logged               
class ByeParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^bye$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.Bye()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "bye\t\t\t\t\t\t\tExit the euler2 tool"
    
@logged               
class HelpParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^help$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.Help()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "help\t\t\t\t\t\t\tShows this help"

class LoadTapParser(CommandParser):
    def __init__(self):
        #example:
        #load tap abstract.txt
        CommandParser.__init__(self, '^load tap (\S*)$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.LoadTap(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "load tap <cleantax file>\t\t\t\tLoads a tap from a cleantax file"

class AddArticulationParser(CommandParser):
    def __init__(self):
        #example: 
        #add articulation [1.A equals 2.B]
        #add articulation [1.A equals 2.B] 2312842819299391
        #add articulation [1.A equals 2.B] my_tap_name
        CommandParser.__init__(self, '^add articulation (\[.*\])( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(2) and match.group(3):
                tap = e3_io.get_tap_from_id_or_name(match.group(3))  
            if tap:          
                return e3_command.AddArticulation(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "add articulation <articulation> [<tap>]\t\t\tAdds <articulation> to the current tap or the optionally provided <tap>"

class RemoveArticulationParser(CommandParser):
    def __init__(self):
        #example: 
        #remove articulation 1
        #remove articulation 1 2312842819299391
        #remove articulation 1 my_tap_name
        CommandParser.__init__(self, '^remove articulation (\d+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(2) and match.group(3):
                tap = e3_io.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.RemoveArticulation(tap, int(match.group(1)))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove articulation <articulation_index> [<tap>]\tRemoves articulation with index <articulation_index> from the current tap or the optionally provided <tap>"

class SetCoverageParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set coverage (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(2) and match.group(3):
                tap = e3_io.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.SetCoverage(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set coverage <true|false> [<tap>]\t\t\tSets the reasoning coverage for the current tap or the optionally provided <tap>"

class SetConfigParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set config (\S+)\s*=\s*(\S*)$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.SetConfig(match.group(1), match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set config <key>=<value>\t\t\t\tSets the configiguration <parameter> with <value>"

class PrintConfigParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print config$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            return e3_command.PrintConfig()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print config\t\t\t\t\t\tPrints the configiguration settings"

class SetSiblingDisjointnessParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set sibling disjointness (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(2) and match.group(3):
                tap = e3_io.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.SetSiblingDisjointness(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set sibling disjointness <true|false> [<tap>]\t\tSets the reasoning regions for the current tap or the optionally provided <tap>"

class SetRegionsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set regions (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(2) and match.group(3):
                tap = e3_io.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.SetRegions(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set regions <mnpw|mncb|mnve|vrpw|vrve> [<tap>]\t\tSets the reasoning regions for the current tap or the optionally provided <tap>"


class NameTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^name tap (\S*)( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input);
        if match:
            tap = e3_io.get_current_tap()
            if match.group(2) and match.group(3):
                tap = e3_io.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.NameTap(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "name tap <name> [<tap>]\t\t\t\t\tNames the current tap or the optionally provided <tap> as <name>"

class PrintNamesParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print names$')
    def get_command(self, input):
        match = self.is_command(input);
        if match:
            return e3_command.PrintNames()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print names\t\t\t\t\t\tShows all stored names and their corresponding taps"

class ClearNamesParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear names$')
    def get_command(self, input):
        match = self.is_command(input);
        if match:
            return e3_command.ClearNames()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear names\t\t\t\t\t\tRemoves all stored named"

class UseTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use tap (\S+)$')
    def get_command(self, input):
        match = self.is_command(input);
        if match:
            tap = e3_io.get_tap_from_id_or_name(match.group(1))
            if tap:
                return e3_command.UseTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use tap <tap>\t\t\t\t\t\tMakes <tap> the current tap"
            
class PrintTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print tap( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print tap [<tap>]\t\t\t\t\tPrints the current tap or the optionally provided <tap>"
        
class PrintTaxonomiesParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print taxonomies( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintTaxonomies(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')   
    def get_help(self):
        return "print taxonomies [<tap>]\t\t\t\tPrints the taxonomies of the current tap or the optionally provided <tap>"
         
class PrintArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print articulations( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)    
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintArticulations(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print articulations [<tap>]\t\t\t\tPrints the articulations of the current tap or the optionally provided <tap>"

class MoreWorldsOrEqualThanParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^>= (\d+) worlds( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(2) and match.group(3):
                tap = e3_io.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.MoreWorldsOrEqualThan(tap, int(match.group(1)))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return ">= <count> worlds [<tap>]\t\t\t\tChecks if there are more than or equal than count number of possible worlds in the current tap or the optionally provided <tap>"

class GraphWorldsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph worlds( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphWorlds(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph worlds [<tap>]\t\t\t\t\tCreates graph visualizations of the possible worlds, if any exist, for the current tap or the optionally provided <tap>"

class GraphTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph tap( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph tap [<tap>]\t\t\t\t\tCreates a graph visualization of the current tap or the optionally provided <tap>"
    
class GraphFourInOneParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph four in one( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphFourInOne(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph four in one [<tap>]\t\t\t\tCreates a four-in-one visualization of the current tap or the optionally provided <tap>"
    
class GraphSummaryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph summary( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphSummary(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph summary [<tap>]\t\t\t\t\tCreates a summary visualization of the current tap or the optionally provided <tap>"
        
class GraphAmbiguityParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph ambiguity( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphAmbiguity(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph ambiguity [<tap>]\t\t\t\t\tCreates an ambiguity visualization of the current tap or the optionally provided <tap>"
        
class IsConsistentParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^is consistent( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.IsConsistent(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "is consistent [<tap>]\t\t\t\t\tChecks the consistency of the current tap or the optionally provided <tap>"
                             
class PrintWorldsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print worlds( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintWorlds(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print worlds [<tap>]\t\t\t\t\tPrints the possible worlds, if any exist, of the current tap or the optionally provided <tap>"
                       
class GraphInconsistencyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph inconsistency( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphInconsistency(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')   
    def get_help(self):
        return "graph inconsistency [<tap>]\t\t\t\tCreates a graph visualization of the inconsistency, if any exists, for the current tap or the optionally provided <tap>"
    
class PrintFixParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print fix( (\S*))?$')
    def get_command(self, input):
        match = self.is_command(input)
        if match:
            tap = e3_io.get_current_tap()
            if match.group(1) and match.group(2):
                tap = e3_io.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintFix(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print fix [<tap>]\t\t\t\t\tPrints a suggested fix of the inconsistency, if any exists, for the current tap or the optionally provided <tap>"
                  
commandParsers = [  ByeParser(),
                    HelpParser(), 
                    LoadTapParser(),
                    PrintTapParser(),
                    PrintTaxonomiesParser(),
                    PrintArticulationsParser(),
                    AddArticulationParser(),
                    RemoveArticulationParser(),
                    SetSiblingDisjointnessParser(),
                    SetCoverageParser(),
                    SetRegionsParser(),
                    NameTapParser(),
                    ClearNamesParser(),
                    PrintNamesParser(),
                    UseTapParser(), 
                    GraphTapParser(), 
                    IsConsistentParser(),
                    MoreWorldsOrEqualThanParser(),
                    GraphWorldsParser(), 
                    PrintWorldsParser(),
                    GraphSummaryParser(),
                    GraphFourInOneParser(),
                    GraphInconsistencyParser(),
                    GraphAmbiguityParser(),
                    PrintFixParser(),
                    CreateProjectParser(),
                    PrintProjectsParser(),
                    OpenProjectParser(),
                    CloseProjectParser(),
                    RemoveProjectParser(),
                    ClearProjectsParser(),
                    PrintProjectHistoryParser(),
                    RemoveProjectHistoryParser(),
                    SetConfigParser(),
                    PrintConfigParser(),
                    ResetParser()
                ]              
                                                
class CommandProvider(object):
    def __init__(self):
        #self.commands = Command.__subclasses__()#
        pass
    def provide(self, input):
        for parser in commandParsers:
            if parser.is_command(input):
               return parser.get_command(input)
'''
Created on Nov 22, 2016

@author: Thomas
'''
from autologging import logged
from pinject import copy_args_to_public_fields
import e3_command

@logged               
class CommandParser(object):
    @copy_args_to_public_fields
    def __init__(self, pattern):
        import re
        import e3_io
        self.re = re.compile(pattern, re.IGNORECASE)
        self.tapManager = e3_io.TapManager()
        pass
    def is_input(self, input):
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
        match = self.is_input(input)
        if match:
            return e3_command.Reset()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "reset\nResets e3 to factory settings"
    
@logged
class ClearParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.Clear()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "empty\nClears e3 taps"
    
@logged
class CreateProjectParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^create project (\S*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.CreateProject(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "create project <name>\nCreates a project with <name> including managable command history"
    
@logged
class OpenProjectParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^open project (\S*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.OpenProject(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "open project <name>\nOpens an existing project with <name>"
        
@logged
class PrintProjectHistoryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print project history$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.PrintProjectHistory(CommandProvider())
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print project history\nPrint the project's command history"
        
@logged
class RemoveProjectHistoryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^remove project history (\d+)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.RemoveProjectHistory(CommandProvider(), int(match.group(1)))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove project history <index>\nRemove command with <index> and all dependent commands from the project's command history"
        
@logged
class CloseProjectParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^close project$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.CloseProject()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "close project\nClose the current project"
@logged
class RemoveProjectParser(CommandParser):    
    def __init__(self):
        CommandParser.__init__(self, '^remove project (\S*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.RemoveProject(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove project <name>\nRemove the project with <name>"
    
@logged
class PrintProjectsParser(CommandParser):    
    def __init__(self):
        CommandParser.__init__(self, '^print projects$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.PrintProjects()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print projects\nPrint an overview of the existing projects"
    
@logged
class ClearProjectsParser(CommandParser):    
    def __init__(self):
        CommandParser.__init__(self, '^clear projects')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ClearProjects()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear projects\nClears all the projects"
    
@logged               
class ByeParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^(?:bye|exit|quit)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.Bye()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "bye\nExit e3"
    
@logged               
class HelpParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^help$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.Help()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "help\nShows this help"
    
@logged               
class GitPullParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git pull (?P<name>.+)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.GitPull(match.group("name"))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git pull\nClones or pulls e3_data from the configured git repository"

@logged               
class GitCachePullParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git cache pull')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.GitCachePull()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git cache pull\nClones or pulls the .e3 cache from the configured git repository"
    
@logged
class ShowHistoryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^show history$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ShowHistory()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "show history\nShows the html rendered history"

@logged               
class SetGitCredentialsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git credentials (.+) (.+) "(.*)"$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.SetGitCredentials(match.group(1), match.group(2), match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git credentials <host> <username> \"<password>\"\nSets the username and password for the git host"

@logged               
class GitPushParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git push (?P<name>.+)(?: (?P<message>.*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            if match.group("name") and match.group("message"):
                return e3_command.GitPush(match.group("name"), match.group("message"))
            else:
                return e3_command.GitPush(match.group("name"), "e3 git push") 
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git push <name> <message>\nCommits and pushes the e3_data to the configured git repository"

@logged               
class GitCachePushParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^git cache push(?: (?P<message>.*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            if match.group("message"):
                return e3_command.GitCachePush(match.group("message"))
            else:
                return e3_command.GitCachePush("e3 git cache push") 
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "git cache push <message>\nCommits and pushes the .e3 cache to the configured git repository"

class LoadTapParser(CommandParser):
    def __init__(self):
        #example:
        #load tap abstract.txt
        CommandParser.__init__(self, '^load tap (\S*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.LoadTap(match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "load tap <cleantax file>\nLoads a tap from a cleantax file"

class ClearTapParser(CommandParser):
    def __init__(self):
        #example:
        #load tap abstract.txt
        CommandParser.__init__(self, '^clear tap$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.ClearTap()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear tap\nSets the empty tap as the current tap"
    
class AddChildrenParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^add children (.+) (\\(.+\\))( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(3) and match.group(4):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(4))  
            if tap:   
                return e3_command.AddChildren(tap, match.group(1), match.group(2))
            else:
                raise Exception('Tap %s not found' % match.group(4))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "add children <taxonomyId> <children> [<tap>]\nAdds children to the taxonomy with <taxonomyId> of the current tap, or the optionally provided <tap>"

class RemoveChildrenParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^remove children(?: recursive)? (.+) (\\(.+\\))( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        recursive = input.startswith("remove children recursive")
        if match:
            tap = self.tapManager.get_current_tap()        
            if match.group(3) and match.group(4):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(4))  
            if tap:   
                return e3_command.RemoveChildren(tap, match.group(1), match.group(2), recursive)
            else:
                raise Exception('Tap %s not found' % match.group(4))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove children <recrusive> <taxonomyId> <children> [<tap>]\nRemoves children from the taxonomy with <taxonomyId> of the current tap, or the optionally provided <tap>"

class AddTaxonomyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^add taxonomy (.+) (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(3) and match.group(4):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(4))  
            if tap:   
                return e3_command.AddTaxonomy(tap, match.group(1), match.group(2))
            else:
                raise Exception('Tap %s not found' % match.group(4))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "add taxonomy <taxonomyId> <taxonomyName> [<tap>]\nAdds a taxonomy with <taxonomyId> and <taxonomyName> to the current tap, or the optionally provided <tap>"

class RemoveTaxonomyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^remove taxonomy (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))  
            if tap:   
                return e3_command.RemoveTaxonomy(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove taxonomy <taxonomyId> [<tap>]\nRemoves the taxonomy with <taxonomyId> and ALL referencing articulations from the current tap, or the optionally provided <tap>"

class ClearTaxonomyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear taxonomy (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))  
            if tap:   
                return e3_command.ClearTaxonomy(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear taxonomy <taxonomyId> [<tap>]\nClears the taxonomy with <taxonomyId> of the current tap, or the optionally provided <tap>"

class ClearArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^clear articulations( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))  
            if tap:   
                return e3_command.ClearArticulations(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "clear articulations [<tap>]\nClears the articulations of the current tap, or the optionally provided <tap>"

class SetTaxonomyInfoParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set taxonomy info (.+) (.+) (.+)( (\S*))?$$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(4) and match.group(5):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(5))  
            if tap:
                return e3_command.SetTaxonomyInfo(tap, match.group(1), match.group(2), match.group(3))
            else:
                raise Exception('Tap %s not found' % match.group(5))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set taxonomy info <oldTaxonomyId> <newTaxonomyId> <newTaxonomyName> [<tap>]\nSets the taxonomy info of the taxonomy with <oldTaxonomyId> to <newTaxonomyId> and <newTaxonomyName> of the current tap, or the optionally provided <tap>"
    
class AddArticulationParser(CommandParser):
    def __init__(self):
        #example: 
        #add articulation [1.A equals 2.B]
        #add articulation [1.A equals 2.B] 2312842819299391
        #add articulation [1.A equals 2.B] my_tap_name
        CommandParser.__init__(self, '^add articulation (.+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))  
            if tap:          
                return e3_command.AddArticulation(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "add articulation <articulation> [<tap>]\nAdds <articulation> to the current tap, or the optionally provided <tap>"

class RemoveArticulationParser(CommandParser):
    def __init__(self):
        #example: 
        #remove articulation 1
        #remove articulation 1 2312842819299391
        #remove articulation 1 my_tap_name
        CommandParser.__init__(self, '^remove articulation (\d+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.RemoveArticulation(tap, int(match.group(1)))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "remove articulation <articulation_index> [<tap>]\nRemoves articulation with index <articulation_index> from the current tap, or the optionally provided <tap>"

class SetCoverageParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set coverage (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                value = match.group(1)
                return e3_command.SetCoverage(tap, True if not (value == 'false' or value == 'False') else False)
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set coverage <true|false> [<tap>]\nSets the reasoning coverage for the current tap, or the optionally provided <tap>"

class SetConfigParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set config (\S+)\s*=\s*(.*)$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.SetConfig(match.group(1), match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set config <key>=<value>\nSets the configiguration <parameter> with <value>"

class PrintConfigParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print config$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            return e3_command.PrintConfig()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print config\nPrints the configiguration settings"

class SetSiblingDisjointnessParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set sibling disjointness (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                value = match.group(1)
                return e3_command.SetSiblingDisjointness(tap, True if not (value == 'false' or value == 'False') else False)
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set sibling disjointness <true|false> [<tap>]\nSets the reasoning regions for the current tap, or the optionally provided <tap>"

class SetRegionsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^set regions (\S+)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.SetRegions(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "set regions <mnpw|mncb|mnve|vrpw|vrve> [<tap>]\nSets the reasoning regions for the current tap, or the optionally provided <tap>"


class NameTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^name tap (\S*)( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input);
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.NameTap(tap, match.group(1))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "name tap <name> [<tap>]\nNames the current tap, or the optionally provided <tap> as <name>"

class PrintNamesParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print names$')
    def get_command(self, input):
        match = self.is_input(input);
        if match:
            return e3_command.PrintNames()
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print names\nShows all stored names and their corresponding taps"

#class ClearNamesParser(CommandParser):
#    def __init__(self):
#        CommandParser.__init__(self, '^clear names$')
#    def get_command(self, input):
#        match = self.is_input(input);
#        if match:
#            return e3_command.ClearNames()
#        else:
#            raise Exception('Unrecognized command line')
#    def get_help(self):
#        return "clear names\nRemoves all stored named"

class UseTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^use tap (\S+)$')
    def get_command(self, input):
        match = self.is_input(input);
        if match:
            tap = self.tapManager.get_tap_from_id_or_name(match.group(1))
            if tap:
                return e3_command.UseTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(1))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "use tap <tap>\nMakes <tap> the current tap"
    
class PrintTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print tap( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print tap [<tap>]\nPrints the current tap, or the optionally provided <tap>"
        
class PrintTaxonomiesParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print taxonomies( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintTaxonomies(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')   
    def get_help(self):
        return "print taxonomies [<tap>]\nPrints the taxonomies of the current tap, or the optionally provided <tap>"
         
class PrintArticulationsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print articulations( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)    
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintArticulations(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print articulations [<tap>]\nPrints the articulations of the current tap, or the optionally provided <tap>"

class MoreWorldsThanParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^more than (\d+) worlds( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(2) and match.group(3):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(3))
            if tap:
                return e3_command.MoreWorldsThan(tap, int(match.group(1)))
            else:
                raise Exception('Tap %s not found' % match.group(3))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "more than <count> worlds [<tap>]\nChecks if there are more than <count> number of possible worlds in the current tap, or the optionally provided <tap>"

class GraphWorldsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph worlds( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphWorlds(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph worlds [<tap>]\nCreates graph visualizations of the possible worlds, if any exist, for the current tap, or the optionally provided <tap>"

class GraphTapParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph tap( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphTap(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph tap [<tap>]\nCreates a graph visualization of the current tap, or the optionally provided <tap>"
    
class GraphFourInOneParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph four in one( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphFourInOne(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph four in one [<tap>]\nCreates a four-in-one visualization of the current tap, or the optionally provided <tap>"
    
class GraphSummaryParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph summary( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphSummary(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph summary [<tap>]\nCreates a summary visualization of the current tap, or the optionally provided <tap>"
        
class GraphAmbiguityParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph ambiguity( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.GraphAmbiguity(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "graph ambiguity [<tap>]\nCreates an ambiguity visualization of the current tap, or the optionally provided <tap>"
        
class IsConsistentParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^is consistent( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.IsConsistent(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "is consistent [<tap>]\nChecks the consistency of the current tap, or the optionally provided <tap>"
                             
class PrintWorldsParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print worlds( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintWorlds(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print worlds [<tap>]\nPrints the possible worlds, if any exist, of the current tap, or the optionally provided <tap>"
                       
class GraphInconsistencyParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^graph\s+(?:(?P<type>full|reduced)\s+)?inconsistency( (?P<tapName>\S+))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            type = match.group("type")
            tapName = match.group("tapName")
            if tapName:
                tap = self.tapManager.get_tap_from_id_or_name(tapName)
            if tap:
                return e3_command.GraphInconsistency(tap, type)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')   
    def get_help(self):
        return "graph inconsistency [<tap>]\nCreates a graph visualization of the inconsistency, if any exists, for the current tap, or the optionally provided <tap>"
    
class PrintFixParser(CommandParser):
    def __init__(self):
        CommandParser.__init__(self, '^print fix( (\S*))?$')
    def get_command(self, input):
        match = self.is_input(input)
        if match:
            tap = self.tapManager.get_current_tap()
            if match.group(1) and match.group(2):
                tap = self.tapManager.get_tap_from_id_or_name(match.group(2))
            if tap:
                return e3_command.PrintFix(tap)
            else:
                raise Exception('Tap %s not found' % match.group(2))
        else:
            raise Exception('Unrecognized command line')
    def get_help(self):
        return "print fix [<tap>]\nPrints a suggested fix of the inconsistency, if any exists, for the current tap, or the optionally provided <tap>"
                  
commandParsers = [  ByeParser(),
                    HelpParser(), 
                    ResetParser(),
                    ClearParser(),
                    SetConfigParser(),
                    PrintConfigParser(),
                    LoadTapParser(),
                    ClearTapParser(),
                    PrintTapParser(),
                    PrintTaxonomiesParser(),
                    PrintArticulationsParser(),
                    AddTaxonomyParser(),
                    RemoveTaxonomyParser(),
                    SetTaxonomyInfoParser(),
                    AddChildrenParser(),
                    RemoveChildrenParser(),
                    ClearTaxonomyParser(),
                    AddArticulationParser(),
                    RemoveArticulationParser(),
                    ClearArticulationsParser(),
                    SetSiblingDisjointnessParser(),
                    SetCoverageParser(),
                    SetRegionsParser(),
                    NameTapParser(),
                    #ClearNamesParser(),
                    PrintNamesParser(),
                    UseTapParser(), 
                    GraphTapParser(), 
                    IsConsistentParser(),
                    MoreWorldsThanParser(),
                    GraphWorldsParser(), 
                    PrintWorldsParser(),
                    GraphSummaryParser(),
                    GraphFourInOneParser(),
                    GraphInconsistencyParser(),
                    GraphAmbiguityParser(),
                    PrintFixParser(),
                    #CreateProjectParser(),
                    #PrintProjectsParser(),
                    #OpenProjectParser(),
                    #CloseProjectParser(),
                    #RemoveProjectParser(),
                    #ClearProjectsParser(),
                    #PrintProjectHistoryParser(),
                    #RemoveProjectHistoryParser(),
                    GitPullParser(),
                    GitPushParser(),
                    GitCachePullParser(),
                    GitCachePushParser(),
                    SetGitCredentialsParser(),
                    ShowHistoryParser()
                ]              
                                                
class CommandProvider(object):
    def __init__(self):
        #self.commands = Command.__subclasses__()#
        pass
    def provide(self, input):
        for parser in commandParsers:
            if parser.is_input(input):
               return parser.get_command(input)
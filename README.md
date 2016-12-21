<img src="http://euler.cs.ucdavis.edu/_/rsrc/1366832610901/home/logo_small.png" alt="The EulerX toolkit" width="100" height="88">
#e3

### Introduction
This repository is for the command line wrapper e3 of the [EulerX](https://github.com/EulerProject/EulerX) toolkit.
The [EulerX](https://github.com/EulerProject/EulerX) toolkit developed by the EulerProject team allows to solve the taxonomy alignment problem ("tap") [<a href="http://www.slideshare.net/taxonbytes/ludaescher-etal-2014hybriddiagnosisconceptreasoning" target="_blank">1</a>, <a href="http://taxonbytes.org/pdf/ChenEtAl2014-HybridDiagnosisApproach.pdf" target="_blank">2</a>].
Here we created a wrapper around the [EulerX](https://github.com/EulerProject/EulerX) toolkit to achieve the following benefits.

### Benefits
* Use of e3 as an interactive shell, or directly in scripts
* Use of modular commands with single responsiblities
* Ability to refine taxonomy alignment problems on-the-go
* Reduced exposure to certain expert options
* Reduced knowledge of the EulerX life-cycle
* Reduced exposure to EulerX generated output data
* Re-use of existing computation results in "projects"

### Demo
#### Configuration
<a target="_blank" href="http://content.screencast.com/users/thomas.rodenhausen/folders/Jing/media/40fbfb71-f76b-44bf-9e45-dbffc0f45b7a/2016-12-09_1457.swf&blurover=false"><img src="https://img.youtube.com/vi/BbqY7htrY5U/0.jpg" alt="Configuration" 
width="180" height="120"></a>

#### Tap naming and refinement on-the-go
<a target="_blank" href="http://content.screencast.com/users/thomas.rodenhausen/folders/Jing/media/87bb6699-1bd4-41c2-87fe-8502bb1a9760/2016-12-09_1442.swf&blurover=false"><img src="https://img.youtube.com/vi/BbqY7htrY5U/0.jpg" alt="Tap naming and refinement on-the-go" 
width="180" height="120"></a>

#### Projects
<a target="_blank" href="http://content.screencast.com/users/thomas.rodenhausen/folders/Jing/media/f9be00bf-18c7-4e76-a308-4d7d5b7e4f1c/2016-12-05_1354.swf&blurover=false"><img src="https://img.youtube.com/vi/BbqY7htrY5U/0.jpg" alt="Projects" 
width="180" height="120"></a>

### Command-Manual
Command                              | Description
-----------------------------------------------------------------|------------
bye							| Exit e3
help							| Shows this help
reset							| Resets e3 to factory settings
set config \<key\>=\<value\>				| Sets the configuration \<parameter\> with \<value\>
print config						| Prints the configuration settings
load tap \<cleantax file\>				| Loads a tap (taxonomy alignment problem) from a CleanTax file
print tap [\<tap\>]					| Prints the current tap, or the optionally provided \<tap\>
print taxonomies [\<tap\>]				| Prints the input taxonomies of the current tap, or the optionally provided \<tap\>
print articulations [\<tap\>]				| Prints the input articulations of the current tap, or the optionally provided \<tap\>
add articulation \<articulation\> [\<tap\>]			| Adds an <articulation> to the current tap, or the optionally provided \<tap\>
remove articulation \<articulation_index\> [\<tap\>]	| Removes an articulation with index <articulation_index> from the current tap, or the optionally provided \<tap\>
set sibling disjointness \<true\|false\> [\<tap\>]		| Sets the "sibling disjointness" reasoning constraint for the current tap, or the optionally provided \<tap\>
set coverage \<true\|false\> [\<tap\>]			| Sets the "coverage" reasoning constraint for the current tap, or the optionally provided \<tap\>
set regions \<mnpw\|mncb\|mnve\|vrpw\|vrve\> [\<tap\>]		| Sets the "region encoding" constraints for the current tap, or the optionally provided \<tap\>
name tap \<name\> [\<tap\>]					| Names the current tap, or the optionally provided \<tap\> as \<name\>
clear names						| Removes all stored names
print names						| Shows all stored names and their corresponding taps
use tap \<tap\>						| Makes \<tap\> the current tap
graph tap [\<tap\>]					| Creates an input graph visualization of the current tap, or the optionally provided \<tap\>
is consistent [\<tap\>]					| Checks the logical consistency of the current tap, or the optionally provided \<tap\>
more than \<count\> worlds [\<tap\>]				| Checks if there are more than <count> number of possible worlds in the current tap, or the optionally provided \<tap\>
graph worlds [\<tap\>]					| Creates output graph visualizations of the possible worlds - if any exist - for the current tap, or the optionally provided \<tap\>
print worlds [\<tap\>]					| Prints the possible worlds - if any exist - of the current tap, or the optionally provided \<tap\>
graph summary [\<tap\>]					| Creates a summary visualization of the current tap, or the optionally provided \<tap\>
graph four in one [\<tap\>]				| Creates a "four-in-one" diagnostic visualization for the "level" of constraint specification of the current tap, or the optionally provided \<tap\>
graph inconsistency [\<tap\>]				|Creates a graph visualization of the inconsistency - if any exists - for the current tap, or the optionally provided \<tap\>
graph ambiguity [\<tap\>]					| Creates an ambiguity visualization of the current tap, or the optionally provided \<tap\>
print fix [\<tap\>]					| Prints a suggested fix of the inconsistency - if any exists - for the current tap, or the optionally provided \<tap\>
create project \<name\>					| Creates a project with \<name\>, including managable command history
print projects						| Prints an overview of the existing projects
open project \<name\>					| Opens an existing project with \<name\>
close project						| Closes the current project
remove project \<name\>					| Removes the project with \<name\>
clear projects						| Clears all projects
print project history					| Prints the project's command history
remove project history \<index\>				| Removes command with \<index\> and all dependent commands from the project's command history

### Prerequisites
* Python 2.7.x
* Python modules: 
 * autologging
 * pinject
 * pyyaml
* [EulerX](https://github.com/EulerProject/EulerX) 

### Setup
* Setup preqrequistis
* Clone this repository
* Run e3
* If euler2 is not in your $PATH, do: 
 * e3 > set config euler2Executable = \<your_path_to_EulerX_src-el\>/euler2


### File organization
Directory                              | Description
-----------------------------------------------------------------|------------
$USER_HOME/.e3 | e3 relevant files
$USER_HOME/.e3/.config | stores the e3 configuration
$USER_HOME/.e3/.current_tap | stores the current tap
$USER_HOME/.e3/.current_project | stores the current project
$USER_HOME/.e3/.names | stores the tap to name mappings
$USER_HOME/.e3/taps | stores treated taps and their computed data
$USER_HOME/.e3/projects | stores user-created projects, their history, commands, inputs and outputs

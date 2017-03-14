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

### Command-Manual
Miscellaneous Commands

Command                              | Description
-----------------------------------------------------------------|------------
exit | Exit e3.
help | Shows this help.
reset | Resets to factory settings.
reset config | Resets the configuration to default.
clear | Clears the history and cache. Keeps the config.
clear history | Clears the history.
show history | Shows the html rendered history.
print config | Prints the configuration settings.
set config \<key\>=\<value\> | Sets the configuration \<parameter\> with \<value\>.
git credentials \<host\> \<username\> "\<password\>" | Sets the \<username\> and \<password\> for the git \<host\>.
git pull \<path\> | Clones or pulls an e3_data workspace from the \<path\> at the configured git repository.
git push \<path\> \<message\> | Commits (with \<message\>) and pushes the e3_data workspace to the \<path\> at the configured git repository.
git state pull \<path\> | Clones or pulls the e3 state from the \<path\> at the configured git repository.
git state push \<path\> \<message\> | Commits (with \<message\> and pushes the e3 state to the \<path\> at the configured git repository.

Tap Commands

Command                              | Description
-----------------------------------------------------------------|------------
print tap [\<tap\>] | Prints the current tap, or the optionally provided \<tap\>
print taxonomies [\<tap\>] | Prints the taxonomies of the current tap, or the optionally provided \<tap\>.
print articulations [\<tap\>] | Prints the articulations of the current tap, or the optionally provided \<tap\>.
add taxonomy \<taxonomyId\> \<taxonomyName\> [\<tap\>] | Adds a taxonomy with \<taxonomyId\> and \<taxonomyName\> to the current tap, or the optionally provided \<tap\>.
remove taxonomy \<taxonomyId\> [\<tap\>] | Removes the taxonomy with \<taxonomyId\> and all referencing articulations from the current tap, or the optionally provided \<tap\>.
set taxonomy info \<oldTaxonomyId\> \<newTaxonomyId\> \<newTaxonomyName\> [\<tap\>] | Sets the \<newTaxonomyid\> and \<newTaxonomyName\> to the taxonomy with \<oldTaxonomyId\> of the current tap, or the optionally provided \<tap\>.
add concept \<taxonomyId\> (\<parentConcepts\> \<childConcept 1\> ... \<childConcept n\>) [\<tap\>] | Adds \<childConcept\>'s to \<parentConcept\>, creating non-existing concept's as needed to the taxonomy with \<taxonomyId\> of the current tap, or the optionally provided \<tap\>.
remove concept \<recursive\> \<taxonomyId\> (\<parentConcepts\> \<childConcept 1\> ... \<childConcept n\>) [\<tap\>] | Removes \<childConcept\>'s from \<parentConcept\> in the taxonomy with \<taxonomyId\> of the current tap, or the optionally provided \<tap\>.
rename concept \<taxonomyId\> \<oldName\> \<newName\> [\<tap\>] | Renames the concept in taxonomy with \<taxonomyId\> from \<oldName\> to \<newName\> for the current tap, or the optionally provided \<tap\>.
clear taxonomy \<taxonomyId\> [\<tap\>] | Clears the taxonomy with \<taxonomyId\> of the current tap, or the optionally provided \<tap\>.
add articulation \<articulation\> [\<tap\>] | Adds \<articulation\> to the current tap, or the optionally provided \<tap\>.
remove articulation \<articulation_index\|articulation\> [\<tap\>] | Removes articulation with index \<articulation_index\> or string \<articulation\> from the current tap, or the optionally provided \<tap\>.
clear articulations [\<tap\>] | Clears the articulations of the current tap, or the optionally provided \<tap\>.
set sibling disjointness \<true\|false\> [\<tap\>] | Sets the sibling disjointness for the current tap, or the optionally provided \<tap\>.
set coverage \<true\|false\> [\<tap\>] | Sets the coverage for the current tap, or the optionally provided \<tap\>.
set regions \<mnpw\|mncb\|mnve\|vrpw\|vrve\> [\<tap\>] | Sets the regions for the current tap, or the optionally provided \<tap\>.
load tap \<cleantax file\> | Loads a tap from the \<cleantax file\>.
clear tap | Sets the empty tap as the current tap.
print names | Shows all stored names and their corresponding taps.
name tap \<name\> [\<tap\>] | Names the current tap, or the optionally provided \<tap\> as \<name\>.
use tap \<tap\> | Makes \<tap\> the current tap.

Euler Commands

Command                              | Description
-----------------------------------------------------------------|------------
graph tap [\<tap\>] | Creates a graph visualization of the current tap, or the optionally provided \<tap\>.
is consistent [\<tap\>] | Checks the consistency of the current tap, or the optionally provided \<tap\>.
is unique [\<tap\>] | Checks if there is a unique world for the current tap, or the optionally provided \<tap\>.
is ambiguous [\<tap\>] | Checks if there is more than 1 world for the current tap, or the optionally provided \<tap\>.
is true \<articulation\> [\<tap\>] | Checks if the articulation holds true for the current tap, or the optionally provided \<tap\>.
more than \<count\> worlds [\<tap\>] | Checks if there are more than \<count\> number of worlds in the current tap, or the optionally provided \<tap\>.
graph worlds [\<maxWorlds\>] [\<tap\>] | Creates graph visualizations of the worlds, if any exist, and if provided maximally \<maxWorlds\> for the current tap, or the optionally provided \<tap\>.
print worlds [\<maxWorlds\>] [\<tap\>] | Prints the worlds, if any exist, and if provided maximally \<maxWorlds\> for the current tap, or the optionally provided \<tap\>.
use world [\<worldId\>] [\<tap\>] | Replaces the articulations of the current tap or the optionally provided \<tap\> with all the articulations extracted from the given \<worldId\> or the unique world of the tap, if applicable and no \<worldId\> is given.
print minimal articulations [\<tap\>] | Prints minimal sets articulations for the unique world of the current tap, or the optionally provided \<tap\>.
use minimal articulations \<minimal articulation set id\> [\<tap\>] | Replaces the articulations of the current tap or the optionally provided \<tap\> with the articulations of the given \<minimal articulation set id\>.
print maximal articulations [\<tap\>] | Prints maximal sets of articulations for all worlds of the current tap, or the optionally provided \<tap\>.
use maximal articulations \<maximal articulation set id\> [\<tap\>] | Replaces the articulations of the current tap or the optionally provided \<tap\> with the articulations of the given \<maximal articulation set id\>.
graph ambiguity [\<tap\>] | Creates an ambiguity visualization of the current tap, or the optionally provided \<tap\>.
graph summary [\<tap\>] | Creates a summary visualization of the current tap, or the optionally provided \<tap\>.
graph four in one [\<tap\>] | Creates a four-in-one visualization of the current tap, or the optionally provided \<tap\>.
print minimal uniqueness [\<tap\>] | Prints the minimal subsets of articulations that create uniqueness for the current tap, or the optionally provided \<tap\>.
use minimal uniqueness \<set id\> [\<tap\>] | Replaces the articulations of the current tap or the optionally provided \<tap\> with the articulations of the given minimal uniqueness \<set id\>.
print minimal inconsistency [\<tap\>] | Prints the minimal subsets of articulations that create inconsistency for the current tap, or the optionally provided \<tap\>.
use minimal inconsistency \<set id\> [\<tap\>] | Replaces the articulations of the current tap or the optionally provided \<tap\> with the articulations of the given minimal inconsistency \<set id\>.
print maximal consistency [\<tap\>] | Prints the maximal subsets of articulations that create consistency for the current tap, or the optionally provided \<tap\>.
use maximal consistency \<set id\> [\<tap\>] | Replaces the articulations of the current tap or the optionally provided \<tap\> with the articulations of the given maximal consistency \<set id\>.
print maximal ambiguity [\<tap\>] | Prints the maximal subsets of articulations that create ambiguity for the current tap, or the optionally provided \<tap\>.
use maximal ambiguity \<set id\> [\<tap\>] | Replaces the articulations of the current tap or the optionally provided \<tap\> with the articulations of the given maximal ambiguity \<set id\>.
graph inconsistency [\<tap\>] | Creates a graph visualization of the inconsistency, if any exists, for the current tap, or the optionally provided \<tap\>.
print fix [\<tap\>] | Prints a set of suggested fixes of the inconsistency, if any exists, for the current tap, or the optionally provided \<tap\>.
use fix \<fix set id\> [\<tap\>] | Uses the fix with \<fix set id\> to create a consistent input from the current tap, or the optionally provided \<tap\>.
create tap from worlds \<tap_1\> ... \<tap_n\> | Creates a tap with the unique worlds of \<tap_1\> ... \<tap_n\> as taxonomies.

### Prerequisites
* Python 2.7.x
* Python modules: 
 * autologging
 * pinject
 * pyyaml
 * networkx
 * gitpython
 * python-numpy
 * matplotlib
 * beautifulsoup4
 * html5lib
* [EulerX](https://github.com/EulerProject/EulerX) 

### Setup
* Setup preqrequistis
* Clone this repository
* Run e3
* If euler2 is not in your $PATH, do: 
 * e3 > set config euler2Executable = \<your_path_to_EulerX_src-el\>/euler2

### File organization

e3 workspace:

Directory                              | Description
-----------------------------------------------------------------|------------
$CWD/e3_data | e3 workspace files.
$CWD/e3_data/index.html | Command history as browsable HTML.
$CWD/e3_data/{tap}/index.html | {tap} as browsable HTML.
$CWD/e3_data/{tap}/input.txt | {tap} as cleantax file.
$CWD/e3_data/{tap}/{command}/config.txt | Configuration at the time of {command} execution on {tap}.
$CWD/e3_data/{tap}/{command}/* | Output files created by {command} execution on {tap}.

e3 state:

Directory                              | Description
-----------------------------------------------------------------|------------
$USER_HOME/.e3 | e3 relevant files
$USER_HOME/.e3/.config | stores the configuration
$USER_HOME/.e3/.current_tap | stores the current tap
$USER_HOME/.e3/.history | stores the command history
$USER_HOME/.e3/.names | stores the tap to name mappings
$USER_HOME/.e3/taps | stores treated taps and their computed data

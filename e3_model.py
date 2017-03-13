'''
Created on Nov 22, 2016

'''
from pinject import copy_args_to_public_fields
import hashlib
import networkx as nx
import matplotlib.pyplot as plt
import copy
from networkx.readwrite import json_graph
import json

class History(object):
    @copy_args_to_public_fields
    def __init__(self, g):
        if g is None:
            self.g = nx.DiGraph()
    def add_edge(self, fromNode, toNode, attributesDict):
        self.g.add_edge(fromNode, toNode, attributesDict)
    def add_node(self, node, attributesDict):
        self.g.add_node(node, attributesDict)
    def clear(self):
        self.g.clear()
    def __str__(self, *args, **kwargs):
        return json_graph.node_link.node_link_data(self.g)
    
class Tap(object):
    @copy_args_to_public_fields
    def __init__(self, isCoverage, isSiblingDisjointness, regions, taxonomies, articulations):
        pass
    def is_euler_ready(self):
        error, note = self.get_status()
        return not error
    def is_underspecified(self):
        return len(self.taxonomies) <= 1 or len(self.articulations) == 0
    def get_status(self):
        error = []
        note = []
        if self.is_underspecified():
            error.append("underspecified")
        for t in self.taxonomies:
            import e3_validation
            if not e3_validation.ModelValidator().is_dag(t):
                error.append(t.id + " not a dag")
            if len(t.get_roots()) > 1:
                note.append(t.id + " has multiple roots (" + str(len(t.get_roots())) + ")")
        return error, note
    def get_status_message(self):
        error, note = self.get_status()
        if error and note:
            return "Invalid tap: " + ' and '.join(error) + ". Note: " + ' and '.join(note)
        if error:
            return "Invalid tap: " + ' and '.join(error);
        if note:
            return "Note: " + ' and '.join(note)
        return None
    def add_taxonomy(self, taxonomy):
        for t in self.taxonomies:
            if t.id == taxonomy.id:
                raise Exception("Taxonomy id " + t.id + " already exists")
        self.taxonomies.append(taxonomy)
    def remove_taxonomy(self, taxonomyId):
        self.articulations = [a for a in self.articulations if not self.is_references_taxonomy(a, taxonomyId)]
        self.taxonomies = [t for t in self.taxonomies if not t.id == taxonomyId]
        pass
    def clear_taxonomy(self, taxonomyId):
        self.articulations = [a for a in self.articulations if not self.is_references_taxonomy(a, taxonomyId)]
        self.get_taxonomy(taxonomyId).clear()
    def get_referenced_taxonomies(self, articulation):
        referencedTaxonomies = []
        for l in articulation.leftNodes:
            id = l.split(".")[0]
            t = self.get_taxonomy(id)
            referencedTaxonomies.append(t)
        for r in articulation.rightNodes:
            id = r.split(".")[0]
            t = self.get_taxonomy(id)
            referencedTaxonomies.append(t) 
        return referencedTaxonomies
    def is_references_taxonomy(self, articulation, taxonomyId):
        referencedTaxonomies = self.get_referenced_taxonomies(articulation)
        for t in referencedTaxonomies:
            if t.id == taxonomyId:
                return True
        return False
    def set_taxonomy_info(self, taxonomyId, newTaxonomyId, newName):
        taxonomy = self.get_taxonomy(taxonomyId)
        taxonomy.id = newTaxonomyId
        taxonomy.name = newName
        for a in self.articulations:
            newLeftNodes = []
            for l in a.leftNodes:
                if l.split(".")[0] == taxonomyId: newLeftNodes.append(newTaxonomyId + "." + l.split(".")[1])
                else: newLeftNodes.append(l)
            a.leftnodes = newLeftNodes
            newRightNodes = []
            for r in a.rightNodes:
                if r.split(".")[0] == taxonomyId: newRightNodes.append(newTaxonomyId + "." + r.split(".")[1])
                else: newRightNodes.append(r)
            a.rightNodes = newRightNodes
    def has_taxonomy(self, id):
        return self.get_taxonomy(id) is not None
    def rename_concept(self, taxonomyId, oldName, newName):
        if self.has_taxonomy(taxonomyId):
            taxonomy = self.get_taxonomy(taxonomyId)
            if taxonomy.contains_node(oldName):
                if not taxonomy.contains_node(newName):
                    taxonomy.rename_node(oldName, newName)
                    for articulation in self.articulations:
                        for i, l in enumerate(articulation.leftNodes):
                            id = l.split(".")[0]
                            node = l.split(".")[1]
                            if id == taxonomyId and node == oldName:
                                articulation.leftNodes[i] = id + "." + newName
                        for i, r in enumerate(articulation.rightNodes):
                            id = r.split(".")[0]
                            node = r.split(".")[1]
                            if id == taxonomyId and node == oldName:
                                articulation.rightNodes[i] = id + "." + newName
                else:
                    raise ValueError("Node with name " + newName + " already exists.")
            else:
                raise ValueError("Node with name " + oldName + " does not exist.")
        else:
            raise ValueError("Taxonomy with id " + taxonomyId + " does not exist.")
    
    def add_node(self, taxonomyId, node):
        taxonomy = self.get_taxonomy(taxonomyId)
        taxonomy.add_node(node);
    def add_children(self, taxonomyId, parent, children):
        taxonomy = self.get_taxonomy(taxonomyId)
        if taxonomy:
            #original = copy.deepcopy(taxonomy)
            taxonomy.add_children(parent, children)
            #if not taxonomy.is_dag():
            #    self.set_taxonomy(taxonomyId, original)
            #    raise e3_validation.ValidationException("Adding the children would not lead to a valid taxonomy")
        else: raise ValueError("Taxonomy with id " + taxonomyId + " not found.")
    def remove_children(self, taxonomyId, parent, children, recursive):
        taxonomy = self.get_taxonomy(taxonomyId)
        if taxonomy:
            #original = copy.deepcopy(taxonomy)
            taxonomy.remove_children(parent, children, recursive)
            #if not taxonomy.is_dag():
            #    self.set_taxonomy(taxonomyId, original)
            #    raise e3_validation.ValidationException("Removing the children would not lead to a valid taxonomy")
        else: raise ValueError("Taxonomy with id " + taxonomyId + " not found.")
        self.articulations = [a for a in self.articulations if self.nodes_in_tap(a)]
    def set_taxonomy(self, taxonomyId, taxonomy):
        self.taxonomies = [taxonomy if t.id == taxonomyId else t for t in self.taxonomies]
    def nodes_in_tap(self, articulation):
        for l in articulation.leftNodes:
            id = l.split(".")[0]
            node = l.split(".")[1]
            taxonomy = self.get_taxonomy(id)
            if not taxonomy is None:
                if not taxonomy.contains_node(node):
                    return False
            else:
                return False
        for r in articulation.rightNodes:
            id = r.split(".")[0]
            node = r.split(".")[1]
            taxonomy = self.get_taxonomy(id)
            if not taxonomy is None:
                if not taxonomy.contains_node(node):
                    return False
            else:
                return False
        return True
        
    def get_taxonomy(self, id):
        for t in self.taxonomies:
            if t.id == id:
                return t
        return None
    def add_articulation(self, articulation):
        for l in articulation.leftNodes:
            id = l.split(".")[0]
            node = l.split(".")[1]
            t = self.get_taxonomy(id)
            if t is None:
                raise Exception("No taxonomy with id " + id + " found.")
            if not t.contains_node(node):
                raise Exception("No node with name " + node + " found in taxonomy " + id)
        for r in articulation.rightNodes:
            id = r.split(".")[0]
            node = r.split(".")[1]
            t = self.get_taxonomy(id)
            if t is None:
                raise Exception("No taxonomy with id " + id + " found.")
            if not t.contains_node(node):
                raise Exception("No node with name " + node + " found in taxonomy " + id)
        if not self.contains_articulation(articulation):
            self.articulations.append(articulation)
    def contains_articulation(self, articulation):
        return articulation in self.articulations
    def remove_articulation_by_index(self, articulationIndex):
        self.remove_articulation(sorted(self.articulations)[int(articulationIndex) - 1])
    def remove_articulation(self, articulation):
        self.articulations.remove(articulation)
    def __str__(self, *args, **kwargs):
        indices = []
        for x in range(1, len(sorted(self.articulations)) + 1):
            indices.append(str(x) + ". ")
        articulationLines = [x + y for x, y in zip(indices, [a.__str__() for a in sorted(self.articulations)])]
        articulationLines.insert(0, 'articulation')
        result = []
        for taxonomy in self.taxonomies:
            result.append(taxonomy.__str__())
               
        result.append('\n'.join(articulationLines))
        result = ('Coverage:' + str(self.isCoverage) + 
                 '\nSibling Disjontness:' + str(self.isSiblingDisjointness) + 
                 '\nRegions:' + self.regions + '\n\n' + 
                '\n\n'.join(result))
        return result
    
    def get_cleantax(self):
        result = []
        for taxonomy in self.taxonomies:      
            result.append(taxonomy.__str__() + '\n\n')
        result.append('articulation\n')
        for articulation in sorted(self.articulations):
            result.append(articulation.__str__() + '\n')
        return "".join(result)
        
    def get_id(self):
        # todo: sort articulations 
        # sort taxonomy lines 
        # to obtain same ids regardless of string output order
        return hashlib.sha1(self.__str__()).hexdigest()

class Taxonomy(object):
    @copy_args_to_public_fields
    def __init__(self, id, name):
        self.g = nx.DiGraph()
        pass
    def rename_node(self, oldNode, newNode):
        map = { }
        map[oldNode] = newNode
        nx.relabel_nodes(self.g, map, False)
    def clear(self):
        self.g.clear()
    def add_node(self, node):
        self.g.add_node(node)
    def add_children(self, parent, children):
        self.g.add_edges_from(zip([parent] * len(children), children))
    def remove_children(self, parent, children, recursive):
        for c in children:
            if self.g.has_edge(parent, c):
                self.g.remove_edge(parent, c)
                if recursive:
                    self.remove_children(c, self.g.successors(c), recursive)
            roots = self.get_roots()
            if not self.g.predecessors(c) and roots and not c == roots[0]:
                self.g.remove_node(c)
        
        #special case: parent = root; and only 1 left over node
        roots = self.get_roots()        
        if roots and parent == roots[0] and self.g.number_of_nodes() == 1:
            self.g.remove_node(parent)
    
        #    self.g.remove_node(parent)
        #for c in children:
        #    if self.g.has_edge(parent, c):
        #        descendants = nx.descendants(self.g, c)
        #        descendants.add(c)
        #        for d in descendants:
        #            if nx.ancestors(self.g, d)
        #            self.g.remove_nodes_from(descendants)
        #special case: parent = root; and only 1 left over node
        #roots = self.get_roots()
        #if roots and parent == roots[0] and self.g.number_of_nodes() == 1:
        #    self.g.remove_node(parent)
    def contains_node(self, node):
        return self.g.has_node(node)
    def get_roots(self):
        roots = []
        for node in self.g.nodes():
            if len(self.g.predecessors(node)) == 0:
                roots.append(node)
        return roots
    def __str__(self, *args, **kwargs):
        result = "taxonomy " + self.id + " " + self.name
        
        edges = []
        roots = self.get_roots()
        # in case we have a well-formed rooted tree, get logical order
        if roots:
            for node in sorted(roots):
                self.add_cleantax_stringyfied_edges(edges, node)
        # in case we don't, still produce something meaningful
        else:
            for node in self.g.nodes():
                line = "(" + node
                if self.g.successors(node):
                    for successor in sorted(self.g.successors(node)):
                        line = line + " " + successor
                    line = line + ")"
                    edges.append(line)
        if len(edges) > 0:
            result = result + '\n' + '\n'.join(edges)
        return result
    def add_cleantax_stringyfied_edges(self, collector, src):
        line = "(" + src
        if self.g.successors(src):
            for successor in sorted(self.g.successors(src)):
                line = line + " " + successor
                self.add_cleantax_stringyfied_edges(collector, successor)
            line = line + ")"
            collector.insert(0, line)
        else:
            if not self.g.predecessors(src):
                line = line + ")"
                collector.insert(0, line)
            
combinedRCC5s = "{ equals|includes|is_included_in|overlaps|disjoint }"
relations = [ "lsum", "l3sum", "l4sum", "rsum", "r3sum", "r4sum", "ldiff", "rdiff", "e4sum", "i4sum", "equals", "includes", 
                      "is_included_in", "overlaps", "disjoint", combinedRCC5s 
                      ]

#see Taxonomy comment
class Articulation(object):
    @copy_args_to_public_fields
    def __init__(self, leftNodes, rightNodes, relation):
        pass
    def __str__(self):
        return "[" + " ".join(self.leftNodes) + " " + self.relation + " " + " ".join(self.rightNodes) + "]"
    def __lt__ (self, other):
        return (self.relation + " " + " ".join(self.leftNodes) + " " + " ".join(self.rightNodes)).__lt__(
            other.relation + " " + " ".join(other.leftNodes) + " " + " ".join(other.rightNodes))
    def __gt__ (self, other):
        return other.__lt__(self)
    def __eq__(self, other):
        return self.__str__() == other.__str__()
    def __ne__ (self, other):
        return not self.__eq__(other)
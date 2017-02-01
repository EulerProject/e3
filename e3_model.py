'''
Created on Nov 22, 2016

'''
from pinject import copy_args_to_public_fields
import hashlib
import networkx as nx
import matplotlib.pyplot as plt
from compiler.ast import Node
import copy

class Tap(object):
    @copy_args_to_public_fields
    def __init__(self, isCoverage, isSiblingDisjointness, regions, taxonomies, articulations):
        pass
    def is_euler_ready(self):
        return not self.get_status()
    def is_underspecified(self):
        return len(self.taxonomies) <= 1 or len(self.articulations) == 0
    def get_status(self):
        result = []
        if self.is_underspecified():
            result.append("underspecified")
        for t in self.taxonomies:
            import e3_validation
            if not e3_validation.ModelValidator().is_dag(t):
                result.append(t.id + " invalid")
        return ' and '.join(result)
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
    def add_node(self, taxonomyId, node):
        taxonomy = self.get_taxonomy(taxonomyId)
        taxonomy.add_node(node);
    def add_children(self, taxonomyId, parent, children):
        taxonomy = self.get_taxonomy(taxonomyId)
        #original = copy.deepcopy(taxonomy)
        taxonomy.add_children(parent, children)
        #if not taxonomy.is_dag():
        #    self.set_taxonomy(taxonomyId, original)
        #    raise e3_validation.ValidationException("Adding the children would not lead to a valid taxonomy")
    def remove_children(self, taxonomyId, parent, children, recursive):
        taxonomy = self.get_taxonomy(taxonomyId)
        #original = copy.deepcopy(taxonomy)
        taxonomy.remove_children(parent, children, recursive)
        #if not taxonomy.is_dag():
        #    self.set_taxonomy(taxonomyId, original)
        #    raise e3_validation.ValidationException("Removing the children would not lead to a valid taxonomy")
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
            t = self.get_taxonomy(id)
            if t is None:
                raise Exception("No taxonomy with id " + id + " found.")
        for r in articulation.rightNodes:
            id = r.split(".")[0]
            t = self.get_taxonomy(id)
            if t is None:
                raise Exception("No taxonomy with id " + id + " found.")        
        self.articulations.append(articulation)
    def remove_articulation(self, articulationIndex):
        del self.articulations[int(articulationIndex) - 1]
    def __str__(self, *args, **kwargs):
        indices = []
        for x in range(1, len(self.articulations) + 1):
            indices.append(str(x) + ". ")
        articulationLines = [x + y for x, y in zip(indices, [a.__str__() for a in self.articulations])]
        articulationLines.insert(0, 'articulation')     
        result = []
        for taxonomy in self.taxonomies:
            taxonomyLines = taxonomy.__str__().split('\n')
            result.append('\n'.join(taxonomyLines))
               
        result.append('\n'.join(articulationLines))
        result = ('Coverage:' + str(self.isCoverage) + 
                 '\nSibling Disjontness:' + str(self.isSiblingDisjointness) + 
                 '\nRegions:' + self.regions + '\n\n' + 
                '\n\n'.join(result))
        return result
        
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
            for node in roots:
                self.add_cleantax_stringyfied_edges(edges, node)
        # in case we don't, still produce something meaningful
        else:
            for node in self.g.nodes():
                line = "(" + node
                if self.g.successors(node):
                    for successor in self.g.successors(node):
                        line = line + " " + successor
                    line = line + ")"
                    edges.append(line)
        if len(edges) > 0:
            result = result + '\n' + '\n'.join(edges)
        return result
    def add_cleantax_stringyfied_edges(self, collector, src):
        line = "(" + src
        if self.g.successors(src):
            for successor in self.g.successors(src):
                line = line + " " + successor
                self.add_cleantax_stringyfied_edges(collector, successor)
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

"""
Circuit simplification using De Morgan's theorem and other Boolean algebra rules
"""

from typing import List, Dict, Set, Optional
from circuit_dag import CircuitDAG, Node

class CircuitSimplifier:
    """Simplify logic circuits using Boolean algebra rules"""
    
    def __init__(self):
        self.optimization_rules = [
            self._apply_double_negation,
            self._apply_de_morgan,
            self._apply_absorption,
            self._apply_identity_laws,
            self._apply_complement_laws,
            self._apply_associativity,
            self._apply_distributivity,
            self._remove_redundant_gates
        ]
    
    def simplify(self, dag: CircuitDAG) -> CircuitDAG:
        """Apply all simplification rules iteratively"""
        current_dag = dag.copy()
        
        # Apply rules until no more changes
        max_iterations = 10
        for iteration in range(max_iterations):
            initial_gate_count = current_dag.gate_count()
            
            for rule in self.optimization_rules:
                current_dag = rule(current_dag)
            
            # If no reduction in gate count, we're done
            if current_dag.gate_count() >= initial_gate_count:
                break
        
        return current_dag
    
    def _apply_double_negation(self, dag: CircuitDAG) -> CircuitDAG:
        """Remove double negations: NOT(NOT(A)) = A"""
        new_dag = dag.copy()
        changed = True
        
        while changed:
            changed = False
            for node in new_dag.nodes[:]:  # Copy list to avoid modification during iteration
                if (node.gate_type == 'NOT' and 
                    len(node.inputs) == 1 and 
                    node.inputs[0].gate_type == 'NOT'):
                    
                    # Replace NOT(NOT(A)) with A
                    inner_input = node.inputs[0].inputs[0]
                    self._replace_node(new_dag, node, inner_input)
                    changed = True
                    break
        
        return new_dag
    
    def _apply_de_morgan(self, dag: CircuitDAG) -> CircuitDAG:
        """Apply De Morgan's laws: NOT(A AND B) = NOT(A) OR NOT(B)"""
        new_dag = dag.copy()
        changed = True
        
        while changed:
            changed = False
            for node in new_dag.nodes[:]:
                if node.gate_type == 'NOT' and len(node.inputs) == 1:
                    inner_node = node.inputs[0]
                    
                    if inner_node.gate_type == 'AND':
                        # NOT(A AND B) = NOT(A) OR NOT(B)
                        not_inputs = []
                        for inp in inner_node.inputs:
                            not_node = Node(f"NOT_{len(new_dag.nodes)}", 'NOT', [inp])
                            new_dag.add_node(not_node)
                            not_inputs.append(not_node)
                        
                        or_node = Node(f"OR_{len(new_dag.nodes)}", 'OR', not_inputs)
                        new_dag.add_node(or_node)
                        self._replace_node(new_dag, node, or_node)
                        changed = True
                        break
                    
                    elif inner_node.gate_type == 'OR':
                        # NOT(A OR B) = NOT(A) AND NOT(B)
                        not_inputs = []
                        for inp in inner_node.inputs:
                            not_node = Node(f"NOT_{len(new_dag.nodes)}", 'NOT', [inp])
                            new_dag.add_node(not_node)
                            not_inputs.append(not_node)
                        
                        and_node = Node(f"AND_{len(new_dag.nodes)}", 'AND', not_inputs)
                        new_dag.add_node(and_node)
                        self._replace_node(new_dag, node, and_node)
                        changed = True
                        break
        
        return new_dag
    
    def _apply_absorption(self, dag: CircuitDAG) -> CircuitDAG:
        """Apply absorption laws: A OR (A AND B) = A, A AND (A OR B) = A"""
        new_dag = dag.copy()
        changed = True
        
        while changed:
            changed = False
            for node in new_dag.nodes[:]:
                if node.gate_type in ['AND', 'OR']:
                    # Check for absorption patterns
                    for i, input1 in enumerate(node.inputs):
                        for j, input2 in enumerate(node.inputs):
                            if i != j and self._is_absorption_case(node, input1, input2):
                                self._replace_node(new_dag, node, input1)
                                changed = True
                                break
                        if changed:
                            break
                    if changed:
                        break
        
        return new_dag
    
    def _apply_identity_laws(self, dag: CircuitDAG) -> CircuitDAG:
        """Apply identity laws: A AND TRUE = A, A OR FALSE = A"""
        new_dag = dag.copy()
        
        # This would require constant propagation
        # For now, we'll implement basic cases
        return new_dag
    
    def _apply_complement_laws(self, dag: CircuitDAG) -> CircuitDAG:
        """Apply complement laws: A AND NOT(A) = FALSE, A OR NOT(A) = TRUE"""
        new_dag = dag.copy()
        changed = True
        
        while changed:
            changed = False
            for node in new_dag.nodes[:]:
                if node.gate_type == 'AND':
                    # Check for A AND NOT(A)
                    for i, input1 in enumerate(node.inputs):
                        for j, input2 in enumerate(node.inputs):
                            if (i != j and input2.gate_type == 'NOT' and 
                                len(input2.inputs) == 1 and input2.inputs[0] == input1):
                                # Replace with FALSE (we'll use a constant node)
                                false_node = Node("FALSE", "CONST_FALSE")
                                new_dag.add_node(false_node)
                                self._replace_node(new_dag, node, false_node)
                                changed = True
                                break
                        if changed:
                            break
                
                elif node.gate_type == 'OR':
                    # Check for A OR NOT(A)
                    for i, input1 in enumerate(node.inputs):
                        for j, input2 in enumerate(node.inputs):
                            if (i != j and input2.gate_type == 'NOT' and 
                                len(input2.inputs) == 1 and input2.inputs[0] == input1):
                                # Replace with TRUE
                                true_node = Node("TRUE", "CONST_TRUE")
                                new_dag.add_node(true_node)
                                self._replace_node(new_dag, node, true_node)
                                changed = True
                                break
                        if changed:
                            break
                
                if changed:
                    break
        
        return new_dag
    
    def _apply_associativity(self, dag: CircuitDAG) -> CircuitDAG:
        """Flatten associative operations"""
        new_dag = dag.copy()
        changed = True
        
        while changed:
            changed = False
            for node in new_dag.nodes[:]:
                if node.gate_type in ['AND', 'OR']:
                    # Flatten nested operations of the same type
                    new_inputs = []
                    for inp in node.inputs:
                        if inp.gate_type == node.gate_type:
                            new_inputs.extend(inp.inputs)
                        else:
                            new_inputs.append(inp)
                    
                    if len(new_inputs) != len(node.inputs):
                        node.inputs = new_inputs
                        changed = True
        
        return new_dag
    
    def _apply_distributivity(self, dag: CircuitDAG) -> CircuitDAG:
        """Apply distributive laws when beneficial"""
        # This is complex and context-dependent
        # For now, return unchanged
        return dag
    
    def _remove_redundant_gates(self, dag: CircuitDAG) -> CircuitDAG:
        """Remove gates that don't contribute to the output"""
        new_dag = CircuitDAG()
        
        if not dag.output:
            return new_dag
        
        # Find all nodes reachable from output
        reachable = set()
        
        def mark_reachable(node: Node):
            if node in reachable:
                return
            reachable.add(node)
            for inp in node.inputs:
                mark_reachable(inp)
        
        mark_reachable(dag.output)
        
        # Copy only reachable nodes
        node_mapping = {}
        for node in dag.get_topological_order():
            if node in reachable:
                if node.gate_type == 'INPUT':
                    new_node = Node(node.name, node.gate_type)
                else:
                    mapped_inputs = [node_mapping[inp] for inp in node.inputs if inp in node_mapping]
                    new_node = Node(node.name, node.gate_type, mapped_inputs)
                
                new_dag.add_node(new_node)
                node_mapping[node] = new_node
        
        if dag.output in node_mapping:
            new_dag.set_output(node_mapping[dag.output])
        
        return new_dag
    
    def _is_absorption_case(self, node: Node, input1: Node, input2: Node) -> bool:
        """Check if this is an absorption case"""
        if node.gate_type == 'OR':
            # A OR (A AND B) = A
            if (input2.gate_type == 'AND' and input1 in input2.inputs):
                return True
        elif node.gate_type == 'AND':
            # A AND (A OR B) = A
            if (input2.gate_type == 'OR' and input1 in input2.inputs):
                return True
        
        return False
    
    def _replace_node(self, dag: CircuitDAG, old_node: Node, new_node: Node):
        """Replace all references to old_node with new_node"""
        # Update all nodes that reference old_node
        for node in dag.nodes:
            if old_node in node.inputs:
                node.inputs = [new_node if inp == old_node else inp for inp in node.inputs]
        
        # Update output if necessary
        if dag.output == old_node:
            dag.set_output(new_node)
        
        # Remove old node from DAG
        if old_node in dag.nodes:
            dag.nodes.remove(old_node)
        
        # Update node map
        if old_node.name in dag._node_map:
            del dag._node_map[old_node.name]

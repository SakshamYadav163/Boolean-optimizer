
"""
Directed Acyclic Graph representation of logic circuits
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass

@dataclass
class Node:
    """Represents a gate or input in the circuit"""
    name: str
    gate_type: str  # 'INPUT', 'AND', 'OR', 'NOT', 'XOR', 'NAND', 'NOR'
    inputs: List['Node'] = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
    
    def __hash__(self):
        return hash(id(self))
    
    def __eq__(self, other):
        return id(self) == id(other)

class CircuitDAG:
    """Directed Acyclic Graph representation of a logic circuit"""
    
    def __init__(self):
        self.nodes: List[Node] = []
        self.output: Optional[Node] = None
        self._node_map: Dict[str, Node] = {}
    
    def add_node(self, node: Node):
        """Add a node to the DAG"""
        self.nodes.append(node)
        if node.name:
            self._node_map[node.name] = node
    
    def set_output(self, node: Node):
        """Set the output node"""
        self.output = node
    
    def get_node_by_name(self, name: str) -> Optional[Node]:
        """Get node by name"""
        return self._node_map.get(name)
    
    def get_inputs(self) -> List[Node]:
        """Get all input nodes"""
        return [node for node in self.nodes if node.gate_type == 'INPUT']
    
    def get_gates(self) -> List[Node]:
        """Get all gate nodes (non-input)"""
        return [node for node in self.nodes if node.gate_type != 'INPUT']
    
    def gate_count(self) -> int:
        """Count the number of gates (excluding inputs)"""
        return len(self.get_gates())
    
    def circuit_depth(self) -> int:
        """Calculate the maximum depth of the circuit"""
        if not self.output:
            return 0
        
        depths = {}
        
        def calculate_depth(node: Node) -> int:
            if node in depths:
                return depths[node]
            
            if node.gate_type == 'INPUT':
                depths[node] = 0
                return 0
            
            max_input_depth = 0
            for input_node in node.inputs:
                max_input_depth = max(max_input_depth, calculate_depth(input_node))
            
            depths[node] = max_input_depth + 1
            return depths[node]
        
        return calculate_depth(self.output)
    
    def get_topological_order(self) -> List[Node]:
        """Get nodes in topological order"""
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(node: Node):
            if node in temp_visited:
                raise ValueError("Circuit contains a cycle")
            if node in visited:
                return
            
            temp_visited.add(node)
            for input_node in node.inputs:
                dfs(input_node)
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
        
        for node in self.nodes:
            if node not in visited:
                dfs(node)
        
        return result
    
    def to_expression(self) -> str:
        """Convert DAG back to Boolean expression"""
        if not self.output:
            return ""
        
        def node_to_expr(node: Node) -> str:
            if node.gate_type == 'INPUT':
                return node.name
            elif node.gate_type == 'NOT':
                return f"NOT({node_to_expr(node.inputs[0])})"
            elif node.gate_type in ['AND', 'OR', 'XOR', 'NAND', 'NOR']:
                op_symbol = {
                    'AND': ' AND ', 'OR': ' OR ', 'XOR': ' XOR ',
                    'NAND': ' NAND ', 'NOR': ' NOR '
                }[node.gate_type]
                
                input_exprs = [node_to_expr(inp) for inp in node.inputs]
                expr = op_symbol.join(input_exprs)
                
                if len(node.inputs) > 1:
                    return f"({expr})"
                return expr
            
            return node.name
        
        return node_to_expr(self.output)
    
    def copy(self) -> 'CircuitDAG':
        """Create a deep copy of the DAG"""
        new_dag = CircuitDAG()
        node_mapping = {}
        
        # First pass: create all nodes
        for node in self.get_topological_order():
            if node.gate_type == 'INPUT':
                new_node = Node(node.name, node.gate_type)
            else:
                mapped_inputs = [node_mapping[inp] for inp in node.inputs]
                new_node = Node(node.name, node.gate_type, mapped_inputs)
            
            new_dag.add_node(new_node)
            node_mapping[node] = new_node
        
        if self.output:
            new_dag.set_output(node_mapping[self.output])
        
        return new_dag

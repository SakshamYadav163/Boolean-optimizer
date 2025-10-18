
"""
Circuit visualization using Graphviz
"""

import graphviz
from circuit_dag import CircuitDAG, Node

class CircuitVisualizer:
    """Visualize logic circuits using Graphviz"""
    
    def __init__(self):
        self.gate_colors = {
            'INPUT': '#90EE90',    # Light green
            'AND': '#FFB6C1',      # Light pink
            'OR': '#87CEEB',       # Sky blue
            'NOT': '#DDA0DD',      # Plum
            'XOR': '#F0E68C',      # Khaki
            'NAND': '#FFA07A',     # Light salmon
            'NOR': '#20B2AA',      # Light sea green
            'CONST_TRUE': '#FFD700',   # Gold
            'CONST_FALSE': '#696969'   # Dim gray
        }
        
        self.gate_shapes = {
            'INPUT': 'ellipse',
            'AND': 'box',
            'OR': 'box',
            'NOT': 'triangle',
            'XOR': 'diamond',
            'NAND': 'box',
            'NOR': 'box',
            'CONST_TRUE': 'circle',
            'CONST_FALSE': 'circle'
        }
    
    def create_graph(self, dag: CircuitDAG, title: str = "Circuit") -> graphviz.Digraph:
        """Create a Graphviz representation of the circuit"""
        dot = graphviz.Digraph(comment=title)
        dot.attr(rankdir='TB', size='8,10')
        dot.attr('node', fontname='Arial', fontsize='10')
        dot.attr('edge', fontname='Arial', fontsize='8')
        
        # Add title
        dot.attr(label=title, fontsize='14', fontname='Arial Bold')
        
        # Add nodes
        for node in dag.nodes:
            self._add_node_to_graph(dot, node)
        
        # Add edges
        for node in dag.nodes:
            for i, input_node in enumerate(node.inputs):
                edge_label = f"in{i}" if len(node.inputs) > 1 else ""
                dot.edge(input_node.name, node.name, label=edge_label)
        
        # Highlight output
        if dag.output:
            dot.node(dag.output.name, style='bold', penwidth='3')
        
        return dot
    
    def _add_node_to_graph(self, dot: graphviz.Digraph, node: Node):
        """Add a single node to the graph"""
        color = self.gate_colors.get(node.gate_type, '#FFFFFF')
        shape = self.gate_shapes.get(node.gate_type, 'box')
        
        label = self._get_node_label(node)
        
        dot.node(
            node.name,
            label=label,
            shape=shape,
            style='filled',
            fillcolor=color,
            color='black'
        )
    
    def _get_node_label(self, node: Node) -> str:
        """Get display label for a node"""
        if node.gate_type == 'INPUT':
            return node.name
        elif node.gate_type == 'CONST_TRUE':
            return '1'
        elif node.gate_type == 'CONST_FALSE':
            return '0'
        else:
            return f"{node.gate_type}\\n{node.name}"
    
    def save_graph(self, dag: CircuitDAG, filename: str, title: str = "Circuit"):
        """Save graph to file"""
        graph = self.create_graph(dag, title)
        graph.render(filename, format='png', cleanup=True)
        return f"{filename}.png"
    
    def create_comparison_graph(self, original_dag: CircuitDAG, 
                              simplified_dag: CircuitDAG) -> graphviz.Digraph:
        """Create side-by-side comparison of original and simplified circuits"""
        dot = graphviz.Digraph(comment="Circuit Comparison")
        dot.attr(rankdir='LR', size='12,8')
        
        # Create subgraphs
        with dot.subgraph(name='cluster_0') as orig:
            orig.attr(label='Original Circuit')
            orig.attr(style='filled', color='lightgrey')
            
            for node in original_dag.nodes:
                self._add_node_to_graph(orig, node)
        
        with dot.subgraph(name='cluster_1') as simp:
            simp.attr(label='Simplified Circuit')
            simp.attr(style='filled', color='lightblue')
            
            for node in simplified_dag.nodes:
                # Prefix node names to avoid conflicts
                node_copy = Node(f"s_{node.name}", node.gate_type, node.inputs)
                self._add_node_to_graph(simp, node_copy)
        
        return dot

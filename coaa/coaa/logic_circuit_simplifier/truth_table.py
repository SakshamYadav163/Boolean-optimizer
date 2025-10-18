
"""
Truth table generation and equivalence checking
"""

import pandas as pd
from typing import List, Dict, Any
from itertools import product
from circuit_dag import CircuitDAG, Node

class TruthTableGenerator:
    """Generate truth tables and verify circuit equivalence"""
    
    def __init__(self):
        pass
    
    def generate_truth_table(self, dag: CircuitDAG) -> pd.DataFrame:
        """Generate truth table for a circuit"""
        inputs = dag.get_inputs()
        input_names = [node.name for node in inputs]
        
        if not input_names:
            return pd.DataFrame()
        
        # Generate all possible input combinations
        num_inputs = len(input_names)
        combinations = list(product([0, 1], repeat=num_inputs))
        
        results = []
        for combo in combinations:
            # Create input assignment
            input_values = dict(zip(input_names, combo))
            
            # Evaluate circuit
            output_value = self._evaluate_circuit(dag, input_values)
            
            # Add to results
            row = input_values.copy()
            row['Output'] = output_value
            results.append(row)
        
        return pd.DataFrame(results)
    
    def generate_combined_table(self, dag1: CircuitDAG, dag2: CircuitDAG) -> pd.DataFrame:
        """Generate combined truth table for two circuits"""
        # Get all unique input names
        inputs1 = {node.name for node in dag1.get_inputs()}
        inputs2 = {node.name for node in dag2.get_inputs()}
        all_inputs = sorted(inputs1.union(inputs2))
        
        if not all_inputs:
            return pd.DataFrame()
        
        # Generate all possible input combinations
        num_inputs = len(all_inputs)
        combinations = list(product([0, 1], repeat=num_inputs))
        
        results = []
        for combo in combinations:
            input_values = dict(zip(all_inputs, combo))
            
            # Evaluate both circuits
            output1 = self._evaluate_circuit(dag1, input_values)
            output2 = self._evaluate_circuit(dag2, input_values)
            
            # Add to results
            row = input_values.copy()
            row['Original'] = output1
            row['Simplified'] = output2
            row['Match'] = output1 == output2
            results.append(row)
        
        return pd.DataFrame(results)
    
    def verify_equivalence(self, dag1: CircuitDAG, dag2: CircuitDAG) -> bool:
        """Check if two circuits are logically equivalent"""
        truth_table = self.generate_combined_table(dag1, dag2)
        
        if truth_table.empty:
            return True
        
        return truth_table['Match'].all()
    
    def _evaluate_circuit(self, dag: CircuitDAG, input_values: Dict[str, int]) -> int:
        """Evaluate circuit with given input values"""
        if not dag.output:
            return 0
        
        # Memoization for efficiency
        node_values = {}
        
        def evaluate_node(node: Node) -> int:
            if node in node_values:
                return node_values[node]
            
            if node.gate_type == 'INPUT':
                value = input_values.get(node.name, 0)
            elif node.gate_type == 'CONST_TRUE':
                value = 1
            elif node.gate_type == 'CONST_FALSE':
                value = 0
            elif node.gate_type == 'NOT':
                input_val = evaluate_node(node.inputs[0])
                value = 1 - input_val
            elif node.gate_type == 'AND':
                value = 1
                for inp in node.inputs:
                    if evaluate_node(inp) == 0:
                        value = 0
                        break
            elif node.gate_type == 'OR':
                value = 0
                for inp in node.inputs:
                    if evaluate_node(inp) == 1:
                        value = 1
                        break
            elif node.gate_type == 'XOR':
                value = 0
                for inp in node.inputs:
                    value ^= evaluate_node(inp)
            elif node.gate_type == 'NAND':
                value = 1
                for inp in node.inputs:
                    if evaluate_node(inp) == 0:
                        value = 1
                        break
                else:
                    value = 0
            elif node.gate_type == 'NOR':
                value = 1
                for inp in node.inputs:
                    if evaluate_node(inp) == 1:
                        value = 0
                        break
            else:
                value = 0
            
            node_values[node] = value
            return value
        
        return evaluate_node(dag.output)

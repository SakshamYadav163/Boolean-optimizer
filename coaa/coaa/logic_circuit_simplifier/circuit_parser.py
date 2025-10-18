
"""
Parser for Boolean expressions and netlists
"""

import re
from typing import Dict, List, Union
from circuit_dag import CircuitDAG, Node

class CircuitParser:
    """Parse Boolean expressions and netlists into DAG representation"""
    
    def __init__(self):
        self.operators = {
            'AND': 2, 'OR': 2, 'XOR': 2, 'NAND': 2, 'NOR': 2,
            'NOT': 1, 'BUFFER': 1
        }
    
    def parse_expression(self, expression: str) -> CircuitDAG:
        """Parse a Boolean expression into a DAG"""
        # Clean and tokenize
        expression = self._clean_expression(expression)
        tokens = self._tokenize(expression)
        
        # Convert to postfix notation
        postfix = self._infix_to_postfix(tokens)
        
        # Build DAG from postfix
        return self._build_dag_from_postfix(postfix)
    
    def parse_netlist(self, netlist: str) -> CircuitDAG:
        """Parse a netlist into a DAG"""
        lines = [line.strip() for line in netlist.split('\n') if line.strip()]
        
        dag = CircuitDAG()
        node_map = {}
        
        for line in lines:
            if line.startswith('INPUT'):
                # INPUT A
                var_name = line.split()[1]
                node = Node(var_name, 'INPUT')
                dag.add_node(node)
                node_map[var_name] = node
                
            elif line.startswith('OUTPUT'):
                # OUTPUT = expression
                parts = line.split('=', 1)
                output_name = parts[0].split()[1] if len(parts[0].split()) > 1 else 'OUTPUT'
                expression = parts[1].strip()
                
                output_node = self._parse_gate_expression(expression, node_map, dag)
                output_node.name = output_name
                dag.set_output(output_node)
                
            elif '=' in line:
                # GATE1 = A AND B
                parts = line.split('=', 1)
                gate_name = parts[0].strip()
                expression = parts[1].strip()
                
                gate_node = self._parse_gate_expression(expression, node_map, dag)
                gate_node.name = gate_name
                node_map[gate_name] = gate_node
        
        return dag
    
    def _clean_expression(self, expression: str) -> str:
        """Clean and normalize expression"""
        # Replace common symbols
        replacements = {
            '&': ' AND ', '|': ' OR ', '!': ' NOT ', '^': ' XOR ',
            '~': ' NOT ', '+': ' OR ', '*': ' AND '
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        return expression.upper()
    
    def _tokenize(self, expression: str) -> List[str]:
        """Tokenize expression into operators, variables, and parentheses"""
        # Split by spaces and filter empty strings
        tokens = []
        current_token = ""
        
        for char in expression:
            if char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            elif char in '()':
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def _infix_to_postfix(self, tokens: List[str]) -> List[str]:
        """Convert infix notation to postfix using Shunting Yard algorithm"""
        precedence = {'NOT': 3, 'AND': 2, 'NAND': 2, 'OR': 1, 'NOR': 1, 'XOR': 1}
        
        output = []
        operator_stack = []
        
        for token in tokens:
            if token in self.operators:
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       operator_stack[-1] in precedence and
                       precedence[operator_stack[-1]] >= precedence[token]):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack:
                    operator_stack.pop()  # Remove '('
            else:
                output.append(token)  # Variable
        
        while operator_stack:
            output.append(operator_stack.pop())
        
        return output
    
    def _build_dag_from_postfix(self, postfix: List[str]) -> CircuitDAG:
        """Build DAG from postfix expression"""
        dag = CircuitDAG()
        stack = []
        
        for token in postfix:
            if token in self.operators:
                arity = self.operators[token]
                inputs = []
                
                for _ in range(arity):
                    if stack:
                        inputs.append(stack.pop())
                
                inputs.reverse()  # Maintain order
                
                node = Node(f"{token}_{len(dag.nodes)}", token, inputs)
                dag.add_node(node)
                stack.append(node)
            else:
                # Variable - check if already exists
                existing_node = dag.get_node_by_name(token)
                if existing_node:
                    stack.append(existing_node)
                else:
                    node = Node(token, 'INPUT')
                    dag.add_node(node)
                    stack.append(node)
        
        if stack:
            dag.set_output(stack[0])
        
        return dag
    
    def _parse_gate_expression(self, expression: str, node_map: Dict, dag: CircuitDAG) -> Node:
        """Parse a single gate expression"""
        expression = self._clean_expression(expression)
        tokens = self._tokenize(expression)
        
        # Simple cases first
        if len(tokens) == 1:
            # Single variable
            var_name = tokens[0]
            if var_name in node_map:
                return node_map[var_name]
            else:
                node = Node(var_name, 'INPUT')
                dag.add_node(node)
                return node
        
        elif len(tokens) == 2 and tokens[0] == 'NOT':
            # NOT gate
            input_name = tokens[1]
            input_node = node_map.get(input_name)
            if not input_node:
                input_node = Node(input_name, 'INPUT')
                dag.add_node(input_node)
                node_map[input_name] = input_node
            
            not_node = Node(f"NOT_{len(dag.nodes)}", 'NOT', [input_node])
            dag.add_node(not_node)
            return not_node
        
        else:
            # Complex expression - use full parser
            temp_dag = self.parse_expression(expression)
            # Merge into main DAG
            return self._merge_dag(temp_dag, dag, node_map)
    
    def _merge_dag(self, source_dag: CircuitDAG, target_dag: CircuitDAG, node_map: Dict) -> Node:
        """Merge source DAG into target DAG"""
        node_mapping = {}
        
        # First pass: create nodes
        for node in source_dag.get_topological_order():
            if node.gate_type == 'INPUT':
                if node.name in node_map:
                    node_mapping[node] = node_map[node.name]
                else:
                    new_node = Node(node.name, 'INPUT')
                    target_dag.add_node(new_node)
                    node_map[node.name] = new_node
                    node_mapping[node] = new_node
            else:
                mapped_inputs = [node_mapping[inp] for inp in node.inputs]
                new_node = Node(f"{node.gate_type}_{len(target_dag.nodes)}", 
                              node.gate_type, mapped_inputs)
                target_dag.add_node(new_node)
                node_mapping[node] = new_node
        
        return node_mapping[source_dag.output]

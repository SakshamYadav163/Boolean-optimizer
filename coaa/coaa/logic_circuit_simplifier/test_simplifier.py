
"""
Test cases for the logic circuit simplifier
"""

import unittest
from circuit_parser import CircuitParser
from circuit_dag import CircuitDAG, Node
from simplifier import CircuitSimplifier
from truth_table import TruthTableGenerator

class TestCircuitSimplifier(unittest.TestCase):
    """Test cases for circuit simplification"""
    
    def setUp(self):
        self.parser = CircuitParser()
        self.simplifier = CircuitSimplifier()
        self.truth_gen = TruthTableGenerator()
    
    def test_double_negation(self):
        """Test double negation elimination"""
        expression = "NOT(NOT(A))"
        dag = self.parser.parse_expression(expression)
        simplified = self.simplifier.simplify(dag)
        
        # Should be equivalent to just A
        self.assertTrue(self.truth_gen.verify_equivalence(dag, simplified))
        self.assertLess(simplified.gate_count(), dag.gate_count())
    
    def test_de_morgan_and(self):
        """Test De Morgan's law for AND"""
        expression = "NOT(A AND B)"
        dag = self.parser.parse_expression(expression)
        simplified = self.simplifier.simplify(dag)
        
        # Should be equivalent to NOT(A) OR NOT(B)
        expected_expr = "NOT(A) OR NOT(B)"
        expected_dag = self.parser.parse_expression(expected_expr)
        
        self.assertTrue(self.truth_gen.verify_equivalence(dag, simplified))
        self.assertTrue(self.truth_gen.verify_equivalence(simplified, expected_dag))
    
    def test_de_morgan_or(self):
        """Test De Morgan's law for OR"""
        expression = "NOT(A OR B)"
        dag = self.parser.parse_expression(expression)
        simplified = self.simplifier.simplify(dag)
        
        # Should be equivalent to NOT(A) AND NOT(B)
        expected_expr = "NOT(A) AND NOT(B)"
        expected_dag = self.parser.parse_expression(expected_expr)
        
        self.assertTrue(self.truth_gen.verify_equivalence(dag, simplified))
        self.assertTrue(self.truth_gen.verify_equivalence(simplified, expected_dag))
    
    def test_absorption_or(self):
        """Test absorption law: A OR (A AND B) = A"""
        expression = "A OR (A AND B)"
        dag = self.parser.parse_expression(expression)
        simplified = self.simplifier.simplify(dag)
        
        # Should be equivalent to just A
        expected_expr = "A"
        expected_dag = self.parser.parse_expression(expected_expr)
        
        self.assertTrue(self.truth_gen.verify_equivalence(dag, simplified))
        self.assertTrue(self.truth_gen.verify_equivalence(simplified, expected_dag))
    
    def test_absorption_and(self):
        """Test absorption law: A AND (A OR B) = A"""
        expression = "A AND (A OR B)"
        dag = self.parser.parse_expression(expression)
        simplified = self.simplifier.simplify(dag)
        
        # Should be equivalent to just A
        expected_expr = "A"
        expected_dag = self.parser.parse_expression(expected_expr)
        
        self.assertTrue(self.truth_gen.verify_equivalence(dag, simplified))
        self.assertTrue(self.truth_gen.verify_equivalence(simplified, expected_dag))
    
    def test_complex_expression(self):
        """Test complex expression simplification"""
        expression = "NOT(NOT(A) AND NOT(B))"
        dag = self.parser.parse_expression(expression)
        simplified = self.simplifier.simplify(dag)
        
        # Should be equivalent to A OR B (by De Morgan's law)
        expected_expr = "A OR B"
        expected_dag = self.parser.parse_expression(expected_expr)
        
        self.assertTrue(self.truth_gen.verify_equivalence(dag, simplified))
        self.assertTrue(self.truth_gen.verify_equivalence(simplified, expected_dag))
    
    def test_complement_laws(self):
        """Test complement laws"""
        # A AND NOT(A) should be FALSE
        expression1 = "A AND NOT(A)"
        dag1 = self.parser.parse_expression(expression1)
        simplified1 = self.simplifier.simplify(dag1)
        
        # A OR NOT(A) should be TRUE
        expression2 = "A OR NOT(A)"
        dag2 = self.parser.parse_expression(expression2)
        simplified2 = self.simplifier.simplify(dag2)
        
        # Verify the simplifications are correct
        self.assertTrue(self.truth_gen.verify_equivalence(dag1, simplified1))
        self.assertTrue(self.truth_gen.verify_equivalence(dag2, simplified2))

if __name__ == '__main__':
    unittest.main()

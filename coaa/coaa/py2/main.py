"""
De Morgan's Theorem Logic Gate Optimizer
A comprehensive tool for simplifying logic circuits using De Morgan's theorem
and boolean algebra optimization techniques.
"""

import sympy
from sympy.logic.boolalg import Or, And, Not, Xor, Implies, Equivalent
from sympy.abc import A, B, C, D, E, F, G, H
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
from tabulate import tabulate
import argparse
import sys

class DeMorganOptimizer:
    """
    A comprehensive logic circuit optimizer using De Morgan's theorem
    and other boolean algebra simplification techniques.
    """
    
    def __init__(self, expr, show_steps=False, original_expr_str=None):
        """
        Initialize the optimizer with a boolean expression.
        
        Args:
            expr: sympy boolean expression
            show_steps: bool, whether to show intermediate optimization steps
        """
        self.original_expr = expr
        # Preserve the exact string the user entered for display purposes
        self.original_expr_display = original_expr_str if original_expr_str is not None else str(expr)
        self.show_steps = show_steps
        self.optimization_steps = []
        self.optimized_expr = self.optimize(expr)
        self.gate_count_original = self.count_gates(self.original_expr)
        self.gate_count_optimized = self.count_gates(self.optimized_expr)
    
    def optimize(self, expr):
        """
        Apply comprehensive boolean algebra optimizations including De Morgan's theorem.
        
        Args:
            expr: sympy boolean expression
            
        Returns:
            Optimized sympy boolean expression
        """
        if self.show_steps:
            self.optimization_steps.append(("Original", expr))
        
        # Step 1: Apply De Morgan's theorem manually
        demorgan_applied = self.apply_demorgan_recursive(expr)
        if self.show_steps and str(demorgan_applied) != str(expr):
            self.optimization_steps.append(("After De Morgan", demorgan_applied))
        
        # Step 2: Use sympy's built-in simplification
        simplified = sympy.simplify_logic(demorgan_applied, form='dnf')
        if self.show_steps and str(simplified) != str(demorgan_applied):
            self.optimization_steps.append(("After Simplification", simplified))
        
        # Step 3: Try CNF form if it's simpler
        cnf_form = sympy.simplify_logic(simplified, form='cnf')
        if self.count_gates(cnf_form) < self.count_gates(simplified):
            simplified = cnf_form
            if self.show_steps:
                self.optimization_steps.append(("CNF Optimization", simplified))
        
        return simplified
    
    def apply_demorgan_recursive(self, expr):
        """
        Recursively apply De Morgan's theorem to the expression.
        
        Args:
            expr: sympy boolean expression
            
        Returns:
            Expression with De Morgan's theorem applied
        """
        if isinstance(expr, Not):
            arg = expr.args[0]
            if isinstance(arg, And):
                # De Morgan: ~(A & B) = ~A | ~B
                return Or(*[Not(term) for term in arg.args])
            elif isinstance(arg, Or):
                # De Morgan: ~(A | B) = ~A & ~B
                return And(*[Not(term) for term in arg.args])
            elif isinstance(arg, Not):
                # Double negation: ~~A = A
                return arg.args[0]
        elif isinstance(expr, (And, Or)):
            # Apply recursively to sub-expressions
            args = [self.apply_demorgan_recursive(subexpr) for subexpr in expr.args]
            return type(expr)(*args)
        
        return expr
    
    def count_gates(self, expr):
        """
        Count the number of logic gates in an expression.
        
        Args:
            expr: sympy boolean expression
            
        Returns:
            int: Number of gates
        """
        if hasattr(expr, 'args') and expr.args:
            return 1 + sum(self.count_gates(arg) for arg in expr.args)
        return 0
    
    def generate_truth_table(self, variables=None):
        """
        Generate truth table for original and optimized expressions.
        
        Args:
            variables: list of variables to include in truth table
            
        Returns:
            dict: Dictionary containing 'data' (list of rows) and 'columns' (list of column names)
        """
        def _eval_to_int(expression, substitutions):
            """Safely evaluate a SymPy boolean expression to a Python int (0/1)."""
            value = expression.subs(substitutions)
            value = sympy.simplify(value)
            # Handle SymPy boolean singletons
            if value == sympy.true:
                return 1
            if value == sympy.false:
                return 0
            # Handle numeric 1/0 that may appear after simplification
            try:
                return int(value)  # works for 1/0 or Python bool
            except Exception:
                # Last-resort fallback: compare against True/False after simplification
                if value == True:  # noqa: E712 - intentional identity comparison fallback
                    return 1
                if value == False:  # noqa: E712 - intentional identity comparison fallback
                    return 0
                # If still indeterminate, treat non-false as 1
                return 1
        if variables is None:
            variables = sorted(list(self.original_expr.free_symbols), key=str)
        
        n_vars = len(variables)
        n_rows = 2 ** n_vars
        
        # Generate all possible combinations
        combinations = []
        for i in range(n_rows):
            combo = []
            for j in range(n_vars):
                combo.append((i >> (n_vars - 1 - j)) & 1)
            combinations.append(combo)
        
        # Create truth table data
        table_data = []
        for combo in combinations:
            row = list(combo)
            
            # Substitute values into expressions
            subs_dict = {var: bool(val) for var, val in zip(variables, combo)}
            
            original_result = _eval_to_int(self.original_expr, subs_dict)
            optimized_result = _eval_to_int(self.optimized_expr, subs_dict)
            
            row.extend([original_result, optimized_result])
            table_data.append(row)
        
        # Create simple data structure (replacing pandas DataFrame)
        columns = [str(var) for var in variables] + ['Original', 'Optimized']
        
        # Return a dictionary with data and columns for tabulate
        return {
            'data': table_data,
            'columns': columns
        }
    
    def create_circuit_diagram(self, expr, title, ax):
        """
        Create a visual representation of the logic circuit.
        
        Args:
            expr: sympy boolean expression
            title: str, title for the diagram
            ax: matplotlib axis object
        """
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Simple visualization - convert expression to text representation
        expr_str = str(expr)
        
        # Replace symbols with more readable format
        expr_str = expr_str.replace('&', ' AND ')
        expr_str = expr_str.replace('|', ' OR ')
        expr_str = expr_str.replace('~', 'NOT ')
        
        # Add text representation
        ax.text(5, 4, expr_str, ha='center', va='center', 
                fontsize=12, bbox=dict(boxstyle="round,pad=0.3", 
                facecolor="lightblue", alpha=0.7))
        
        # Add gate count
        gate_count = self.count_gates(expr)
        ax.text(5, 2, f"Gate Count: {gate_count}", ha='center', va='center', 
                fontsize=10, bbox=dict(boxstyle="round,pad=0.3", 
                facecolor="lightyellow", alpha=0.7))
    
    def visualize_optimization(self):
        """
        Create a visual comparison of original vs optimized circuits.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        self.create_circuit_diagram(self.original_expr, "Original Circuit", ax1)
        self.create_circuit_diagram(self.optimized_expr, "Optimized Circuit", ax2)
        
        plt.tight_layout()
        plt.show()
    
    def display_optimization_steps(self):
        """
        Display all optimization steps if show_steps was enabled.
        """
        if not self.show_steps or not self.optimization_steps:
            return
        
        print("\n" + "="*50)
        print("OPTIMIZATION STEPS")
        print("="*50)
        
        for i, (step_name, expr) in enumerate(self.optimization_steps, 1):
            print(f"Step {i}: {step_name}")
            print(f"Expression: {expr}")
            print(f"Gate Count: {self.count_gates(expr)}")
            print("-" * 30)
    
    def display_comparison(self):
        """
        Display comprehensive comparison between original and optimized expressions.
        """
        print("\n" + "="*60)
        print("DE MORGAN'S THEOREM LOGIC GATE OPTIMIZER")
        print("="*60)
        
        print(f"\n📋 ORIGINAL EXPRESSION:")
        print(f"   {self.original_expr_display}")
        print(f"   Gate Count: {self.gate_count_original}")
        
        print(f"\n✨ OPTIMIZED EXPRESSION:")
        print(f"   {self.optimized_expr}")
        print(f"   Gate Count: {self.gate_count_optimized}")
        
        # Calculate optimization metrics
        if self.gate_count_original > 0:
            reduction_percentage = ((self.gate_count_original - self.gate_count_optimized) / 
                                  self.gate_count_original) * 100
        else:
            reduction_percentage = 0
        
        print(f"\n📊 OPTIMIZATION METRICS:")
        print(f"   Gate Reduction: {self.gate_count_original - self.gate_count_optimized}")
        print(f"   Percentage Saved: {reduction_percentage:.1f}%")
        
        if str(self.original_expr) != str(self.optimized_expr):
            print("   Status: ✅ Optimization successful!")
        else:
            print("   Status: ℹ️ Expression already in optimal form")
        
        # Display optimization steps if enabled
        self.display_optimization_steps()

def create_predefined_circuits():
    """
    Create a collection of predefined circuit examples.
    
    Returns:
        dict: Dictionary of circuit names and expressions
    """
    circuits = {
        "NAND Gate": Not(And(A, B)),
        "NOR Gate": Not(Or(A, B)),
        "Complex De Morgan": Not(Or(And(A, B), And(C, D))),
        "Adder Carry-out": Or(And(A, B), And(B, C), And(A, C)),
        "XOR using basic gates": Or(And(A, Not(B)), And(Not(A), B)),
        "Full Adder Sum": Xor(Xor(A, B), C),
        "Majority Function": Or(And(A, B), And(B, C), And(A, C)),
        "Nested Negations": Not(And(Not(Or(A, B)), Not(And(C, D)))),
    }
    return circuits

def interactive_mode():
    """
    Run the optimizer in interactive mode.
    """
    print("🔧 Interactive De Morgan's Theorem Logic Gate Optimizer")
    print("="*55)
    
    circuits = create_predefined_circuits()
    
    while True:
        print("\nAvailable options:")
        print("1. Use predefined circuits")
        print("2. Enter custom expression")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\nPredefined Circuits:")
            for i, name in enumerate(circuits.keys(), 1):
                print(f"{i}. {name}")
            
            try:
                circuit_choice = int(input("\nSelect circuit number: ")) - 1
                circuit_names = list(circuits.keys())
                if 0 <= circuit_choice < len(circuit_names):
                    selected_name = circuit_names[circuit_choice]
                    selected_expr = circuits[selected_name]
                    
                    print(f"\n🔍 Analyzing: {selected_name}")
                    
                    show_steps = input("Show optimization steps? (y/n): ").lower() == 'y'
                    optimizer = DeMorganOptimizer(selected_expr, show_steps=show_steps, original_expr_str=str(selected_expr))
                    optimizer.display_comparison()
                    
                    # Generate truth table
                    if input("\nGenerate truth table? (y/n): ").lower() == 'y':
                        truth_table = optimizer.generate_truth_table()
                        print("\n📋 TRUTH TABLE:")
                        print(tabulate(truth_table['data'], headers=truth_table['columns'], tablefmt='grid'))
                    
                    # Show visualization
                    if input("\nShow circuit diagrams? (y/n): ").lower() == 'y':
                        optimizer.visualize_optimization()
                
                else:
                    print("Invalid circuit selection!")
                    
            except ValueError:
                print("Invalid input! Please enter a number.")
        
        elif choice == '2':
            print("\nEnter custom boolean expression using sympy syntax:")
            print("Variables: A, B, C, D, etc.")
            print("Operations: & (AND), | (OR), ~ (NOT), ^ (XOR)")
            print("Example: ~(A & B) | (C & ~D)")
            
            try:
                expr_str = input("\nExpression: ").strip()
                # Parse the expression
                expr = sympy.sympify(expr_str)
                
                show_steps = input("Show optimization steps? (y/n): ").lower() == 'y'
                optimizer = DeMorganOptimizer(expr, show_steps=show_steps, original_expr_str=expr_str)
                optimizer.display_comparison()
                
                # Generate truth table
                if input("\nGenerate truth table? (y/n): ").lower() == 'y':
                    truth_table = optimizer.generate_truth_table()
                    print("\n📋 TRUTH TABLE:")
                    print(tabulate(truth_table['data'], headers=truth_table['columns'], tablefmt='grid'))
                
                # Show visualization
                if input("\nShow circuit diagrams? (y/n): ").lower() == 'y':
                    optimizer.visualize_optimization()
                    
            except Exception as e:
                print(f"Error parsing expression: {e}")
        
        elif choice == '3':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice! Please enter 1, 2, or 3.")

def demo_all_circuits():
    """
    Run demonstration of all predefined circuits.
    """
    print("🚀 De Morgan's Theorem Logic Gate Optimizer - Full Demo")
    print("="*60)
    
    circuits = create_predefined_circuits()
    
    for name, expr in circuits.items():
        print(f"\n{'='*60}")
        print(f"🔍 Analyzing: {name}")
        print('='*60)
        
        optimizer = DeMorganOptimizer(expr, show_steps=True)
        optimizer.display_comparison()
        
        # Generate and display truth table
        truth_table = optimizer.generate_truth_table()
        print("\n📋 TRUTH TABLE:")
        print(tabulate(truth_table['data'], headers=truth_table['columns'], tablefmt='grid'))
        
        input("\nPress Enter to continue to next circuit...")

def main():
    """
    Main function with command line argument support.
    """
    parser = argparse.ArgumentParser(description='De Morgan\'s Theorem Logic Gate Optimizer')
    parser.add_argument('--demo', action='store_true', help='Run full demonstration')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--expression', type=str, help='Optimize specific expression')
    parser.add_argument('--steps', action='store_true', help='Show optimization steps')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_all_circuits()
    elif args.interactive:
        interactive_mode()
    elif args.expression:
        try:
            expr = sympy.sympify(args.expression)
            optimizer = DeMorganOptimizer(expr, show_steps=args.steps, original_expr_str=args.expression)
            optimizer.display_comparison()
            
            truth_table = optimizer.generate_truth_table()
            print("\n📋 TRUTH TABLE:")
            print(tabulate(truth_table['data'], headers=truth_table['columns'], tablefmt='grid'))
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()

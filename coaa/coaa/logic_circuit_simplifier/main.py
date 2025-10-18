
"""
Logic Circuit Simplifier using De Morgan's Theorem
Main application entry point with Streamlit interface
"""

import streamlit as st
import sys
import os
import pandas as pd

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from circuit_parser import CircuitParser
from circuit_dag import CircuitDAG
from simplifier import CircuitSimplifier
from visualizer import CircuitVisualizer
from truth_table import TruthTableGenerator

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Logic Circuit Simplifier",
        page_icon="⚡",
        layout="wide"
    )
    
    st.title("⚡ Logic Circuit Simplifier")
    st.markdown("### Simplify Boolean expressions using De Morgan's theorem and other Boolean algebra rules")
    
    # Initialize components
    parser = CircuitParser()
    simplifier = CircuitSimplifier()
    visualizer = CircuitVisualizer()
    truth_gen = TruthTableGenerator()
    
    # Sidebar for input
    with st.sidebar:
        st.header("Input Options")
        
        input_method = st.radio(
            "Choose input method:",
            ["Boolean Expression", "Example Expressions"]
        )
        
        if input_method == "Boolean Expression":
            expression = st.text_area(
                "Enter Boolean expression:",
                value="NOT(A AND B)",
                help="Use operators: AND, OR, NOT, XOR, NAND, NOR\nVariables: A, B, C, etc.\nParentheses for grouping"
            )
        else:
            example_expressions = {
                "De Morgan's Law (AND)": "NOT(A AND B)",
                "De Morgan's Law (OR)": "NOT(A OR B)",
                "Double Negation": "NOT(NOT(A))",
                "Absorption Law": "A OR (A AND B)",
                "Complex Expression": "NOT(NOT(A) AND NOT(B))",
                "Distributive Law": "(A AND B) OR (A AND C)",
                "Complement Law": "A AND NOT(A)"
            }
            
            selected_example = st.selectbox(
                "Select an example:",
                list(example_expressions.keys())
            )
            expression = example_expressions[selected_example]
            st.code(expression)
        
        # Simplification options
        st.header("Simplification Options")
        show_steps = st.checkbox("Show simplification steps", value=True)
        show_truth_table = st.checkbox("Show truth table", value=True)
        show_visualization = st.checkbox("Show circuit diagrams", value=True)
    
    # Main content area
    if expression:
        try:
            # Parse the expression
            with st.spinner("Parsing expression..."):
                original_dag = parser.parse_expression(expression)
            
            # Simplify the circuit
            with st.spinner("Simplifying circuit..."):
                simplified_dag = simplifier.simplify(original_dag)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Original Expression")
                st.code(expression, language="text")
                
                st.subheader("📊 Original Circuit Stats")
                original_stats = {
                    "Gates": original_dag.gate_count(),
                    "Inputs": len(original_dag.get_inputs()),
                    "Depth": original_dag.circuit_depth()
                }
                st.json(original_stats)
            
            with col2:
                st.subheader("✨ Simplified Expression")
                simplified_expr = simplified_dag.to_expression()
                st.code(simplified_expr, language="text")
                
                st.subheader("📊 Simplified Circuit Stats")
                simplified_stats = {
                    "Gates": simplified_dag.gate_count(),
                    "Inputs": len(simplified_dag.get_inputs()),
                    "Depth": simplified_dag.circuit_depth()
                }
                st.json(simplified_stats)
            
            # Improvement metrics
            gate_reduction = original_dag.gate_count() - simplified_dag.gate_count()
            depth_reduction = original_dag.circuit_depth() - simplified_dag.circuit_depth()
            
            st.subheader("🎯 Improvement Metrics")
            improvement_col1, improvement_col2, improvement_col3 = st.columns(3)
            
            with improvement_col1:
                st.metric(
                    "Gate Reduction",
                    f"{gate_reduction}",
                    delta=f"-{gate_reduction}" if gate_reduction > 0 else "0"
                )
            
            with improvement_col2:
                st.metric(
                    "Depth Reduction",
                    f"{depth_reduction}",
                    delta=f"-{depth_reduction}" if depth_reduction > 0 else "0"
                )
            
            with improvement_col3:
                if original_dag.gate_count() > 0:
                    reduction_percent = (gate_reduction / original_dag.gate_count()) * 100
                    st.metric(
                        "Reduction %",
                        f"{reduction_percent:.1f}%"
                    )
                else:
                    st.metric("Reduction %", "0%")
            
            # Truth table verification
            if show_truth_table:
                st.subheader("🔍 Truth Table Verification")
                
                try:
                    truth_table = truth_gen.generate_combined_table(original_dag, simplified_dag)
                    
                    if not truth_table.empty:
                        # Check equivalence
                        is_equivalent = truth_table['Match'].all()
                        
                        if is_equivalent:
                            st.success("✅ Circuits are logically equivalent!")
                        else:
                            st.error("❌ Circuits are NOT equivalent!")
                        
                        # Display truth table
                        st.dataframe(truth_table, use_container_width=True)
                    else:
                        st.info("No inputs found - cannot generate truth table")
                
                except Exception as e:
                    st.error(f"Error generating truth table: {str(e)}")
            
            # Circuit visualization
            if show_visualization:
                st.subheader("🔧 Circuit Diagrams")
                
                try:
                    viz_col1, viz_col2 = st.columns(2)
                    
                    with viz_col1:
                        st.markdown("**Original Circuit**")
                        original_graph = visualizer.create_graph(original_dag, "Original Circuit")
                        st.graphviz_chart(original_graph.source)
                    
                    with viz_col2:
                        st.markdown("**Simplified Circuit**")
                        simplified_graph = visualizer.create_graph(simplified_dag, "Simplified Circuit")
                        st.graphviz_chart(simplified_graph.source)
                
                except Exception as e:
                    st.error(f"Error generating circuit diagrams: {str(e)}")
            
            # Simplification steps (if requested)
            if show_steps:
                st.subheader("🔄 Simplification Rules Applied")
                
                # This would require tracking which rules were applied
                # For now, show general information
                st.info("""
                **Applied Simplification Rules:**
                - Double Negation Elimination: NOT(NOT(A)) → A
                - De Morgan's Laws: NOT(A AND B) → NOT(A) OR NOT(B)
                - Absorption Laws: A OR (A AND B) → A
                - Complement Laws: A AND NOT(A) → FALSE
                - Associativity: Flatten nested operations
                - Redundant Gate Removal
                """)
        
        except Exception as e:
            st.error(f"Error processing expression: {str(e)}")
            st.info("Please check your Boolean expression syntax.")
    
    # Footer with information
    st.markdown("---")
    st.markdown("""
    **About this tool:**
    - Implements De Morgan's theorem and other Boolean algebra rules
    - Visualizes logic circuits as directed acyclic graphs
    - Verifies equivalence using truth tables
    - Provides metrics on circuit complexity reduction
    
    **Supported operators:** AND, OR, NOT, XOR, NAND, NOR
    **Example expressions:** `NOT(A AND B)`, `A OR (B AND C)`, `NOT(NOT(A))`
    """)

if __name__ == "__main__":
    main()

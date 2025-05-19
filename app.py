import streamlit as st
import random
from sympy import symbols, Eq, S, latex, expand, collect # Ensure all are imported
from datetime import datetime

# --- Core Logic Functions ---

def generate_linear_equation_medium():
    """
    Generates a linear equation of the form ax + b = cx + d.
    Ensures integer coefficients and an integer solution.
    """
    x_sol = random.randint(-10, 10)

    a = random.randint(-10, 10)
    while a == 0:
        a = random.randint(-10, 10)

    c = random.randint(-10, 10)
    while c == 0 or c == a:
        c = random.randint(-10, 10)

    diff_b_d = c * x_sol - a * x_sol
    b_val = random.randint(-20, 20)
    d_val = b_val - diff_b_d

    x_sym = symbols('x')
    lhs = a * x_sym + b_val
    rhs = c * x_sym + d_val
    equation = Eq(lhs, rhs)
    return equation, x_sol

def solve_linear_equation_step_by_step(equation):
    steps = []
    x = symbols('x')
    
    # current_eq will be transformed step-by-step
    # Ensure LHS and RHS are Sympy expressions for robust processing
    current_eq = Eq(S(equation.lhs), S(equation.rhs))
    steps.append(f"Original Equation: ${latex(current_eq.lhs)} = {latex(current_eq.rhs)}$")

    # --- Extract initial components (ax+b = cx+d) ---
    # Use .as_poly() for reliable coefficient extraction
    lhs_poly = S(current_eq.lhs).as_poly(x)
    rhs_poly = S(current_eq.rhs).as_poly(x)

    # 'a_orig' and 'b_orig' are coefficients from the initial LHS
    a_orig = lhs_poly.coeff_monomial(x) if lhs_poly else S.Zero
    b_orig = lhs_poly.coeff_monomial(1) if lhs_poly else (S(current_eq.lhs) if not S(current_eq.lhs).has(x) else S.Zero)
    
    # 'c_orig' and 'd_orig' are coefficients from the initial RHS
    c_orig = rhs_poly.coeff_monomial(x) if rhs_poly else S.Zero
    d_orig = rhs_poly.coeff_monomial(1) if rhs_poly else (S(current_eq.rhs) if not S(current_eq.rhs).has(x) else S.Zero)

    # These variables will hold the "current" effective coefficients/constants as we simplify
    current_a = a_orig
    current_b = b_orig
    # c_orig is only used to modify current_a; it doesn't persist as a standalone variable after step 1
    current_d = d_orig
    
    # --- Step 1: Move x-term (c_orig*x) from RHS to LHS ---
    # Goal: (a_orig-c_orig)x + b_orig = d_orig
    if c_orig != 0:
        op_desc = "Subtract" if c_orig > 0 else "Add"
        term_val_desc = latex(abs(c_orig) * x)
        steps.append(f"Move x-terms to LHS: {op_desc} ${term_val_desc}$ from both sides.")
        
        current_a = a_orig - c_orig # This is the new coefficient of x on LHS
        # The equation becomes (current_a)x + b_orig = d_orig
        current_eq = Eq(current_a * x + current_b, current_d) # Using current_b and current_d which are still b_orig, d_orig
        steps.append(f"Result: ${latex(current_eq.lhs)} = {latex(current_eq.rhs)}$")
    
    # --- Step 2: Move constant term (current_b, which is b_orig) from LHS to RHS ---
    # Goal: current_a*x = current_d - current_b (using current_a from Step 1, current_d is d_orig)
    # Current state of equation (from end of Step 1 or original if c_orig was 0): current_a*x + current_b = current_d
    if current_b != 0:
        op_desc = "Subtract" if current_b > 0 else "Add"
        term_val_desc = latex(abs(current_b))
        steps.append(f"Move constant terms to RHS: {op_desc} ${term_val_desc}$ from both sides.")
        
        current_d = current_d - current_b # This is the new constant on RHS
        # The equation becomes current_a*x = current_d
        current_eq = Eq(current_a * x, current_d)
        steps.append(f"Result: ${latex(current_eq.lhs)} = {latex(current_eq.rhs)}$")

    # --- Step 3: Isolate x ---
    # Current state of equation: current_a*x = current_d (using updated current_a and current_d)
    if current_a == S.Zero:
        if current_d == S.Zero:
            steps.append("This equation simplifies to $0 = 0$, which means there are **infinitely many solutions** (identity).")
        else:
            steps.append(f"This equation simplifies to $0 = {latex(current_d)}$, which means there are **no solutions** (contradiction).")
    elif current_a == S.One:
        current_eq = Eq(x, current_d) # Ensure current_eq reflects the final solution form
        steps.append(f"Solution: ${latex(current_eq.lhs)} = {latex(current_eq.rhs)}$")
    else:
        steps.append(f"Isolate x: Divide both sides by ${latex(current_a)}$.")
        solution_val = current_d / current_a
        current_eq = Eq(x, solution_val) 
        steps.append(f"Solution: ${latex(current_eq.lhs)} = {latex(current_eq.rhs)}$")
        
    return steps


# --- Streamlit App --- (Using the UI from previous correct versions)

st.set_page_config(page_title="IntelliQuiz Algebra Tutor", layout="wide", initial_sidebar_state="auto")

try:
    st.sidebar.image("mascot.png", width=100, caption="Your Math Buddy!")
except Exception:
    st.sidebar.markdown("*(Your Math Buddy Here)*")

st.title("🎓 IntelliQuiz - ✨ Magical Math Solver!")

if 'problem_eq' not in st.session_state:
    st.session_state.problem_eq = None
    st.session_state.actual_solution = None
    st.session_state.solution_steps = None
    st.session_state.solution_visible_flag = False
    st.session_state.student_name = ""
    st.session_state.current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S SAST")

if not st.session_state.student_name:
    name_input = st.text_input("👋 Hi Math Explorer! What's your name?", key="student_name_input_field")
    if name_input:
        st.session_state.student_name = name_input
        st.rerun()
elif st.session_state.student_name:
    st.markdown(f"### Hello, {st.session_state.student_name}! Ready for a math adventure? 🚀")

st.write("""
Welcome to the IntelliQuiz Solver! This tool helps you practice solving
linear equations like $ax + b = cx + d$.
Generate a new problem and then reveal the step-by-step solution.
""")

col1, col2 = st.columns([1, 1.5])

with col1:
    if st.button("🔄 ✨ Get New Mission!", use_container_width=True, key="generate_problem_btn"):
        st.session_state.problem_eq, st.session_state.actual_solution = generate_linear_equation_medium()
        st.session_state.solution_steps = None
        st.session_state.solution_visible_flag = False
        st.rerun()

    if st.session_state.problem_eq is not None:
        with st.container(border=True):
            st.subheader("🎯 Your Current Challenge:")
            st.latex(latex(st.session_state.problem_eq.lhs) + " = " + latex(st.session_state.problem_eq.rhs))
            # Uncomment for debugging to see the intended solution
            # st.caption(f"(Psst! The answer is x = {st.session_state.actual_solution})") 

        if not st.session_state.solution_visible_flag:
            if st.button("💡 Decode Mission (Show Solution)", use_container_width=True, key="show_solution_btn"):
                st.session_state.solution_visible_flag = True
                if st.session_state.problem_eq is not None:
                    st.session_state.solution_steps = solve_linear_equation_step_by_step(st.session_state.problem_eq)
                st.rerun()
        else:
            if st.button("🙈 Got It! (Hide Solution)", use_container_width=True, key="hide_solution_btn"):
                st.session_state.solution_visible_flag = False
                st.rerun()
    else:
        st.info("Click '✨ Get New Mission!' to start your algebra adventure.")

with col2:
    if st.session_state.problem_eq is not None and \
       st.session_state.solution_visible_flag and \
       st.session_state.solution_steps is not None:

        with st.container(border=True):
            st.subheader("🗺️ Solution Map (Step-by-Step):")
            for i, step_text in enumerate(st.session_state.solution_steps):
                step_emoji = "➡️" if i % 2 == 0 else "↪️"
                st.markdown(f"**Step {i + 1} {step_emoji}** {step_text}", unsafe_allow_html=True)
                if i < len(st.session_state.solution_steps) - 1:
                    st.markdown("---")

            if st.session_state.actual_solution is not None:
                st.markdown("---")
                name_for_msg = st.session_state.student_name if st.session_state.student_name else 'Explorer'
                success_message = f"🎉 Mission Accomplished, {name_for_msg}!"
                
                # Verification based on the *intended* solution
                final_app_solution_str = "Not found"
                is_special_case = False
                if st.session_state.solution_steps and st.session_state.solution_steps[-1]:
                    last_step_str = st.session_state.solution_steps[-1]
                    if "Solution: x =" in last_step_str:
                        try:
                            rhs_part = last_step_str.split("=")[-1].strip().replace("$", "")
                            final_app_solution_str = rhs_part
                            app_solution_val = S(rhs_part)
                            if app_solution_val.equals(S(st.session_state.actual_solution)):
                                st.success(f"{success_message} The steps led to the correct solution: $x = {latex(S(st.session_state.actual_solution))}$")
                                st.balloons()
                            else:
                                st.error(f"Hmm, {name_for_msg}. The steps led to $x = {latex(app_solution_val)}$, but the expected answer was $x = {latex(S(st.session_state.actual_solution))}$. Let's recheck the map (steps)!")
                        except Exception:
                             st.warning(f"{success_message} The expected answer was $x = {latex(S(st.session_state.actual_solution))}$. Could not parse the final solution from steps for automatic check.")
                    elif "infinitely many solutions" in last_step_str or "no solutions" in last_step_str:
                        is_special_case = True
                        # For special cases, we'd need to evaluate if the original equation *should* be a special case.
                        # This is harder to auto-verify without re-solving independently.
                        st.info(f"{success_message} The equation resulted in a special case: {last_step_str.split(':')[-1].strip()}")
                    else:
                        st.warning(f"{success_message} The expected answer was $x = {latex(S(st.session_state.actual_solution))}$. The final step format was not recognized for automatic check.")
                else:
                     st.warning(f"{success_message} The expected answer was $x = {latex(S(st.session_state.actual_solution))}$. No solution steps found to verify.")


    elif st.session_state.solution_visible_flag and st.session_state.problem_eq is not None :
        st.info("Generating the solution map... get ready!")
    elif st.session_state.problem_eq is not None and not st.session_state.solution_visible_flag:
        st.markdown("Ready to see the solution steps? Click the 'Decode Mission' button! 👍")

st.markdown("---")
st.caption(f"IntelliQuiz Algebra Tutor | Soweto, Gauteng | {st.session_state.get('current_date', 'Date not available')}")
# src/dag.py

def build_backdoor_dot_graph(treatment_col, outcome_col, confounders):
    lines = ["digraph {"]

    for confounder in confounders:
        lines.append(f'    "{confounder}" -> "{treatment_col}";')
        lines.append(f'    "{confounder}" -> "{outcome_col}";')

    lines.append(f'    "{treatment_col}" -> "{outcome_col}";')
    lines.append("}")

    return "\n".join(lines)
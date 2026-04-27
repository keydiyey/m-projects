import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as go

def load_data():
    df = pd.read_excel("Cell eff v Scribe v Params.xlsx")

    return df

df = load_data()

# ------------ Inputs
with st.sidebar:
    st.sidebar.header("Control Panel")
    selected_project = st.selectbox("Current Project", df['Remarks'].unique())
    current_project = df[df['Remarks']==selected_project]

    # so confused with splits and shit
    selected_splits = st.multiselect("Splits", current_project['Project'].unique())

    current_project = current_project[current_project['Project'].isin(selected_splits)]
    selected_test = st.pills("Test Type", df['Test'].unique())

    selected_group = st.selectbox("Group", current_project.columns[:7])

    selected_param = st.pills("Parameters", current_project.columns[-8:-1])

    data = [panel for panel in current_project['Sample ID']]

    data = df[df["Sample ID"].isin(data) & (df["Test"] == selected_test)]

dashboard_tab, report_tab, raw_data_tab = st.tabs(["Dashboard", "Report", "Raw Data"])

with dashboard_tab:
    st.subheader(f"📊 {selected_param} by {selected_test} and {selected_group}")

    figure = go.scatter(data, x="Readout", y=selected_param, color=selected_group, trendline="ols")
    #figure.update_layout(plot_bgcolor='white') nvm idk why it doesnt cover the whole bg
    
    st.plotly_chart(figure)
    # Create a list to store the clean data
    summary_list = []

    results = go.get_trendline_results(figure)

    for index, row in results.iterrows():
        group = row[selected_group]      
        model = row["px_fit_results"]
        
        r2 = model.rsquared
        slope = model.params[1]  # This is your degradation rate
        intercept = model.params[0]
        
        summary_list.append({
            "Group" : group,
            "R²": f"{r2:.4f}",
            "Slope": f"{slope:.6f}",
            "Intercept": f"{intercept:.2f}"
        })

    # Display as a nice table in Streamlit
    st.subheader("🤡 Trend Summary")
    st.table(summary_list)


with report_tab:
    st.subheader("📋 Report")

    # 1. ---- DATA PRE-PROCESSING (The "Point System" & Cross-Param Engine) ----
    all_params = current_project.columns[-8:-1].tolist()
    cross_param_data = {}

    # Background calculation for all parameters to enable "Majority" logic
    for p in all_params:
        try:
            # We use a quiet trendline calculation
            temp_fig = go.scatter(data, x="Readout", y=p, color=selected_group, trendline="ols")
            temp_res = go.get_trendline_results(temp_fig)
            
            p_slopes = {}
            for _, row in temp_res.iterrows():
                grp = row[selected_group]
                slp = row["px_fit_results"].params[1]
                p_slopes[grp] = slp
            cross_param_data[p] = p_slopes
        except:
            continue

    if cross_param_data:
        # Convert to DataFrame for easier math: Rows = Groups, Columns = Parameters
        full_slope_df = pd.DataFrame(cross_param_data)
        abs_slope_df = full_slope_df.abs()
        
        # Point System: Rank 1 is the best (closest to 0 degradation)
        rank_df = abs_slope_df.rank(axis=0, ascending=True)
        # Score = How many parameters was this group #1 in?
        score_series = (rank_df == 1).sum(axis=1).astype(int)
        
        top_group = score_series.idxmax()
        top_score = score_series.max()
        total_metrics = len(all_params)

        # 2. ---- THE NARRATIVE GENERATOR (Your requested style) ----
        # Identify test context
        is_cyclic = any(x in selected_test for x in ["TC", "HF"])
        test_type_str = "cyclic stress" if is_cyclic else "steady-state"
        
        # Determine if it's a majority or total win
        if top_score == total_metrics:
            win_scope = "across all tested parameters"
        elif top_score >= (total_metrics / 2):
            win_scope = f"across the majority of parameters ({top_score}/{total_metrics})"
        else:
            win_scope = "in specific key parameters only."

        st.info(f"""
        **Executive Summary:**
        In {test_type_str} tests ({selected_test}), a performance gap was observed between experimental splits. 
        The **{top_group}** configuration emerged as the more stable option, performing better {win_scope}.
        
        This trend was consistently reflected in the degradation slopes for {selected_param}. 
        Overall, the results for **{top_group}** are within acceptable limits for **{selected_project}**, 
        demonstrating improved stability compared to alternative splits in this test block.
        """)


        #  ---- SUMMARY METRICS ----
        st.divider()
        c1, c2, c3 = st.columns(3)
        
        # Best Group Slope for the specific selected parameter
        selected_best_slope = full_slope_df.loc[top_group, selected_param] if selected_param in full_slope_df.columns else 0.0
        
        c1.metric("Overall Winner", top_group)
        c2.metric("Stability Score", f"{top_score}/{total_metrics}", help="Number of parameters where this group had the lowest degradation.")
        c3.metric(f"{selected_param} Slope", f"{selected_best_slope:.6f}")

    else:
        st.warning("Insufficient data to generate cross-parameter analysis.")

    # 5. ---- DETAILED BREAKDOWN PER GROUP ----
    with st.expander("Detailed Group Interpretations"):
        for row in summary_list:
            grp = row["Group"]
            slp = float(row["Slope"])
            r2 = float(row["R²"])
            
            if abs(slp) < 0.0001:
                stability_status = "✅ **High Stability**"
                risk_desc = "Negligible drift; performance is holding steady."
            elif abs(slp) < 0.0004:
                stability_status = "⚠️ **Moderate Drift**"
                risk_desc = "Standard aging observed; monitors required for long-term reliability."
            else:
                stability_status = "🚨 **Significant Degradation**"
                risk_desc = "Accelerated loss detected; suggests potential failure mode in these conditions."

            # 2. Confidence Assessment
            if r2 > 0.9:
                conf_status = "Deterministic"
                conf_desc = "Highly predictable linear behavior."
            elif r2 > 0.7:
                conf_status = "Consistent"
                conf_desc = "Clear trend established with minor data noise."
            else:
                conf_status = "Stochastic"
                conf_desc = "Erratic behavior; data may be influenced by localized defects or measurement noise."

            # --- UI Rendering
            st.markdown(f"#### Group: {grp}")
            
            # Status Pills
            c1, c2, c3 = st.columns(3)
            c1.write(stability_status)
            c2.write(f"**Confidence:** {conf_status}")
            c3.write(f"**Ranking:** {'🏆 Top Performer' if grp == top_group else 'Standard Build'}")

            # Summary Box
            st.info(f"""
            **Technical Breakdown:**
            - **Trend:** The degradation rate is `{slp:.6f}` units/readout. {risk_desc}
            - **Predictability:** With an R² of `{r2:.4f}`, the results show {conf_desc}
            """)



with raw_data_tab:
    st.dataframe(data)
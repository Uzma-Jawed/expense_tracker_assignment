import streamlit as st
import plotly.express as px

# ---------- Page setup ----------
st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="centered")

st.title("💸 Expense Tracker & Financial Health Checker")

# ---------- Sidebar inputs ----------
st.sidebar.header("👤 User Profile")
name = st.sidebar.text_input("Your Name")
profession = st.sidebar.text_input("Your Profession")

st.sidebar.header("💰 Monthly Finances")
income = st.sidebar.number_input("Monthly Income", min_value=1, step=100)

st.sidebar.header("📊 Expense Categories")
essentials = st.sidebar.number_input("Essentials (rent, groceries, utilities)", min_value=0, step=100)
wants = st.sidebar.number_input("Wants (shopping, eating out, fun)", min_value=0, step=100)

# Auto savings (investments) from income - (essentials + wants)
raw_savings = income - (essentials + wants)
auto_investments = max(raw_savings, 0)

# Optional manual override
st.sidebar.caption("💡 Savings are auto-calculated from Income − (Essentials + Wants).")
override = st.sidebar.checkbox("Override auto Savings/Investments?")
investments = st.sidebar.number_input(
    "Savings / Investments",
    min_value=0,
    value=int(auto_investments),
    step=100,
    disabled=not override
)

st.sidebar.header("🎯 Goal")
goal = st.sidebar.number_input("Savings Goal (%)", min_value=0, max_value=100, value=20, step=1)

# ---------- Derived metrics ----------
total_expenses = essentials + wants
# Savings used for health/goal logic is always Income - (Essentials + Wants)
savings = raw_savings
savings_pct = (savings / income) * 100 if income else 0

# For breakdown visualization we show the current 'investments' bucket (auto or overridden)
breakdown_total = essentials + wants + investments
ess_pct = (essentials / breakdown_total) * 100 if breakdown_total else 0
wants_pct = (wants / breakdown_total) * 100 if breakdown_total else 0
inv_pct = (investments / breakdown_total) * 100 if breakdown_total else 0

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Overview", "🧾 Breakdown", "🎯 Goal Tracker", "💡 Tips", "📄 Report & Download"]
)

# ---------- Tab 1: Overview ----------
with tab1:
    if name and profession and income > 0:
        st.success(f"Welcome, **{name}**! Let’s analyze your finances as a **{profession}**.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Income", f"Rs. {income:,}")
        c2.metric("Total Expenses", f"Rs. {total_expenses:,}", delta=f"{(total_expenses/income)*100:.1f}% of income")
        c3.metric("Savings", f"Rs. {savings:,}", delta=f"{savings_pct:.1f}% of income")

        # Inline validations / badges
        if total_expenses > income:
            st.error("⚠️ Your expenses exceed your income. Reduce Wants or Essentials immediately.")
        elif savings <= 0:
            st.warning("😬 You’re not saving anything this month. Try trimming non-essentials.")
        else:
            st.info("✅ Savings detected. Keep going!")

        # Health Badge
        st.subheader("📌 Financial Health")
        if savings_pct >= 20:
            st.success("💎 **Excellent Saver** — you’re hitting healthy savings levels (≥ 20%).")
        elif 10 <= savings_pct < 20:
            st.warning("👍 **Good Saver** — aim for ≥ 20% to build a stronger safety net.")
        else:
            st.error("⚠️ **Needs Improvement** — try moving Wants into Savings to reach 10–20%+.")
    else:
        st.info("👈 Fill out **User Profile** and **Monthly Finances** in the sidebar to see your overview.")

# ---------- Tab 2: Breakdown ----------
with tab2:
    st.subheader("📊 Expense Distribution")
    if breakdown_total > 0:
        # Table-style bullets
        st.write(f"- **Essentials:** {ess_pct:.1f}%  (Rs. {essentials:,})")
        st.write(f"- **Wants:** {wants_pct:.1f}%  (Rs. {wants:,})")
        st.write(f"- **Savings / Investments:** {inv_pct:.1f}%  (Rs. {investments:,})")

        # Interactive Plotly Pie
        pie_df = {
            "Category": ["Essentials", "Wants", "Savings/Investments"],
            "Amount": [essentials, wants, investments]
        }
        fig_pie = px.pie(
            pie_df,
            names="Category",
            values="Amount",
            hole=0.3,
        )
        fig_pie.update_traces(textinfo="percent+label", hovertemplate="%{label}<br>Rs. %{value:,} (%{percent})")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Interactive Plotly Bar
        bar_df = {
            "Category": ["Essentials", "Wants", "Savings/Investments"],
            "Amount": [essentials, wants, investments]
        }
        fig_bar = px.bar(
            bar_df,
            x="Category",
            y="Amount",
            text="Amount",
        )
        fig_bar.update_traces(texttemplate="Rs. %{text:,}", hovertemplate="%{x}<br>Rs. %{y:,}")
        fig_bar.update_layout(yaxis_title="Amount (Rs.)")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Smart nudges
        st.divider()
        if wants > essentials:
            st.warning("🧠 Your **Wants** exceed **Essentials**. Consider a 50/30/20 style split.")
        if essentials > 0.7 * income:
            st.warning("🏠 Essentials are > 70% of income — housing or utilities may be too high.")
    else:
        st.info("Enter amounts for Essentials, Wants, and Savings to view charts.")

# ---------- Tab 3: Goal Tracker ----------
with tab3:
    st.subheader("🎯 Progress to Goal")
    st.write(f"**Current Savings Rate:** {savings_pct:.1f}%")
    if goal > 0:
        progress = min(max(savings_pct / goal, 0), 1.0)  # clamp 0..1
        st.progress(progress)
        if savings_pct >= goal:
            st.success(f"🏆 Goal achieved! You met your {goal}% savings target.")
        else:
            st.warning(f"📉 You’re {goal - savings_pct:.1f}% away from your {goal}% target.")
    else:
        st.info("Set a **Savings Goal (%)** in the sidebar to track progress.")

# ---------- Tab 4: Tips ----------
with tab4:
    st.subheader("💡 Personalized Tips")
    tips = []
    if total_expenses > income:
        tips.append("Cut Wants immediately until expenses ≤ income.")
    if wants > 0.3 * income:
        tips.append("Try capping **Wants** near 30% of income.")
    if savings_pct < 10:
        tips.append("Automate transfers to savings on payday to hit ≥ 10%.")
    if essentials > 0.5 * income:
        tips.append("Negotiate rent, review utilities, or consider shared costs to lower Essentials.")
    if not tips:
        st.success("👏 You’re doing great! Consider investing with a long-term plan.")
    else:
        for i, t in enumerate(tips, 1):
            st.write(f"{i}. {t}")

# ---------- Tab 5: Report & Download ----------
with tab5:
    st.subheader("📄 Financial Summary")
    if name and profession and income > 0 and breakdown_total > 0:
        summary = f"""
Financial Health Summary for {name} ({profession})

💰 Income: Rs. {income:,}
🏠 Essentials: Rs. {essentials:,}
🛍 Wants: Rs. {wants:,}
✅ Savings (Income − Expenses): Rs. {savings:,}  ({savings_pct:.1f}% of income)

📊 Expense Breakdown (using current Savings/Investments = Rs. {investments:,}):
- Essentials: {ess_pct:.1f}%
- Wants: {wants_pct:.1f}%
- Savings/Investments: {inv_pct:.1f}%

🎯 Goal: {goal}%
Status: {"✅ Achieved" if savings_pct >= goal else f"❌ {goal - savings_pct:.1f}% away from goal"}
"""
        st.text_area("Summary Preview", summary.strip(), height=260)
        st.download_button("📥 Download Summary (.txt)", summary, file_name="financial_summary.txt")
    else:
        st.info("Provide all inputs in the sidebar to generate a summary.")

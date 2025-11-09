import streamlit as st
import datetime
import pandas as pd

# ---------------- APP CONFIG ---------------- #
st.set_page_config(page_title="🌞 Daily Routine Planner", layout="wide")

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
    <style>
    body { background-color: #f8f9fa; }
    .stApp { background-color: #ffffff; color: #222; }
    .task-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 10px;
    }
    div[data-testid="stButton"] > button {
        background-color: #f8f9fa !important;
        color: #333 !important;
        border: 1px solid #dcdcdc !important;
        border-radius: 10px !important;
        padding: 0.4rem 0.8rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #e9ecef !important;
    }
    .meta {
        color: #555;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ---------------- #
if "tasks_by_date" not in st.session_state:
    st.session_state["tasks_by_date"] = {}

if "show_score" not in st.session_state:
    st.session_state["show_score"] = False

def reset_evaluation():
    st.session_state["show_score"] = False

def mark_status(index, new_status):
    st.session_state["tasks_by_date"][date_key][index]["status"] = new_status
    reset_evaluation()

# ---------------- SIDEBAR DATE SELECTION ---------------- #
st.sidebar.header("📅 Select Date")
selected_date = st.sidebar.date_input("Choose a day", datetime.date.today())
month_year = selected_date.strftime("%B %Y")
st.sidebar.markdown(f"**Month:** {month_year.split()[0]} &nbsp;&nbsp; **Year:** {month_year.split()[1]}")

# Initialize date key
date_key = str(selected_date)
if date_key not in st.session_state["tasks_by_date"]:
    st.session_state["tasks_by_date"][date_key] = []

tasks = st.session_state["tasks_by_date"][date_key]

# ---------------- ADD NEW TASK ---------------- #
st.sidebar.header("🕒 Add a New Task")

col1, col2 = st.sidebar.columns(2)
with col1:
    start_time = st.time_input("Start Time", datetime.time(6, 0), key="start_time_input")
    start_ampm = st.selectbox("Start AM/PM", ["AM", "PM"], key="start_ampm")
with col2:
    end_time = st.time_input("End Time", datetime.time(7, 0), key="end_time_input")
    end_ampm = st.selectbox("End AM/PM", ["AM", "PM"], key="end_ampm")

task_description = st.sidebar.text_input("📝 Task Description", "")
add_clicked = st.sidebar.button("➕ Add Task")

if add_clicked:
    if task_description.strip():
        start_str = start_time.strftime("%I:%M") + " " + start_ampm
        end_str = end_time.strftime("%I:%M") + " " + end_ampm
        tasks.append({
            "start": start_str,
            "end": end_str,
            "task": task_description.strip(),
            "status": "Pending"
        })
        st.sidebar.success(f"Task added for {start_str} → {end_str}")
        reset_evaluation()
    else:
        st.sidebar.error("Please enter a task description.")

# ---------------- MAIN DISPLAY ---------------- #
st.title("🌤️ Daily Routine Planner")
st.markdown(f"### 🗓️ {selected_date.strftime('%A, %B %d, %Y')}")

if not tasks:
    st.info("No tasks added yet. Add one from the sidebar!")
else:
    now = datetime.datetime.now()
    tasks_to_remove = []

    for i, task in list(enumerate(tasks)):
        try:
            start_dt = datetime.datetime.strptime(task["start"], "%I:%M %p").replace(
                year=selected_date.year, month=selected_date.month, day=selected_date.day
            )
            end_dt = datetime.datetime.strptime(task["end"], "%I:%M %p").replace(
                year=selected_date.year, month=selected_date.month, day=selected_date.day
            )
            # Set status display
            if task["status"] == "Pending":
                if selected_date > datetime.date.today() or now < start_dt:
                    task["status_display"] = "Yet to start"
                else:
                    task["status_display"] = "Update the status"
            else:
                task["status_display"] = task["status"]
        except Exception:
            task["status_display"] = task["status"]

        st.markdown(
            f"""
            <div class="task-card">
                <b>🕒 {task['start']} → {task['end']}</b><br>
                <span style="font-size:0.95rem; color:#000;">📘 {task['task']}</span><br>
                <span class="meta">Status: {task['status_display']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Buttons
        is_future_task = selected_date > datetime.date.today() or now < start_dt
        col_done, col_missed, col_delete = st.columns([1, 1, 1])
        with col_done:
            st.button("✅ Done", key=f"done_{date_key}_{i}", disabled=is_future_task, on_click=lambda i=i: mark_status(i, "Done"))
        with col_missed:
            st.button("❌ Missed", key=f"missed_{date_key}_{i}", disabled=is_future_task, on_click=lambda i=i: mark_status(i, "Missed"))
        with col_delete:
            if st.button("🗑️ Delete", key=f"delete_{date_key}_{i}"):
                tasks_to_remove.append(i)

    # Safe deletion
    if tasks_to_remove:
        for idx in sorted(tasks_to_remove, reverse=True):
            try:
                tasks.pop(idx)
            except Exception:
                pass
        reset_evaluation()

# ---------------- SCORE & EVALUATION ---------------- #
total_tasks = len(tasks)
completed_count = sum(1 for t in tasks if t["status"] == "Done")
st.markdown("---")
st.write(f"✅ Completed **{completed_count}/{total_tasks}** Tasks")

if total_tasks > 0:
    if st.button("🌅 How was the day?"):
        all_marked = all(t["status"] in ("Done", "Missed") for t in tasks)
        if not all_marked:
            st.warning("Please mark all tasks as Done or Missed before checking your day!")
        else:
            st.session_state["show_score"] = True

if st.session_state.get("show_score", False) and total_tasks > 0:
    st.subheader("📈 Daily Accomplishment Score")
    done = sum(1 for t in tasks if t["status"] == "Done")
    score = int((done / total_tasks) * 100)
    st.progress(score / 100)
    st.write(f"✅ Completed **{done}/{total_tasks}** Tasks — **{score}%** success")

    if score == 100:
        st.success("🌟 Outstanding! You completed everything — keep shining!")
    elif score >= 80:
        st.info("💪 Great job! You're staying consistent.")
    elif score >= 65:
        st.warning("🌱 Keep going! Every bit of effort counts.")
    else:
        st.error("😴 Let’s try again tomorrow — small steps lead to big wins!")

# ---------------- MONTHLY PERFORMANCE SUMMARY ---------------- #
st.markdown("---")
if st.button("📆 View Progress Summary"):
    records = []
    for day, task_list in st.session_state["tasks_by_date"].items():
        if len(task_list) > 0:
            done = sum(1 for t in task_list if t["status"] == "Done")
            total = len(task_list)
            score = int((done / total) * 100)
            if score == 100:
                feedback = "🌟 Excellent"
            elif score >= 80:
                feedback = "💪 Great"
            elif score >= 65:
                feedback = "🌱 Good Effort"
            else:
                feedback = "😴 Needs focus"
            records.append({"Date": day, "Tasks": total, "Done": done, "Score (%)": score, "Feedback": feedback})
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No tracked data yet. Complete some days first!")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit — Demo Prototype")

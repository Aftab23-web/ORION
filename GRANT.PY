import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# Define project start date
start_date = datetime(2025, 10, 1)

# Project tasks with dependencies
tasks = [
    # Week 1: Planning & Setup
    dict(Task="Requirements & Design", Start=start_date, Finish=start_date + timedelta(days=2), Resource="Planning"),
    dict(Task="Environment Setup", Start=start_date + timedelta(days=2), Finish=start_date + timedelta(days=4), Resource="Planning"),
    dict(Task="Database Implementation", Start=start_date + timedelta(days=4), Finish=start_date + timedelta(days=7), Resource="Planning"),
    
    # Week 2: Backend Core
    dict(Task="Authentication System", Start=start_date + timedelta(days=7), Finish=start_date + timedelta(days=10), Resource="Backend"),
    dict(Task="Data Fetching Service", Start=start_date + timedelta(days=10), Finish=start_date + timedelta(days=14), Resource="Backend"),
    
    # Week 3: Portfolio Management
    dict(Task="Portfolio CRUD Operations", Start=start_date + timedelta(days=14), Finish=start_date + timedelta(days=17), Resource="Backend"),
    dict(Task="Portfolio Analytics", Start=start_date + timedelta(days=17), Finish=start_date + timedelta(days=21), Resource="Backend"),
    
    # Week 4: Risk Analysis & AI
    dict(Task="Risk Metrics Calculation", Start=start_date + timedelta(days=21), Finish=start_date + timedelta(days=25), Resource="Backend"),
    dict(Task="AI Recommendation Engine", Start=start_date + timedelta(days=25), Finish=start_date + timedelta(days=28), Resource="Backend"),
    dict(Task="Sentiment Analysis", Start=start_date + timedelta(days=28), Finish=start_date + timedelta(days=30), Resource="Backend"),
    
    # Week 5: Frontend Development
    dict(Task="UI Design & Layout", Start=start_date + timedelta(days=30), Finish=start_date + timedelta(days=34), Resource="Frontend"),
    dict(Task="Dashboard & Pages", Start=start_date + timedelta(days=34), Finish=start_date + timedelta(days=38), Resource="Frontend"),
    dict(Task="Interactive Features", Start=start_date + timedelta(days=38), Finish=start_date + timedelta(days=42), Resource="Frontend"),
    
    # Week 6: Integration & Features
    dict(Task="Stock Search & Comparison", Start=start_date + timedelta(days=42), Finish=start_date + timedelta(days=45), Resource="Integration"),
    dict(Task="Advanced Features", Start=start_date + timedelta(days=45), Finish=start_date + timedelta(days=48), Resource="Integration"),
    dict(Task="Legal & Compliance", Start=start_date + timedelta(days=48), Finish=start_date + timedelta(days=50), Resource="Documentation"),
    
    # Week 7: Testing & Documentation
    dict(Task="Testing", Start=start_date + timedelta(days=50), Finish=start_date + timedelta(days=53), Resource="Testing"),
    dict(Task="Bug Fixes & Optimization", Start=start_date + timedelta(days=53), Finish=start_date + timedelta(days=56), Resource="Testing"),
    dict(Task="Documentation", Start=start_date + timedelta(days=56), Finish=start_date + timedelta(days=59), Resource="Documentation"),
    
    # Week 8: Polish & Deployment
    dict(Task="Final Polish", Start=start_date + timedelta(days=59), Finish=start_date + timedelta(days=62), Resource="Testing"),
    dict(Task="Deployment Prep", Start=start_date + timedelta(days=62), Finish=start_date + timedelta(days=65), Resource="Deployment"),
    dict(Task="Launch", Start=start_date + timedelta(days=65), Finish=start_date + timedelta(days=67), Resource="Deployment"),
]

# Color mapping for resources
colors = {
    'Planning': 'rgb(255, 99, 132)',
    'Backend': 'rgb(54, 162, 235)',
    'Frontend': 'rgb(255, 206, 86)',
    'Integration': 'rgb(75, 192, 192)',
    'Testing': 'rgb(153, 102, 255)',
    'Documentation': 'rgb(255, 159, 64)',
    'Deployment': 'rgb(255, 99, 71)'
}

# Create Gantt chart
fig = ff.create_gantt(
    tasks,
    colors=colors,
    index_col='Resource',
    show_colorbar=True,
    group_tasks=True,
    showgrid_x=True,
    showgrid_y=True,
    title='🚀 ORION Project - Gantt Chart Timeline',
    height=800,
    width=1400
)

# Update layout
fig.update_layout(
    xaxis_title="Timeline",
    font=dict(family="Arial, sans-serif", size=12),
    plot_bgcolor='white',
    paper_bgcolor='#f8f9fa',
    title_font_size=24,
    title_font_color='#667eea',
    title_x=0.5,
    xaxis=dict(
        tickformat='%b %d',
        tickangle=-45,
        gridcolor='#e9ecef'
    )
)

# Add annotations for weeks (converted to timestamp for compatibility)
for i in range(8):
    week_start = start_date + timedelta(weeks=i)
    fig.add_vline(
        x=week_start.timestamp() * 1000,  # Convert to milliseconds
        line_width=2,
        line_dash="dash",
        line_color="red"
    )
    # Add annotation separately
    fig.add_annotation(
        x=week_start,
        y=1,
        yref="paper",
        text=f"Week {i+1}",
        showarrow=False,
        textangle=-90,
        xanchor="left",
        font=dict(size=10, color="red")
    )

# Save as HTML
fig.write_html("orion_gantt_chart.html")
print("✅ Gantt chart saved as 'orion_gantt_chart.html'")

# Show the chart
fig.show()

# Generate statistics
df = pd.DataFrame(tasks)
print("\n📊 Project Statistics:")
print(f"Total Tasks: {len(tasks)}")
print(f"Total Duration: {(df['Finish'].max() - df['Start'].min()).days} days")
print(f"Start Date: {start_date.strftime('%B %d, %Y')}")
print(f"End Date: {(start_date + timedelta(days=67)).strftime('%B %d, %Y')}")
print("\nTasks by Resource:")
print(df['Resource'].value_counts())
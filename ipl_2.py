import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Load data
file_path = "/Users/hradyesh512/Desktop/dashboard_uploads/ipl2/ipl2.csv"
df = pd.read_csv(file_path)

# Create Dash app
app = Dash(__name__)
app.title = "IPL Dashboard"

# Define elevated layout theme
common_layout = dict(
    paper_bgcolor="#121212",
    plot_bgcolor="#121212",
    font=dict(color="#FAFAFA", size=15, family="Segoe UI"),
    margin=dict(l=40, r=40, t=60, b=40),
    title_font=dict(size=22, family="Segoe UI", color="#ffffff"),
    hoverlabel=dict(bgcolor="#1e1e1e", bordercolor="#888", font_size=13, font_family="Segoe UI"),
    legend=dict(bgcolor="#1e1e1e", bordercolor="#333")
)

# Data transformations
# Top 10 Run Scorers
top_scorers = df.groupby("batter")["batsman_run"].sum().sort_values(ascending=False).head(10).reset_index()

# Top 10 Wicket Takers
wickets = df[(df["isWicketDelivery"] == 1) & (df["kind"].notna())]
top_wicket_takers = wickets["bowler"].value_counts().head(10).reset_index()
top_wicket_takers.columns = ["bowler", "wickets"]

# Run Distribution
run_distribution = df["batsman_run"].value_counts().sort_index().reset_index()
run_distribution.columns = ["runs", "count"]

# Extras Breakdown
extras_breakdown = df["extra_type"].value_counts().reset_index()
extras_breakdown.columns = ["extra_type", "count"]

# Dismissal Types
dismissals = df[df["kind"].notna()]["kind"].value_counts().reset_index()
dismissals.columns = ["dismissal_type", "count"]

# Total Runs by Team
team_runs = df.groupby("BattingTeam")["total_run"].sum().sort_values().reset_index()
team_runs.columns = ["team", "total_runs"]

# Best Economy Rates
bowler_stats = df.groupby("bowler").agg(
    balls_bowled=("total_run", "count"),
    runs_conceded=("total_run", "sum")
)
bowler_stats = bowler_stats[bowler_stats["balls_bowled"] >= 500].copy()
bowler_stats["economy_rate"] = (bowler_stats["runs_conceded"] / bowler_stats["balls_bowled"]) * 6
best_economy = bowler_stats.sort_values("economy_rate").head(10).reset_index()

# Layout
app.layout = html.Div([
    html.H1([
        html.Span("🔥 IPL Performance Dashboard ", style={"color": "#ff5e57"}),
        html.Span("– The Ultimate Cricket Insight", style={"color": "#00d8d6"})
    ], style={
        "textAlign": "center",
        "fontSize": "40px",
        "fontFamily": "Segoe UI",
        "fontWeight": "bold",
        "letterSpacing": "1px",
        "marginBottom": "40px"
    }),

    html.Div([
        dcc.Graph(
            id="top-scorers",
            figure=px.bar(top_scorers, x="batsman_run", y="batter", orientation="h", title="Top 10 Run Scorers",
                         color="batsman_run", color_continuous_scale=px.colors.sequential.Magma,
                         hover_data=["batsman_run", "batter"]).update_layout(common_layout)
        ),
        dcc.Graph(
            id="top-wicket-takers",
            figure=px.bar(top_wicket_takers, x="wickets", y="bowler", orientation="h", title="Top 10 Wicket Takers",
                         color="wickets", color_continuous_scale=px.colors.sequential.Cividis,
                         hover_data=["wickets", "bowler"]).update_layout(common_layout)
        ),
    ], style={"display": "flex", "gap": "25px"}),

    html.Div([
        dcc.Graph(
            id="run-distribution",
            figure=px.bar(run_distribution, x="runs", y="count", title="Run Distribution Per Ball",
                         color="count", color_continuous_scale=px.colors.sequential.Inferno,
                         hover_data=["count"]).update_layout(common_layout)
        ),
        dcc.Graph(
            id="extras-breakdown",
            figure=go.Figure(
                data=[go.Pie(
                    labels=extras_breakdown["extra_type"],
                    values=extras_breakdown["count"],
                    hole=0.2,
                    pull=[0.05]*len(extras_breakdown),
                    marker=dict(colors=px.colors.qualitative.Vivid),
                    textinfo='label+percent',
                    hoverinfo='label+value+percent')
                ]
            ).update_layout(title="Extras Breakdown (3D Style Pie)", **common_layout)
        )
    ], style={"display": "flex", "gap": "25px"}),

    html.Div([
        dcc.Graph(
            id="dismissals",
            figure=px.bar(dismissals, x="count", y="dismissal_type", orientation="h",
                         title="Dismissal Types Distribution",
                         color="count", color_continuous_scale=px.colors.sequential.Rainbow,
                         hover_data=["count"]).update_layout(common_layout)
        ),
        dcc.Graph(
            id="team-runs",
            figure=px.bar(team_runs, x="total_runs", y="team", orientation="h",
                         title="Total Runs by Batting Team",
                         color="total_runs", color_continuous_scale=px.colors.sequential.Tealgrn,
                         hover_data=["total_runs"]).update_layout(common_layout)
        ),
    ], style={"display": "flex", "gap": "25px"}),

    html.Div([
        dcc.Graph(
            id="economy-rate",
            figure=px.bar(best_economy, x="economy_rate", y="bowler", orientation="h",
                         title="Best Bowling Economy Rates (Min 500 Balls)",
                         color="economy_rate", color_continuous_scale=px.colors.sequential.Viridis,
                         hover_data=["economy_rate"]).update_layout(common_layout)
        )
    ], style={"display": "flex"})

], style={"backgroundColor": "#121212", "padding": "40px", "fontFamily": "Segoe UI"})

if __name__ == '__main__':
    app.run(debug=True)

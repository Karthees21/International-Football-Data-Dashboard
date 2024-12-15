import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

# Load datasets
results_df = pd.read_csv('results.csv')
goalscorers_df = pd.read_csv('goalscorers.csv')
shootouts_df = pd.read_csv('shootouts.csv') 

# Combine home and away performance for each team
team_performance = results_df.groupby('home_team').agg({
    'home_score': 'sum', 
    'away_score': 'sum', 
    'date': 'count'
}).rename(columns={'home_score': 'Goals Scored', 'away_score': 'Goals Conceded', 'date': 'Matches Played'})

away_performance = results_df.groupby('away_team').agg({
    'away_score': 'sum', 
    'home_score': 'sum', 
    'date': 'count'
}).rename(columns={'away_score': 'Goals Scored', 'home_score': 'Goals Conceded', 'date': 'Matches Played'})

team_performance = team_performance.add(away_performance, fill_value=0).reset_index()
team_performance.rename(columns={'index': 'Team', 'home_team': 'Team'}, inplace=True)

# Add match_id if missing in goalscorers_df
if 'match_id' not in goalscorers_df.columns:
    goalscorers_df['match_id'] = (
        goalscorers_df['team'] + '_' + goalscorers_df['date'].astype(str)
        if 'date' in goalscorers_df.columns else
        np.arange(len(goalscorers_df))
    )

# Add a minute column if missing
goalscorers_df['minute'] = goalscorers_df['minute'].fillna(0).astype(int)

# Count Penalty Wins by team
penalty_wins = shootouts_df['winner'].value_counts().rename_axis('Team').reset_index(name='Penalty Wins')
# Merge Penalty Wins into team_performance
team_performance = team_performance.merge(penalty_wins, on='Team', how='left')
# Fill NaN values with 0 (teams with no penalty shootout wins)
team_performance['Penalty Wins'] = team_performance['Penalty Wins'].fillna(0)

# Calculate clean sheets for each team
clean_sheets_home = results_df[results_df['away_score'] == 0].groupby('home_team').size()
clean_sheets_away = results_df[results_df['home_score'] == 0].groupby('away_team').size()

clean_sheets = clean_sheets_home.add(clean_sheets_away, fill_value=0)
team_performance['Clean Sheets'] = team_performance['Team'].map(clean_sheets).fillna(0)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
server=app.server

# Updated Layout
app.layout = dbc.Container([
# Combined Title and Dropdown Row   
    dbc.Row(
        [
            # Title on the Left
            dbc.Col(
                html.H3(
                    "International Football Data Dashboard", style={'textAlign': 'left', 'marginBottom': '0px'}
                ),width=6,style={'display': 'flex', 'alignItems': 'center'}
            ),
            # Label and Dropdown on the Same Line
            dbc.Col(
                html.Div(
                    [
                        html.Label(
                            "Select Team:",
                            style={'fontWeight': 'bold', 'whiteSpace': 'nowrap','marginRight': '10px' }
                    ),
                    dcc.Dropdown(
                        id='team-dropdown',
                        options=[{'label': team, 'value': team} for team in team_performance['Team']],
                        value='Argentina',
                        clearable=False,
                        style={'width': '150px', 'display': 'inline-block'}
                    )
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'flex-start',  # Align closer to the left
                    'marginRight': '10px'  # Slight right margin adjustment
                    }
                ),width=6
            )
        ],align="center"),

    # Row with All Charts (Top Row)
    dbc.Row([
        dbc.Col(dcc.Graph(id='sunburst-chart', style={"height": "350px"}), width=4),
        dbc.Col(dcc.Graph(id='bar-line-chart', style={"height": "350px"}), width=4),
        dbc.Col(dcc.Graph(id='radar-chart', style={"height": "350px"}), width=4)
    ], className="mb-0",style={"marginTop": "-10px"}),  # Reduce margin-bottom

    # Row with 3D Surface and Bubble Charts (Bottom Row)
    dbc.Row([
        dbc.Col(dcc.Graph(id='surface-3d-chart', style={"height": "250px"}), width=5),
        dbc.Col(dcc.Graph(id='scatter-bubble-chart', style={"height": "250px"}), width=7)
    ], className="mb-0", style={"marginTop": "-20px"})  # Remove margin-bottom
], fluid=True, style={"padding": "0px", "margin": "0px", "height": "100vh", "overflow": "hidden"})


@app.callback(
    Output('surface-3d-chart', 'figure'),
    Input('team-dropdown', 'value')
)
def surface_3d_chart(selected_team):
    team_data = team_performance[team_performance['Team'] == selected_team]
    metrics = ['Goals Scored', 'Goals Conceded', 'Matches Played', 'Penalty Wins', 'Clean Sheets']
    values = [
        team_data['Goals Scored'].values[0],
        team_data['Goals Conceded'].values[0],
        team_data['Matches Played'].values[0],
        team_data['Penalty Wins'].values[0],
        team_data['Clean Sheets'].values[0]
    ]

    # 3D Surface Chart
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([0, 1])
    z = np.array([values, values])

    fig = go.Figure(data=[go.Surface(
        z=z, x=x, y=y, colorscale='Viridis'
    )])

    # Layout adjustments
    fig.update_layout(
        title=f"3D Surface Chart for {selected_team}",
        scene=dict(
            xaxis=dict(tickvals=list(range(len(metrics))), ticktext=metrics),
            yaxis=dict(title=""),
            zaxis=dict(title="Values"),
        ),
        margin=dict(t=30, l=10, r=10, b=30),
        height=350
    )
    return fig


@app.callback(
    Output('bar-line-chart', 'figure'),
    Input('team-dropdown', 'value')
)
def bar_line_chart(selected_team):
    # Filter data based on the selected team
    team_goals = goalscorers_df[goalscorers_df['team'] == selected_team]
    
    # Group goals by minute and count unique scorers
    grouped_data = team_goals.groupby('minute')['scorer'].nunique().reset_index()
    grouped_data.columns = ['minute', 'unique_scorers']
    
    # Create custom hover text
    hover_text = [
        f"Minute: {row['minute']}<br>Scorers: {row['unique_scorers']}"
        for _, row in grouped_data.iterrows()
    ]
    
    # Create the bar chart
    fig = go.Figure(data=go.Bar(
        x=grouped_data['minute'],
        y=grouped_data['unique_scorers'],
        marker_color='orange',
        name='Goals Scored',
        hovertext=hover_text,  # Custom hover info
        hoverinfo="text"       # Only show custom hover text
    ))
    
    # Add line chart overlay
    fig.add_trace(go.Scatter(
        x=grouped_data['minute'],
        y=grouped_data['unique_scorers'],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Trend Line',
        hoverinfo="skip"  # No hover for line chart
    ))
    
    fig.update_layout(
        title="Goals and Unique Scorers Per Minute",
        xaxis_title="Minute",
        yaxis_title="Unique Scorers",
        hovermode="closest"  # Ensure smooth hover display
    )
    return fig


@app.callback(
    Output('sunburst-chart', 'figure'),
    Input('team-dropdown', 'value')
)
def sunburst_chart(selected_team):
    # Merge results.csv and goalscorers.csv to access location and minute data
    merged_df = pd.merge(goalscorers_df, results_df, on=['date', 'home_team', 'away_team'], how='inner')

    # Determine match location (home/away/neutral) for each goal
    merged_df['location'] = merged_df.apply(
        lambda row: (
            'Home' if row['country'] == row['home_team'] else
            'Away' if row['country'] == row['away_team'] else
            'Neutral' if row['neutral'] else None
        ),
        axis=1
    )

    # Filter for the selected team
    team_goals = merged_df[merged_df['team'] == selected_team]

    # Classify goals by location and half
    goals_data = []
    for location in ['Home', 'Away']:
        for half, minute_range in [('First Half', range(0, 46)), ('Second Half', range(46, 91))]:
            goals = team_goals[
                (team_goals['minute'].isin(minute_range)) &
                (
                    (location == 'Home' and team_goals['team'] == team_goals['home_team']) |
                    (location == 'Away' and team_goals['team'] == team_goals['away_team'])
                )
            ].shape[0]
            goals_data.append({'location': location, 'half': half, 'goals': goals})

    # Prepare data for sunburst
    labels = ["Goals Scored"]
    parents = [""]
    values = [sum(entry['goals'] for entry in goals_data)]

    for loc in ['Home', 'Away']:
        loc_goals = sum(entry['goals'] for entry in goals_data if entry['location'] == loc)
        labels.append(loc)
        parents.append("Goals Scored")
        values.append(loc_goals)

        for entry in goals_data:
            if entry['location'] == loc:
                labels.append(f"{entry['location']} - {entry['half']}")
                parents.append(entry['location'])
                values.append(entry['goals'])

    # Create the sunburst chart
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total"
    ))

    fig.update_layout(title="Goals Scored by Location and Halves")
    return fig


@app.callback(
    Output('radar-chart', 'figure'),
    Input('team-dropdown', 'value')
)
def radar_chart(selected_team):
    team_results = results_df[
        (results_df['home_team'] == selected_team) | (results_df['away_team'] == selected_team)
    ]

    # Calculate metrics
    penalties_scored = goalscorers_df[
        (goalscorers_df['team'] == selected_team) & (goalscorers_df['penalty'] == True)
    ].shape[0]

    total_matches = team_results.shape[0]
    wins = team_results[
        ((team_results['home_team'] == selected_team) & (team_results['home_score'] > team_results['away_score'])) |
        ((team_results['away_team'] == selected_team) & (team_results['away_score'] > team_results['home_score']))
    ].shape[0]

    losses = total_matches - wins

    metrics = ['Penalties Scored', 'Win Rate (%)', 'Loss Rate (%)']
    values = [
        penalties_scored,
        (wins / total_matches) * 100 if total_matches > 0 else 0,
        (losses / total_matches) * 100 if total_matches > 0 else 0
    ]
    metrics += [metrics[0]]
    values += [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name="Performance Metrics"
    ))

    fig.update_layout(title="Performance Metrics Radar Chart")
    return fig


@app.callback(
    Output('scatter-bubble-chart', 'figure'),
    Input('team-dropdown', 'value')
)
def scatter_bubble_chart(selected_team):
    # Filter goals for the selected team
    team_goals = goalscorers_df[goalscorers_df['team'] == selected_team]

    # Extract year from the date column
    team_goals['year'] = pd.to_datetime(team_goals['date']).dt.year

    # Merge tournament information from results_df
    merged_df = pd.merge(
        team_goals,
        results_df[['date', 'tournament']],
        on='date',
        how='left'
    )

    # Fixed color mapping for tournaments
    fixed_tournament_colors = {
        'FIFA World Cup': '#1f77b4',     # Blue
        'UEFA Euro': '#ff7f0e',          # Orange
        'Copa América': '#2ca02c',       # Green
        'AFC Asian Cup': '#d62728',      # Red
        'African Cup of Nations': '#9467bd',  # Purple
        'CONCACAF Gold Cup': '#8c564b',  # Brown
        'Friendly': '#e377c2',           # Pink
        'Confederations Cup': '#7f7f7f', # Grey
        'Nations League': '#bcbd22',     # Yellow-Green
        'UEFA Nations League': '#111111',# Black
        'CONCACAF Nations League': '#800000', # Maroon
        'Other': '#17becf'               # Cyan
    }

    # Assign default color for tournaments not in the fixed list
    merged_df['color'] = merged_df['tournament'].map(fixed_tournament_colors).fillna('#17becf')  # Default color: Cyan

    # Prepare hover information
    hover_text = [
        f"Scorer: {row['scorer']}<br>"
        f"Minute: {row['minute']}<br>"
        f"Year: {row['year']}<br>"
        f"Tournament: {row['tournament']}"
        for _, row in merged_df.iterrows()
    ]

    # Create the scatter bubble chart
    fig = go.Figure(data=go.Scatter(
        x=merged_df['minute'],  # X-axis: Minute of goal
        y=merged_df['year'],    # Y-axis: Year of goal
        mode='markers',
        marker=dict(
            size=merged_df['minute'] * 0.2,  # Bubble size proportional to minute
            color=merged_df['color'],        # Fixed color based on tournament
            showscale=False  # Turn off color scale
        ),
        hovertext=hover_text,  # Custom hover text
        hoverinfo="text"
    ))

    fig.update_layout(
        title="Goal Contribution Scatter Bubble Chart",
        xaxis_title="Minute of Goal",
        yaxis_title="Year",
        hovermode="closest",
        height=350
    )
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)

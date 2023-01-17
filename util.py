import matplotlib.pyplot as plt
from mplsoccer import Pitch
import datetime
import numpy as np
import pandas as pd
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st


def plot_shots(match_df):
    # get team names
    team1, team2 = match_df.team_name.unique()
    # A dataframe of shots
    shots = match_df.loc[match_df['type_name'] == 'Shot'].set_index('id')
    shots = shots[shots['period'] < 5].copy(deep=True)
    pitch = Pitch(line_color="black")
    fig, ax = pitch.draw()
    # Size of the pitch in yards (!!!)
    pitchLengthX = 120
    pitchWidthY = 80
    # Plot the shots by looping through them.
    for i, shot in shots.iterrows():
        # get the information
        x = shot['x']
        y = shot['y']
        goal = shot['outcome_name'] == 'Goal'
        team_name = shot['team_name']
        # set circlesize
        circleSize = 1.3
        if team_name == team1:
            if goal:
                shotCircle = plt.Circle((x, y), circleSize, color="red")
                plt.text(x - len(shot['player_name']), y - 2, shot['player_name'], fontdict={'fontsize': 20})
            else:
                shotCircle = plt.Circle((x, y), circleSize, color="red")
                shotCircle.set_alpha(.2)
        else:
            if goal:
                shotCircle = plt.Circle((pitchLengthX - x, pitchWidthY - y), circleSize, color="blue")
                plt.text(pitchLengthX - x + 1, pitchWidthY - y - 2, shot['player_name'], fontdict={'fontsize': 20})
            else:
                shotCircle = plt.Circle((pitchLengthX - x, pitchWidthY - y), circleSize, color="blue")
                shotCircle.set_alpha(.2)
        ax.add_patch(shotCircle)
    # set title
    fig.suptitle(f"{team1} (red) and {team2} (blue) shots", fontsize=40)
    return fig


def plot_passes(match_df, player):
    passes = match_df.loc[match_df['type_name'] == 'Pass'].loc[match_df['sub_type_name'] != 'Throw-in'].set_index('id')
    # drawing pitch
    pitch = Pitch(line_color="black")
    fig, ax = pitch.draw(figsize=(10, 7))
    for i, thepass in passes.iterrows():
        # if pass made by Lucy Bronze
        if thepass['player_name'] == player:
            x = thepass['x']
            y = thepass['y']
            # plot circle
            passCircle = plt.Circle((x, y), 1.3, color="blue")
            passCircle.set_alpha(.2)
            ax.add_patch(passCircle)
            dx = thepass['end_x'] - x
            dy = thepass['end_y'] - y
            # plot arrow
            passArrow = plt.Arrow(x, y, dx, dy, width=2, color="blue")
            ax.add_patch(passArrow)
    fig.suptitle(f"{player} passes", fontsize=40)
    return fig


def five_secs(match_df, team_1_name, team_2_name):
    five_seconds_dict = {}
    team1_dfforbins, team2_dfforbins = [], []
    periods = match_df['period'].unique()
    five_seconds_dict[team_1_name], five_seconds_dict[team_2_name] = {}, {}
    slider_range = st.slider('Periods', min_value=int(np.min(periods)), max_value=int(np.max(periods)), value=[1, 2])
    periods = list(range(slider_range[0], slider_range[1]+1))
    for period in periods:
        ball_lost_team1, ball_lost_team2, five_secs_team1, five_secs_team2 = 0, 0, 0, 0
        for i, row in match_df[match_df['period'] == period].iterrows():
            if i == 0:
                ball_possession = row['possession_team_name']
                timestamp = datetime.datetime.combine(datetime.date.today(), row['timestamp'])
                pass
            if ball_possession != row['possession_team_name']:
                if ball_possession == team_1_name:
                    ball_lost_team1 += 1
                    team1_dfforbins.append([row['x'], row['y'], False])
                if ball_possession == team_2_name:
                    ball_lost_team2 += 1
                    team2_dfforbins.append([row['x'], row['y'], False])
                timestamp_new = datetime.datetime.combine(datetime.date.today(), row['timestamp'])
                diff = timestamp_new - timestamp
                if np.abs(diff.total_seconds()) < 5:
                    if ball_possession == team_1_name:
                        five_secs_team1 += 1
                        team1_dfforbins.append([row['x'], row['y'], True])
                    if ball_possession == team_2_name:
                        five_secs_team2 += 1
                        team2_dfforbins.append([row['x'], row['y'], True])
                timestamp = timestamp_new
            ball_possession = row['possession_team_name']
        five_seconds_dict[team_1_name][period] = (five_secs_team1, ball_lost_team1)
        five_seconds_dict[team_2_name][period] = (five_secs_team2, ball_lost_team2)
    tot_lost_team1 = sum([five_seconds_dict[team_1_name][period][1] for period in periods])
    tot_lost_team2 = sum([five_seconds_dict[team_2_name][period][1] for period in periods])
    tot_five_team1 = sum([five_seconds_dict[team_1_name][period][0] for period in periods])
    tot_five_team2 = sum([five_seconds_dict[team_2_name][period][0] for period in periods])
    five_seconds_dict[team_1_name]['total'] = (tot_five_team1, tot_lost_team1)
    five_seconds_dict[team_2_name]['total'] = (tot_five_team2, tot_lost_team2)
    team1_fivesec = pd.DataFrame(team1_dfforbins, columns=['x', 'y', 'event'])
    team2_fivesec = pd.DataFrame(team2_dfforbins, columns=['x', 'y', 'event'])
    return team1_fivesec, team2_fivesec


def plot_five_secs(five_data):
    pitch = Pitch(line_zorder=2, line_color="black", line_alpha=0.4)
    bins = (3, 3)  # 16 cells x 12 cells
    media = pitch.bin_statistic(five_data['x'], five_data['y'], values=five_data['event'],
                                statistic='mean', bins=bins)
    media['statistic'][np.isnan(media['statistic'])] = 0
    somma = pitch.bin_statistic(five_data['x'], five_data['y'], values=five_data['event'],
                                statistic='sum', bins=bins)
    totale = pitch.bin_statistic(five_data['x'], five_data['y'], values=five_data['event'],
                                 statistic='count', bins=bins)
    fig, ax = pitch.draw(figsize=(20, 14))
    cmap = LinearSegmentedColormap.from_list('rg', ["r", "w", "g"], N=32)
    pitch.heatmap(media, ax=ax, cmap=cmap, alpha=0.6, edgecolor='grey')

    path_eff = [path_effects.Stroke(linewidth=1.5, foreground='black'),
                path_effects.Normal()]
    _ = pitch.label_heatmap(media, ax=ax, str_format='{:.0%}',
                            color='white', fontsize=40, va='center', ha='center', path_effects=path_eff)
    for i in range(bins[0]):
        for j in range(bins[1]):
            x = somma['cx'][i][j]
            y = somma['cy'][i][j] + 4
            stats1 = somma['statistic'][i][j]
            stats2 = totale['statistic'][i][j]
            ax.text(x, y, f'{int(stats1)} / {int(stats2)}', ha='center', fontsize=25, color='black')

    return fig

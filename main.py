import unicodedata
from mplsoccer import Sbopen
from util import *

parser = Sbopen()
euro2020_matches = parser.match(competition_id=55, season_id=43)

euro2020_matches = euro2020_matches[['match_id', 'match_date', 'home_score', 'away_score',
                                     'home_team_name', 'away_team_name',
                                     'competition_stage_name']].sort_values(by='match_date', ascending=False)
matches_dict = {}
for i, match in euro2020_matches.iterrows():
    stage = match['competition_stage_name']
    h = match['home_team_name']
    a = match['away_team_name']
    hg = match['home_score']
    ag = match['away_score']
    matches_dict[f'{stage}. {h} - {a}. {hg}-{ag}'] = match['match_id']

matches_list = list(matches_dict.keys())
matches_id_list = list(matches_dict.values())

# Set page config
st.set_page_config(page_title='Euro2020 Game Stats', page_icon=':soccer:', initial_sidebar_state='expanded')

# Drop-down menu "Select Football Game"
st.sidebar.markdown('## Select Match')
menu_game = st.sidebar.selectbox('Select Match', matches_list)

df, related, freeze, tactics = parser.event(match_id=matches_dict.get(menu_game))

# Replace non-unicode characters in players names
df['player_name'] = df['player_name'].astype(str)
df['player_name'] = df['player_name'].apply(lambda val: unicodedata.normalize('NFC', val).encode('ascii', 'ignore').decode('utf-8'))
df['player_name'] = df['player_name'].replace('nan', np.nan)


# Get teams and players names
team_1 = df['team_name'].unique()[0]
team_2 = df['team_name'].unique()[1]
mask_1 = df.loc[df['team_name'] == team_1]
mask_2 = df.loc[df['team_name'] == team_2]
player_names_1 = mask_1['player_name'].dropna().unique()
player_names_2 = mask_2['player_name'].dropna().unique()

# List of plot for drop-down menus
activities = ['Shot', 'Pass', '5-seconds rule']

menu_activity = st.sidebar.selectbox('Select Activity', activities)
if menu_activity == 'Pass':
    menu_team = st.sidebar.selectbox('Select Team', (team_1, team_2))
    if menu_team == team_1:
        menu_player = st.sidebar.selectbox('Select Player', player_names_1)
    else:
        menu_player = st.sidebar.selectbox('Select Player', player_names_2)
    # Titles and text above the pitch
    st.title('Euro 2022')
    st.write('###', menu_activity, 'map')
    st.write('###### Game:', menu_game)
    st.write('###### Player:', menu_player, '(', menu_team, ')')

    figg = plot_passes(match_df=df, player=menu_player)
    figg.set_size_inches(20, 15)
    st.pyplot(figg)

elif menu_activity == 'Shot':
    # Titles and text above the pitch
    st.title('Euro 2022')
    st.write('###', menu_activity, 'map')
    figg = plot_shots(match_df=df)
    figg.set_size_inches(20, 15)
    st.pyplot(figg)

elif menu_activity == '5-seconds rule':
    st.write('###', menu_activity, 'map')
    team1_five_secs, team2_five_secs = five_secs(match_df=df, team_1_name=team_1, team_2_name=team_2)
    menu_team = st.sidebar.selectbox('Select Team', (team_1, team_2))
    five_secs_data = team1_five_secs if menu_team == team_1 else team2_five_secs
    figg = plot_five_secs(five_data=five_secs_data)
    figg.set_size_inches(20, 15)
    st.pyplot(figg)


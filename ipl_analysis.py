import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IPL", page_icon="🏏",
                   layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title(f"*IPL Analysis*")
st.markdown("""---""")


@st.cache
def load_data():
    # loading csv as pandas dataframe
    df = pd.read_csv(
        r'C:\Users\SAHIL\OneDrive\Documents\CODES\python\projects\pbl\matches.csv')

    return df


data_df = load_data()

# filters

# season range filter

seasons_list = list(data_df['season'].drop_duplicates())

seasons_range = st.sidebar.slider(
    'Select a range of seasons',
    min(seasons_list), max(seasons_list), (min(seasons_list), max(seasons_list)))

data_df = data_df[data_df['season'] >= seasons_range[0]]
data_df = data_df[data_df['season'] <= seasons_range[1]]

st.sidebar.markdown("""---""")

# teams filter

teams_list = list(data_df['team1'].drop_duplicates())

teams_list_filtered = st.sidebar.multiselect(
    'Select teams to analyze', teams_list, default=teams_list)
data_df = data_df[data_df['team1'].isin(teams_list_filtered)]
data_df = data_df[data_df['team2'].isin(teams_list_filtered)]

with st.expander("See original data:"):
    st.write(data_df)

st.markdown("""---""")

# teams with the highest win %

st.subheader('Teams with the highest win percentage')

winners_list = data_df['winner'].value_counts()
winners_df = pd.DataFrame(winners_list)
winners_df.rename(columns={'winner': 'matches won'}, inplace=True)

matches_played_list_1 = data_df['team1'].value_counts()
matches_played_list_2 = data_df['team2'].value_counts()

matches_played_list = pd.concat(
    [matches_played_list_1, matches_played_list_2], axis=1)

matches_played_df = pd.DataFrame(matches_played_list)
matches_played_df['matches played'] = matches_played_df['team1'] + \
    matches_played_df['team2']
matches_played_df.drop(columns=['team1', 'team2'], inplace=True)

matches_won_percent_df = pd.concat([winners_df, matches_played_df], axis=1)
matches_won_percent_df['win %'] = (
    matches_won_percent_df['matches won'] / matches_won_percent_df['matches played'])*100
matches_won_percent_df.reset_index(inplace=True)
matches_won_percent_df = matches_won_percent_df.rename(
    columns={'index': 'team'})

st.write(matches_won_percent_df.sort_values(['win %'], ascending=False))

matches_won_percent_chart = px.scatter(matches_won_percent_df, x="matches played", y="win %", hover_data=[
                                       'matches played', 'matches won', 'win %'], size='matches won', color='team')
st.plotly_chart(matches_won_percent_chart, use_container_width=True)

st.markdown("""---""")

# players who have won the most POM awards

st.subheader("Players who have won the most number of 'player of match' awards")

pom_list = data_df['player_of_match'].value_counts()
pom_df = pd.DataFrame(pom_list)
pom_df.rename(columns={'player_of_match': 'POM won'}, inplace=True)

st.write(pom_df)

pom_df.reset_index(inplace=True)
pom_df = pom_df.rename(
    columns={'index': 'player'})

pom_chart = px.bar(pom_df.head(10), x='player', y='POM won')
st.plotly_chart(pom_chart)

st.markdown("""---""")

# biggest match winning margins

st.subheader('Biggest match winning margins')

matches_df = data_df.drop(columns=['id', 'toss_winner', 'toss_decision',
                          'result', 'dl_applied', 'player_of_match', 'umpire1', 'umpire2', 'umpire3'])
matches_df = matches_df[['team1', 'team2', 'winner', 'win_by_runs',
                         'win_by_wickets', 'season', 'date', 'city', 'venue']]

st.write('-by runs')
st.write(matches_df.sort_values(
    ['win_by_runs'], ascending=False).drop(columns='win_by_wickets'))

st.write('-by wickets')
st.write(matches_df.sort_values(
    ['win_by_wickets'], ascending=False).drop(columns='win_by_runs'))

st.markdown("""---""")

# toss win -> match win probability

st.subheader('Correlation between winning the toss and winning the match')

valid_matches_df = data_df[data_df['result'] != 'no result']
toss_win_vs_match_win = (
    valid_matches_df['toss_winner'] == valid_matches_df['winner']).value_counts()

st.write((toss_win_vs_match_win.at[True]/(
    toss_win_vs_match_win.at[True]+toss_win_vs_match_win.at[False]))*100)

st.markdown("""---""")

# bat first / field first -> win probability

st.subheader(
    'Correlation between batting or fielding first and winning the match')

bat_first_df = valid_matches_df[valid_matches_df['toss_decision'] == 'bat']
bat_first_vs_match_win = (
    bat_first_df['toss_winner'] == bat_first_df['winner']).value_counts()

st.write('Correlation between batting first and winning the match')
st.write((bat_first_vs_match_win.at[True]/(
    bat_first_vs_match_win.at[True]+bat_first_vs_match_win.at[False]))*100)

field_first_df = valid_matches_df[valid_matches_df['toss_decision'] == 'field']
field_first_vs_match_win = (
    field_first_df['toss_winner'] == field_first_df['winner']).value_counts()

st.write('Correlation between fielding first and winning the match')
st.write((field_first_vs_match_win.at[True]/(
    field_first_vs_match_win.at[True]+field_first_vs_match_win.at[False]))*100)

st.markdown("""---""")

# venue -> batting/fielding

st.subheader('Which venue is suitable for batting or fielding?')

batting_venues = data_df[data_df['win_by_runs'] > 0]
batting_venues = batting_venues['venue'].value_counts()
batting_venues.rename('won by batting team', inplace=True)

fielding_venues = data_df[data_df['win_by_wickets'] > 0]
fielding_venues = fielding_venues['venue'].value_counts()
fielding_venues.rename('won by fielding team', inplace=True)

venue_df = pd.concat([batting_venues, fielding_venues], axis=1)
venue_df = venue_df.fillna(0)
venue_df = venue_df.astype(int)


def conditional_format(row):
    highlight_green = 'color: lightgreen;'
    highlight_red = 'color: red'
    default = ''
    # must return one string per cell in this row
    if row['won by batting team'] > row['won by fielding team']:
        return [highlight_green, highlight_red]
    elif row['won by fielding team'] > row['won by batting team']:
        return [highlight_red, highlight_green]
    else:
        return [default, default]


st.write(venue_df.style.apply(conditional_format, axis=1))

# venue_list = list(venue_df.index)
# venue_option = st.selectbox('Select stadium', venue_list)
# st.write(venue_df.loc[venue_option])

st.markdown("""---""")

# team strength -> batting/fielding

st.subheader('Analyzing strength of teams based on batting or fielding')

st.markdown("""---""")

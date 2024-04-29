#!/usr/bin/env python
# coding: utf-8

# # NHL API Scraper v2.0
# 
# A hockey scraper for the new NHL API. The `game_id` parameter is the same used to call the NHL API. This script tries to improve on the speed and efficiency of the v1.0 which was largely smashed together just to get something to work. The `hockey_scraper` library now works again and is currently faster than this scraper but may as well use this scraper as I can get the exact data that I want from it. 
# 
# ### Implemented Functions
# 
# - `get_away_roster(game_id)`: returns a dictionary with player names and IDs of the away roster.
# - `get_home_roster(game_id)`: returns a dictionary with player names and IDs of the home roster.
# - `get_game_roster(game_id)`: returns a dictionary with player names and IDs of both teams.
# 
# - `get_away_positions(game_id)`: returns a dictionary with player IDs and player positions of the away roster.
# - `get_home_positions(game_id)`: returns a dictionary with player IDs and player positions of the home roster.
# - `get_game_positions(game_id)`: returns a dictionary with player IDs and player positions of both teams.
# - `get_goalies_id(game_id)`: returns list of player_ids belonging to the goalies of the game.
# 
# - `get_play_by_play(game_id)`: returns a pandas DataFrame of the play-by-play. 
# - `get_multi_play_by_play([list of game ids])`: returns a pandas DataFrame of the play-by-play of all the listed games. 
# 
# 
# ### Other Functions to Implement
# 
# - ?
# 
# <br>
# 
# ### Methods of Improvement
# 
# - Cutting out unnecessary loop run throughs
# 
# ## Current State
# 
# - The shift data implementation has been corrected so that on-ice players are by-and-large correct over stoppages (as far as I can tell). There are a few discrepancies (bugs) that need to be found and corrected still. 
# - Little bug on some games for `situationCode`
# 
# <br>
# 
# ### Useful Endpoints
# 
# - https://api-web.nhle.com/v1/gamecenter/2023020001/play-by-play
# - https://api-web.nhle.com/v1/player/8477474/landing
# - https://api-web.nhle.com/v1/gamecenter/2023020001/boxscore
# 
# <br>

# In[1]:


import requests
import pandas as pd
import numpy as np
from datetime import datetime


# In[2]:


game_id = 2023020001


# ## Player Names and IDs Dictionary

# In[3]:


def get_away_roster(game_id):
    
    url = 'https://api-web.nhle.com/v1/gamecenter/{}/boxscore'.format(game_id)
    
    try:
        data = requests.get(url)
        boxscore = data.json()
        
    except Exception as e:
        print('URL does not exist for Game_Id {}'.format(game_id))
        return None
        
    else:
        away_roster = {}
        forwards = boxscore.get('playerByGameStats').get('awayTeam').get('forwards')
        defense = boxscore.get('playerByGameStats').get('awayTeam').get('defense')
        goalies = boxscore.get('playerByGameStats').get('awayTeam').get('goalies')

        for spot in forwards:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            away_roster.update({ spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
        
        for spot in defense:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            away_roster.update({spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
        
        for spot in goalies:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            away_roster.update({spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
                
        return away_roster


# In[4]:


# Testing
# get_away_roster(game_id)


# In[5]:


def get_home_roster(game_id):
    
    url = 'https://api-web.nhle.com/v1/gamecenter/{}/boxscore'.format(game_id)
    
    try:
        data = requests.get(url)
        boxscore = data.json()
        
    except Exception as e:
        print('URL does not exist for Game_Id {}'.format(game_id))
        return None
        
    else:
        home_roster = {}
        forwards = boxscore.get('playerByGameStats').get('homeTeam').get('forwards')
        defense = boxscore.get('playerByGameStats').get('homeTeam').get('defense')
        goalies = boxscore.get('playerByGameStats').get('homeTeam').get('goalies')

        for spot in forwards:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            home_roster.update({ spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
        
        for spot in defense:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            home_roster.update({ spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
        
        for spot in goalies:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            home_roster.update({ spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
                
        return home_roster


# In[6]:


# Testing
# get_home_roster(game_id)


# In[7]:


def get_game_roster(game_id):
    
    away_roster = get_away_roster(game_id)
    home_roster = get_home_roster(game_id)
    
    game_roster = away_roster.update(home_roster)
    
    return away_roster


# In[8]:


# Testing
# get_game_roster(2023020001)


# <br>
# 
# ## Getting Player Positions
# 
# For the purposes of my model, skaters are classified as either forwards or defencemen with no differentiation between centers or wingers. 

# In[9]:


def get_away_positions(game_id):
    
    url = 'https://api-web.nhle.com/v1/gamecenter/{}/boxscore'.format(game_id)
    
    try:
        data = requests.get(url)
        boxscore = data.json()
        
    except Exception as e:
        print('URL does not exist for Game_Id {}'.format(game_id))
        return None
        
    else:
        away_roster = {}
        forwards = boxscore.get('playerByGameStats').get('awayTeam').get('forwards')
        defense = boxscore.get('playerByGameStats').get('awayTeam').get('defense')
        goalies = boxscore.get('playerByGameStats').get('awayTeam').get('goalies')

        for spot in forwards:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            away_roster.update({ spot.get('playerId') : 'F'})
        
        for spot in defense:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            away_roster.update({spot.get('playerId') : 'D'})
        
        for spot in goalies:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            away_roster.update({spot.get('playerId') : 'G'})
                
        return away_roster


# In[10]:


# Testing
# get_away_positions(2023020001)


# In[11]:


def get_home_positions(game_id):
    
    url = 'https://api-web.nhle.com/v1/gamecenter/{}/boxscore'.format(game_id)
    
    try:
        data = requests.get(url)
        boxscore = data.json()
        
    except Exception as e:
        print('URL does not exist for Game_Id {}'.format(game_id))
        return None
        
    else:
        home_roster = {}
        forwards = boxscore.get('playerByGameStats').get('homeTeam').get('forwards')
        defense = boxscore.get('playerByGameStats').get('homeTeam').get('defense')
        goalies = boxscore.get('playerByGameStats').get('homeTeam').get('goalies')

        for spot in forwards:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            home_roster.update({ spot.get('playerId') : 'F'})
        
        for spot in defense:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            home_roster.update({spot.get('playerId') : 'D'})
        
        for spot in goalies:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            home_roster.update({spot.get('playerId') : 'G'})
                
        return home_roster


# In[12]:


# Testing
# get_home_positions(2023020001)


# In[13]:


def get_game_positions(game_id):
    
    away_positions = get_away_positions(game_id)
    home_positions = get_home_positions(game_id)
    
    game_positions = away_positions.update(home_positions)
    
    return away_positions


# In[14]:


# Testing
# get_game_positions(2023020001)


# <br>
# 
# ### Getting Goalies (Helper Function)

# In[15]:


def get_goalies_id(game_id):
    
    url = 'https://api-web.nhle.com/v1/gamecenter/{}/boxscore'.format(game_id)
    
    try:
        data = requests.get(url)
        boxscore = data.json()
        
    except Exception as e:
        print('URL does not exist for Game_Id {}'.format(game_id))
        return None
        
    else:
        goalies = {}
        away_goalies = boxscore.get('playerByGameStats').get('awayTeam').get('goalies')
        home_goalies = boxscore.get('playerByGameStats').get('homeTeam').get('goalies')
        
        for spot in away_goalies:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            goalies.update({ spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
            
        for spot in home_goalies:
            url = 'https://api-web.nhle.com/v1/player/{}/landing'.format(spot.get('playerId'))
            playerInfo = requests.get(url)
            playerInfo = playerInfo.json()
            goalies.update({ spot.get('playerId') : ' '.join([playerInfo.get('firstName').get('default').upper(),playerInfo.get('lastName').get('default').upper()])})
                
        return goalies


# In[16]:


# Tester
# get_goalies_id(2023020105)


# <br>

# ### Known Event typeCodes

# In[17]:


typeCodes = {502 : 'FACEOFF', 503 : 'HIT', 504 : 'GIVEAWAY', 505 : 'GOAL', 506 : 'SHOT_ON_GOAL', 507 : 'MISSED_SHOT',
             508 : 'BLOCKED_SHOT', 509 : 'PENALTY', 516 : 'STOPPAGE', 520 : 'PERIOD_START', 521 : 'PERIOD_END',
             523 : 'SHOOTOUT_COMPLETE', 524 : 'GAME_END', 525 : 'TAKEAWAY', 535 : 'DELAYED_PENALTY', 
             537 : 'FAILED_SHOT_ATTEMPT'}

shotCodes = [505,506,507,508]


# In[18]:


teamCodes = { 1 : 'NJD', 2 : 'NYI', 3 : 'NYR', 4 : 'PHI', 5 : 'PIT', 6 : 'BOS', 7 : 'BUF', 8 : 'MTL',
              9 : 'OTT', 10 : 'TOR', 12 : 'CAR', 13 : 'FLA', 14 : 'TBL', 15 : 'WSH', 16 : 'CHI', 17 : 'DET', 
              18 : 'NSH', 19 : 'STL', 20 : 'CGY', 21 : 'COL', 22 : 'EDM', 23 : 'VAN', 24 : 'ANA', 25 : 'DAL',
              26 : 'LAK', 28 : 'SJS', 29 : 'CBJ', 30 : 'MIN', 52 : 'WPG', 53 : 'ARI', 54 : 'VGK', 55 : 'SEA'}


# ## Play-By-Play DataFrame
# 
# This combines the play-by-play and shift data. Most of the chosen columns were inspired by Harry Shomer's public hockey scraper that I had used previously. 

# In[19]:


def parse_event(play_dict):
    
    event_dict_keys = ['Period','Event_tc','Event','Time_Remaining','Time_Elapsed','Strength','Ev_Zone','Type','Ev_Team',
                       'p1_name','p1_ID','p2_name','p2_ID','p3_name','p3_ID','xC','yC']
    
    event_dict = dict()
    
    for key in event_dict_keys:
        if key not in event_dict.keys():
            event_dict.update({ key : None})
    
    # Common play items across all plays
    event_dict['Period'] = play_dict['periodDescriptor']['number']
    event_dict['Event_tc'] = play_dict['typeCode']
    event_dict['Event'] = play_dict['typeDescKey'].upper()
    event_dict['Time_Remaining'] = play_dict['timeRemaining']
    event_dict['Time_Elapsed'] = play_dict['timeInPeriod']
    if 'situationCode' in play_dict.keys():
        event_dict['Strength'] = play_dict['situationCode']
    else:
        event_dict['Strength'] = '1551' # Default
    event_dict['sortOrder'] = play_dict['sortOrder']
    
      
    # Below is applicable for FACEOFF, HIT, GIVEAWAY, GOAL, SHOT_ON_GOAL, MISSED_SHOT, BLOCKED_SHOT, PENALTY, TAKEAWAY, DELAYED_PENALTY    
    if 'details' in play_dict.keys(): 
        if 'zoneCode' in play_dict['details'].keys():
            event_dict['Ev_Zone'] = play_dict['details']['zoneCode']
        if 'xCoord' in play_dict['details'].keys():
            event_dict['xC'] = play_dict['details']['xCoord']
            event_dict['yC'] = play_dict['details']['yCoord']
        
        if event_dict['Event_tc'] == 502: # Faceoffs
            if 'winningPlayerId' in play_dict['details'].keys():
                event_dict['p1_ID'] = play_dict['details']['winningPlayerId']
                event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            if 'losingPlayerId' in play_dict['details'].keys():
                event_dict['p2_ID'] = play_dict['details']['losingPlayerId']
            
        if event_dict['Event_tc'] == 503: # Hits
            if 'hittingPlayerId' in play_dict['details'].keys():
                event_dict['p1_ID'] = play_dict['details']['hittingPlayerId']
                event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            if 'hitteePlayerId' in play_dict['details'].keys():
                event_dict['p2_ID'] = play_dict['details']['hitteePlayerId']
  
        if event_dict['Event_tc'] == 504: # Giveaways
            if 'playerId' in play_dict['details'].keys():
                event_dict['p1_ID'] = play_dict['details']['playerId']
                event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            
        if event_dict['Event_tc'] in [505,506,507,508]: # Goals, Shots_On_Goal, Missed_Shots, Blocked_Shots
            if 'scoringPlayerId' in play_dict['details'].keys():
                event_dict['p1_ID'] = play_dict['details']['scoringPlayerId']
                if 'eventOwnerTeamId' in play_dict['details'].keys():
                    event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            if 'shootingPlayerId' in play_dict['details'].keys():
                event_dict['p1_ID'] = play_dict['details']['shootingPlayerId']
                if 'eventOwnerTeamId' in play_dict['details'].keys():
                    event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            if 'assist1PlayerId' in play_dict['details'].keys():
                event_dict['p2_ID'] = play_dict['details']['assist1PlayerId']
            if 'assist2PlayerId' in play_dict['details'].keys():
                event_dict['p3_ID'] = play_dict['details']['assist2PlayerId']
            if 'blockingPlayerId' in play_dict['details'].keys():
                event_dict['p2_ID'] = play_dict['details']['blockingPlayerId']
                if 'eventOwnerTeamId' in play_dict['details'].keys():
                    event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            if 'shotType' in play_dict['details'].keys():
                event_dict['Type'] = play_dict['details']['shotType'].upper()
            if 'homeScore' in play_dict['details'].keys():
                event_dict['Home_Score'] = play_dict['details']['homeScore']
                event_dict['Away_Score'] = play_dict['details']['awayScore']
            
        if event_dict['Event_tc'] == 509: # Penalties
            if 'committedByPlayerId' in play_dict['details'].keys():
                event_dict['p1_ID'] = play_dict['details']['committedByPlayerId']
                event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            if 'drawnByPlayerId' in play_dict['details'].keys():
                event_dict['p2_ID'] = play_dict['details']['drawnByPlayerId']
            if 'descKey' in play_dict['details'].keys():
                event_dict['Type'] = ' '.join([play_dict['details']['typeCode'],'for',play_dict['details']['descKey'].upper()])
            
        if event_dict['Event_tc'] == 525: # Takeaways
            if 'playerId' in play_dict['details'].keys():
                event_dict['p1_ID'] = play_dict['details']['playerId']
                event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            
        if event_dict['Event_tc'] == 535: # Delayed Penalties
            if 'eventOwnerTeamId' in play_dict['details'].keys():
                event_dict['Ev_Team'] = teamCodes.get(play_dict['details']['eventOwnerTeamId'])
            
        # Failed_Shot_Attempts?
    
    return event_dict


# In[20]:


def get_pbp(game_id):
    
    try:
        url = 'https://api-web.nhle.com/v1/gamecenter/{}/play-by-play'.format(game_id)
        pbp = requests.get(url)
        pbp_data = pbp.json()
        roster = get_game_roster(game_id)
    
    except Exception as e:
        print('Unable to get play-by-play for Game_Id {}'.format(game_id))
        return None
        
    else:
        plays = pbp_data['plays']
        events = [parse_event(play) for play in plays]
        pbp_df = pd.DataFrame(events)
        
        pbp_df['Away_Team'] = pbp_data['awayTeam']['abbrev']
        pbp_df['Home_Team'] = pbp_data['homeTeam']['abbrev']
        pbp_df['p1_name'] = None
        pbp_df['p2_name'] = None
        pbp_df['p3_name'] = None
        pbp_df['Game_Id'] = game_id
        
        pbp_df = pbp_df.sort_values(by='sortOrder',ascending=True).reset_index(drop=True)
        
        for i in pbp_df.index:
            if pd.isna(pbp_df.at[i,'p1_ID']) == False:
                if pd.isna(pbp_df.at[i,'p1_name']) == True:
                    pbp_df.at[i,'p1_name'] = roster.get(pbp_df.at[i,'p1_ID'])
            if pd.isna(pbp_df.at[i,'p2_ID']) == False:
                if pd.isna(pbp_df.at[i,'p2_name']) == True:
                    pbp_df.at[i,'p2_name'] = roster.get(pbp_df.at[i,'p2_ID'])
            if pd.isna(pbp_df.at[i,'p3_ID']) == False:
                if pd.isna(pbp_df.at[i,'p3_name']) == True:
                    pbp_df.at[i,'p3_name'] = roster.get(pbp_df.at[i,'p3_ID'])
            
            if i == 0:
                pbp_df.at[i,'Home_Score'] = 0
                pbp_df.at[i,'Away_Score'] = 0
            else:
                if pbp_df.at[i,'Event_tc'] != 505:
                    pbp_df.at[i,'Home_Score'] = pbp_df.at[i-1,'Home_Score']
                    pbp_df.at[i,'Away_Score'] = pbp_df.at[i-1,'Away_Score']
                    
            pbp_df.at[i,'Home_Skaters'] = pbp_df.at[i,'Strength'][2]
            pbp_df.at[i,'Away_Skaters'] = pbp_df.at[i,'Strength'][1]
            
#         needed_columns = ['Game_Id','Period','Event_tc','Event','Time_Remaining','Time_Elapsed','Strength','Type','p1_ID',
#                           'p1_name','Ev_Team','p2_ID','p2_name','p3_ID','p3_name','xC', 'yC','Home_Skaters','Away_Skaters',
#                           'Home_Score','Away_Score','Away_Team','Home_Team','sortOrder']
        
#         for col in needed_columns:
#             if col not in pbp_df.columns:
#                 pbp_df[col] = None
                    
        return pbp_df[['Game_Id','Period','Event_tc','Event','Time_Remaining','Time_Elapsed','Strength','Type','p1_ID',
                       'p1_name','Ev_Team','p2_ID','p2_name','p3_ID','p3_name','xC', 'yC','Home_Skaters','Away_Skaters',
                       'Home_Score','Away_Score','Away_Team','Home_Team','sortOrder']]


# In[21]:


# %%time
# pbp = get_pbp(2022020160)


# <br>
# 
# ### Adding Shift Data to Play-By-Play
# 
# I had to be careful that the appropriate start and end times of shifts are connected appropriately to the corresponding plays. My previous attempt fell apart as I had failed to account for the fact that any specific time could have differing sets of on-ice players due to stoppages and faceoffs occuring at the "same" timestamp. 

# In[22]:


def parse_shifts(shift):
    
    shift_info = {}
    
    if (shift['firstName'] == None) & (shift['lastName'] == None):
        return shift_info
    else:
        shift_info['player'] = ' '.join([shift['firstName'].upper(),shift['lastName'].upper()])
        shift_info['playerId'] = shift['playerId']
        shift_info['team'] = teamCodes.get(shift['teamId'])
        shift_info['period'] = shift['period']
        shift_info['start'] = shift['startTime']
        shift_info['end'] = shift['endTime']
    
    return shift_info


# In[23]:


def get_shifts(game_id):
    
    try:
        url = 'https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId={}'.format(game_id)
        data = requests.get(url)
        shifts = data.json()
        
    except Exception as e:
        print('Unable to get shifts for Game_Id {}'.format(game_id))
        return None
    
    else:
        shift_df = [parse_shifts(shift) for shift in shifts.get('data')]
        shift_df = pd.DataFrame(shift_df)
        
        return shift_df.dropna(axis=0,how='any').reset_index(drop=True)


# In[24]:


# %%time
# shifts = get_shifts(2022020160)


# ### Conditions for Start and End of a Shift
# 
# Let X be a given timestamp:
# - Start < X < End : Player is ON the ice at X
# - Start = X < End : Player is NOT ON the ice EXCEPT if event is a faceoff
# - Start < X = End : Player is ON the ice EXCEPT if event is a faceoff
# 
# This protocol should also ensure that shot events are connected to players leaving the ice rather than entering the ice. This could make the model more descriptive of real-life events since if a player goes for a change as the team is getting scored on or scoring, it makes more sense to discredit/credit the player leaving rather than entering play. 

# In[25]:


def check_if_on_ice_conditions_met(start,current,end,event_tc):
    
    if (start < current) & (current < end):
        return True
    
    elif (start == current) & (current < end):
        if event_tc == 502:
            return True
        else:
            return False
        
    elif (start < current) & (current == end):
        if event_tc == 502:
            return False
        else:
            return True
        
    elif (start == current) & (current == end):
        return True
        
    elif start > current:
        return False
        
    elif current > end:
        return False


# <br>
# 
# ### Getting Combined Play-By-Play with Shift Data

# In[26]:


def get_play_by_play(game_id):
    
    try:
        pbp = get_pbp(game_id)
        goalies = get_goalies_id(game_id)
        
        cols_to_add = ['awayPlayer1','awayPlayer1_id','awayPlayer2','awayPlayer2_id','awayPlayer3','awayPlayer3_id','awayPlayer4',
                       'awayPlayer4_id','awayPlayer5','awayPlayer5_id','awayPlayer6','awayPlayer6_id','homePlayer1','homePlayer1_id',
                       'homePlayer2','homePlayer2_id','homePlayer3','homePlayer3_id','homePlayer4','homePlayer4_id','homePlayer5',
                       'homePlayer5_id','homePlayer6','homePlayer6_id','Away_Goalie','Away_Goalie_Id','Home_Goalie','Home_Goalie_Id']
        
        for col in cols_to_add:
            if col not in pbp.columns:
                pbp[col] = None
                
        shifts = get_shifts(game_id)
        
        homePlayerList = ['homePlayer1_id','homePlayer2_id','homePlayer3_id','homePlayer4_id','homePlayer5_id','homePlayer6_id']
        homePlayerList_names = ['homePlayer1','homePlayer2','homePlayer3','homePlayer4','homePlayer5','homePlayer6']
        awayPlayerList = ['awayPlayer1_id','awayPlayer2_id','awayPlayer3_id','awayPlayer4_id','awayPlayer5_id','awayPlayer6_id']
        awayPlayerList_names = ['awayPlayer1','awayPlayer2','awayPlayer3','awayPlayer4','awayPlayer5','awayPlayer6']

        for i in range(len(shifts)):

            period = shifts.at[i,'period']
            shift_start = datetime.strptime(shifts.at[i,'start'],'%M:%S')
            shift_end = datetime.strptime(shifts.at[i,'end'],'%M:%S')

            for j in range(len(pbp)):

                time_elapsed = datetime.strptime(pbp.at[j,'Time_Elapsed'],'%M:%S')

                awayPlayerList_loop = [pbp.at[j,'awayPlayer1_id'],pbp.at[j,'awayPlayer2_id'],pbp.at[j,'awayPlayer3_id'],
                                               pbp.at[j,'awayPlayer4_id'],pbp.at[j,'awayPlayer5_id'],pbp.at[j,'awayPlayer6_id']]
                homePlayerList_loop = [pbp.at[j,'homePlayer1_id'],pbp.at[j,'homePlayer2_id'],pbp.at[j,'homePlayer3_id'],
                                               pbp.at[j,'homePlayer4_id'],pbp.at[j,'homePlayer5_id'],pbp.at[j,'homePlayer6_id']]

                if (period == pbp.at[j,'Period']) & (check_if_on_ice_conditions_met(shift_start,time_elapsed,shift_end,pbp.at[j,'Event_tc']) == True):

                    if shifts.at[i,'team'] == pbp.at[j,'Away_Team']:
                        if shifts.at[i,'playerId'] not in awayPlayerList_loop:
                            for k in range(len(awayPlayerList)):
                                if pd.isna(pbp.at[j,awayPlayerList[k]]) == True:
                                    pbp.at[j,awayPlayerList[k]] = shifts.at[i,'playerId']
                                    pbp.at[j,awayPlayerList_names[k]] = shifts.at[i,'player']
                                    if shifts.at[i,'playerId'] in goalies:
                                        pbp.at[j,'Away_Goalie_Id'] = shifts.at[i,'playerId']
                                        pbp.at[j,'Away_Goalie'] = shifts.at[i,'player']
                                    break

                    if shifts.at[i,'team'] == pbp.at[j,'Home_Team']:
                        if shifts.at[i,'playerId'] not in homePlayerList_loop:
                            for k in range(len(homePlayerList)):
                                if pd.isna(pbp.at[j,homePlayerList[k]]) == True:
                                    pbp.at[j,homePlayerList[k]] = shifts.at[i,'playerId']
                                    pbp.at[j,homePlayerList_names[k]] = shifts.at[i,'player']
                                    if shifts.at[i,'playerId'] in goalies:
                                        pbp.at[j,'Home_Goalie_Id'] = shifts.at[i,'playerId']
                                        pbp.at[j,'Home_Goalie'] = shifts.at[i,'player']
                                    break
                        
    except Exception as e:
        print('Unable to return play-by-play because of an issue at',e)
        return None
    
    else:
        
        return pbp


# In[27]:


# %%time

# Testing
# get_play_by_play(2022020160)


# ### Getting Multiple Play-By-Plays

# In[28]:


def get_multi_play_by_play(range_of_ids):
    
    df = get_play_by_play(range_of_ids[0])
    
    for i in range(1,len(range_of_ids)):
        df2 = get_play_by_play(range_of_ids[i])
        df = pd.concat([df,df2],axis=0)
        
    return df


# In[29]:


# %%time

# Testing
# get_multi_play_by_play([2023020001,2023020002])


# <br>

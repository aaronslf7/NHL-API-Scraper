#!/usr/bin/env python
# coding: utf-8

# # NHL API Scraper
# 
# A hockey scraper for the new NHL API. The `game_id` parameter is the same used to call the NHL API. These functions get the job done although I'm sure they can be optimized for speed and efficiency. 
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

# In[1]:


import requests
import pandas as pd
import numpy as np
from datetime import datetime

# from Game_Contribution_v1dot1 import *


# In[2]:


game_id = 2023020172


# ## Player Names and IDs Dictionary

# In[3]:


def get_away_roster(game_id):
    
    pbp = requests.get('https://api-web.nhle.com/v1/gamecenter/'+str(game_id)+'/play-by-play')
    pbp_data = pbp.json()
    
    game_roster = pbp_data.get('rosterSpots')
    awayTeam_Id = pbp_data.get('awayTeam').get('id')
    
    away_roster = {}

    for i in range(len(game_roster)):
    
        playerName = (game_roster[i].get('firstName').get('default') + ' ' + game_roster[i].get('lastName').get('default')).upper()
    
        if game_roster[i].get('teamId') == awayTeam_Id: # If player is on the away team
            away_roster.update({game_roster[i].get('playerId') : playerName})
            
    return away_roster


# In[4]:


# Testing
# get_away_roster(2023020001) 


# In[5]:


def get_home_roster(game_id):
    
    pbp = requests.get('https://api-web.nhle.com/v1/gamecenter/'+str(game_id)+'/play-by-play')
    pbp_data = pbp.json()
    
    game_roster = pbp_data.get('rosterSpots')
    homeTeam_Id = pbp_data.get('homeTeam').get('id')
    
    home_roster = {}

    for i in range(len(game_roster)):
    
        playerName = (game_roster[i].get('firstName').get('default') + ' ' + game_roster[i].get('lastName').get('default')).upper()
    
        if game_roster[i].get('teamId') == homeTeam_Id: # If player is on the home team
            home_roster.update({game_roster[i].get('playerId') : playerName})
            
    return home_roster


# In[6]:


# Testing
# get_home_roster(2023020001)


# In[7]:


def get_game_roster(game_id):
    
    pbp = requests.get('https://api-web.nhle.com/v1/gamecenter/'+str(game_id)+'/play-by-play')
    pbp_data = pbp.json()
    
    game_roster = pbp_data.get('rosterSpots')
    team_rosters = {}

    for i in range(len(game_roster)):
    
        playerName = (game_roster[i].get('firstName').get('default') + ' ' + game_roster[i].get('lastName').get('default')).upper()
            
        team_rosters.update({game_roster[i].get('playerId') : playerName})
            
    return team_rosters


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
    
    pbp = requests.get('https://api-web.nhle.com/v1/gamecenter/'+str(game_id)+'/play-by-play')
    pbp_data = pbp.json()

    game_roster = pbp_data.get('rosterSpots')

    forwards = ['C','R','L']

    away_positions = {}

    for i in range(len(game_roster)):

        if game_roster[i].get('teamId') == pbp_data.get('awayTeam').get('id'):
            if game_roster[i].get('positionCode') in forwards:
                away_positions.update({ game_roster[i].get('playerId') : 'F'})
            else:
                away_positions.update({ game_roster[i].get('playerId') : game_roster[i].get('positionCode')})

    return away_positions


# In[10]:


# Testing
# get_away_positions(2023020001)


# In[11]:


def get_home_positions(game_id):
    
    pbp = requests.get('https://api-web.nhle.com/v1/gamecenter/'+str(game_id)+'/play-by-play')
    pbp_data = pbp.json()

    game_roster = pbp_data.get('rosterSpots')

    forwards = ['C','R','L']

    home_positions = {}

    for i in range(len(game_roster)):

        if game_roster[i].get('teamId') == pbp_data.get('homeTeam').get('id'):
            if game_roster[i].get('positionCode') in forwards:
                home_positions.update({ game_roster[i].get('playerId') : 'F'})
            else:
                home_positions.update({ game_roster[i].get('playerId') : game_roster[i].get('positionCode')})

    return home_positions


# In[12]:


# Testing
# get_home_positions(2023020001)


# In[13]:


def get_game_positions(game_id):
    
    pbp = requests.get('https://api-web.nhle.com/v1/gamecenter/'+str(game_id)+'/play-by-play')
    pbp_data = pbp.json()

    game_roster = pbp_data.get('rosterSpots')

    forwards = ['C','R','L']

    game_positions = {}

    for i in range(len(game_roster)):

        if game_roster[i].get('positionCode') in forwards:
            game_positions.update({ game_roster[i].get('playerId') : 'F'})
        else:
            game_positions.update({ game_roster[i].get('playerId') : game_roster[i].get('positionCode')})

    return game_positions


# In[14]:


# Testing
# get_game_positions(2023020001)


# <br>
# 
# ### Getting Goalies (Helper Function)

# In[15]:


def get_goalies_id(game_id):
    
    roster = get_game_positions(game_id)
    
    goalies = []
    
    for key in roster.keys():
        if roster.get(key) == 'G':
            goalies.append(key)
            
    return goalies


# In[16]:


# Tester
# get_goalies_id(game_id)


# <br>

# ### Known Event typeCodes

# In[17]:


typeCodes = {502 : 'FACEOFF', 503 : 'HIT', 504 : 'GIVEAWAY', 505 : 'GOAL', 506 : 'SHOT_ON_GOAL', 507 : 'MISSED_SHOT',
             508 : 'BLOCKED_SHOT', 509 : 'PENALTY', 516 : 'STOPPAGE', 520 : 'PERIOD_START', 521 : 'PERIOD_END',
             523 : 'SHOOTOUT_COMPLETE', 524 : 'GAME_END', 525 : 'TAKEAWAY', 535 : 'DELAYED_PENALTY', 
             537 : 'FAILED_SHOT_ATTEMPT'}

shotCodes = [505,506,507,508]


# <br>

# ## Play-By-Play DataFrame
# 
# This combines the play-by-play and shift data. Most of the chosen columns were inspired by Harry Shomer's public hockey scraper that I had used previously. 

# In[18]:


def get_play_by_play(game_id):
    
    pbp = requests.get('https://api-web.nhle.com/v1/gamecenter/'+str(game_id)+'/play-by-play')
    
    # Print status message
    print('Scraping Game Id',game_id)
    
    pbp_data = pbp.json()
    
    game_roster = get_game_roster(game_id)
    awayTeam_Id = pbp_data.get('awayTeam').get('id')
    homeTeam_Id = pbp_data.get('homeTeam').get('id')
    
    goalie_ids = get_goalies_id(game_id)
    
    NoneType = type(None)
    
    away_on_ice_player_ids = ['awayPlayer1_id','awayPlayer2_id','awayPlayer3_id','awayPlayer4_id','awayPlayer5_id',
                              'awayPlayer6_id']
    home_on_ice_player_ids = ['homePlayer1_id','homePlayer2_id','homePlayer3_id','homePlayer4_id','homePlayer5_id',
                              'homePlayer6_id']
    
    rows = len(pbp_data.get('plays'))
    cols = ['Game_Id','Date','Period','Event_tc','Event','Time_Elapsed','Strength','Ev_Zone','Type','Ev_Team','Away_Team',
            'Home_Team','p1_name','p1_ID','p2_name','p2_ID','p3_name','p3_ID','awayPlayer1','awayPlayer1_id','awayPlayer2',
            'awayPlayer2_id','awayPlayer3','awayPlayer3_id','awayPlayer4','awayPlayer4_id','awayPlayer5','awayPlayer5_id',
            'awayPlayer6','awayPlayer6_id','homePlayer1','homePlayer1_id','homePlayer2','homePlayer2_id','homePlayer3',
            'homePlayer3_id','homePlayer4','homePlayer4_id','homePlayer5','homePlayer5_id','homePlayer6','homePlayer6_id',
            'Away_Score','Home_Score','Away_Goalie','Away_Goalie_Id','Home_Goalie','Home_Goalie_Id','xC','yC']

    pbp_df = pd.DataFrame(index=np.arange(rows),columns=cols)
    
    for i in range(len(pbp_data.get('plays'))):
    
        pbp_df['Game_Id'] = pbp_data.get('id')
        pbp_df['Date'] = pbp_data.get('gameDate')
        pbp_df['Away_Team'] = pbp_data.get('awayTeam').get('abbrev')
        pbp_df['Home_Team'] = pbp_data.get('homeTeam').get('abbrev')
      
        this_play = pbp_data.get('plays')[i]
    
        pbp_df.at[i,'Period'] = this_play.get('period')
        pbp_df.at[i,'Event_tc'] = this_play.get('typeCode')
        pbp_df.at[i,'Event'] = typeCodes.get(this_play.get('typeCode'))
        pbp_df.at[i,'Time_Elapsed'] = this_play.get('timeInPeriod')
        pbp_df.at[i,'Strength'] = str(this_play.get('situationCode'))
    
        if i == 0:
            pbp_df.at[i,'Away_Score'] = 0
            pbp_df.at[i,'Home_Score'] = 0
        elif this_play.get('typeCode') != 505:
            pbp_df.at[i,'Away_Score'] = pbp_df.at[i-1,'Away_Score']
            pbp_df.at[i,'Home_Score'] = pbp_df.at[i-1,'Home_Score']
   
        if this_play.get('typeCode') in [502,503,504,505,506,507,508,509,525,537]: # If Event has xC and yC
            pbp_df.at[i,'xC'] = this_play.get('details').get('xCoord')
            pbp_df.at[i,'yC'] = this_play.get('details').get('yCoord')
            pbp_df.at[i,'Ev_Zone'] = this_play.get('details').get('zoneCode')
            if this_play.get('details').get('eventOwnerTeamId') == awayTeam_Id:
                pbp_df.at[i,'Ev_Team'] = pbp_data.get('awayTeam').get('abbrev')
            else:
                pbp_df.at[i,'Ev_Team'] = pbp_data.get('homeTeam').get('abbrev')
            
        if this_play.get('typeCode') == 502: # If it's a faceoff
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('winningPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('winningPlayerId'))
            pbp_df.at[i,'p2_ID'] = this_play.get('details').get('losingPlayerId')
            pbp_df.at[i,'p2_name'] = game_roster.get(this_play.get('details').get('losingPlayerId'))
        
        if this_play.get('typeCode') == 503: # If it's a hit
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('hittingPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('hittingPlayerId'))
            pbp_df.at[i,'p2_ID'] = this_play.get('details').get('hitteePlayerId')
            pbp_df.at[i,'p2_name'] = game_roster.get(this_play.get('details').get('hitteePlayerId'))
    
        if this_play.get('typeCode') == 504: # If it's a giveaway
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('playerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('playerId'))
            
        if this_play.get('typeCode') in shotCodes: # If the play is a shot type
            if this_play.get('details').get('eventOwnerTeamId') == pbp_data.get('awayTeam').get('id'): # Away team shooting
                pbp_df.at[i,'Home_Goalie_Id'] = this_play.get('details').get('goalieInNetId')
                pbp_df.at[i,'Home_Goalie'] = game_roster.get(this_play.get('details').get('goalieInNetId'))     
            if this_play.get('details').get('eventOwnerTeamId') == pbp_data.get('homeTeam').get('id'): # Home team shooting
                pbp_df.at[i,'Away_Goalie_Id'] = this_play.get('details').get('goalieInNetId')
                pbp_df.at[i,'Away_Goalie'] = game_roster.get(this_play.get('details').get('goalieInNetId'))            
        
        if this_play.get('typeCode') == 505: # If it's a goal
            if type(this_play.get('details').get('shotType')) != NoneType: # If shotType is not available
                pbp_df.at[i,'Type'] = this_play.get('details').get('shotType').upper()
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('scoringPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('scoringPlayerId'))
            pbp_df.at[i,'p2_ID'] = this_play.get('details').get('assist1PlayerId')
            pbp_df.at[i,'p2_name'] = game_roster.get(this_play.get('details').get('assist1PlayerId'))
            pbp_df.at[i,'p3_ID'] = this_play.get('details').get('assist2PlayerId')
            pbp_df.at[i,'p3_name'] = game_roster.get(this_play.get('details').get('assist2PlayerId'))
            pbp_df.at[i,'Away_Score'] = this_play.get('details').get('awayScore')
            pbp_df.at[i,'Home_Score'] = this_play.get('details').get('homeScore')

        if this_play.get('typeCode') == 506: # If it's a shot on goal
            if type(this_play.get('details').get('shotType')) != NoneType: # If shotType is not available
                pbp_df.at[i,'Type'] = this_play.get('details').get('shotType').upper()
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('shootingPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('shootingPlayerId'))
        
        if this_play.get('typeCode') == 507: # If it's a missed shot
            if type(this_play.get('details').get('shotType')) != NoneType: # If shotType is not available
                pbp_df.at[i,'Type'] = this_play.get('details').get('shotType').upper()
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('shootingPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('shootingPlayerId'))

        if this_play.get('typeCode') == 508: # If it's blocked shot
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('blockingPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('blockingPlayerId'))
            pbp_df.at[i,'p2_ID'] = this_play.get('details').get('shootingPlayerId')
            pbp_df.at[i,'p2_name'] = game_roster.get(this_play.get('details').get('shootingPlayerId'))  
        
        if this_play.get('typeCode') == 509: # If it's a penalty
            pbp_df.at[i,'Type'] = this_play.get('details').get('typeCode') + ' for ' + this_play.get('details').get('descKey').upper()
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('committedByPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('committedByPlayerId'))
            pbp_df.at[i,'p2_ID'] = this_play.get('details').get('drawnByPlayerId')
            pbp_df.at[i,'p2_name'] = game_roster.get(this_play.get('details').get('drawnByPlayerId'))

        if this_play.get('typeCode') == 516: # If it's a stoppage
            pbp_df.at[i,'Type'] = this_play.get('details').get('reason').upper()

        if this_play.get('typeCode') == 525: # If it's a takeaway
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('playerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('playerId'))
        
#      if this_play.get('typeCode') == 535: # If it's a delayed penalty
        
    
        if this_play.get('typeCode') == 537: # If it's a failed shot attempt
            if type(this_play.get('details').get('shotType')) != NoneType: # If shotType is not available
                pbp_df.at[i,'Type'] = this_play.get('details').get('shotType').upper()
            pbp_df.at[i,'p1_ID'] = this_play.get('details').get('shootingPlayerId')
            pbp_df.at[i,'p1_name'] = game_roster.get(this_play.get('details').get('shootingPlayerId'))

    # Adding Shift Data
    shifts = requests.get('https://api.nhle.com/stats/rest/en/shiftcharts?cayenneExp=gameId='+str(game_id))

    shift_data = shifts.json()
    shift_data.get('data')
    
    homePlayerList = ['homePlayer1_id','homePlayer2_id','homePlayer3_id','homePlayer4_id','homePlayer5_id','homePlayer6_id']
    homePlayerList_names = ['homePlayer1','homePlayer2','homePlayer3','homePlayer4','homePlayer5','homePlayer6']
    awayPlayerList = ['awayPlayer1_id','awayPlayer2_id','awayPlayer3_id','awayPlayer4_id','awayPlayer5_id','awayPlayer6_id']
    awayPlayerList_names = ['awayPlayer1','awayPlayer2','awayPlayer3','awayPlayer4','awayPlayer5','awayPlayer6']
    
    for i in range(len(shift_data.get('data'))):
    
        shift = shift_data.get('data')[i]

        period = shift.get('period')
        shift_start = datetime.strptime(shift.get('startTime'),'%M:%S')
        shift_end = datetime.strptime(shift.get('endTime'),'%M:%S')
    
        for j in range(len(pbp_df)):

            time_elapsed = datetime.strptime(pbp_df.at[j,'Time_Elapsed'],'%M:%S')

            awayPlayerList_loop = [pbp_df.at[j,'awayPlayer1_id'],pbp_df.at[j,'awayPlayer2_id'],pbp_df.at[j,'awayPlayer3_id'],
                                   pbp_df.at[j,'awayPlayer4_id'],pbp_df.at[j,'awayPlayer5_id'],pbp_df.at[j,'awayPlayer6_id']]
            homePlayerList_loop = [pbp_df.at[j,'homePlayer1_id'],pbp_df.at[j,'homePlayer2_id'],pbp_df.at[j,'homePlayer3_id'],
                                   pbp_df.at[j,'homePlayer4_id'],pbp_df.at[j,'homePlayer5_id'],pbp_df.at[j,'homePlayer6_id']]

            if (period == pbp_df.at[j,'Period']) & (shift_start <= time_elapsed < shift_end):

                if shift.get('teamId') == awayTeam_Id:
                    if shift.get('playerId') not in awayPlayerList_loop:
                        for k in range(len(awayPlayerList)):
                            if pd.isna(pbp_df.at[j,awayPlayerList[k]]) == True:
                                pbp_df.at[j,awayPlayerList[k]] = shift.get('playerId')
                                pbp_df.at[j,awayPlayerList_names[k]] = game_roster.get(shift.get('playerId'))
                                break

                if shift.get('teamId') == homeTeam_Id:
                    if shift.get('playerId') not in homePlayerList_loop:
                        for k in range(len(homePlayerList)):
                            if pd.isna(pbp_df.at[j,homePlayerList[k]]) == True:
                                pbp_df.at[j,homePlayerList[k]] = shift.get('playerId')
                                pbp_df.at[j,homePlayerList_names[k]] = game_roster.get(shift.get('playerId'))
                                break
                                
    # Adding goalies to blocked shots
    for i in range(len(pbp_df)):
        for j in range(len(away_on_ice_player_ids)):
            for g_id in goalie_ids:
                if g_id == pbp_df.at[i,away_on_ice_player_ids[j]]:
                    pbp_df.at[i,'Away_Goalie_Id'] = g_id
                    pbp_df.at[i,'Away_Goalie'] = game_roster.get(g_id)
        for j in range(len(home_on_ice_player_ids)):
            for g_id in goalie_ids:
                if g_id == pbp_df.at[i,home_on_ice_player_ids[j]]:
                    pbp_df.at[i,'Home_Goalie_Id'] = g_id
                    pbp_df.at[i,'Home_Goalie'] = game_roster.get(g_id)
                                
    return pbp_df


# In[19]:


# Testing
# get_play_by_play(game_id)


# <br>
# 
# ## Getting Play-By-Play for Multiple Games

# In[20]:


def get_multi_play_by_play(range_of_ids):
    
    df = get_play_by_play(range_of_ids[0])
    
    for i in range(1,len(range_of_ids)):
        df2 = get_play_by_play(range_of_ids[i])
        df = pd.concat([df,df2],axis=0)
        
    return df


# In[21]:


# Testing
# get_multi_play_by_play(game_ids)


# <br>

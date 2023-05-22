from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import pandas as pd
import PySimpleGUI as sg

class scouting_sq:
    def __init__(self, user, server, role):
        self.user = user
        self.server = server
        self.role = role

    def generate_profile_link(self):
        self.user = self.user.lower().replace(' ', '%20')
        self.link = f"https://u.gg/lol/profile/{self.server}/{self.user}/champion-stats?role={self.role}"

    def html_function(self):
        html = urlopen(self.link)
        self.soup = BeautifulSoup(html, 'html.parser')

    def scouting_function(self):
        list_of_champions = self.soup.findAll('div', {'class':'rt-tr-group'})

        champions_list = []
        winrate_list = []
        wins_list = []
        loses_list = []
        kda_list = []
        kills_list = []
        deaths_list = []
        assists_list = []

        for row in list_of_champions:
            champions_list.append(row.find('span', {'class':'champion-name'}).get_text())
            winrate_list.append(row.find('strong').get_text())
            wins_list.append(int(row.find('span', {'class':'match-record'}).get_text()[:2].replace('W', '')))
            loses_list.append(int(row.find('span', {'class':'match-record'}).get_text()[3:6].replace(' ', '').replace('L', '')))
            kda_list.append(row.find('div', {'class': 'kda'}).get_text()[:4])
            kills_list.append(row.find('div', {'class': 'kda'}).get_text()[4:8].replace(' ', ''))
            deaths_list.append(row.find('div', {'class': 'kda'}).get_text()[10:14].replace(' ', ''))
            assists_list.append(row.find('div', {'class': 'kda'}).get_text()[16:].replace(' ', ''))

        total_games_list = pd.DataFrame([wins_list, loses_list]).sum()

        data = {
            "Champion": champions_list,
            "Winrate": winrate_list,
            "Wins": wins_list,
            "Loses": loses_list,
            "Total Games": total_games_list,
            "KDA": kda_list,
            "Kills": kills_list,
            "Deaths": deaths_list,
            "Assists": assists_list
        }

        df_player = pd.DataFrame(data)
        if df_player.empty:
            df_empty_layout = [[sg.Text("The player hasn't played a game in this role yet!")],
                               [sg.Button('Ok')]]
            df_empty_window = sg.Window('No games yet', df_empty_layout)
            dfew_event, dfew_values = df_empty_window.read()
            if dfew_event == sg.WIN_CLOSED or dfew_event == 'Ok':
                df_empty_window.close()
        else:
            sheet_name = f"u.gg_lol_profile_user={self.user}_role={self.role}"
            df_player.to_excel(f'{sheet_name}.xlsx')

            sw_layout = [[sg.Text('The Excel file was created successfully!')],
                        [sg.Button('Ok')]]
            success_window = sg.Window('Success!', sw_layout)
            sw_event, sw_values = success_window.read()
            if sw_event == sg.WIN_CLOSED or sw_event == 'Ok':
                success_window.close()

username_input = sg.Input(key='username')

list_of_servers = ['NA', 'EUW', 'EUN', 'KR', 'BR', 'JP', 'RU', 'OCE', 'TR', 'LAN', 'LAS', 'PH', 'SG', 'TH', 'TW', 'VN']
server_combobox = sg.Combo(list_of_servers, default_value='  ', size=(5), readonly=True, key='server')

list_of_roles = ['TOP', 'JUNGLE', 'MIDDLE', 'ADC', 'SUPPORT']
roles_combobox = sg.Combo(list_of_roles, default_value=' ', size=(9), readonly=True, key='role')

layout = [[sg.Text('Player Username:')],
          [username_input],
          [sg.Text('Player Server:')],
          [server_combobox],
          [sg.Text('Player Role:')],
          [roles_combobox],
          [sg.Button('Search'), sg.Exit()]]

window = sg.Window('Scouting u.gg', layout)

while True:
    event, values = window.read()
    username = values['username'].lower().replace(' ', '%20')
    user_server = server_combobox.get()
    user_role = roles_combobox.get().lower()

    if user_server in ['NA', 'EUW', 'EUN', 'BR', 'JP', 'TR']:
        user_server = user_server.lower() + '1'
    elif user_server in ['PH', 'SG', 'TH', 'TW', 'VN']:
        user_server = user_server.lower() + '2'
    elif user_server in ['KR', 'RU']:
        user_server = user_server.lower()
    elif user_server in ['OCE', 'LAN']:
        user_server = user_server[:2].lower() + '1'
    else:
        user_server = 'la2'

    if event == 'Search':
        try:
            profile = scouting_sq(username, user_server, user_role)
            profile.generate_profile_link()
            profile.html_function()
            profile.scouting_function()
        except HTTPError:
            error_layout = [[sg.Text('Unknown user! Make sure the username and the server are correct!')], 
                            [sg.Button('Ok')]]
            error_window = sg.Window('Error', error_layout)
            er_event, er_values = error_window.read()
            if er_event == sg.WIN_CLOSED or er_event == 'Ok':
                error_window.close()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break      

window.close()
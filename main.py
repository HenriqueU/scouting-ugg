from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import pandas as pd

class scouting_sq:
    def __init__(self, link, role):
        self.link = link
        self.role = role

    def validator(self):
        roles = ['top', 'jungle', 'middle', 'adc', 'support']

        if 'u.gg' not in self.link:
            print('\nLink do perfil inválido\n')
        elif self.role.lower() not in roles:
            print('\nRole inválida. Apenas estas roles são aceitas:\n')
            for i in roles:
                print(i)
            print(' ')
        else:
            self.role = self.role.lower()    
            self.valid_link = self.link.replace('overview', f'champion-stats?role={self.role}')

    def html_function(self):
        html = urlopen(self.valid_link)
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
            print('\nO jogador não possui jogos nesta role')
        else:
            sheet_name = self.valid_link.replace('/', '_').replace('?', '_')
            df_player.to_excel(f'{sheet_name[8:]}.xlsx')

while True:
    try:
        player_profile = input('Insira o link do perfil do jogador (Apenas links do site u.gg são aceitos): ')
        player_role = input('Insira a role do jogador: ')

        profile = scouting_sq(player_profile, player_role)
        profile.validator()
        profile.html_function()
        profile.scouting_function()
    except ValueError:
        print('\nLink do perfil inválido\n')
        continue
    except AttributeError:
        continue
    except HTTPError:
        print('\nLink do perfil inválido\n')
    else:
        break
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, render_template
import time
import requests
import json
import templates
import signal
import sys

# Create a WebDriver instance (for Chrome)

driver = webdriver.Chrome()
target = 0
popped = False
# CHANGE INPUTS HERE 
url = "https://cricclubs.com/NormanCricketChampionship/viewScorecard.do?matchId=920&clubId=1005270"
team_bat = "CK"

# Initialize the previous score
previous_score = None
current_score = None 

# Default values for the score
score = {'Team': 'Team 1', 'Score': '0/0', 'Overs': '0/20 ov'}
bat1={'Name': 'Bat 1', 'Runs': '0', 'Balls': '0', 'Fours': '0', 'Sixes': '0', 'StrikeRate': '0'}
bat2={'Name': 'Bat 2', 'Runs': '0', 'Balls': '0', 'Fours': '0', 'Sixes': '0', 'StrikeRate': '0'} 
bowl1 = {'Name': 'Bowler', 'Overs': '0.0', 'Maidens': '0', 'Runs': '0', 'Wickets': '0', 'Economy': '0'} 
target_pass = '-'

# Initialize the Flask API 
app = Flask(__name__)

def get_score(url, previous_score, team_bat, target=0): 
        
        driver.get(url)
        # global popped
        global score 
        global bat1 
        global bat2 
        global bowl1
        global popped

        try:
            # Wait for the dynamically loaded content to appear (if applicable)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="mainDiv"]/div[1]/div[1]/div/div[1]/div/div/div/ul')))

            # Once the content is loaded, you can scrape it
            element = driver.find_element(By.XPATH, '//*[@id="mainDiv"]/div[1]/div[1]/div/div[1]/div/div/div/ul')
            #//*[@id="mainDiv"]/div[1]/div[1]/div/div[1]/div/div/div/ul/li[1]/span[2]
            current_score = element.text  # Store the text content of the element in a variable

            element2 = driver.find_element(By.XPATH, '//*[@id="tab1default"]/table/tbody[1]')
            batsmen = element2.text # Store the text content of the element in a variable 

            element3 = driver.find_element(By.XPATH, '//*[@id="tab1default"]/table/tbody[2]/tr[1]')
            bowlers = element3.text # Store the text content of the element in a variable

            # Check if the score has changed
            if current_score != previous_score:
                # Print the scraped data
                # print("Current score:", current_score)

                score_elements = current_score.split('\n')
                batsmen_elements = batsmen.split('\n')
                bowler_elements = bowlers.split('\n')

                batsmen1 = batsmen_elements[0].split(' ')
                batsmen2 = batsmen_elements[1].split(' ')
                bowler = bowler_elements[0].split(' ') 


                # Updating team 1 name to use abbrevation 
                score_elements[0] = [i for i in score_elements[0] if i.isupper() ]
                score_elements[0] = ''.join(score_elements[0])
                # print(score_elements[0])

                # updating team 2 name to use abbrevation
                # score_elements[3] = "A-Team"
                score_elements[3] = [i for i in score_elements[3] if i.isupper() ]
                score_elements[3] = ''.join(score_elements[3])
                # print(score_elements[3])

                bat1={'Name': batsmen1[0], 'Runs': batsmen1[-5], 'Balls': batsmen1[-4], 'Fours': batsmen1[-3], 'Sixes': batsmen1[-2], 'StrikeRate': batsmen1[-1]}
                bat2={'Name': batsmen2[0], 'Runs': batsmen2[-5], 'Balls': batsmen2[-4], 'Fours': batsmen2[-3], 'Sixes': batsmen2[-2], 'StrikeRate': batsmen2[-1]} 
                bowl1 = {'Name': bowler[0], 'Overs': bowler[-5], 'Maidens': bowler[-4], 'Runs': bowler[-3], 'Wickets': bowler[-2], 'Economy': bowler[-1]}  
                score = {'Team1': score_elements[0], 'Score1': score_elements[1], 'Overs1': score_elements[2],
                        'Team2': score_elements[3], 'Score2': score_elements[4], 'Overs2': score_elements[5]}

                # print(score)

                ov1 = score['Overs1'].split('/')[0]
                ov2 = score['Overs2'].split('/')[0] 
                ov1 = int(ov1.split('.')[0])
                ov2 = int(ov2.split('.')[0])

                if ov1 == 20:
                    target_list = score['Score1'].split('/') 
                    target = int(target_list[0]) + 1
                    # if not popped:
                    #     team_bat.pop(0)
                    #     popped = True 
                
                elif ov2 == 20: 
                    target_list = score['Score2'].split('/') 
                    target = int(target_list[0]) + 1
                    # if not popped:
                    #     team_bat.pop(0)
                    #     popped = True 
                
                # Update the previous score
                if team_bat == score['Team1']:
                    batting_team = {'Team': score['Team1'], 'Score': score['Score1'], 'Overs': score['Overs1']}
                elif team_bat == score['Team2']:
                    batting_team = {'Team': score['Team2'], 'Score': score['Score2'], 'Overs': score['Overs2']}
                else:
                    pass
                
                print("Batting Team: ", batting_team) 

                if target == 0:
                    target_pass = '-'
                else: 
                    target_pass = str(target)

                # print("Batting Team: ", batting_team)  
        except :
            print("Error Loop Activated")
            pass

        return batting_team, bat1, bat2, bowl1, target_pass, current_score,



@app.route('/')
def index():
    global score, bat1, bat2, bowl1, target_pass 

    print(score, bat1, bat2, bowl1)  

    try: 
        try:
            score, bat1, bat2, bowl1, target_pass, current_score = get_score(url, previous_score, team_bat=team_bat, target=target)
        except:
            pass
        return render_template('index.html', score = score, bat1 = bat1, bat2 = bat2, bowl1 = bowl1, target = target_pass) 
    
    
    # except KeyboardInterrupt:
    #     try:
    #         element = driver.find_element(By.XPATH, '//*[@id="mainDiv"]/div[1]/div[1]/div/h3')
    #         # result = get_score(url, previous_score, team_bat=team_bat, target=target)
    #         print("Updated!")
    #         return render_template('subindex.html', result = element.text)
            
    except: 
        print("Error")

if __name__ == '__main__':
    app.run()
    driver.quit() # Close the browser 
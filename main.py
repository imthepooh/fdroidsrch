from bs4 import BeautifulSoup
import requests
import urllib 
import os
import telegram

# declare the bot
bot = telegram.Bot(token=os.environ['TOKEN'])
# set the base url for scrapping
url = 'https://search.f-droid.org/?lang=en&page='

def appsearch(request):
    ''' This bot will do a search on f-droid site for apps with the 
    provided search string
    '''
    if request.method == 'POST':
        fin_text = ''
        fin_list = list()
        update = telegram.Update.de_json(request.get_json(request),bot)
        chat_id = update.message.chat.id
        rec_msg = update.message.text.split(' ')
        # start handler for the bot
        if rec_msg[0] == '/start':
            res_text = 'Hello, I am a bot. \nI can search apps on f-droid based on search keyword. \nPlease check /help for details'
            bot.send_message(chat_id=chat_id,text=res_text)
        # help handler for the bot
        elif rec_msg[0] == '/help':
            res_text = 'Enter the search string as /s<space><search string> to get a list of all applications from f-droid containing the string'
            bot.send_message(chat_id=chat_id,text=res_text)
        # search handler starting with /s command 
        elif rec_msg[0] == '/s':
            # check for valid search string
            if len(rec_msg) < 2:
                res_text = 'Please enter a valid search string. Use /help for details'
                bot.send_message(chat_id=chat_id,text=res_text)
            else:
                search_app = urllib.parse.quote_plus(' '.join(rec_msg[1:]))
                i = 1
                url_set = url + str(i) + '&q=' + search_app
                s_page = requests.get(url_set)
                # fetch the search results
                soup = BeautifulSoup(s_page.content,'html.parser')
                num = 0
                # check if the search results are multipaged
                for nums in soup.find_all('span',class_='step-links'):
                    try:
                        num = int(nums.get_text())
                    except:
                        num_str = nums.get_text()
                # set the number of pages to be scrapped
                i = 1 if num == 0 else num
                for n in range(1,i+1):
                    if n > 1:
                        url_set = url + str(n) + '&q=' + search_app
                        s_page = requests.get(url_set)
                        soup = BeautifulSoup(s_page.content,'html.parser')
                    # get app name, details and url 
                    for app_h in soup.find_all('a',class_='package-header'):
                        app_url = app_h['href'].strip()
                        
                        app_n = app_h.find('h4',class_='package-name')
                        app_name = app_n.get_text().strip()

                        app_s = app_h.find('span',class_='package-summary')
                        app_sum = app_s.get_text().strip()
                        # prepare result string
                        fin_text += 'name: ' + app_name + '\n'+ 'desc: ' + app_sum+'\n'+ 'url: ' + app_url +'\n\n'
                # respond with message if no results found
                if fin_text == '':
                    res_text = 'Sorry, No results found'
                    bot.send_message(chat_id=chat_id,text=res_text)
                else:
                    fin_list = [fin_text[i:i+4096] for i in range(0,len(fin_text),4096)]
                    for text_msg in fin_list:
                        bot.send_message(chat_id=chat_id,text=text_msg)
        else:
            # handle invalid command sent to bot
            res_text = 'Invalid command, please use /help for details'
            bot.send_message(chat_id=chat_id,text=res_text)
    return f'ok'



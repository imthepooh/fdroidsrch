from bs4 import BeautifulSoup
import requests
import urllib 
import os
import telegram

bot = telegram.Bot(token=os.environ['TOKEN'])
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
        if rec_msg[0] == '/start':
            res_text = 'Hello, I am a bot. \nI can search apps on f-droid based on search keyword. \nPlease check /help for details'
            bot.send_message(chat_id=chat_id,text=res_text)
        elif rec_msg[0] == '/help':
            res_text = 'Enter the search string as /s<space><search string> to get a list of all applications from f-droid containing the string'
            bot.send_message(chat_id=chat_id,text=res_text)
        elif rec_msg[0] == '/s':
            if len(rec_msg) < 2:
                res_text = 'Please enter a valid search string. Use /help for details'
                bot.send_message(chat_id=chat_id,text=res_text)
            else:
                search_app = urllib.parse.quote_plus(' '.join(rec_msg[1:]))
                i = 1
                url_set = url + str(i) + '&q=' + search_app
                #print('log: Getting data for url: ',url_set)
                s_page = requests.get(url_set)
                soup = BeautifulSoup(s_page.content,'html.parser')
                #print('log: retrieved the page')
                num = 0
                for nums in soup.find_all('span',class_='step-links'):
                    #print('log: nums value: ', nums.get_text())
                    try:
                        num = int(nums.get_text())
                    except:
                        num_str = nums.get_text()
                #print('log: checking for page numbers')
                i = 1 if num == 0 else num
                #print(f'log: iterating for {i} times')
                for n in range(1,i+1):
                    if n > 1:
                        #print('log: fetching page: ',n)
                        url_set = url + str(n) + '&q=' + search_app
                        s_page = requests.get(url_set)
                        soup = BeautifulSoup(s_page.content,'html.parser')
                    #print('log: finding the results')
                    for app_h in soup.find_all('a',class_='package-header'):
                        # print(app_h)
                        app_url = app_h['href'].strip()
                        # print(app_url)
                        
                        app_n = app_h.find('h4',class_='package-name')
                        app_name = app_n.get_text().strip()
                        # print(app_name)

                        app_s = app_h.find('span',class_='package-summary')
                        app_sum = app_s.get_text().strip()
                        # print(app_sum)
                        fin_text += 'name: ' + app_name + '\n'+ 'desc: ' + app_sum+'\n'+ 'url: ' + app_url +'\n\n'
                        #fin_list.append(fin_text)
                #if len(fin_list) == 0:
                if fin_text == '':
                    res_text = 'Sorry, No results found'
                    bot.send_message(chat_id=chat_id,text=res_text)
                else:
                    fin_list = [fin_text[i:i+4096] for i in range(0,len(fin_text),4096)]
                    for text_msg in fin_list:
                        bot.send_message(chat_id=chat_id,text=text_msg)
        else:
            res_text = 'Invalid command, please use /help for details'
            bot.send_message(chat_id=chat_id,text=res_text)
    return f'ok'



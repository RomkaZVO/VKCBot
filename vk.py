import json
import requests
import time
import threading 
import os
 
config = {} 
with open('config.json', 'r') as f:
	config = json.load(f)
 
cmd_list = {}
with open('cmds.json', 'r') as f:
	cmd_list = json.load(f)
 
class VKCBot:
    def __init__(self):
        self.vk_url = 'https://api.vk.com/method/'
        self.token = config['token']
        self.api_ver = config['api_ver']
        self.name = config['name']
        self.userid = 0
        self.peer = 0
        self.msgid = 0
        self.msg = []
 
    def send(self,text,peer):
        msg = requests.post('{}messages.send'.format(self.vk_url), data=(('v', self.api_ver), ('random_id', '0'), ('access_token', self.token), ('peer_id', self.peer), ('message', text))).json()
        return msg
 
    def gproupid(self):
        res = requests.get('{}groups.getById?access_token={}&v={}&lp_version=3'.format(self.vk_url, self.token, self.api_ver)).json()
        groupid = res["response"][0]["id"]
        return groupid
 
    def cmds(self,cmd,peer,msgid,message):
        filename = ('plugins/{}').format(cmd_list[cmd])
        print('Вызван: '+filename+'\n')
        exec(open(filename).read()) 
 
    def get_lp(self):
        groupid = self.gproupid()
        while True:
            try:
                lp = requests.get('{}groups.getLongPollServer?access_token={}&v={}&lp_version=3&group_id={}'.format(self.vk_url, self.token, self.api_ver, groupid), timeout=30).json()
                if 'error' in lp:
                    lp = requests.get('{}}groups.getLongPollServer?access_token={}&v={}&lp_version=3&group_id={}'.format(self.vk_url, self.token, self.api_ver, groupid)).json()
                    time.sleep(6.5)
                else:
                    break
            except:
                pass
        return lp['response']
 
    def lp(self):
        data = self.get_lp()
        longpoll = requests.session()
        print('Подключено\n')
        while True:
            time.sleep(0.20)
            try:
                res = longpoll.get('{}?act=a_check'.format(data['server']), params={'key': data['key'], 'ts': data['ts'], 'wait': 30, 'mode': 2, 'version': 3}, timeout=40).json()
                data['ts'] = res['ts']
                if 'updates' in res:
                    for updates in res['updates']:
                        if updates['type'] == 'message_new':
                            peer = updates['object']['peer_id']
                            self.peer = peer
                            userid = updates['object']['from_id']
                            msgid = updates['object']['conversation_message_id']
                            message = updates['object']['text'].lower().split()
                            message_text = updates['object']['text']
                            msg = message_text[len(message[0])+len(message[1])+2:]
                            self.msg = msg
                            if message[0] in self.name and message[1] in cmd_list:
                                print('Упоминание в @id'+str(peer), message[1])
                                #threading.Thread(target=self.cmds,args=(message[1],self.peer,self.msgid,message), daemon=True).start()
                                self.cmds(message[1],self.peer,self.msgid,message)
                            elif message[0] in self.name and message[1] not in cmd_list:
                                print('Команда не найдена:',message[1])
                                self.send('Команда '+message[1]+' не найдена!', self.peer)
                            else:
                                pass
            except:
                data = self.get_lp()
 
if __name__ == '__main__':
    bot = VKCBot()
    bot.lp()
import random,time,re,requests,json,os,asyncio
from datetime import datetime,timedelta
from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes

BOT_TOKEN="8494424963:AAHTw2e_StKFPrdt9A-2U21IO7rKFAu0pqE"
ADMIN_IDS={5562144078}
URLS={"جمم":"https://raw.githubusercontent.com/AL3ATEL/TXT-bot-telegram-/refs/heads/main/sentences.txt","شرط":"https://raw.githubusercontent.com/AL3ATEL/txt-telegram-2/refs/heads/main/conditions.txt","فكك":"https://raw.githubusercontent.com/AL3ATEL/txt-telegram-3/refs/heads/main/FKK.txt","مكت":"https://raw.githubusercontent.com/AL3ATEL/txt-telegram-4/refs/heads/main/arabic_sentences.json","شكت":"https://raw.githubusercontent.com/BoulahiaAhmed/Arabic-Quotes-Dataset/main/Arabic_Quotes.csv","اكت":"https://raw.githubusercontent.com/AL3ATEL/txt-telegram-5/refs/heads/main/3amh.txt","عكس":"https://raw.githubusercontent.com/AL3ATEL/txt-telegram-3/refs/heads/main/FKK.txt"}
REPEAT_WORDS=["صمت","صوف","سين","عين","جيم","كتب","خبر","حلم","جمل","تعب","حسد","نار","برد","علي","عمر","قطر","درب","خطر","علم","صوت"]
CONDITIONS=["كرر أول كلمة","كرر ثاني كلمة","كرر آخر كلمة","كرر أول كلمة وآخر كلمة","فكك أول كلمة","فكك آخر كلمة","بدل أول كلمتين","بدل آخر كلمتين","بدل ثاني كلمة والكلمة الأخيرة"]
CHAR_MAP={'أ':'ا','إ':'ا','آ':'ا','ى':'ي','ة':'ه','ئ':'ي','ؤ':'و','ٱ':'ا','ٳ':'ا'}
NUM_WORDS={'0':'صفر','1':'واحد','2':'اثنان','3':'ثلاثة','4':'أربعة','5':'خمسة','6':'ستة','7':'سبعة','8':'ثمانية','9':'تسعة','10':'عشرة','11':'احدى عشر','12':'اثنا عشر','13':'ثلاثة عشر','14':'أربعة عشر','15':'خمسة عشر','16':'ستة عشر','17':'سبعة عشر','18':'ثمانية عشر','19':'تسعة عشر','20':'عشرون','30':'ثلاثون','40':'أربعون','50':'خمسون','60':'ستون','70':'سبعون','80':'ثمانون','90':'تسعون','100':'مائة','1000':'ألف'}

class Storage:
    def __init__(self):self.file="bot_data.json";self.data=self.load()
    def load(self):
        try:return json.load(open(self.file,'r',encoding='utf-8'))
        except:return {"users":{},"chats":{},"banned":[],"scores":{},"patterns":{},"sessions":{},"awards":{},"weekly_awards":{},"stats":{},"broadcast_mode":{},"rounds":{},"round_mode":{}}
    def save(self):json.dump(self.data,open(self.file,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    def add_user(self,uid,usr,name):
        uid_str=str(uid)
        if uid_str not in self.data["users"]:self.data["users"][uid_str]={"username":usr,"first_name":name,"created_at":datetime.now().isoformat()};self.save()
        elif self.data["users"][uid_str].get("username")!=usr or self.data["users"][uid_str].get("first_name")!=name:self.data["users"][uid_str].update({"username":usr,"first_name":name});self.save()
    def add_chat(self,cid,title):
        cid_str=str(cid)
        if cid_str not in self.data["chats"]:self.data["chats"][cid_str]={"title":title,"created_at":datetime.now().isoformat()};self.save()
    def is_banned(self,uid):return str(uid)in self.data["banned"]
    def ban_user(self,uid):self.data["banned"].append(str(uid))if str(uid)not in self.data["banned"]else None;self.data["sessions"].pop(str(uid),None);self.save()
    def unban_user(self,uid):self.data["banned"].remove(str(uid))if str(uid)in self.data["banned"]else None;self.save()
    def update_score(self,uid,typ,wpm):self.data["scores"][f"{uid}_{typ}"]=max(self.data["scores"].get(f"{uid}_{typ}",0),wpm);self.save()
    def get_score(self,uid,typ):return self.data["scores"].get(f"{uid}_{typ}",0)
    def add_pattern(self,uid,key):self.data["patterns"].setdefault(str(uid),[]).append(key)if key not in self.data["patterns"].get(str(uid),[])else None;self.save()
    def is_pattern_used(self,uid,key):return key in self.data["patterns"].get(str(uid),[])
    def clear_patterns(self,uid):self.data["patterns"][str(uid)]=[];self.save()
    def save_session(self,uid,cid,typ,txt,tm):self.data["sessions"][f"{uid}_{cid}"]={"type":typ,"text":txt,"time":tm};self.save()
    def get_session(self,uid,cid):return self.data["sessions"].get(f"{uid}_{cid}")
    def del_session(self,uid,cid):self.data["sessions"].pop(f"{uid}_{cid}",None);self.save()
    def get_leaderboard(self,typ):scores=[(k.split('_')[0],self.data["users"].get(k.split('_')[0],{}).get("username"),self.data["users"].get(k.split('_')[0],{}).get("first_name","مستخدم"),v)for k,v in self.data["scores"].items()if k.endswith(f"_{typ}")];scores.sort(key=lambda x:x[3],reverse=True);return scores[:3]
    def add_award(self,uid,name,wpm,typ):self.data["weekly_awards"].setdefault(str(uid),[]).append({"name":name,"wpm":wpm,"type":typ,"date":datetime.now().isoformat()});self.save()
    def get_awards(self,uid):return self.data["weekly_awards"].get(str(uid),[])
    def log_cmd(self,cmd):dt=datetime.now().strftime("%Y-%m-%d");self.data["stats"].setdefault(dt,{}).setdefault(cmd,0);self.data["stats"][dt][cmd]+=1;self.save()
    def set_broadcast_mode(self,uid,status):self.data["broadcast_mode"][str(uid)]=status;self.save()
    def get_broadcast_mode(self,uid):return self.data["broadcast_mode"].get(str(uid),False)
    def start_round(self,cid,target):self.data["rounds"][str(cid)]={"target":target,"wins":{},"started_at":datetime.now().isoformat()};self.save()
    def get_round(self,cid):return self.data["rounds"].get(str(cid))
    def end_round(self,cid):self.data["rounds"].pop(str(cid),None);self.save()
    def add_win(self,cid,uid):
        if str(cid)not in self.data["rounds"]:return False
        self.data["rounds"][str(cid)]["wins"].setdefault(str(uid),0);self.data["rounds"][str(cid)]["wins"][str(uid)]+=1;self.save();return self.data["rounds"][str(cid)]["wins"][str(uid)]
    def set_round_mode(self,cid,status):self.data["round_mode"][str(cid)]=status;self.save()
    def get_round_mode(self,cid):return self.data["round_mode"].get(str(cid),False)
    def cleanup(self):
        now=time.time();to_del=[k for k,v in self.data["sessions"].items()if now-v["time"]>3600];changed=bool(to_del)
        for k in to_del:del self.data["sessions"][k]
        month_ago=(datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
        for dt in list(self.data["stats"].keys()):
            if dt<month_ago:del self.data["stats"][dt];changed=True
        if changed or self.data.get("stats"):self.save()

storage=Storage()

class RemoteManager:
    def __init__(self,url,min_words=5,max_words=25,disasm=False):self.url,self.min_words,self.max_words,self.disasm,self.sentences,self.last_update=url,min_words,max_words,disasm,[],0
    def load(self):
        try:
            r=requests.get(self.url,timeout=10)
            if r.status_code==200:
                self.sentences=[clean(s)for s in(r.json()if self.url.endswith('.json')else r.text.split('\n'))if s.strip()and self.min_words<=len(clean(s).split())<=self.max_words];self.last_update=time.time()
        except:pass
    def get(self):
        if not self.sentences or time.time()-self.last_update>3600:self.load()
        return random.choice(self.sentences)if self.sentences else"لا توجد جمل حالياً"

class WikiManager:
    def __init__(self,api_url,namespace=0):self.api_url,self.namespace,self.used,self.last_fetch,self.headers=api_url,namespace,set(),0,{'User-Agent':'NKL-TypingBot/1.0'}
    def fetch(self):
        if time.time()-self.last_fetch<2:time.sleep(2-(time.time()-self.last_fetch))
        try:
            r=requests.get(self.api_url,params={'action':'query','list':'random','rnnamespace':self.namespace,'rnlimit':20,'format':'json'},headers=self.headers,timeout=10).json()
            for page in r.get('query',{}).get('random',[]):
                c=requests.get(self.api_url,params={'action':'query','pageids':page['id'],'prop':'extracts','exchars':1200,'explaintext':True,'format':'json'},headers=self.headers,timeout=10).json()
                for s in re.split(r'[.!?؟]\s+',c.get('query',{}).get('pages',{}).get(str(page['id']),{}).get('extract','')):
                    s=clean_wiki(s.strip())
                    if 8<=len(s.split())<=21 and s not in self.used:self.used.add(s);self.last_fetch=time.time();return s
        except:pass
        self.last_fetch=time.time();return"جرب مرة أخرى"

class CSVQuotesManager:
    def __init__(self,url,min_words=3,max_words=30):self.url,self.min_words,self.max_words,self.quotes,self.last_update=url,min_words,max_words,[],0
    def load(self):
        try:
            r=requests.get(self.url,timeout=10)
            if r.status_code==200:
                self.quotes=[clean(parts[0].strip('"').strip())for line in r.text.strip().split('\n')[1:]if '","'in line or','in line for parts in[line.split('","')]if len(parts)>=1 and(quote:=clean(parts[0].strip('"').strip()))and self.min_words<=len(quote.split())<=self.max_words];self.last_update=time.time()
        except:pass
    def get(self):
        if not self.quotes or time.time()-self.last_update>3600:self.load()
        return random.choice(self.quotes)if self.quotes else"لا توجد اقتباسات حالياً"

def clean(txt):
    txt=re.sub(r'[\u064B-\u065F\u0670]','',txt.replace(' ≈ ',' ').replace('≈',' '));txt=re.sub(r'\([^)]*[a-zA-Z]+[^)]*\)','',txt);txt=re.sub(r'\[[^\]]*\]','',txt);txt=re.sub(r'\([^)]*\)','',txt);txt=' '.join([w for w in txt.split()if not re.search(r'[a-zA-Z]',w)]);txt=re.sub(r'\d+',lambda m:NUM_WORDS.get(m.group(),' '.join(NUM_WORDS.get(d,d)for d in m.group())if len(m.group())>1 else m.group()),txt);txt=re.sub(r'[،,:;؛\-–—\.\!؟\?\(\)\[\]\{\}""''«»…]',' ',txt);return re.sub(r'\s+',' ',txt).strip()

def clean_wiki(txt):txt=re.sub(r'\([^)]*\)','',txt);txt=re.sub(r'\[[^\]]*\]','',txt);txt=re.sub(r'[^\u0600-\u06FF\s≈]','',txt);txt=re.sub(r'[،,:;؛\-–—\.\!؟\?\(\)\[\]\{\}""''«»…]',' ',txt);txt=re.sub(r'\d+',lambda m:NUM_WORDS.get(m.group(),' '.join(NUM_WORDS.get(d,d)for d in m.group())if len(m.group())>1 else m.group()),txt);return re.sub(r'\s+',' ',txt).strip()

def normalize(txt):return re.sub(r'\s+',' ',''.join(CHAR_MAP.get(c,c)for c in re.sub(r'[\u064B-\u065F\u0670]','',txt))).strip()
def format_display(s):return' ≈ '.join(s.split())
def match_text(orig,usr):return normalize(orig)==normalize(usr)
def disassemble_sentence(sentence):return' '.join([' '.join(list(word))for word in sentence.split()])
def is_correct_disassembly(original,user_disassembly):return normalize(user_disassembly)==normalize(disassemble_sentence(original))
def reverse_sentence(sentence):return' '.join(reversed(sentence.split()))
def is_correct_reverse(original,user_reverse):return normalize(user_reverse)==normalize(reverse_sentence(original))

def apply_condition(cond,sent):
    words=sent.split()
    if not words:return sent
    if cond=="كرر أول كلمة":return f"{words[0]} {sent}"
    elif cond=="كرر ثاني كلمة"and len(words)>=2:return f"{words[1]} {sent}"
    elif cond=="كرر آخر كلمة":return f"{sent} {words[-1]}"
    elif cond=="كرر أول كلمة وآخر كلمة":return f"{words[0]} {sent} {words[-1]}"
    elif cond=="فكك أول كلمة":return f"{' '.join(words[0])} {' '.join(words[1:])}"if len(words)>1 else' '.join(words[0])
    elif cond=="فكك آخر كلمة":return f"{' '.join(words[:-1])} {' '.join(words[-1])}"if len(words)>1 else' '.join(words[-1])
    elif cond=="بدل أول كلمتين"and len(words)>=2:words[0],words[1]=words[1],words[0];return' '.join(words)
    elif cond=="بدل آخر كلمتين"and len(words)>=2:words[-1],words[-2]=words[-2],words[-1];return' '.join(words)
    elif cond=="بدل ثاني كلمة والكلمة الأخيرة"and len(words)>=3:words[1],words[-1]=words[-1],words[1];return' '.join(words)
    return sent

def validate_condition(cond,orig,usr):return normalize(usr)==normalize(apply_condition(cond,orig)),apply_condition(cond,orig)

def validate_repeat(exp,usr):
    matches=re.findall(r'(\S+)\((\d+)\)',exp);user_words=usr.split();total=sum(int(c)for _,c in matches)
    if len(user_words)!=total:return False,f"عدد الكلمات غير صحيح. المفترض: {total}"
    idx=0
    for word,count in matches:
        for j in range(idx,idx+int(count)):
            if normalize(user_words[j])!=normalize(word):return False,f"الكلمة '{user_words[j]}' يجب أن تكون '{word}'"
        idx+=int(count)
    return True,""

def gen_pattern(uid):
    for _ in range(100):
        words=random.sample(REPEAT_WORDS,4);pattern,key_parts=[],[]
        for w in words:c=random.randint(2,4);pattern.append(f"{w}({c})");key_parts.append(f"{w}_{c}")
        key="|".join(key_parts)
        if not storage.is_pattern_used(uid,key):storage.add_pattern(uid,key);return" ".join(pattern)
    storage.clear_patterns(uid);return gen_pattern(uid)

managers={"جمم":RemoteManager(URLS["جمم"]),"شرط":RemoteManager(URLS["شرط"],3),"فكك":RemoteManager(URLS["فكك"],3),"ويكي":WikiManager("https://ar.wikipedia.org/w/api.php",0),"مكت":RemoteManager(URLS["مكت"],8),"اكت":RemoteManager(URLS["اكت"],3),"شكت":CSVQuotesManager(URLS["شكت"],5),"عكس":RemoteManager(URLS["عكس"],3)}

def is_admin(user_id):return user_id in ADMIN_IDS

async def cmd_start(u:Update,c:ContextTypes.DEFAULT_TYPE):
    uid,usr,name=u.message.from_user.id,u.message.from_user.username,u.message.from_user.first_name
    if storage.is_banned(uid):await u.message.reply_text("تم حظرك");return
    storage.add_user(uid,usr,name);await u.message.reply_text("أهلاً بك في بوت NKL\n• جمم - جمل عربية\n• ويكي - جمل Wikipedia\n• مكت - مولد الكلمات العربية\n• اكت - جمل عامية\n• شكت - اقتباسات عربية ملهمة\n• كرر - تكرار الكلمات\n• شرط - جمل بالشروط\n• فكك - فك وتركيب\n• عكس - اكتب الجملة بالعكس\n• فتح جولة - لبدء جولة منافسة\n• الصدارة - النتائج\n• جوائزي - جوائزك\n• عرض/مقالات - التعليمات")

async def cmd_leaderboard(u:Update,c:ContextTypes.DEFAULT_TYPE):
    storage.cleanup();msg="قائمة أسرع الناس\n\n"
    for typ,name in[('جمم','الجمل'),('ويكي','ويكيبيديا'),('مكت','مولد الكلمات العربية'),('اكت','الجمل العامية'),('شكت','الاقتباسات'),('كرر','التكرار'),('شرط','الشروط'),('فكك','فكك'),('عكس','العكس')]:
        lb=storage.get_leaderboard(typ)
        if lb:
            msg+=f"{name}:\n"
            for i,(uid,usr,fname,wpm)in enumerate(lb,1):storage.add_award(uid,f"المركز {i} في {name}",wpm,typ);mention=f"@{usr}"if usr else f"{fname} (لا يوجد يوزر)";msg+=f"{i}. {mention}: {wpm:.1f} WPM\n"
            msg+="\n"
    await u.message.reply_text(msg if msg!="قائمة أسرع الناس\n\n"else"لا توجد نتائج بعد!")

async def cmd_awards(u:Update,c:ContextTypes.DEFAULT_TYPE):
    uid=u.message.from_user.id;awards=storage.get_awards(uid)
    if not awards:await u.message.reply_text(f"{u.message.from_user.first_name} ما عنده جوائز أسبوعية حتى الآن");return
    msg=f"جوائز {u.message.from_user.first_name} الأسبوعية:\n\n"
    for a in awards:msg+=f"• {a['name']}\nالسرعة: {a['wpm']:.1f} WPM\n\n"
    await u.message.reply_text(msg)

async def cmd_stats(u:Update,c:ContextTypes.DEFAULT_TYPE):
    if u.message.from_user.id not in ADMIN_IDS:await u.message.reply_text("أمر للمشرفين فقط!");return
    stats={k:v for k,v in{(datetime.now()-timedelta(days=i)).strftime("%Y-%m-%d"):storage.data["stats"].get((datetime.now()-timedelta(days=i)).strftime("%Y-%m-%d"),{})for i in range(2)}.items()if v}
    if not stats:await u.message.reply_text("لا توجد إحصائيات!");return
    msg="إحصائيات الأوامر:\n\n"
    for dt in sorted(stats.keys(),reverse=True):
        dt_name=("اليوم"if dt==datetime.now().strftime("%Y-%m-%d")else"أمس"if dt==(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")else dt);msg+=f"{dt_name}:\n"
        for cmd,cnt in stats[dt].items():msg+=f" {cmd}: {cnt}\n"
        msg+=f" المجموع: {sum(stats[dt].values())}\n\n"
    await u.message.reply_text(msg)

async def broadcast_message(context:ContextTypes.DEFAULT_TYPE,message:str):
    users,chats,success,failed,banned=storage.data.get("users",{}),storage.data.get("chats",{}),0,0,set(storage.data.get("banned",[]))
    for user_id in users.keys():
        if user_id in banned:continue
        try:await context.bot.send_message(chat_id=int(user_id),text=message);success+=1;await asyncio.sleep(0.05)
        except Exception as e:failed+=1
    for chat_id in chats.keys():
        try:await context.bot.send_message(chat_id=int(chat_id),text=message);success+=1;await asyncio.sleep(0.05)
        except Exception as e:failed+=1
    return success,failed

def arabic_to_num(text):
    ar_nums={'صفر':0,'واحد':1,'اثنان':2,'اثنين':2,'ثلاثة':3,'ثلاث':3,'أربعة':4,'أربع':4,'خمسة':5,'خمس':5,'ستة':6,'ست':6,'سبعة':7,'سبع':7,'ثمانية':8,'ثماني':8,'تسعة':9,'تسع':9,'عشرة':10,'عشر':10,'احدى عشر':11,'احدى عشرة':11,'اثنا عشر':12,'اثنتا عشرة':12,'ثلاثة عشر':13,'ثلاث عشرة':13,'أربعة عشر':14,'أربع عشرة':14,'خمسة عشر':15,'خمس عشرة':15,'ستة عشر':16,'ست عشرة':16,'سبعة عشر':17,'سبع عشرة':17,'ثمانية عشر':18,'ثماني عشرة':18,'تسعة عشر':19,'تسع عشرة':19,'عشرون':20,'ثلاثون':30,'أربعون':40,'خمسون':50,'ستون':60,'سبعون':70,'ثمانون':80,'تسعون':90,'مائة':100,'مئة':100}
    try:return ar_nums.get(text.strip().lower(),int(text))
    except:return None

async def check_win(u,uid,usr,name,cid,wpm,typ):
    round_data=storage.get_round(cid)
    if round_data:
        wins=storage.add_win(cid,uid);target=round_data['target'];mention=f"@{usr}"if usr else name
        if wins>=target:storage.end_round(cid);await u.message.reply_text(f"🏆🎉 مبروك {mention}!\n\nفزت في الجولة بـ {wins} فوز من أصل {target}!\n⚡ سرعتك: {wpm:.2f} WPM\n\nتهانينا يا بطل! 🎊")
        else:await u.message.reply_text(f"✅ ممتاز! سرعتك {wpm:.2f} WPM\n\n🎯 فوزك رقم {wins} من {target}")
    else:await u.message.reply_text(f"ممتاز! سرعتك {wpm:.2f} WPM"if typ not in['فكك','عكس']else f"ممتاز! {'فككت'if typ=='فكك'else'عكست'} الجملة بشكل صحيح\nسرعتك: {wpm:.2f} WPM")

async def handle_msg(u:Update,c:ContextTypes.DEFAULT_TYPE):
    uid,cid,name,text,usr=u.message.from_user.id,u.message.chat.id,u.message.from_user.first_name,u.message.text.strip(),u.message.from_user.username
    if cid<0:storage.add_chat(cid,u.message.chat.title if u.message.chat.title else"مجموعة")
    else:storage.add_user(uid,usr,name)
    if storage.get_broadcast_mode(uid):
        if text=="إلغاء":storage.set_broadcast_mode(uid,False);await u.message.reply_text("تم إلغاء وضع الإذاعة");return
        await u.message.reply_text("جاري إرسال الإذاعة... الرجاء الانتظار");success,failed=await broadcast_message(c,text);storage.set_broadcast_mode(uid,False);await u.message.reply_text(f"✅ تم إرسال الإذاعة بنجاح!\n\n📊 التفاصيل:\n• تم الإرسال لـ {success} مستخدم/مجموعة\n• فشل الإرسال لـ {failed} مستخدم/مجموعة");return
    if u.message.reply_to_message and is_admin(uid)and text=='حظر':target_user=u.message.reply_to_message.from_user;storage.ban_user(target_user.id);await u.message.reply_text(f"تم حظر {target_user.first_name} (ID: {target_user.id})");return
    if u.message.reply_to_message and is_admin(uid)and text=='فك حظر':target_user=u.message.reply_to_message.from_user;storage.unban_user(target_user.id);await u.message.reply_text(f"تم فك حظر {target_user.first_name} (ID: {target_user.id})");return
    if is_admin(uid)and text.startswith('حظر '):
        try:target_id=int(text.split()[1]);storage.ban_user(target_id);await u.message.reply_text(f"تم حظر المستخدم (ID: {target_id})");return
        except:await u.message.reply_text("استخدم: حظر [user_id]");return
    if is_admin(uid)and text.startswith('فك حظر '):
        try:
            parts=text.split(maxsplit=2)
            if len(parts)<3:await u.message.reply_text("استخدم: فك حظر [user_id]");return
            target_id=int(parts[2]);storage.unban_user(target_id);await u.message.reply_text(f"تم فك حظر المستخدم (ID: {target_id})");return
        except:await u.message.reply_text("استخدم: فك حظر [user_id]");return
    if is_admin(uid)and text in['اذاعة','إذاعة']:storage.set_broadcast_mode(uid,True);await u.message.reply_text("📢 وضع الإذاعة\n\nارسل الرسالة التي تريد إذاعتها الآن لجميع المستخدمين والمجموعات\n\nأو اكتب 'إلغاء' للإلغاء");return
    if storage.is_banned(uid):await u.message.reply_text("تم حظرك");return
    if storage.get_round_mode(cid):
        target_num=arabic_to_num(text)
        if target_num and target_num>0 and target_num<=100:storage.start_round(cid,target_num);storage.set_round_mode(cid,False);await u.message.reply_text(f"🎮 تم فتح جولة جديدة من {target_num} فوز!\n\nابدأوا اللعب الآن والفائز الأول من يصل لـ {target_num} فوز سيتم الإعلان عنه 🏆");return
        else:await u.message.reply_text("⚠️ الرجاء إدخال رقم صحيح من 1 إلى 100\n\nمثال: 5 أو خمسة");return
    if text in['فتح جولة','فتح جوله']:storage.set_round_mode(cid,True);await u.message.reply_text("🎯 تبي الجولة من كم؟\n\nأدخل عدد الفوزات المطلوبة (مثال: 5 أو خمسة)");return
    if text in['إنهاء الجولة','انهاء الجولة','إنهاء جولة','انهاء جوله']:
        round_data=storage.get_round(cid)
        if round_data:storage.end_round(cid);await u.message.reply_text("✅ تم إنهاء الجولة")
        else:await u.message.reply_text("❌ لا توجد جولة نشطة حالياً")
        return
    if text in['جمم','ويكي','مكت','اكت','شكت','كرر','شرط','فكك','عكس','الصدارة','جوائزي','عرض','مقالات','احصاء']:storage.log_cmd(text)
    if text=='جمم':t=managers["جمم"].get();storage.save_session(uid,cid,'جمم',t,time.time());await u.message.reply_text(format_display(t));return
    elif text=='ويكي':t=managers["ويكي"].fetch();storage.save_session(uid,cid,'ويكي',t,time.time());await u.message.reply_text(format_display(t));return
    elif text=='مكت':t=managers["مكت"].get();storage.save_session(uid,cid,'مكت',t,time.time());await u.message.reply_text(format_display(t));return
    elif text=='اكت':t=managers["اكت"].get();storage.save_session(uid,cid,'اكت',t,time.time());await u.message.reply_text(format_display(t));return
    elif text=='شكت':t=managers["شكت"].get();storage.save_session(uid,cid,'شكت',t,time.time());await u.message.reply_text(format_display(t));return
    elif text=='كرر':p=gen_pattern(uid);storage.save_session(uid,cid,'كرر',p,time.time());await u.message.reply_text(p);return
    elif text=='شرط':s,cond=managers["شرط"].get(),random.choice(CONDITIONS);storage.save_session(uid,cid,'شرط',f"{s}||{cond}",time.time());await u.message.reply_text(f"{cond}\n\n{format_display(s)}");return
    elif text=='فكك':s=managers["فكك"].get();storage.save_session(uid,cid,'فكك_تفكيك',s,time.time());await u.message.reply_text(f"فكك الجملة التالية (افصل بين حروف كل كلمة):\n\n{format_display(s)}");return
    elif text=='عكس':s=managers["عكس"].get();storage.save_session(uid,cid,'عكس',s,time.time());await u.message.reply_text(format_display(s));return
    elif text=='الصدارة':await cmd_leaderboard(u,c);return
    elif text=='جوائزي':await cmd_awards(u,c);return
    elif text=='احصاء':await cmd_stats(u,c);return
    elif text in['عرض','مقالات']:await cmd_start(u,c);return
    session=storage.get_session(uid,cid)
    if not session:return
    typ,orig,tm=session["type"],session["text"],session["time"];elapsed=time.time()-tm
    if typ in['جمم','ويكي','مكت','اكت','شكت']and match_text(orig,text):wpm=(len(orig.split())/elapsed)*60;storage.update_score(uid,typ,wpm);await check_win(u,uid,usr,name,cid,wpm,typ);storage.del_session(uid,cid)
    elif typ=='كرر':
        valid,err=validate_repeat(orig,text)
        if valid:wpm=(len(text.split())/elapsed)*60;storage.update_score(uid,'كرر',wpm);await check_win(u,uid,usr,name,cid,wpm,'كرر');storage.del_session(uid,cid)
    elif typ=='شرط':
        orig_s,cond=orig.split('||');valid,exp=validate_condition(cond,orig_s,text)
        if valid:wpm=(len(text.split())/elapsed)*60;storage.update_score(uid,'شرط',wpm);await check_win(u,uid,usr,name,cid,wpm,'شرط');storage.del_session(uid,cid)
    elif typ=='فكك_تفكيك':
        if is_correct_disassembly(orig,text):wpm=(len(text.split())/elapsed)*60;storage.update_score(uid,'فكك',wpm);await check_win(u,uid,usr,name,cid,wpm,'فكك');storage.del_session(uid,cid)
    elif typ=='عكس':
        if is_correct_reverse(orig,text):wpm=(len(text.split())/elapsed)*60;storage.update_score(uid,'عكس',wpm);await check_win(u,uid,usr,name,cid,wpm,'عكس');storage.del_session(uid,cid)
    if elapsed>60:storage.del_session(uid,cid)

def main():
    if not BOT_TOKEN:print("خطأ: لم يتم العثور على BOT_TOKEN في متغيرات البيئة!\nالرجاء إضافة متغير البيئة BOT_TOKEN من خلال Secrets في Replit");return
    app=Application.builder().token(BOT_TOKEN).build();app.add_handler(CommandHandler('start',cmd_start));app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,handle_msg));print("✅ البوت يعمل الآن!\n📊 استخدم /start للبدء");app.run_polling()

if __name__=='__main__':main()

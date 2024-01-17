from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import os
import webbrowser
import speech_recognition
import openai
import requests
import re
import wave
import time
import winsound
from pyowm.utils.config import get_default_config
import dnevnikmos

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = str(OUTPUT_PATH) + "\\build\\assets\\frame0"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


target_path = str(Path(__file__).parent) + '\\media'

dnevnik_login = ""
dnevnik_password = ""
DRIVER_PATH = str(Path(__file__).parent) + "\\chromedriver_win32\\chromedriver.exe"


openai.organization = ""
openai.api_key = ""




def record_and_recognize_audio(*args: tuple):
    with microphone:
        recognized_data = ""

        # регулирование уровня окружающего шума
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        try:
            play_voice_assistant_speech("Я слушаю вас")
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            play_voice_assistant_speech("Не удалось обнаружить микрофон.")
            return
        try:
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()

        except speech_recognition.UnknownValueError:
            pass
        except speech_recognition.RequestError:
            play_voice_assistant_speech("Нет подключения к интернету.")

        return recognized_data
    

def synthesize(folder_id, apikey, text):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': 'Api-Key ' + apikey,
    }

    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': 'jane',
        'folderId': folder_id,
        'format': 'lpcm',
        'sampleRateHertz': 48000,
    }

    with requests.post(url, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

        for chunk in resp.iter_content(chunk_size=None):
            yield chunk


def convert(filename):
    with open(target_path + '\\a.raw', "rb") as inp_f:
        data = inp_f.read()
        with wave.open(target_path + '\\a.wav', "wb") as out_f:
            out_f.setnchannels(1)
            out_f.setsampwidth(2) # number of bytes
            out_f.setframerate(44100)
            out_f.writeframesraw(data)
    """
    cmd = " ".join([
        "sox -r 48000 -b 16 -e signed-integer -c 1",
        target_path + '\\' + filename + ".raw",
        target_path + '\\' + filename + ".wav",
        ])
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
    """


def play_voice_assistant_speech(text_to_speech):
    filename = r'a'
    with open(target_path + '\\' + filename + ".raw", "wb") as f:
        for audio_content in synthesize("", "", text_to_speech):
            f.write(audio_content)
        
    convert(filename)
    time.sleep(0.5)
    winsound.PlaySound(target_path + '\\' + filename + '.wav', winsound.SND_NODEFAULT)


def execute_command_with_name(user_request):
    ma = 0
    sh = 0
    cc = 0
    rm = 0
    am = 0
    wr = 0
    dn = 0
    mk = 0
    ls = 0
    hk = 0
    mh = 0
    global func_argument
    list_user_request = user_request.split(' ')
    for i in range(len(list_user_request)):
        list_user_request[i] = list_user_request[i].replace(',', '')
        list_user_request[i] = list_user_request[i].replace('!', '')
        list_user_request[i] = list_user_request[i].replace('.', '')
        list_user_request[i] = list_user_request[i].replace('?', '')
    func_argument = list_user_request
    if list_user_request[0] in b['qs']:
        sh += 1
        func_argument.pop(0)
    for i in a:
        for j in list_user_request:
            if j in a[i]:
                func_argument.remove(j)
                if j in a['media']:
                    ma += 1
                if j in a['search']:
                    sh += 1
                if j in a['rem']:
                    rm += 1
                if j in a['am']:
                    am += 1
                if j in a['wr']:
                    wr += 1
                if j in a['dn']:
                    dn += 1
                if j in a['mh']:
                    mh += 1
    if ma == am and ma != 0 and am != 0:
        ma += 1
    if ma == 0 and sh == 0 and cc == 0 and rm == 0 and am == 0 and wr == 0:
        sh += 1
    if sh == dn and sh != 0 and dn != 0:
        dn += 1
    if sh == mh and sh != 0 and mh != 0:
        mh += 1
    var = {ma: 'ma', sh: 'sh', cc: 'cc', rm: 'rm', am: 'am', wr: 'wr', dn: 'dn', mh: 'mh'}
    if var.get(max(var)) == 'dn':
        for i in list_user_request:
            for j in dnevnik_dict:
                if i in dnevnik_dict[j]:
                    if i in dnevnik_dict['mark']:
                        mk += 1
                    if i in dnevnik_dict['lessons']:
                        ls += 1
                    if i in dnevnik_dict['homework']:
                        hk += 1
        var_d = {mk: 'mk', ls: 'ls', hk: 'hk'}
        return var_d.get(max(var_d))
    return var.get(max(var))


def search_for_video_on_youtube(func_argument):
    search_term = " ".join(func_argument)
    url = "https://www.youtube.com/results?search_query=" + search_term
    webbrowser.get().open(url)


def talk_to_me(func_argument):
    promt = func_argument
    response = openai.Completion.create(engine="text-davinci-003", prompt=promt, max_tokens=1200)
    response_text = response["choices"][0]['text']
    response_text = re.sub("^\s+|\n|\r|\s+$", '', response_text)
    play_voice_assistant_speech(response_text)


def help_with_theme(func_argument):
    for i in range(len(func_argument)):
        try:
            if func_argument[i] in prepositions:
                func_argument.pop(i)
        except IndexError:
            pass
    search_term = "%20".join(func_argument)
    webbrowser.open(f"https://uchebnik.mos.ru/catalogue?search={search_term}&by_tags=рэш")


def set_alarm(func_argument):
    def validate_time(alarm_time):
        if len(alarm_time) != 6:
            return "Неверный формат, попробуйте снова"
        else:
            if int(alarm_time[0:1]) > 23:
                return "Неверный формат часов, попробуйте снова"
            else:
                return "ok"


        
    for i in range(len(prepositions)):
        try:
            func_argument.remove(prepositions[i])
        except ValueError:
            pass
    try:
            func_argument.remove('часов')
    except ValueError:
        pass
    try:
            func_argument.remove('часа')
    except ValueError:
        pass
    try:
        func_argument.remove('часу')
    except ValueError:
        pass
    try:
        func_argument.remove('часам')
    except ValueError:
        pass
    if 'утра' in func_argument:
        func_argument.remove('утра')
        for i in trn:
            if func_argument[0] == i:
                func_argument.append(trn[i])
                func_argument.pop(0)
        if len(func_argument[0]) < 2:
            alarm_time = f'0{func_argument[0]}0000'
        else:
            alarm_time = f'{func_argument[0]}0000'
        validate = validate_time(alarm_time)
        if validate != "ok":
            print(validate)
        else:
            print(f"Будильник установлен на время {alarm_time}...")

    global alarm_hour
    global alarm_min
    global alarm_sec
    alarm_hour = int(alarm_time[0:2])
    alarm_min = int(alarm_time[2:4])
    alarm_sec = int(alarm_time[4:6])

    global al_w 
    al_w = True
    

def separate_dnevnik_command(user_request, data):
    list_user_request = user_request
    for i in time_for_dnevnik:
        if i in list_user_request:
            list_user_request.insert((list_user_request.index(i)+1), time_for_dnevnik[i])
            list_user_request.pop(list_user_request.index(i))
    for i in dnevnik_dict[data]:
        if i in list_user_request:
            list_user_request.remove(i)
    for i in prepositions:
        if i in list_user_request:
            list_user_request.remove(i)
    for i in b['qs']:
        if i in list_user_request:
            list_user_request.remove(i)
    for i in pronouns:
        if i in list_user_request:
            list_user_request.remove(i)
    return list_user_request


def conclusion_marks(user_request):
    a = f""
    subject_m = ''
    command_for_d = user_request.split(' ')
    for i in time_for_dnevnik:
        if i[0] in command_for_d or i[1] in command_for_d:
            day = i[0]
            day_of_m = time_for_dnevnik[i]
    marks_data = separate_dnevnik_command(command_for_d, 'mark')
    for i in tm:
        for j in marks_data:
            if i == j:
                month_for_concl = i
                marks_data.insert((marks_data.index(j)+1), tm[i])
                marks_data.pop(marks_data.index(j))
                month_of_m = marks_data[marks_data.index(tm[i])]
                break
    for i in subject:
        for j in marks_data:    
            if j in subject[i]:
                marks_data.insert((marks_data.index(j)+1), i)
                marks_data.pop(marks_data.index(j))
                subject_m = marks_data[marks_data.index(i)]
                break
    for i in marks_data:
        if i in lang:
            marks_data.remove(i)
    marks_data.sort()
    try:
        user = dnevnikmos.User(token=Token)
        marks = dnevnikmos.Marks(user=user)
        marks_data.remove(month_of_m)
        try:
            marks_data.remove(subject_m)
        except Exception:
            pass
        date = dnevnikmos.User.get_date_in_format(user, year='2023', month=month_of_m, day=day_of_m)
        k = dnevnikmos.Marks.get_marks_by_data(marks, date=date)
        if subject_m == '':
            for i in range(len(k)):
                if a == '':
                    a = a = f"{k[i]['name']}: {k[i]['mark']}"
                else:
                    a = f"{a}; {k[i]['name']}: {k[i]['mark']}"
            play_voice_assistant_speech(f"За {day} {month_for_concl} вы получили оценки по следующим предметам: {a}")
        else:
            for i in range(len(k)):
                if k[i]['name'] == subject_m:
                    if len(k[i]['mark']) == 1:
                        play_voice_assistant_speech(f"За {day} {month_for_concl} вы получили оценку {k[i]['mark']}")
    except Exception:
        play_voice_assistant_speech('За этот период времени у вас нет оценок по выбранному предмету')


def conclusion_homework(user_request):
    a = f""
    subject_m = ''
    command_for_d = user_request.split(' ')
    for i in time_for_dnevnik:
        if i[0] in command_for_d or i[1] in command_for_d:
            day = i[0]
            day_of_m = time_for_dnevnik[i]

    homeworks_data = separate_dnevnik_command(command_for_d, 'homework')
    for i in tm:
        for j in homeworks_data:
            if i == j:
                month_for_concl = i
                homeworks_data.insert((homeworks_data.index(j)+1), tm[i])
                homeworks_data.pop(homeworks_data.index(j))
                month_of_m = homeworks_data[homeworks_data.index(tm[i])]
                break
    for i in subject:
        for j in homeworks_data:    
            if j in subject[i]:
                homeworks_data.insert((homeworks_data.index(j)+1), i)
                homeworks_data.pop(homeworks_data.index(j))
                subject_for_conc = j
                subject_m = homeworks_data[homeworks_data.index(i)]
                break
    for i in homeworks_data:
        if i in lang:
            homeworks_data.remove(i)
    homeworks_data.sort()
    try:
        user = dnevnikmos.User(token=Token)
        homework = dnevnikmos.Marks(user=user)
        homeworks_data.remove(month_of_m)
        try:
            homeworks_data.remove(subject_m)
        except Exception:
            pass
        date = dnevnikmos.User.get_date_in_format(user, year='2023', month=month_of_m, day=day_of_m)
        k = dnevnikmos.Homeworks.get_homeworks_by_data(homework, date=date)
        if subject_m == '':
            for i in range(len(k)):
                if a == '':
                    a = a = f"{k[i]['name']}: {k[i]['homework']}"
                else:
                    a = f"{a}; {k[i]['name']}: {k[i]['homework']}"
            play_voice_assistant_speech(f"На {day} {month_for_concl} вам задано: {a}")
        else:
            for i in range(len(k)):
                if subject_m in k[i]['name']:
                    play_voice_assistant_speech(f"На {day} {month_for_concl} по {subject_for_conc} вам надо сделать {k[i]['homework']}")
    except Exception:
        play_voice_assistant_speech('На этот день вам ничего не задано')

if __name__ == "__main__":
    trn = {
        'один': '1',
        'два': '2',
        'три': '3',
        'четыре': '4',
        'пять': '5',
        'шесть': '6',
        'семь': '7',
        'восемь': '8',
        'девять': '9',
        'десять': '10',
        'одиндцать': '11',
        'двенадцать': '12',
        'тринадцать': '13',
        'четырнадцать': '14',
        'пятнадцать': '15',
        'шестнадцать': '16',
        'семнадцать': '17',
        'восемнадцать': '18',
        'девятнадцать': '19',
        'двадцать': '20',
        'двадцать один': '21',
        'двадцать два': '22',
        'двадцать три': '23',
        'двадцать четыре': '24',
    }
    tm = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05', 
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12',
    }
    time_for_dnevnik = {
        ('первое', '1'): '01',
        ('второе', '2'): '02',
        ('третье', '3'): '03',
        ('четвертое', '4'): '04',
        ('пятое', '5'): '05',
        ('шестое', '6'): '06',
        ('седьмое', '7'): '07',
        ('восьмое', '8'): '08',
        ('девятое', '9'): '09',
        ('десятое', '10'): '10',
        ('одинадцатое', '11'): '11',
        ('двенадцатое', '12'): '12',
        ('тринадцатое', '13'): '13',
        ('четырнадцатое', '14'): '14',
        ('пятнадцатое', '15'): '15',
        ('шестнадцатое', '16'): '16',
        ('семнадцатое', '17'): '17',
        ('восемнадцатое', '18'): '18',
        ('девятнадцатое', '19'): '19',
        ('двадцатое', '20'): '20',
        ('двадцать первое', '21'): '21',
        ('двадцать второе', '22'): '22',
        ('двадцать третье', '23'): '23',
        ('двадцать четвертое', '24'): '24',
        ('двадцать пятое', '25'): '25',
        ('двадцать шестое', '26'): '26',
        ('двадцать седьмое', '27'): '27',
        ('двадцать восьмое', '28'): '28',
        ('двадцать девятое', '29'): '29',
        ('тридцатое', '30'): '30',
        ('тридцать перовое', '31'): '31',
    }
    
    greetings = ["hello", "hi", "morning", "привет", "здравствуй", "мое почтение", "добрый день"]
    farewell = ["bye", "goodbye", "quit", "exit", "stop", "пока", "до встречи", "увидимся", "прощайте", "до связи"]

    prepositions = ["без", "близ", "в", "вместо", "вне", "для", "до", "за", "из", "из-за", "из-под", "к", "кроме", "между", 
    "на", "над", "о", "перед", "по", "под", "при", "про", "ради", "с", "сквозь", "среди", "у", "через", "пред"]

    a = {
        'media': ('включи', 'поставь', 'покажи'),
        'search': ('расскажи', 'определение', 'принцип действия'),
        'rem': ('напомни', 'установи', 'напоминание'),
        'am': ('разбуди', 'поставь', 'будильник', 'установи'),
        'wr': ('погода', 'прогноз', 'погоды'),
        'dn': ('оценки', 'расписание', 'домашнее задание', 'задано', 'домашняя работа', 'уроки', 'делать', 'задали', 'домашка'),
        'mh': ('презентация', 'презентацию', 'теме', 'тему', 'найди', 'покажи', 'поставь')
    }
    b = {
        'qs': ('что', 'как', 'почему', 'где', 'зачем', 'какой', 'каков', 'когда', 'который', 'кто', 'куда', 'откуда', 'сколько', 'чей', 'какие')
    }

    pronouns = ["я", "ты", "он", "она", "оно", "мы", "вы", "они"]



    subject = {
        'Биология': ('биологию', 'биологии', 'биологией'),
        'Алгебра': ('алгебру', 'алгебре', 'алгеброй'),
        'Русский язык': ('русского', 'русскому', 'русский', 'русским'),
        'Геометрия': ('геометрию', 'геометрии', 'геометрией'),
        'Информатика': ('информатику', 'информатике', 'информатикой'),
        'Английский язык': ('английского', 'английскому', 'английский', 'английским'),
        'История': ('историю', 'истории', 'историей'),
        'Обществознание': ('обществознание', 'обществознанию', 'обществознанием'),
        'Физика': ('физику', 'физике', 'физикой'),
        'Химия': ('химию', 'химии', 'химией')
    }
    lang = ['язык', 'языка', 'языку', 'языком']

    dnevnik_dict = {
        'mark': ('оценка', 'оценки', 'получил'),
        'lessons': ('расписание', 'график'),
        'homework': ('домашняя', 'работа', 'уроки', 'делать', 'задали', 'домашка')
    }

    Token = ""
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()
    al_w = False


def __main__():
    global dnevnik_login
    global dnevnik_password
    global Token
    global DRIVER_PATH
    if dnevnik_login == "":
        dnevnik_login = entry_1.get()
    if dnevnik_password == "":
        dnevnik_password = entry_2.get()
    if Token == "" and dnevnik_login != "" and dnevnik_password != "":
        Token = dnevnikmos.UserToken.get_token(login=dnevnik_login, password=dnevnik_password, executable_path=DRIVER_PATH)
    try:
        os.remove(str(Path(__file__).parent) + '\\media' + '\\a.waw')
        os.remove(str(Path(__file__).parent) + '\\media' + '\\a.raw')
    except FileNotFoundError:
        pass
    voice_input = record_and_recognize_audio()
    try:
        os.remove(str(Path(__file__).parent) + '\\media' + '\\a.waw')
        os.remove(str(Path(__file__).parent) + '\\media' + '\\a.raw')
    except FileNotFoundError:
        pass
    os.remove("microphone-results.wav")
    user_request = voice_input.lower()
    if user_request == '':
        pass
    else:
        command = execute_command_with_name(user_request)
        if command == 'am':
            set_alarm(func_argument)
        elif command == 'ma':
            search_for_video_on_youtube(func_argument)
        elif command == 'sh':
            talk_to_me(user_request)
        elif command == 'mk':
            conclusion_marks(user_request)
        elif command == 'hk':
            conclusion_homework(user_request)
        elif command == 'mh':
            help_with_theme(func_argument)


window = Tk()

window.geometry("1280x800")
window.configure(bg = "#291F38")


canvas = Canvas(
    window,
    bg = "#291F38",
    height = 800,
    width = 1280,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: __main__(),
   relief="flat"
)
button_1.place(
    x=471.0,
    y=436.0,
    width=338.0,
    height=311.01123046875
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    640.0,
    131.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=225.0,
    y=91.0,
    width=830.0,
    height=79.0
)

canvas.create_text(
    230.0,
    28.0,
    anchor="nw",
    text="Логин от дневника",
    fill="#FFFFFF",
    font=("Inter Regular", 30 * -1)
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    640.0,
    304.0,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(
    x=225.0,
    y=264.0,
    width=830.0,
    height=78.0
)

canvas.create_text(
    230.0,
    200.0,
    anchor="nw",
    text="Пароль от дневника\n",
    fill="#FFFFFF",
    font=("Inter Regular", 30 * -1)
)
window.resizable(False, False)
window.mainloop()
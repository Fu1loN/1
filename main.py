import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import VkUpload
import random
import requests
import sqlite3
import json
from PIL import Image
import os


def make_commands():
    d = {}
    for i in [1, '1', 'пятнашки', '15', 15]:
        d[i] = 1

    for i in [2, '2', 'угадать страну на карте']:
        d[i] = 2
    for i in [3, '3', 'угадать страну по флагу']:
        d[i] = 3

    return d


def send_message(vk, id, messege='', attachment=None):
    if attachment is None:
        vk.messages.send(user_id=id, message=messege, random_id=random.randint(0, 2 ** 64))
    else:
        vk.messages.send(user_id=id, message=messege, random_id=random.randint(0, 2 ** 64),
                         attachment=attachment)


def make_attacment(image):
    upload_image = upload.photo_messages(photos=image)[0]
    attachments = 'photo{}_{}'.format(upload_image['owner_id'], upload_image['id'])

    return attachments


def mes_info(event):
    d = {}
    id = event.obj.message['from_id']
    text = event.obj.message['text'].lower()
    return (id, text)


def start_first(vk, id):
    send_message(vk, id, messege=ruls1)
    c = make_15()
    im = 'images/staticimgs/1/' + random.choice(os.listdir('images/staticimgs/1/'))
    img = Image.open(im)
    img = crimg(img, c)
    z = 'images/usersimgs/{}.jpg'.format(id)
    img.save(z)
    ab = '''UPDATE users SET game=1, img=\'{}\' WHERE id={}'''.format(im, id)
    cur = con.cursor()
    cur.execute(ab)
    con.commit()
    dump = {
        'arr': c,
        'game': 1,
        'hod': 0
    }

    with open(f'jsons/{id}.json', 'w', encoding='utf8') as f:
        json.dump(dump, f)
    send_message(vk, id, attachment=make_attacment(z))


def crimg(img, c) -> Image:
    x, y = img.size
    net = img.load()
    img2 = Image.new('RGB', (x, y), (255, 255, 255))
    net2 = img2.load()
    for n in range(4):
        for m in range(4):
            num = c[n][m]
            if num is None:
                continue
            a, b = num // 4, num % 4 - 1
            if b == -1:
                b = 3
                a -= 1
            xc1 = x // 4 * b
            yc1 = y // 4 * a
            xc2 = x // 4 * (b + 1)
            yc2 = y // 4 * (a + 1)
            # print(xc1, xc2, yc1, yc2, num, (m * x // 4, n * x // 4))
            imgt = img.crop((xc1 + 2, yc1 + 2, xc2 - 2, yc2 - 2))
            img2.paste(imgt, (m * x // 4, n * y // 4))

    return img2


def continue_first(vk, id, mess):
    if mess in ['заново', 'restart']:
        start_first(vk, id)
        return


    ab = """Select * from users Where id={}""".format(id)
    cur = con.cursor()
    ans = cur.execute(ab).fetchall()
    print(ans)
    p = ans[0]
    q, games, game, ball, img, js = p
    with open('jsons/' + js, encoding='utf8') as f:
        d = json.load(f)
    c = d["arr"]
    print(*c, sep='\n')
    flag = False
    for i in range(4):
        if flag:
            break
        for j in range(4):
            if c[i][j] is None:
                x = i
                y = j
                flag = True
                break
    try:

        for i in mess.split():

            num = int(i)

            if 0 >= num or num > 16:
                raise ValueError

            a, b = num // 4, num % 4 - 1
            if b == -1:
                b = 3
                a -= 1
            flag = False
            print('gere', a, b, x, y)
            for ap, bp in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                if a + ap == x and b + bp == y:
                    flag = True

                    break

            if not flag:
                raise ValueError

            c[a][b], c[x][y] = c[x][y], c[a][b]
            x, y = a, b


    except:
        send_message(vk, id, messege='Ошибка ввода')
        z = 'images/usersimgs/{}.jpg'.format(id)
        send_message(vk, id, attachment=make_attacment(z))
        return
    img = crimg(Image.open(img), c)
    z = 'images/usersimgs/{}.jpg'.format(id)
    img.save(z)
    send_message(vk, id, attachment=make_attacment(z))
    d["arr"] = c
    d["hod"] += 1
    print(d["arr"])
    if c == C:
        hods = d["hod"]
        bal = max((100 - hods) // 5, 1)

        games += 1
        ball += bal
        game = 0
        ab = """Update users set games={}, game={}, ball={} where id={}""".format(games, game, ball, id)
        cur.execute(ab).fetchall()
        con.commit()
        send_message(vk, id, messege=f'Вы закончили игру за {hods} ходов(а) и набрали {bal} баллов(а)')
    else:
        with open('jsons/' + js, 'w', encoding='utf8') as f:
            json.dump(d, f)


def make_15():
    c = [[i * 4 + j for j in range(1, 5)] for i in range(4)]
    x, y = 3, 3
    c[x][y] = None
    for i in range(200):
        d = []
        for a, b in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
            if 0 <= x + a < 4 and 0 <= y + b < 4:
                d.append((a, b))
        a, b = random.choice(d)
        a += x
        b += y
        c[x][y], c[a][b] = c[a][b], c[x][y]
        x, y = a, b
    # print(*c, sep='\n')
    return c


def new_user(id):
    ab = '''SELECT * from users WHERE id={}'''.format(id)
    cur = con.cursor()
    z = cur.execute(ab).fetchall()
    if z:
        return False
    else:
        return True


def create_user(vk, id):
    user = User(id)
    user.ins(con)
    send_message(vk, id, messege=welcom)


def get_game(id):
    # return 0
    cur = con.cursor()
    ab = '''select * from users where id={}'''.format(id)
    z = cur.execute(ab).fetchall()
    return z[0][2]


def start(vk, id, mess):
    if command[mess] == 1:
        start_first(vk, id)

    elif command[mess] == 2:
        start_second(vk, id)
    elif command[mess] == 3:
        start_fird(vk, id)


def start_second(vk, id):
    send_message(vk, id, messege=ruls2)
    with open('jsons/contr.json', encoding='utf8') as f:
        d = json.load(f)
    c = d["arr"]
    contr = random.choice(c)
    with open(f'jsons/{id}.json', encoding='utf8') as f:
        d = json.load(f)
    map_request = "https://static-maps.yandex.ru/1.x/?ll={}%2C{}&spn=10,10&l=sat&pt={},{}".format(*contr["cords"],
                                                                                                  *contr["cords"])
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
    map_file = f"images/usersimgs/{id}.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    b = [i["name"] for i in c]
    z = []
    b.pop(b.index(contr["name"]))
    for i in range(3):
        z.append(random.choice(b))
        b.pop(b.index(z[i]))
    z.append(contr["name"])
    random.shuffle(z)
    send_message(vk, id, messege="Какая страна изображенна?", attachment=make_attacment(map_file))
    ab = ''
    for i in range(4):
        ab += f'{i + 1}.{z[i]}\n'
    send_message(vk, id, messege=ab)

    dump = {
        'arr': z,
        'game': 2,
        'bal': 4,
        'name': contr["name"]
    }

    with open(f'jsons/{id}.json', 'w', encoding='utf8') as f:
        json.dump(dump, f)
    ab = '''UPDATE users SET game=2, img=\'{}\' WHERE id={}'''.format(map_file, id)
    cur = con.cursor()
    cur.execute(ab)
    con.commit()


def continue_second(vk, id, mess):
    ab = """Select * from users Where id={}""".format(id)
    cur = con.cursor()
    ans = cur.execute(ab).fetchall()
    print(ans)
    p = ans[0]
    q, games, game, ball, img, js = p
    with open('jsons/' + js, encoding='utf8') as f:
        d = json.load(f)
    c = d["arr"]
    if mess in ['заново', 'restart']:
        start_second(vk, id)
        return
    try:
        s = int(mess) - 1
        if c[s] == d["name"]:
            bal = d["bal"]
            me = 'Вы угадали и заработали {} балла'.format(max(bal, 1))
            send_message(vk, id, messege=me)
            games += 1
            ball += bal
            game = 0
            ab = """Update users set games={}, game={}, ball={} where id={}""".format(games, game, ball, id)
            cur.execute(ab).fetchall()
            con.commit()
        else:
            dump = {
                'arr': c,
                'game': 2,
                'bal': d["bal"] - 1,
                'name': d["name"]
            }
            with open('jsons/' + js, 'w', encoding='utf8') as f:
                json.dump(dump, f)
            send_message(vk, id, messege="НЕПРАВИЛЬНО!!")

    except:
        send_message(vk, id, messege='Ошибка ввода')


def continue_fird(vk, id, mess):
    ab = """Select * from users Where id={}""".format(id)
    cur = con.cursor()
    ans = cur.execute(ab).fetchall()
    print(ans)
    p = ans[0]
    q, games, game, ball, img, js = p
    with open('jsons/' + js, encoding='utf8') as f:
        d = json.load(f)
    c = d["arr"]
    if mess in ['заново', 'restart']:
        start_second(vk, id)
        return
    try:
        s = int(mess) - 1
        if c[s] == d["name"]:
            bal = d["bal"]
            me = 'Вы угадали и заработали {} балла'.format(max(bal, 1))
            send_message(vk, id, messege=me)
            games += 1
            ball += bal
            game = 0
            ab = """Update users set games={}, game={}, ball={} where id={}""".format(games, game, ball, id)
            cur.execute(ab).fetchall()
            con.commit()
        else:
            dump = {
                'arr': c,
                'game': 2,
                'bal': d["bal"] - 1,
                'name': d["name"]
            }
            with open('jsons/' + js, 'w', encoding='utf8') as f:
                json.dump(dump, f)
            send_message(vk, id, messege="НЕПРАВИЛЬНО!!")

    except:
        send_message(vk, id, messege='Ошибка ввода')


def start_fird(vk, id):
    send_message(vk, id, messege=ruls3)
    with open('jsons/contr.json', encoding='utf8') as f:
        d = json.load(f)
    c = d["arr"]
    contr = random.choice(c)
    with open(f'jsons/{id}.json', encoding='utf8') as f:
        d = json.load(f)
    img = contr["flag"]
    b = [i["name"] for i in c]
    z = []
    b.pop(b.index(contr["name"]))
    for i in range(3):
        z.append(random.choice(b))
        b.pop(b.index(z[i]))
    z.append(contr["name"])
    random.shuffle(z)
    send_message(vk, id, messege="Флаг какой странны изображен?",
                 attachment=make_attacment('images/staticimgs/2/' + img))
    ab = ''
    for i in range(4):
        ab += f'{i + 1}.{z[i]}\n'
    send_message(vk, id, messege=ab)

    dump = {
        'arr': z,
        'game': 3,
        'bal': 4,
        'name': contr["name"]
    }

    with open(f'jsons/{id}.json', 'w', encoding='utf8') as f:
        json.dump(dump, f)
    ab = '''UPDATE users SET game=3, img=\'{}\' WHERE id={}'''.format(img, id)
    cur = con.cursor()
    cur.execute(ab)
    con.commit()


def continue_game(vk, id, mess, a):
    if mess == "end":
        ab = """Select * from users Where id={}""".format(id)
        cur = con.cursor()
        ans = cur.execute(ab).fetchall()
        print(ans)
        p = ans[0]

        q, games, game, ball, img, js = p
        game = 0
        ab = """Update users set games={}, game={}, ball={} where id={}""".format(games, game, ball, id)
        cur.execute(ab).fetchall()
        con.commit()
        send_message(vk, id, messege=commands)
        return

    if a == 1:
        continue_first(vk, id, mess)
    elif a == 2:
        continue_second(vk, id, mess)
    elif a == 3:
        continue_fird(vk, id, mess)


class User():
    def __init__(self, id):
        self.id = id
        self.games = 0
        self.game = 0
        self.ball = 0
        self.img = '\'\''
        with open('jsons/' + f'{self.id}.json', 'w', encoding='utf8') as f:
            print('{\"arr\":    []}', file=f)
        self.json = f'\'{self.id}.json\''

    def ins(self, con):
        cur = con.cursor()
        ab = """INSERT into users (id, games, game, ball, img, json) VALUES({}, {}, {}, {}, {}, {})""".format(self.id,
                                                                                                              self.games,
                                                                                                              self.game,
                                                                                                              self.ball,
                                                                                                              self.img,
                                                                                                              self.json)
        cur.execute(ab
                    ).fetchall()
        con.commit()


def main():
    print("CONECTED")
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            id, mess, *args = mes_info(event)
            print(mess)
            if new_user(id):
                create_user(vk, id)
                continue
            if mess in ["команды", "помощь", "help"]:
                send_message(vk, id, messege=commands)
                continue
            a = get_game(id)
            if a == 0 and mess in command.keys():
                start(vk, id, mess)
            elif 1 <= a <= 3:
                continue_game(vk, id, mess, a)

            else:
                send_message(vk, id, messege=error)

            print('YES')


if __name__ == '__main__':
    with open('token.file') as f:
        token = f.read()
    vk_session = vk_api.VkApi(
        token=token)

    commands = 'вы можете написать:\n' \
               '1 или пятнашки\n2 или угадать страну на карте\n3 или угадать страну по флагу\nтакже ты можешь завершить свою игру написав \"end\"'
    error = 'Ошибка, Бот не понимает вас. Чтобы получить помощь, напишите \"помощь\"'
    welcom = 'Привет, добро пожаловать к маленькому боту с географическими задачками, чтобы ознакомиться со списком команд напиши: \"помощь\"'
    ruls1 = 'В этой игре тебе предстоит собрать пазл-пятнашки какого-либо известногостроения\nЧтобы передвинуть плитку напиши ее номер(от одного до шестнадцати) и она  поменяется с пустой.\n Также у тебя есть возможность менять несколько плиток за раз, просто напиши их номера через пробел'
    ruls2 = 'В этой игре тебе предстоит угадать название страны по карте. Напиши мне НОМЕР твоего ответа и проверь себя!!'
    ruls3 = 'В этой игре тебе предстоит угадать название страны по её флагу. Напиши мне НОМЕР твоего ответа и проверь себя!!'

    command = make_commands()
    longpoll = VkBotLongPoll(vk_session, 204090529)
    upload = VkUpload(vk_session)
    con = sqlite3.connect('users.db')

    C = [[i * 4 + j for j in range(1, 5)] for i in range(4)]
    x, y = 3, 3
    C[x][y] = None
    main()

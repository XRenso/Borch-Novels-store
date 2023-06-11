import pymongo
import re
class Mongo:
    def __init__(self):
        self.connection = pymongo.MongoClient("mongodb://admin:safeKillPassword@79.143.29.191/admin")['store']
        self.user = self.connection['user']
        self.frame = self.connection['frame']
        self.game = self.connection['game']
    def add_user(self,user_id):
        if self.user.count_documents({'user_id':user_id}) == 0:
            user = {
                'user_id' : user_id, # Пользовательский id
                'curr_game_code': None, # Текущая игра
                'games_config': [], # Игровой конфиг
                'achivements' : [], # Ачивки
                'is_admin': 0 #Проверка на админа
            }
            self.user.insert_one(user)
        else:
            return 0

    def add_frame(self,game_code:str, frame_num:int, is_demo:int, content_code:int, text:dict,variants:str, variants_frame:str, sound:str = None, content:str=None,  modificators:str=None, sticker:str=None, change_add_conditions:str=None,check_add_conditions:str=None, fail_condition_frame:int=None, achivement:str=None) -> 0:
        if self.frame.count_documents({'frame_num':frame_num, 'game_code':game_code}) == 0 and self.game.count_documents({'game_code':game_code}) == 1:
            frame = {
                'game_code':game_code, #Уникальный код игры
                'frame_num': frame_num, # уникальный номер кадра
                'content_code' : content_code, # Контент код, что необходимо отправить 0 - текст, 1 - фото, 2 -видео, 3 - аудио
                'is_demo':is_demo, # Является ли кадр демо или нет
                'text' : text, # Основной текст кадра
                'content' : content, # Медиа файл, согласно контент коду
                'variants': variants, # Варианты событий, разделяются через \n
                'variants_frame': variants_frame, # Кадры в которые ведут варианты, пишутся на том же месте, что и текст вариантов. Разделяются через \n
                'sound': sound, #Звук, что будет отправлен вместе с сообщением
                'sticker':sticker, # Отправит стикер вместе с вашим кадром
                'modificators':modificators, # battle - бой, все остальное - ничего
                'change_add_conditions': change_add_conditions, # Доп. условия, которые нужно изменить в условиях игры
                'check_add_conditions' : check_add_conditions, # Проверка на доп. условия из конфига игры
                'fail_condition_frame': fail_condition_frame, # кадр, который наступит, если проверка будет провалена
                'achivement': achivement # Название достижение, которое дадут на этом кадре
            }
            self.frame.insert_one(frame)
        else:
            return 0

    def add_game(self, code: str, name: str, description: str, cover: str, creator:str, publisher:str,can_buy:int, price: int, discount:int, genre_code:str, genre:str, config: dict) -> 0 or None:
        if self.game.count_documents({'game_code':code}) == 0:
            cfg = {
                'frame_num': 1,
                'is_demo': 1
            }
            cfg.update(config)
            game = {
            'game_code': code, # Уникальный код игры
            'game_name': name, # Название игры
            'game_description': description, # Описание игры
            'game_cover': cover, # Обложка игры
            'creator': creator, #Разработчик
            'publisher': publisher, # Издатель
            'price': price, # Цена
            'can_buy':can_buy, #Доступна ли игра для продажи
            'discount':discount, # Скидка
            'genre_code': genre_code, # Код жанра
            'genre': genre, #Жанр
            'game_config': cfg # Конфиг игры

            }
            self.game.insert_one(game)
        else:
            return 0

    def reset_game_setings(self, game_code:str, user_id:int):
        now_cfg = self.return_game_cfg(user_id, game_code)

        self.user.update_one({'user_id': user_id, f'games_config.{game_code}': {'$exists': True}},
                             {'$set': {f'games_config.$.{game_code}': self.return_game_info(game_code)['game_config']}})

        self.user.update_one({'user_id': user_id, f'games_config.{game_code}': {'$exists': True}},
                             {'$set': {f'games_config.$.{game_code}.is_demo': now_cfg['is_demo']}})
    def give_game_to_user(self, game_code:str, user_id:int, is_demo:int):
        if self.user.count_documents({'user_id':user_id}) == 1:

            check = self.return_game_cfg(user_id,game_code)
            game_config = {
                game_code:self.return_game_info(game_code)['game_config']
            }
            if not check:


                self.user.update_one({'user_id': user_id}, {'$push': {'games_config': game_config}})
                if is_demo == 0:
                    self.user.update_one({'user_id': user_id, f'games_config.{game_code}': {'$exists': True}},
                                         {'$set': {f'games_config.$.{game_code}.is_demo': 0}})

            elif check != 0 and is_demo == 0 and check['is_demo'] == 1:
                self.user.update_one({'user_id': user_id, f'games_config.{game_code}': {'$exists': True}},
                                     {'$set': {f'games_config.$.{game_code}.is_demo': 0}})
            else:
                return 0
        else:
            return 0

    def return_game_cfg(self, user_id, game_code):
        user = self.return_user_info(user_id)
        if user:
            for i in user['games_config']:
                for key,value in i.items():
                    if key == game_code:
                        return i[key]
            return 0
    def return_game_info(self, game_code):
        if self.game.count_documents({'game_code': game_code}) == 1:
            return self.game.find_one({'game_code': game_code})
        else:
            return 0
    def return_user_info(self,user_id):
        if self.user.count_documents({'user_id': user_id}):
            return self.user.find_one({'user_id':user_id})
        else:
            return 0
    def return_frame(self,frame_num, game_code):
        if self.frame.count_documents({'frame_num':frame_num, 'game_code':game_code}):
            return self.frame.find_one({'frame_num':frame_num, 'game_code':game_code})
        else:
            return 0
    def return_genre_name_by_code(self,genre_code):
        return self.game.find_one({'genre_code':genre_code})['genre']


    def update_user_frame_num(self,user_id,frame_num, game_code):
        user = self.return_user_info(user_id)
        if user:
            self.user.update_one({'user_id':user_id, f'games_config.{game_code}': {'$exists':True}},
                                  {'$set': {f'games_config.$.{game_code}.frame_num' : int(frame_num)}})
        else:
            return 0

    def update_now_user_game(self, user_id, game_code):
        user = self.return_user_info(user_id)
        if user:
            self.user.update_one({'user_id':user_id}, {'$set':{'curr_game_code':game_code}})
        else:
            return 0

    def search_game_by_name(self, search):
        return self.game.find({'game_name': re.compile(rf"(?i){search}")})


    def return_user_library_games(self,user_id:int) -> list or 0:
        user = self.return_user_info(user_id)
        if user:
            games = []
            for i in user['games_config']:
                try:
                    for key, value in i.items():
                        games.append(self.return_game_info(key))
                except:
                    return 0
            return games
        else:
            return 0

    def check_is_game_in_user_library(self, user_id,game_code) -> int:
        library = self.return_user_library_games(user_id)
        if library != 0:
            for i in library:
                if i['game_code'] == game_code:
                    return 1
        return 0


    def return_genres(self):
        genres = self.game.distinct('genre_code')
        genres.remove('off_guides')
        genres.insert(0,'off_guides')
        return genres
    def return_game_by_genre(self, genre_code):
        return self.game.find({'genre_code':genre_code})

if __name__ == '__main__':
    print('Тест')
    check = Mongo()
    check.__init__()
    check.add_frame(game_code='zeleria_new_year', frame_num=1, content_code=0,is_demo=0,text={'ru':'Эта небольшая новогодняя история развивает одну из концовок игры «Заповедник Зелирия»,'
    'повествующую о приключениях земного спецназовца Макса на планете Зелирия. Компанию в пути ему составляют девушка-кошка Лика из расы умари, зелирийка Эйка и Хамки – одно из '
    'самых древних существ на планете, похожий на фиолетового хомяка, невидимый для местных обитателей и общающийся с Максом исключительно телепатией. Умари почитают Хамки как '
    'божество, но он и в самом деле владеет древними технологиями, которые выглядят для жителей Зелирии как магия. Макс, благодаря Хамки, стал правителем умари, которые поклоняются'
    'ему как пророку. Хотите знать больше – добро пожаловать в «Заповедник Зелирия»! Стим: https://store.steampowered.com/app/855630/Zeliria_Sanctuary/'},variants='Продолжить',
                    variants_frame='2')
    check.add_frame(game_code='zeleria_new_year', frame_num=2, content_code=1, is_demo=0,
                    text={'ru': 'Я сидел в своих покоях, расположенных на верхнем этаже Храма Салангана и смотрел в окно. Ласса, моя «заместительница» и бывшая верховная жрица умари, сразу определила это место как «лучшее в Храме» и «достойное Гласа Салангана». Пожалуй, она права – тут как минимум тихо и вся храмовая суета проходит мимо меня. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='3',
                    sound='CQACAgIAAxkBAAIH9mSF5Z8NQuo8CEZ_aH6JGOR8Qji4AALcLwACYVgwSDa7zqTztczuLwQ')
    check.add_frame(game_code='zeleria_new_year', frame_num=3, content_code=1, is_demo=0,
                    text={
                        'ru': '...'},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='4')

    check.add_frame(game_code='zeleria_new_year', frame_num=4, content_code=1, is_demo=0,
                    text={
                        'ru': 'Пожалуй, она права – тут как минимум тихо и вся храмовая суета проходит мимо меня. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='5')
    check.add_frame(game_code='zeleria_new_year', frame_num=5, content_code=1, is_demo=0,
                    text={
                        'ru': 'Полгода прошло с тех пор как я, боец земного спецназа, первый в истории человечества испытатель первого в мире телепорта, оказался на Зелирии – далёкой планете, населённой полудикими племенами и похожими на людей существами – зелирийцами и людьми-кошками умари. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='6')
    check.add_frame(game_code='zeleria_new_year', frame_num=6, content_code=1, is_demo=0,
                    text={
                        'ru': 'На счастье, я встретил фиолетового хомяка по имени Хамки, который на поверку оказался представителем древней цивилизации Саланганцев, много лет назад покинувших эту планету и отправившихся изучать космос. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='7')
    check.add_frame(game_code='zeleria_new_year', frame_num=7, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки же остался эдаким «хранителем» планеты, который провёл в глубоком сне несколько миллионов лет.'},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='8')
    check.add_frame(game_code='zeleria_new_year', frame_num=8, content_code=1, is_demo=0,
                    text={
                        'ru': ' Он невидим для местных обитателей, потому что его пси-поле скрывает Хамки от их восприятия, у меня же с этим проблем нет. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='9')
    check.add_frame(game_code='zeleria_new_year', frame_num=9, content_code=1, is_demo=0,
                    text={
                        'ru': 'Куда важнее, что умари считают Хамки богом, и моя способность видеть его дала мне возможность стать для них своего рода пророком – Гласом Салангана. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='10')
    check.add_frame(game_code='zeleria_new_year', frame_num=10, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что ж, вернуться домой на Землю я уже не могу, так что это не самый плохой вариант. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='11')
    check.add_frame(game_code='zeleria_new_year', frame_num=11, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс (грусть): Эх...'},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='12')
    check.add_frame(game_code='zeleria_new_year', frame_num=12, content_code=1, is_demo=0,
                    text={
                        'ru': ' Я облокотился о каменный подоконник и посмотрел на улицу. Закатное солнце освещало двор храма, послушницы Салангана как обычно занимались хозяйственными делами, а мне захотелось взвыть.'},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='13')
    check.add_frame(game_code='zeleria_new_year', frame_num=13, content_code=1, is_demo=0,
                    text={
                        'ru': 'Мои наручные часы ещё не остановились, и, если они не сбились при телепортации, то сейчас у меня дома вечер 31-го декабря. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='14')
    check.add_frame(game_code='zeleria_new_year', frame_num=14, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Новый год... Мой любимый праздник... А здесь никто о таком и знать не знает '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='15')
    check.add_frame(game_code='zeleria_new_year', frame_num=15, content_code=1, is_demo=0,
                    text={
                        'ru': 'Решив немного отвлечься, я вышел из покоев и направился в тронный зал. Там скучать не приходилось никогда – получившие от меня приказ на «активное развитие страны», девушки взялись за дело с фанатичным энтузиазмом. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='16')
    check.add_frame(game_code='zeleria_new_year', frame_num=16, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Может, хоть чего интересного расскажут. '},
                    content='AgACAgIAAxkBAAIHZWSFvmPK0F9pF6fe01i99QcAAR1U4AACTc0xG2FYKEhTPwleIkI1pQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='17')
    check.add_frame(game_code='zeleria_new_year', frame_num=17, content_code=1, is_demo=0,
                    text={
                        'ru': 'Гвалт донёсся до меня ещё на подходе. Когда же я вошёл в зал, вопли девушек буквально ударили по ушам. '},
                    content='AgACAgIAAxkBAAIHpmSF1pgg4oqzEm1Qgrn7ptV844YwAAIhzjEbYVgoSPM7wNnEu7GLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='18')
    check.add_frame(game_code='zeleria_new_year', frame_num=18, content_code=1, is_demo=0,
                    text={
                        'ru': 'Ласса: Вы сумасшедшие?! Вы хоть знаете, каких усилий это будет стоить? '},
                    content='AgACAgIAAxkBAAIHpmSF1pgg4oqzEm1Qgrn7ptV844YwAAIhzjEbYVgoSPM7wNnEu7GLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='19')
    check.add_frame(game_code='zeleria_new_year', frame_num=19, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Сама дура! Если сделаем этот туннель – у нас будет быстрый доступ ко множеству отдалённых районов! И тамошние обитатели смогут легко посещать основную территорию Теократии! '},
                    content='AgACAgIAAxkBAAIHqGSF1sWBaWC47bNbAtEv0s3rlcLBAAJlzjEbYVgoSCNaZWbyFz5gAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='20')
    check.add_frame(game_code='zeleria_new_year', frame_num=20, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: И те места не интересуют зелирийцев. Опасности оттуда ждать не стоит! '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='21')
    check.add_frame(game_code='zeleria_new_year', frame_num=21, content_code=1, is_demo=0,
                    text={
                        'ru': 'Только в этот момент они заметили меня и заметно стушевались. В моём присутствии они не позволяли себе таких громких споров с руганью. Хорошо, что до драки не дошли. '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='22')
    check.add_frame(game_code='zeleria_new_year', frame_num=22, content_code=1, is_demo=0,
                    text={
                        'ru': ' Макс: Что у вас тут такое? '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='23')
    check.add_frame(game_code='zeleria_new_year', frame_num=23, content_code=1, is_demo=0,
                    text={
                        'ru': 'Ласса: Решаем вопрос целесообразности постройки туннеля на северо-западной окраине. На мой взгляд, это неоправданная трата времени и ресурсов '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='24')
    check.add_frame(game_code='zeleria_new_year', frame_num=24, content_code=1, is_demo=0,
                    text={
                        'ru': 'Ласса: А мы с Эйкой считаем, что туннель необходим! Он свяжет всех жителей пограничного района с центральными частями страны. Без этого туннеля им нужно сделать крюк длинной в сутки, просто чтобы дойти до перевала, который можно пересечь. В других местах горы слишком высокие и отвесные. '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='25')
    check.add_frame(game_code='zeleria_new_year', frame_num=25, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: И за безопасность не надо волноваться – зелирийцы в тех местах особой активности не проявляют. А умари за горами живёт много.  '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='26')
    check.add_frame(game_code='zeleria_new_year', frame_num=26, content_code=1, is_demo=0,
                    text={
                        'ru': 'Только вздохнул. Им было трудно друг с другом. Ласса, привыкшая решать всё самостоятельно, была прекрасно осведомлена о всех тонкостях жизни теократии и умела разумно распоряжаться имеющимися ресурсами. Лика, в прошлом отшельница-изгнанница, больше думала о простых жителях, а Эйка, зелирийка, вовсе оценивала любое действие с точки зрения «какую реакцию это вызовет у зелирийских королевств». '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='27')
    check.add_frame(game_code='zeleria_new_year', frame_num=27, content_code=1, is_demo=0,
                    text={
                        'ru': 'Но стоит признать, что обычно они находили общий язык и принимали оптимальное решение. Формально все они были лишь моими наложницами, а право командовать имел только я, Глас Салангана. Но я в этом мире пришелец, я учусь, но всё ещё знаю о нём слишком мало, чтобы вершить его судьбу, и мне приходится полагаться на них. '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='28')
    check.add_frame(game_code='zeleria_new_year', frame_num=28, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я вижу их старания и ощущаю, что они соперничают не только и не столько в политических делах, сколько за моё внимание к ним как к девушкам. И рано или поздно мне стоит определиться с выбором.  '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='29')
    check.add_frame(game_code='zeleria_new_year', frame_num=29, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Думаю, туннель – идея стоящая. Давайте обсудим это завтра вместе. '},
                    content='AgACAgIAAxkBAAIHqmSF1uTlj8Ry7thsm1H8xQIEJMzHAAJnzjEbYVgoSJYCmLrOupC9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='30')
    check.add_frame(game_code='zeleria_new_year', frame_num=30, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я махнул рукой и отправился в коридор, с которого можно было выйти на балкон. Постою, подышу свежим воздухом. '},
                    content='AgACAgIAAxkBAAIHpmSF1pgg4oqzEm1Qgrn7ptV844YwAAIhzjEbYVgoSPM7wNnEu7GLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='31')
    check.add_frame(game_code='zeleria_new_year', frame_num=31, content_code=1, is_demo=0,
                    text={
                        'ru': 'Не хочу торчать там один, но и отвлекать их не хочу... '},
                    content='AgACAgIAAxkBAAIHpmSF1pgg4oqzEm1Qgrn7ptV844YwAAIhzjEbYVgoSPM7wNnEu7GLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='32')
    check.add_frame(game_code='zeleria_new_year', frame_num=32, content_code=1, is_demo=0,
                    text={
                        'ru': 'Выбор:'},
                    content='AgACAgIAAxkBAAIHpmSF1pgg4oqzEm1Qgrn7ptV844YwAAIhzjEbYVgoSPM7wNnEu7GLAQADAgADeQADLwQ',
                    variants=' Надеюсь, Лика найдёт время заглянуть ко мне\nНадеюсь, Эйка надумает зайти сегодня.', variants_frame='33\n159')
    check.add_frame(game_code='zeleria_new_year', frame_num=33, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я вышел на балкон и посмотрел вдаль. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='34')
    check.add_frame(game_code='zeleria_new_year', frame_num=34, content_code=1, is_demo=0,
                    text={
                        'ru': 'Максим: А ведь совсем скоро полночь.'},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='35')
    check.add_frame(game_code='zeleria_new_year', frame_num=35, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Что случилось, Макс? Ты выглядел таким расстроенным, что я начала волноваться. '},
                    content='AgACAgIAAxkBAAIHrmSF13b_Hh3P5WNZo8V0RrnPjcHAAAJpzjEbYVgoSG4Wcu3-BWVyAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='36')
    check.add_frame(game_code='zeleria_new_year', frame_num=36, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика подошла ко мне и обняла за плечи. '},
                    content='AgACAgIAAxkBAAIHrmSF13b_Hh3P5WNZo8V0RrnPjcHAAAJpzjEbYVgoSG4Wcu3-BWVyAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='37')
    check.add_frame(game_code='zeleria_new_year', frame_num=37, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Что с тобой? Расскажи, я попробую тебе помочь!   '},
                    content='AgACAgIAAxkBAAIHrmSF13b_Hh3P5WNZo8V0RrnPjcHAAAJpzjEbYVgoSG4Wcu3-BWVyAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='38')
    check.add_frame(game_code='zeleria_new_year', frame_num=38, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Не знаю, как тебе это объяснить. В моём мире этой ночью будет праздник – Новый год. Ну, знаешь, мы отмечаем дату, когда один год сменяется другим. '},
                    content='AgACAgIAAxkBAAIHrmSF13b_Hh3P5WNZo8V0RrnPjcHAAAJpzjEbYVgoSG4Wcu3-BWVyAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='39')
    check.add_frame(game_code='zeleria_new_year', frame_num=39, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Но ведь это здорово!  У нас тоже есть такой праздник! День сомкнутых век – самая длинная ночь, когда, согласно нашей вере, Саланган Хамки проспал особенно долго, отчего сама Зелирия погрузилась во тьму на большую часть суток. В честь этого мы... '},
                    content='AgACAgIAAxkBAAIHsGSF159oTRcvQl8jc_YYDXdycArMAAJqzjEbYVgoSC4zI5ZYS100AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='40')
    check.add_frame(game_code='zeleria_new_year', frame_num=40, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Нет-нет, я не об этом. В моём мире Новый год – это... Как бы лучше сказать – это атмосфера праздника. Это пушистый снег, новогодние украшения улиц, шикарные ёлки на площадях, а дома – маленькая наряженная ёлка. Гирлянды на окнах, блестящая мишура... '},
                    content='AgACAgIAAxkBAAIHsGSF159oTRcvQl8jc_YYDXdycArMAAJqzjEbYVgoSC4zI5ZYS100AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='41')
    check.add_frame(game_code='zeleria_new_year', frame_num=41, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Но самое главное – снег. Еловый аромат. Взрывы фейерверков на улице... Я сам любил их запускать. '},
                    content='AgACAgIAAxkBAAIHsGSF159oTRcvQl8jc_YYDXdycArMAAJqzjEbYVgoSC4zI5ZYS100AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='42')
    check.add_frame(game_code='zeleria_new_year', frame_num=42, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Эм... Макс... Прости, но я не поняла и половины сказанных тобой слов... '},
                    content='AgACAgIAAxkBAAIHsmSF1736nAbQ-GPGTAqiAmdbE67VAAJhyjEbYVgwSBy0yMBBIVUfAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='43')
    check.add_frame(game_code='zeleria_new_year', frame_num=43, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Не расстраивайся, я... '},
                    content='AgACAgIAAxkBAAIHsmSF1736nAbQ-GPGTAqiAmdbE67VAAJhyjEbYVgwSBy0yMBBIVUfAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='44')
    check.add_frame(game_code='zeleria_new_year', frame_num=44, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: НОВЫЙ ГОД, МАТЬ ВАШУ!!!! '},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='45')
    check.add_frame(game_code='zeleria_new_year', frame_num=45, content_code=1, is_demo=0,
                    text={
                        'ru': 'Куда же без него... Хотя целую неделю где-то бродил. Кажется, изучал местные сады. Искал еду. '},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='46')
    check.add_frame(game_code='zeleria_new_year', frame_num=46, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: ТЫ СКАЗАЛ «НОВЫЙ ГОД»!? '},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='47')
    check.add_frame(game_code='zeleria_new_year', frame_num=47, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эти истерические вопли раздавались у меня в сознании, потому что местные не только не видят Хамки, но и не слышат его. По сути, я единственный на всей планете, кто способен общаться с ним. В том числе телепатией – он читает мои мысли и транслирует мне в мозг свои. '},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='48')
    check.add_frame(game_code='zeleria_new_year', frame_num=48, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Макс, ты что-то знаешь про Новый год? Ты сказал там был снег? Там была ёлка?! А подарки?! Люди дарили друг другу подарки?! 	'},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='49')
    check.add_frame(game_code='zeleria_new_year', frame_num=49, content_code=1, is_demo=0,
                    text={
                        'ru': ': Вот это поворот! Сейчас Хамки выглядел куда бОльшим маньяком, чем Лика, когда говорила о нём. '},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='50')
    check.add_frame(game_code='zeleria_new_year', frame_num=50, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Ну... Да, на Новый год мы дарим друг другу подарки и... '},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='51')
    check.add_frame(game_code='zeleria_new_year', frame_num=51, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Ни слова больше! Макс, я тебя поздравляю! Только что в моих глазах человечество стало хоть и технологически отсталой, но весьма развитой цивилизацией! Саланган не видел этого праздника многие миллионы лет, но сейчас мы вернём этим недоразвитым Новый год! '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='52')
    check.add_frame(game_code='zeleria_new_year', frame_num=52, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я смотрел, как Хамки мечется по каменному подоконнику, махая лапами и исторгая беззвучные вопли радости. Вёл он себя так, словно собирался не отмечать Новый год, а как минимум захватывать соседнюю страну или вовсе другую планету. '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='53')
    check.add_frame(game_code='zeleria_new_year', frame_num=53, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: На Салангане праздновали Новый год? '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='54')
    check.add_frame(game_code='zeleria_new_year', frame_num=54, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Конечно! На этот день контроллер погоды перенастраивали, и на всей планете шёл снег! Мы играли в снежки, кувыркались в сугробах, лепили снеговиков! '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='55')
    check.add_frame(game_code='zeleria_new_year', frame_num=55, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я представил полчища грызунов, закидывающих друг друга снежками, и невольно улыбнулся. '},
                    content='AgACAgIAAxkBAAIHuGSF2Cpzxb4n4ymHhSFibTvmYsZ8AAJmyjEbYVgwSH8YQ4DejU72AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='56')
    check.add_frame(game_code='zeleria_new_year', frame_num=56, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: И что тут смешного? '},
                    content='AgACAgIAAxkBAAIHuGSF2Cpzxb4n4ymHhSFibTvmYsZ8AAJmyjEbYVgwSH8YQ4DejU72AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='57')
    check.add_frame(game_code='zeleria_new_year', frame_num=57, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Ничего! Просто представил толпу хомяков, отмечающих праздник... '},
                    content='AgACAgIAAxkBAAIHuGSF2Cpzxb4n4ymHhSFibTvmYsZ8AAJmyjEbYVgwSH8YQ4DejU72AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='58')
    check.add_frame(game_code='zeleria_new_year', frame_num=58, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Я НЕ ХОМЯК!!!'},
                    content='AgACAgIAAxkBAAIHumSF2LVOtQupvr-v8Y9zX3bC4tZAAAJoyjEbYVgwSBuCXm8k2D_CAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='59')
    check.add_frame(game_code='zeleria_new_year', frame_num=60, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Ладно, ладно. Саланганцев. И ещё я подумал о том, что сам встречал Новый год всегда именно так, как ты описал. И, знаешь, мне грустно, что здесь у нас ничего этого нет. '},
                    content='AgACAgIAAxkBAAIHumSF2LVOtQupvr-v8Y9zX3bC4tZAAAJoyjEbYVgwSBuCXm8k2D_CAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='61')
    check.add_frame(game_code='zeleria_new_year', frame_num=61, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Нет, говоришь...  '},
                    content='AgACAgIAAxkBAAIHvGSF2Piqh8ZjCtU5QXBwT5QHUzsqAAJpyjEbYVgwSFKG5PlpVkNSAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='62')
    check.add_frame(game_code='zeleria_new_year', frame_num=62, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Макс? '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='63')
    check.add_frame(game_code='zeleria_new_year', frame_num=63, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика уже привыкла к нашим с Хамки «молчаливым беседам», поэтому когда я внезапно «зависал» – умолкала и терпеливо ждала, когда я вновь обращу на неё внимание. Интересно, она в этот момент не чувствует себя предметом мебели?'},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='64')
    check.add_frame(game_code='zeleria_new_year', frame_num=64, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Ты обсуждаешь с Саланганом Хамки что-то важное? '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='65')
    check.add_frame(game_code='zeleria_new_year', frame_num=65, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Да, бестолковая ты умари! У нас с Максом будет Новый год!!! '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='46')
    check.add_frame(game_code='zeleria_new_year', frame_num=66, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика этой фразы, конечно, не услышала. '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='67')
    check.add_frame(game_code='zeleria_new_year', frame_num=67, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Да. Пожалуй, сейчас самое время немного поменять ваши устаревшие традиции! '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='68')
    check.add_frame(game_code='zeleria_new_year', frame_num=68, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Хамки, а что ты собрался делать? '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='69')
    check.add_frame(game_code='zeleria_new_year', frame_num=69, content_code=1, is_demo=0,
                    text={
                        'ru': 'Пока этот фиолетовый комок шерсти лучится энтузиазмом справить Новый год – надо этим пользоваться.  '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='70')
    check.add_frame(game_code='zeleria_new_year', frame_num=70, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Значит, так. Макс, сейчас ты идёшь и прямо с этого балкона во всё горло объявляешь, что сейчас Саланган Хамки явит чудо! '},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='71')
    check.add_frame(game_code='zeleria_new_year', frame_num=71, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Эм? Зачем?!'},
                    content='AgACAgIAAxkBAAIHvmSF2SG06B_UZB8HXfr4HOJgNU8rAAJryjEbYVgwSCMNr-jy2y7SAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='72')
    check.add_frame(game_code='zeleria_new_year', frame_num=72, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Чтобы умари не обосрались от страха, когда я начну новогодние приготовления! '},
                    content='AgACAgIAAxkBAAIHwGSF2YOgqabR75udYN8wv7RM7iU9AAJvyjEbYVgwSIY_KKlu8lbKAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='73')
    check.add_frame(game_code='zeleria_new_year', frame_num=73, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Что ты задумал?! '},
                    content='AgACAgIAAxkBAAIHwGSF2YOgqabR75udYN8wv7RM7iU9AAJvyjEbYVgwSIY_KKlu8lbKAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='74')
    check.add_frame(game_code='zeleria_new_year', frame_num=74, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Увидишь! Вали давай горлопанить'},
                    content='AgACAgIAAxkBAAIHwGSF2YOgqabR75udYN8wv7RM7iU9AAJvyjEbYVgwSIY_KKlu8lbKAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='75')
    check.add_frame(game_code='zeleria_new_year', frame_num=75, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что-то будет...'},
                    content='AgACAgIAAxkBAAIHwmSF2aQHk22U4v_XjPlqIEn4Q2KnAAJwyjEbYVgwSCvfhKDcYcxGAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='76')
    check.add_frame(game_code='zeleria_new_year', frame_num=76, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Лика, идём, нам нужно сделать важное объявление. '},
                    content='',
                    variants='Продолжить', variants_frame='77')
    check.add_frame(game_code='zeleria_new_year', frame_num=77, content_code=1, is_demo=0,
                    text={
                        'ru': 'Глаза девушки заметно округлились от удивления, но она молча послушалась. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='78')
    check.add_frame(game_code='zeleria_new_year', frame_num=78, content_code=1, is_demo=0,
                    text={
                        'ru': 'Пока я шёл те несколько метров, что изначально отделяли меня от перил каменного балкона, который мне было положено использовать для обращения к обитателям храма и вообще народу, который собирался на площади перед ним, я успел подумать лишь о том, что поговорка «бойся своих желаний, они имеют свойство сбываться» не так уж далека от реальности. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='79')
    check.add_frame(game_code='zeleria_new_year', frame_num=79, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что этот фиолетовый собрался творить? Что я сейчас скажу? И кому? Сейчас же вечереет, послушницы уже заканчивают работу, внизу почти никого нет. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='80')
    check.add_frame(game_code='zeleria_new_year', frame_num=80, content_code=1, is_demo=0,
                    text={
                        'ru': 'Выйдя на балкон, я осмотрел полупустой двор храма. Чёрт, я уже чувствую себя полным идиотом, а если сейчас ещё и вещать начну! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='81')
    check.add_frame(game_code='zeleria_new_year', frame_num=81, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Макс, давай же! Ты Глас Салангана! Донеси нам то, что он поведал тебе! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='82')
    check.add_frame(game_code='zeleria_new_year', frame_num=82, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика шёпотом подбадривала меня, а сама буквально лучилась счастьем. Ох, не понимает она, с кем связалась... '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='83')
    check.add_frame(game_code='zeleria_new_year', frame_num=83, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что ж, приступим'},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='84')
    check.add_frame(game_code='zeleria_new_year', frame_num=84, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Люд... Мои верные послушники! Сегодня, в этот самый день и час, Саланган Хамки явит нам свою силу! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='85')
    check.add_frame(game_code='zeleria_new_year', frame_num=85, content_code=1, is_demo=0,
                    text={
                        'ru': 'Мои вопли, разносящиеся над храмовым двором, утонули в окрестных лесах, привлеча внимание лишь тех немногих послушниц, которые всё же оказались поблизости. Обычно на мои «проповеди» народ собирается заранее со всех окрестных деревень, сейчас же ничего такого не предвиделось и посторонних в храме не было. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='86')
    check.add_frame(game_code='zeleria_new_year', frame_num=86, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Сегодня, волею Салангана Хамки, мы будем отмечать новый праздник, который станет точкой отсчёта Новой Эры! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='87')
    check.add_frame(game_code='zeleria_new_year', frame_num=87, content_code=1, is_demo=0,
                    text={
                        'ru': 'Чёрт, чувствую себя форменным кретином. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='88')
    check.add_frame(game_code='zeleria_new_year', frame_num=88, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Сегодня ночью, на рубеже этих суток, начнётся новое летоисчисление! Сегодня в полночь наступит первый год Эры Явившегося Салангана Хамки! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='89')
    check.add_frame(game_code='zeleria_new_year', frame_num=89, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что я несу?! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='90')
    check.add_frame(game_code='zeleria_new_year', frame_num=90, content_code=1, is_demo=0,
                    text={
                        'ru': 'Плевать! Просто плевать! Всё равно тут мало народа, и им никто не поверит! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='91')
    check.add_frame(game_code='zeleria_new_year', frame_num=91, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Наступление новой эры мы ознаменуем новым национ... великим праздником – Новым годом! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='92')
    check.add_frame(game_code='zeleria_new_year', frame_num=92, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: И мы отметим его с размахом! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='93')
    check.add_frame(game_code='zeleria_new_year', frame_num=93, content_code=1, is_demo=0,
                    text={
                        'ru': 'И эта дурочка туда же!'},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='94')
    check.add_frame(game_code='zeleria_new_year', frame_num=94, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я замолчал. Звенящая тишина и несколько пар зелёных глаз, с трепетом взирающих на меня с площади под балконом. Эффектное выступление, ничего не скажешь! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='95')
    check.add_frame(game_code='zeleria_new_year', frame_num=95, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Будь добр, скажи «С Новым годом!» '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='96')
    check.add_frame(game_code='zeleria_new_year', frame_num=96, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: С Новым годом! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='97')
    check.add_frame(game_code='zeleria_new_year', frame_num=97, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я с трудом сдержался, чтобы не вмазать ладонью себе по лицу. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='98')
    check.add_frame(game_code='zeleria_new_year', frame_num=98, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: С Наступающим! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='99')
    check.add_frame(game_code='zeleria_new_year', frame_num=100, content_code=1, is_demo=0,
                    text={
                        'ru': 'И в этот момент я понял, почему Хамки попросил меня выступить.'},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='101')
    check.add_frame(game_code='zeleria_new_year', frame_num=101, content_code=1, is_demo=0,
                    text={
                        'ru': 'Небо потемнело, солнце буквально испарилось с горизонта, погрузив всё во тьму, а проявившиеся звезды засверкали в несколько раз ярче, чем обычно. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='102')
    check.add_frame(game_code='zeleria_new_year', frame_num=103, content_code=1, is_demo=0,
                    text={
                        'ru': 'Несколько порывов ледяного ветра едва не сбили нас с ног, а перепуганная Лика вцепилась в меня, прижавшись всем телом. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='104')
    check.add_frame(game_code='zeleria_new_year', frame_num=105, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что-то сверкнуло впереди, и буквально перед балконом возникла огромная ёлка! Её макушка была намного выше, чем шпиль храма, а ровно перед нами теперь болтались пушистые хвойные ветки. '},
                    content='AgACAgIAAxkBAAIHxGSF2vgZrwzzEnxQ6P2ZrrH9FIBsAAKLyjEbYVgwSCMkbzEsNDP1AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='106')
    check.add_frame(game_code='zeleria_new_year', frame_num=106, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я медленно поднял голову, и первая снежинка попала мне прямо в глаз. '},
                    content='AgACAgIAAxkBAAIHxGSF2vgZrwzzEnxQ6P2ZrrH9FIBsAAKLyjEbYVgwSCMkbzEsNDP1AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='107')
    check.add_frame(game_code='zeleria_new_year', frame_num=107, content_code=1, is_demo=0,
                    text={
                        'ru': 'Снег! Кружась в воцарившемся безветрии, с совершенно безоблачного звездного неба падал снег! '},
                    content='AgACAgIAAxkBAAIHxGSF2vgZrwzzEnxQ6P2ZrrH9FIBsAAKLyjEbYVgwSCMkbzEsNDP1AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='108')
    check.add_frame(game_code='zeleria_new_year', frame_num=108, content_code=1, is_demo=0,
                    text={
                        'ru': 'Чёртов хомяк! Эта зверюга и впрямь сделала это! У нас будет Новый год! '},
                    content='AgACAgIAAxkBAAIHxGSF2vgZrwzzEnxQ6P2ZrrH9FIBsAAKLyjEbYVgwSCMkbzEsNDP1AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='109')
    check.add_frame(game_code='zeleria_new_year', frame_num=109, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: М... М... Макс! Новая эра... Она... Настанет без умари?.. Мы прогневили Салангана?.. '},
                    content='AgACAgIAAxkBAAIHxmSF2x0WSdd5mpIitdlI0714_qGiAAKMyjEbYVgwSK0z_qh_PwW9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='110')
    check.add_frame(game_code='zeleria_new_year', frame_num=110, content_code=1, is_demo=0,
                    text={
                        'ru': 'Во даёт! '},
                    content='AgACAgIAAxkBAAIHxmSF2x0WSdd5mpIitdlI0714_qGiAAKMyjEbYVgwSK0z_qh_PwW9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='111')
    check.add_frame(game_code='zeleria_new_year', frame_num=111, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Нет! Не бойся! Новый год – добрый и светлый праздник. В Новый год возможны любые чудеса! И обязательно хорошие!  '},
                    content='AgACAgIAAxkBAAIHxmSF2x0WSdd5mpIitdlI0714_qGiAAKMyjEbYVgwSK0z_qh_PwW9AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='112')
    check.add_frame(game_code='zeleria_new_year', frame_num=112, content_code=1, is_demo=0,
                    text={
                        'ru': 'Словно завороженный, я смотрел, как на исполинской ели, словно по волшебству, загораются свечки, появляются большие блестящие шары, разлетается по веткам «дождик» мишуры. '},
                    content='AgACAgIAAxkBAAIHyGSF2zl9N4A_vCaMJ6T-gbT5AW6xAAKNyjEbYVgwSHOMHihNcxzDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='123')
    check.add_frame(game_code='zeleria_new_year', frame_num=123, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Приятно знать, что не я один рад этому празднику! '},
                    content='AgACAgIAAxkBAAIHymSF20x2tpEMZcST5yAemNq0TFP6AAKOyjEbYVgwSOA2gpABB9WGAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='124')
    check.add_frame(game_code='zeleria_new_year', frame_num=124, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки, с непонятно откуда взявшимся красным колпаком на голове, сидел на перилах и смотрел на падающие снежинки. '},
                    content='AgACAgIAAxkBAAIHymSF20x2tpEMZcST5yAemNq0TFP6AAKOyjEbYVgwSOA2gpABB9WGAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='125')
    check.add_frame(game_code='zeleria_new_year', frame_num=125, content_code=1, is_demo=0,
                    text={
                        'ru': 'На его пушистой морде застыла улыбка. Не та, саркастичная, почти издевательская, а та счастливая умиротворённая улыбка, какая бывает у людей, вернувшихся в тепло родного дома после долгого отсутствия. '},
                    content='AgACAgIAAxkBAAIHymSF20x2tpEMZcST5yAemNq0TFP6AAKOyjEbYVgwSOA2gpABB9WGAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='126')
    check.add_frame(game_code='zeleria_new_year', frame_num=126, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Это мой первый Новый год за многие миллионы лет, Макс. Спасибо, что напомнил мне о нём... Я так счастлив...'},
                    content='AgACAgIAAxkBAAIHymSF20x2tpEMZcST5yAemNq0TFP6AAKOyjEbYVgwSOA2gpABB9WGAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='127')
    check.add_frame(game_code='zeleria_new_year', frame_num=127, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Чудеса?.. '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='128')
    check.add_frame(game_code='zeleria_new_year', frame_num=128, content_code=1, is_demo=0,
                    text={
                        'ru': 'Голос Лики ещё дрожал, но она сама уже почти не тряслась, хоть и по-прежнему прижималась ко мне. '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='129')
    check.add_frame(game_code='zeleria_new_year', frame_num=129, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Это правда? В Новый год случаются хорошие чудеса?.. '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='130')
    check.add_frame(game_code='zeleria_new_year', frame_num=130, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Да. И сбываются самые сокровенные мечты. '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='131')
    check.add_frame(game_code='zeleria_new_year', frame_num=131, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика замялась, явно собираясь сказать что-то серьёзное. '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='132')
    check.add_frame(game_code='zeleria_new_year', frame_num=132, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Тогда... Тогда могу я стать не просто верховной жрицей, но и... твоей женой? Я люблю тебя, Макс! '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='133')
    check.add_frame(game_code='zeleria_new_year', frame_num=133, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я повернулся и взглянул в её бездонные зелёные глаза. Наверное, и впрямь пора сказать ей это. '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='134')
    check.add_frame(game_code='zeleria_new_year', frame_num=134, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Да. Лика, я люблю тебя. Будь моей женой! '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='135')
    check.add_frame(game_code='zeleria_new_year', frame_num=135, content_code=1, is_demo=0,
                    text={
                        'ru': 'Девушка улыбнулась, а не её глазах блеснули слёзы. '},
                    content='AgACAgIAAxkBAAIHzGSF23LWfgva3qUGXgvcSzEWFo3PAAKRyjEbYVgwSMHScep6s1WAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='136')
    check.add_frame(game_code='zeleria_new_year', frame_num=136, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я склонил голову и поцеловал Лику. '},
                    content='AgACAgIAAxkBAAIHzmSF25oVRPU52V2RiZxSYr0f0HfqAAKTyjEbYVgwSIKOHOThst1IAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='137')
    check.add_frame(game_code='zeleria_new_year', frame_num=137, content_code=1, is_demo=0,
                    text={
                        'ru': 'Лика: Макс...'},
                    content='AgACAgIAAxkBAAIHzmSF25oVRPU52V2RiZxSYr0f0HfqAAKTyjEbYVgwSIKOHOThst1IAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='138')
    check.add_frame(game_code='zeleria_new_year', frame_num=138, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Лика...  '},
                    content='AgACAgIAAxkBAAIHzmSF25oVRPU52V2RiZxSYr0f0HfqAAKTyjEbYVgwSIKOHOThst1IAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='139')
    check.add_frame(game_code='zeleria_new_year', frame_num=139, content_code=1, is_demo=0,
                    text={
                        'ru': 'Мы стояли на балконе, слившись в страстном поцелуе. '},
                    content='AgACAgIAAxkBAAIHzmSF25oVRPU52V2RiZxSYr0f0HfqAAKTyjEbYVgwSIKOHOThst1IAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='140')
    check.add_frame(game_code='zeleria_new_year', frame_num=140, content_code=1, is_demo=0,
                    text={
                        'ru': 'Мне уже не было дела до происходящего вокруг. '},
                    content='AgACAgIAAxkBAAIHzmSF25oVRPU52V2RiZxSYr0f0HfqAAKTyjEbYVgwSIKOHOThst1IAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='141')
    check.add_frame(game_code='zeleria_new_year', frame_num=141, content_code=1, is_demo=0,
                    text={
                        'ru': 'В этот Новый год для нас с Ликой началась новая жизнь. '},
                    content='AgACAgIAAxkBAAIHzmSF25oVRPU52V2RiZxSYr0f0HfqAAKTyjEbYVgwSIKOHOThst1IAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='142')
    check.add_frame(game_code='zeleria_new_year', frame_num=80, content_code=1, is_demo=0,
                    text={
                        'ru': 'Счастливая жизнь.'},
                    content='AgACAgIAAxkBAAIHzmSF25oVRPU52V2RiZxSYr0f0HfqAAKTyjEbYVgwSIKOHOThst1IAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='143')
    check.add_frame(game_code='zeleria_new_year', frame_num=143, content_code=1, is_demo=0,
                    text={
                        'ru': 'Снег, которого планета не видела миллионы лет, безмолвно падал на уже припорошённую им траву. Хамки не беспокоился о последствиях – он знал, что созданный им холод – искусственный, праздничный, он никому не мог причинить вреда – от него было просто невозможно замёрзнуть  '},
                    content='AgACAgIAAxkBAAIH0GSF28c2H-YwdiYHQMnCaALFTdvcAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='144')
    check.add_frame(game_code='zeleria_new_year', frame_num=144, content_code=1, is_demo=0,
                    text={
                        'ru': 'И сейчас неописуемо счастливый и довольный саланганец сидел в сугробе под ёлкой и задумчиво смотрел в звездное небо. '},
                    content='AgACAgIAAxkBAAIH0GSF28c2H-YwdiYHQMnCaALFTdvcAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='145')
    check.add_frame(game_code='zeleria_new_year', frame_num=145, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эта ночь была волшебной и для него. То забытое чувство тепла и уюта, по которому древний зверь, к собственному удивлению, так соскучился. '},
                    content='AgACAgIAAxkBAAIH0GSF28c2H-YwdiYHQMnCaALFTdvcAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='146')
    check.add_frame(game_code='zeleria_new_year', frame_num=146, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Я люблю эту планету. '},
                    content='AgACAgIAAxkBAAIH0GSF28c2H-YwdiYHQMnCaALFTdvcAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='147')
    check.add_frame(game_code='zeleria_new_year', frame_num=147, content_code=1, is_demo=0,
                    text={
                        'ru': 'Он глубоко вздохнул и выпустил изо рта облачко пара. '},
                    content='AgACAgIAAxkBAAIH0GSF28c2H-YwdiYHQMnCaALFTdvcAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='147')
    check.add_frame(game_code='zeleria_new_year', frame_num=147, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Но тебя, моя милая Хемли, я люблю больше. Мне пора домой. Следующий Новый год мы отметим вместе. На Новом Салангане! '},
                    content='AgACAgIAAxkBAAIH0GSF28c2H-YwdiYHQMnCaALFTdvcAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='148')
    check.add_frame(game_code='zeleria_new_year', frame_num=147, content_code=1, is_demo=0,
                    text={
                        'ru': '... '},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='148')
    check.add_frame(game_code='zeleria_new_year', frame_num=80, content_code=1, is_demo=0,
                    text={
                        'ru': 'Впрочем, остальным обитателям Зелирии было не до маленьких радостей нового праздника.  '},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='149')
    check.add_frame(game_code='zeleria_new_year', frame_num=149, content_code=1, is_demo=0,
                    text={
                        'ru': 'Бесчисленные толпы зелирийцев и умари по всей планете в панике метались во внезапно воцарившейся тьме. '},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='150')
    check.add_frame(game_code='zeleria_new_year', frame_num=150, content_code=1, is_demo=0,
                    text={
                        'ru': 'Ледяные белые хлопья, падающие прямо с почерневшего неба, наводили на них животный ужас. '},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='151')
    check.add_frame(game_code='zeleria_new_year', frame_num=151, content_code=1, is_demo=0,
                    text={
                        'ru': 'Ставший ледяным воздух словно звенел от отчаяния, ведь от него нельзя было укрыться, он было буквально везде! '},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='152')
    check.add_frame(game_code='zeleria_new_year', frame_num=152, content_code=1, is_demo=0,
                    text={
                        'ru': 'Несчастные, они взывали ко всем мыслимым и немыслимым богам, лишь бы те смилостивились и не насылали на них ледяную смерть во тьме...'},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='153')
    check.add_frame(game_code='zeleria_new_year', frame_num=153, content_code=1, is_demo=0,
                    text={
                        'ru': '... '},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='154')
    check.add_frame(game_code='zeleria_new_year', frame_num=154, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки всегда мог выполнить свои прихоти, но никогда не умел думать о других и видеть дальше собственного носа. Даже на Новый год. '},
                    content='AgACAgIAAxkBAAIH0mSF2_0cCcGHVet1SDo4n-sibuktAAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='155')
    check.add_frame(game_code='zeleria_new_year', frame_num=155, content_code=1, is_demo=0,
                    text={
                        'ru': 'Друзья! Команда Salangan Games поздравляет вас с новым годом! '},
                    content='AgACAgIAAxkBAAIH1GSF3EfFm6NgD3AEni_UQwABJuW2qgAClsoxG2FYMEgui9sD4utPDgEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='156')
    check.add_frame(game_code='zeleria_new_year', frame_num=156, content_code=1, is_demo=0,
                    text={
                        'ru': 'И приглашает поиграть в нашу игру «Заповедник Зелирия»: https://store.steampowered.com/app/855630/Zeliria_Sanctuary/!'},
                    content='AgACAgIAAxkBAAIH1GSF3EfFm6NgD3AEni_UQwABJuW2qgAClsoxG2FYMEgui9sD4utPDgEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='157')
    check.add_frame(game_code='zeleria_new_year', frame_num=157, content_code=1, is_demo=0,
                    text={
                        'ru': 'А в следующем, 2022 году, мы порадуем вас второй частью игры – «Заповедник Зелирия 2: Убежище Ксинори»: https://store.steampowered.com/app/1256330/__2/!   '},
                    content='AgACAgIAAxkBAAIH1GSF3EfFm6NgD3AEni_UQwABJuW2qgAClsoxG2FYMEgui9sD4utPDgEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='158')
    check.add_frame(game_code='zeleria_new_year', frame_num=158, content_code=1, is_demo=0,
                    text={
                        'ru': 'Если вам понравилось – поддержите нас! https://www.patreon.com/salangan и https://vk.com/topic-66614302_40265703 . Приятные плюшки донаторам прилагаются!   '},
                    content='AgACAgIAAxkBAAIH1GSF3EfFm6NgD3AEni_UQwABJuW2qgAClsoxG2FYMEgui9sD4utPDgEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='-1')
    check.add_frame(game_code='zeleria_new_year', frame_num=159, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я вышел на балкон вдохнул прохладный вечерний воздух.  '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='160')
    check.add_frame(game_code='zeleria_new_year', frame_num=160, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: А дома сейчас зима, холодно... '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='161')
    check.add_frame(game_code='zeleria_new_year', frame_num=161, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Макс, с тобой всё в порядке? Ты сам не свой! Из-за туннеля расстроился, что ли?! '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='162')
    check.add_frame(game_code='zeleria_new_year', frame_num=162, content_code=1, is_demo=0,
                    text={
                        'ru': 'При всей своей энергичности и умении «видеть» собеседника, иногда Эйка ведёт себя странно. '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='163')
    check.add_frame(game_code='zeleria_new_year', frame_num=163, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Я тут подумала – ты всё ещё ни разу никого из нас не позвал к себе в ложе. Может тебе этого не хватает? '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='164')
    check.add_frame(game_code='zeleria_new_year', frame_num=164, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Можем исправить! '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='165')
    check.add_frame(game_code='zeleria_new_year', frame_num=165, content_code=1, is_demo=0,
                    text={
                        'ru': 'Классная смена темы!'},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='166')
    check.add_frame(game_code='zeleria_new_year', frame_num=166, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Нет-нет, не в этом дело. '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='167')
    check.add_frame(game_code='zeleria_new_year', frame_num=167, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Хм? '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='168')
    check.add_frame(game_code='zeleria_new_year', frame_num=168, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Ностальгия накатила просто. По зиме соскучился. В том мире откуда я родом сейчас зима, там холодно, идёт снег, а в эту ночь отмечается праздник – Новый год. Ну, знаешь, мы отмечаем дату, когда один год сменяется другим. '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='169')
    check.add_frame(game_code='zeleria_new_year', frame_num=169, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: У нас тоже есть такой. Только у нас это День нового урожая. Он тоже отделяет один год от другого. А что такое «снег»? '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='170')
    check.add_frame(game_code='zeleria_new_year', frame_num=170, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Снег? Это замёрзшая вода, кристаллики такие. Ты никогда его не видела. '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='171')
    check.add_frame(game_code='zeleria_new_year', frame_num=171, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Нет. Он вкусный? '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='172')
    check.add_frame(game_code='zeleria_new_year', frame_num=172, content_code=1, is_demo=0,
                    text={
                        'ru': 'Такой вопрос я скорее ожидал услышать от Хамки, а тут она. '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='173')
    check.add_frame(game_code='zeleria_new_year', frame_num=173, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Это всего лишь замерзшая вода, которая падает с неба, подобно дождю. Он холодный и безвкусный. '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='174')
    check.add_frame(game_code='zeleria_new_year', frame_num=174, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: И Новый год я привык отмечать, гуляя с друзьями по заснеженному городу, любуясь новогодней ёлкой, запуская праздничные фейерверки. '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='175')
    check.add_frame(game_code='zeleria_new_year', frame_num=175, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Ёлка? Это что такое? Сладость? Или какое-нибудь праздничное чучело?   '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='176')
    check.add_frame(game_code='zeleria_new_year', frame_num=176, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Нет! Это...  '},
                    content='AgACAgIAAxkBAAIH1mSF3Ns8-PwoY_ugQdfWHXM6LJDsAAKZyjEbYVgwSK7yulPV06eIAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='177')
    check.add_frame(game_code='zeleria_new_year', frame_num=177, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Ёлка? Снег? Да неужели!'},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='178')
    check.add_frame(game_code='zeleria_new_year', frame_num=178, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки целую неделю где-то шастал и возник у меня на плече только сейчас. Неужели услышал мои рассказы про Новый год?  '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='179')
    check.add_frame(game_code='zeleria_new_year', frame_num=179, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Что ты там говорил про «новый год»?  '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='180')
    check.add_frame(game_code='zeleria_new_year', frame_num=180, content_code=1, is_demo=0,
                    text={
                        'ru': 'Его удивлённые крики вопли раздавались исключительно у меня в сознании, потому что местные не только не видят Хамки, но и не слышат его. По сути, я единственный на всей планете, кто способен общаться с ним. В том числе телепатией – он читает мои мысли и транслирует мне в мозг свои. '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='181')
    check.add_frame(game_code='zeleria_new_year', frame_num=181, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Макс, что ты только что тут заливал Эйке? Ёлка? Фейерверки? Снег? Поди, у вас ещё и Древний Пустотник был, который подарки дарит!?'},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='182')
    check.add_frame(game_code='zeleria_new_year', frame_num=182, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Древний... кто?  '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='183')
    check.add_frame(game_code='zeleria_new_year', frame_num=183, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Древний Пустотник. Который ходит с мешком, где лежит Чёрная дыра, из которой он может вынуть любой предмет и подарить его тебе, если ты себя хорошо вёл. А если ты был плохим малышом – то он сложит в мешок тебя самого и ты навечно застрянешь в чёрной дыре! Просто сказочка, сам понимаешь, но… В детстве она очень хорошо мотивирует на прилежность!    '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='184')
    check.add_frame(game_code='zeleria_new_year', frame_num=184, content_code=1, is_demo=0,
                    text={
                        'ru': 'Видимо, за неимением религий и связанных с ними мифов, саланганцы придумали себе вот такое вот «псевдонаучное» существо. '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='185')
    check.add_frame(game_code='zeleria_new_year', frame_num=185, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Пустотника не было, зато был Дед Мороз. Но да, он тоже приходил к детям с мешком подарков. '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='186')
    check.add_frame(game_code='zeleria_new_year', frame_num=186, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Но он подобрее был – он непослушных детей в небытие не отправлял!  '},
                    content='AgACAgIAAxkBAAIH2GSF3TgOdzm616BfCbIGThQp0blrAAKcyjEbYVgwSImcrTzV-4rLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='187')
    check.add_frame(game_code='zeleria_new_year', frame_num=187, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Ого! Это же здорово! Впрочем, плевать, пора заняться делом! 	'},
                    content='AgACAgIAAxkBAAIHtGSF19CmBfjxjlD1VOPFcfH1sm8HAAJiyjEbYVgwSEeDMVRXQZ0AAQEAAwIAA3kAAy8E',
                    variants='Продолжить', variants_frame='188')
    check.add_frame(game_code='zeleria_new_year', frame_num=188, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Делом?..  '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='189')
    check.add_frame(game_code='zeleria_new_year', frame_num=189, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки): Да! Сейчас мы с тобой познакомим местных недоразвитых приматов со славными традициями разумных цивилизаций! '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='190')
    check.add_frame(game_code='zeleria_new_year', frame_num=190, content_code=1, is_demo=0,
                    text={
                        'ru': 'Это он человечество внезапно так в ранге поднял? Всё из-за подарков Деда Мороза? '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='191')
    check.add_frame(game_code='zeleria_new_year', frame_num=191, content_code=1, is_demo=0,
                    text={
                        'ru': 'Спрыгнув с моего плеча, Хамки заметался по каменным перилам, то воздевая лапы к небу, то мечтательно зажмуриваясь. Ой, не нравится мне его эта фонтанирующая энергия. '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='192')
    check.add_frame(game_code='zeleria_new_year', frame_num=192, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Значит и на Салангане праздновали Новый год? Интересное совпадение обычаев. '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='193')
    check.add_frame(game_code='zeleria_new_year', frame_num=193, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Конечно! На этот день контроллер погоды перенастраивали, и на все планете шёл снег! Мы играли в снежки, кувыркались в сугробах, лепили снеговиков! Дарили друг другу подарки, а детишки, отправляясь спать, ждали Древнего Пустотника, который положит им под ёлку подарки. '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='194')
    check.add_frame(game_code='zeleria_new_year', frame_num=194, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я представил полчища грызунов, закидывающих друг друга снежками и невольно улыбнулся. '},
                    content='AgACAgIAAxkBAAIHtmSF1_9Y1YY35KAlgqSpvcSYyMYVAAJkyjEbYVgwSJntjA6LkoVLAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='195')
    check.add_frame(game_code='zeleria_new_year', frame_num=195, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки : И что тут смешного? '},
                    content='AgACAgIAAxkBAAIHuGSF2Cpzxb4n4ymHhSFibTvmYsZ8AAJmyjEbYVgwSH8YQ4DejU72AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='196')
    check.add_frame(game_code='zeleria_new_year', frame_num=196, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Ничего! Просто представил толпу хомяков, отмечающих праздник... '},
                    content='AgACAgIAAxkBAAIHuGSF2Cpzxb4n4ymHhSFibTvmYsZ8AAJmyjEbYVgwSH8YQ4DejU72AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='197')
    check.add_frame(game_code='zeleria_new_year', frame_num=197, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Я НЕ ХОМЯК!!!'},
                    content='AgACAgIAAxkBAAIHumSF2LVOtQupvr-v8Y9zX3bC4tZAAAJoyjEbYVgwSBuCXm8k2D_CAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='198')
    check.add_frame(game_code='zeleria_new_year', frame_num=198, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Ладно, ладно. Саланганцев. И ещё я подумал о том, что сам встречал Новый год всегда именно так, как ты описал. И, знаешь, мне грустно, что здесь у нас ничего этого нет. '},
                    content='AgACAgIAAxkBAAIHumSF2LVOtQupvr-v8Y9zX3bC4tZAAAJoyjEbYVgwSBuCXm8k2D_CAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='199')
    check.add_frame(game_code='zeleria_new_year', frame_num=199, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Нет, говоришь...  '},
                    content='AgACAgIAAxkBAAIHvGSF2Piqh8ZjCtU5QXBwT5QHUzsqAAJpyjEbYVgwSFKG5PlpVkNSAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='200')
    check.add_frame(game_code='zeleria_new_year', frame_num=200, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Макс? Вы там общаетесь? '},
                    content='AgACAgIAAxkBAAIH2mSF3er7wQXEvsDlsc1jVEVUJ-rKAAKlyjEbYVgwSCGrH8045xEaAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='201')
    check.add_frame(game_code='zeleria_new_year', frame_num=201, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка уже привыкла к нашим с Хамки «молчаливым беседам», поэтому когда я внезапно «зависал» – просто ждала, когда я вновь обращу на неё внимание. Обычно это надоедало ей очень быстро. Всё же, не будучи умари, она хоть и принимала его как божество, но какого-то трепета не испытывала. И относилась скорее как к раздражающему фактору, каким он иногда и был.'},
                    content='AgACAgIAAxkBAAIH2mSF3er7wQXEvsDlsc1jVEVUJ-rKAAKlyjEbYVgwSCGrH8045xEaAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='202')
    check.add_frame(game_code='zeleria_new_year', frame_num=202, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Вы обсуждаете туннель?'},
                    content='AgACAgIAAxkBAAIH2mSF3er7wQXEvsDlsc1jVEVUJ-rKAAKlyjEbYVgwSCGrH8045xEaAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='203')
    check.add_frame(game_code='zeleria_new_year', frame_num=203, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Да срать мне на ваш туннель! Я вам сейчас наконец-то нормальный праздник организую!  '},
                    content='AgACAgIAAxkBAAIH2mSF3er7wQXEvsDlsc1jVEVUJ-rKAAKlyjEbYVgwSCGrH8045xEaAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='204')
    check.add_frame(game_code='zeleria_new_year', frame_num=204, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка этой фразы, конечно, не услышала. '},
                    content='AgACAgIAAxkBAAIH2mSF3er7wQXEvsDlsc1jVEVUJ-rKAAKlyjEbYVgwSCGrH8045xEaAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='205')
    check.add_frame(game_code='zeleria_new_year', frame_num=205, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Нет. У Хамки тут возникла одна хорошая идея.  '},
                    content='AgACAgIAAxkBAAIH3GSF3hdINcY25SrxXeEQhAxTcvNIAAK0yjEbYVgwSN5xTDLi9BkmAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='206')
    check.add_frame(game_code='zeleria_new_year', frame_num=206, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Эм? '},
                    content='AgACAgIAAxkBAAIH3GSF3hdINcY25SrxXeEQhAxTcvNIAAK0yjEbYVgwSN5xTDLi9BkmAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='207')
    check.add_frame(game_code='zeleria_new_year', frame_num=207, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Я только что рассказал тебе про Новый год. Его мы сегодня и отпразднуем! '},
                    content='AgACAgIAAxkBAAIH3GSF3hdINcY25SrxXeEQhAxTcvNIAAK0yjEbYVgwSN5xTDLi9BkmAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='208')
    check.add_frame(game_code='zeleria_new_year', frame_num=208, content_code=1, is_demo=0,
                    text={
                        'ru': 'И только сейчас до меня дошло...  '},
                    content='AgACAgIAAxkBAAIH3GSF3hdINcY25SrxXeEQhAxTcvNIAAK0yjEbYVgwSN5xTDLi9BkmAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='209')
    check.add_frame(game_code='zeleria_new_year', frame_num=209, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Хамки, у нас нет ни снега, ни ёлки, ни подарков. Как ты собирался создавать нам «атмосферу зимнего праздника»?  '},
                    content='AgACAgIAAxkBAAIHvGSF2Piqh8ZjCtU5QXBwT5QHUzsqAAJpyjEbYVgwSFKG5PlpVkNSAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='210')
    check.add_frame(game_code='zeleria_new_year', frame_num=210, content_code=1, is_demo=0,
                    text={
                        'ru': 'Фиолетовый зверь поднял на меня глаза, как бы говоря «ты ещё не понял?». Мне стало слегка не по себе. '},
                    content='AgACAgIAAxkBAAIHvGSF2Piqh8ZjCtU5QXBwT5QHUzsqAAJpyjEbYVgwSFKG5PlpVkNSAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='211')
    check.add_frame(game_code='zeleria_new_year', frame_num=211, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Хамки... '},
                    content='AgACAgIAAxkBAAIHvGSF2Piqh8ZjCtU5QXBwT5QHUzsqAAJpyjEbYVgwSFKG5PlpVkNSAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='212')
    check.add_frame(game_code='zeleria_new_year', frame_num=212, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки : Смотри и наслаждайся! Ты же сам хотел Новый год!  '},
                    content='AgACAgIAAxkBAAIHvGSF2Piqh8ZjCtU5QXBwT5QHUzsqAAJpyjEbYVgwSFKG5PlpVkNSAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='213')
    check.add_frame(game_code='zeleria_new_year', frame_num=213, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Хамки, подожди! '},
                    content='AgACAgIAAxkBAAIHvGSF2Piqh8ZjCtU5QXBwT5QHUzsqAAJpyjEbYVgwSFKG5PlpVkNSAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='214')
    check.add_frame(game_code='zeleria_new_year', frame_num=214, content_code=1, is_demo=0,
                    text={
                        'ru': 'Подумал я это слишком поздно – он уже испарился с подоконника. '},
                    content='AgACAgIAAxkBAAIHrGSF12J_uMFr87d3iZSdYCmso9-gAAJozjEbYVgoSNs1Zopg_vhXAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='215')
    check.add_frame(game_code='zeleria_new_year', frame_num=215, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что-то будет...'},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='216')
    check.add_frame(game_code='zeleria_new_year', frame_num=216, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Эйка, короче, постарайся не удивляться ничему, что сейчас произойдёт. '},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='217')
    check.add_frame(game_code='zeleria_new_year', frame_num=217, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: А что сейчас может произойти?!'},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='218')
    check.add_frame(game_code='zeleria_new_year', frame_num=218, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Всё, что угодно – Хамки посетила очередная гениальная идея как всех осчастливить. '},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='219')
    check.add_frame(game_code='zeleria_new_year', frame_num=219, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Переживут процесс, возможно, не все. '},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='220')
    check.add_frame(game_code='zeleria_new_year', frame_num=220, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Что?! '},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='221')
    check.add_frame(game_code='zeleria_new_year', frame_num=221, content_code=1, is_demo=0,
                    text={
                        'ru': 'Не успел я сказать, что это шутка, как вокруг начался форменный хаос. '},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='222')
    check.add_frame(game_code='zeleria_new_year', frame_num=222, content_code=1, is_demo=0,
                    text={
                        'ru': 'Небо потемнело, солнце буквально испарилось с горизонта, погрузив всё во тьму, а проявившиеся звезды засверкали в несколько раз ярче, чем обычно. '},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='223')
    check.add_frame(game_code='zeleria_new_year', frame_num=223, content_code=1, is_demo=0,
                    text={
                        'ru': 'Несколько порывов горячего ветра едва не сбили нас с ног, а перепуганная Эйка вцепилась в меня, прижавшись всем телом. '},
                    content='AgACAgIAAxkBAAIH3mSF3nL31LjUXQK0yDVYT_e03q-PAAK4yjEbYVgwSKty7bH5485iAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='224')
    check.add_frame(game_code='zeleria_new_year', frame_num=224, content_code=1, is_demo=0,
                    text={
                        'ru': 'Что-то сверкнуло впереди, и буквально перед балконом возникла огромная ёлка! Её макушка была намного выше, чем шпиль храма, а ровно перед нами теперь болтались пушистые хвойные ветки. '},
                    content='AgACAgIAAxkBAAIH4GSF3sEXzzIZW5cib4FckPt0gjbgAAK9yjEbYVgwSL9Q-FSFuXtwAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='225')
    check.add_frame(game_code='zeleria_new_year', frame_num=225, content_code=1, is_demo=0,
                    text={
                        'ru': 'Нет! Это не ёлка! Ветви были неестественного кроваво-красного цвета!  '},
                    content='AgACAgIAAxkBAAIH4GSF3sEXzzIZW5cib4FckPt0gjbgAAK9yjEbYVgwSL9Q-FSFuXtwAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='226')
    check.add_frame(game_code='zeleria_new_year', frame_num=226, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Аааай! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='227')
    check.add_frame(game_code='zeleria_new_year', frame_num=227, content_code=1, is_demo=0,
                    text={
                        'ru': 'Она ещё сильнее вжалась в меня, ткнувшись лицом в грудь. Я сам не дёргался лишь потому, что был твёрдо уверен – какую бы глупость ни задумал Хамки – пострадавших он не допустит. '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='228')
    check.add_frame(game_code='zeleria_new_year', frame_num=228, content_code=1, is_demo=0,
                    text={
                        'ru': 'Но нарастающий жар от горячего ветра всё быстрее рассеивал и мою уверенность. '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='229')
    check.add_frame(game_code='zeleria_new_year', frame_num=229, content_code=1, is_demo=0,
                    text={
                        'ru': 'Но нарастающий жар от горячего ветра всё быстрее рассеивал и мою уверенность. '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='230')
    check.add_frame(game_code='zeleria_new_year', frame_num=230, content_code=1, is_demo=0,
                    text={
                        'ru': 'И Эйке прямо в незакрытую платьем спину. '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='231')
    check.add_frame(game_code='zeleria_new_year', frame_num=231, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Горячий снег?! Что за дрянь?! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='232')
    check.add_frame(game_code='zeleria_new_year', frame_num=232, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Макс! Что творится?! Хамки решил на радостях нас всех поубивать?! В жертву принести?! Успокой его!  '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='233')
    check.add_frame(game_code='zeleria_new_year', frame_num=233, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Горячо!  '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='234')
    check.add_frame(game_code='zeleria_new_year', frame_num=234, content_code=1, is_demo=0,
                    text={
                        'ru': 'Снег? Нет, что-то другое! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='235')
    check.add_frame(game_code='zeleria_new_year', frame_num=235, content_code=1, is_demo=0,
                    text={
                        'ru': 'Кружась в мгновенно воцарившемся безветрии, с совершенно безоблачного звёздного неба падали горячие красные хлопья! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='236')
    check.add_frame(game_code='zeleria_new_year', frame_num=236, content_code=1, is_demo=0,
                    text={
                        'ru': 'Чёртов хомяк! Что он устроил?! Что вообще происходит?! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='237')
    check.add_frame(game_code='zeleria_new_year', frame_num=237, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Макс! Да сделай же что-нибудь! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='238')
    check.add_frame(game_code='zeleria_new_year', frame_num=238, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Хамки, твою мать! Останови это безумие! БЫСТРО!!! '},
                    content='AgACAgIAAxkBAAIH4GSF3sEXzzIZW5cib4FckPt0gjbgAAK9yjEbYVgwSL9Q-FSFuXtwAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='239')
    check.add_frame(game_code='zeleria_new_year', frame_num=239, content_code=1, is_demo=0,
                    text={
                        'ru': 'Мохнатая тварюшка послушно материализовалась на перилах. '},
                    content='AgACAgIAAxkBAAIH4GSF3sEXzzIZW5cib4FckPt0gjbgAAK9yjEbYVgwSL9Q-FSFuXtwAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='240')
    check.add_frame(game_code='zeleria_new_year', frame_num=240, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Чего ты развопился, Макс? Ты просил ёлку – вот она стоит, украшения прилагаются. Хотел снега? Пожалуйста – вон он, с неба падает, всё как положено! Что за нелепая истерика? '},
                    content='AgACAgIAAxkBAAIH5GSF3yytuVZhWO5Z6hTCLRcnT_rGAAK_yjEbYVgwSNSIRua6XJlTAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='241')
    check.add_frame(game_code='zeleria_new_year', frame_num=241, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка прижалась ко мне, боясь даже оглянуться. '},
                    content='AgACAgIAAxkBAAIH5GSF3yytuVZhWO5Z6hTCLRcnT_rGAAK_yjEbYVgwSNSIRua6XJlTAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='242')
    check.add_frame(game_code='zeleria_new_year', frame_num=242, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Это не ёлка! Ёлки зеленые! Это не снег! Он белый и холодный! '},
                    content='AgACAgIAAxkBAAIH5GSF3yytuVZhWO5Z6hTCLRcnT_rGAAK_yjEbYVgwSNSIRua6XJlTAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='243')
    check.add_frame(game_code='zeleria_new_year', frame_num=243, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Что за чушь ты несёшь?! Тёплые новогодние сугробы – что может быть лучше? Ты иногда ведешь себя как полный идиот, Макс! '},
                    content='AgACAgIAAxkBAAIH5mSF31k7hkYPdhY4Z9RNBKjyyAkjAALdyjEbYVgwSEx4SpFH3UA1AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='244')
    check.add_frame(game_code='zeleria_new_year', frame_num=244, content_code=1, is_demo=0,
                    text={
                        'ru': 'Он тут вместо новогодней сказки создал подобие кровавого ада, а идиот всё равно я?! '},
                    content='AgACAgIAAxkBAAIH5mSF31k7hkYPdhY4Z9RNBKjyyAkjAALdyjEbYVgwSEx4SpFH3UA1AQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='245')
    check.add_frame(game_code='zeleria_new_year', frame_num=245, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: У нас с тобой очень разные представления про Новый год! '},
                    content='',
                    variants='Продолжить', variants_frame='246')
    check.add_frame(game_code='zeleria_new_year', frame_num=246, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я развернулся к Эйке. '},
                    content='AgACAgIAAxkBAAIH4GSF3sEXzzIZW5cib4FckPt0gjbgAAK9yjEbYVgwSL9Q-FSFuXtwAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='247')
    check.add_frame(game_code='zeleria_new_year', frame_num=247, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Эйка, Хамки опять всё сделал не так! Ничего страшного не происходит, не бойся, но я просто не хочу участвовать в этом дурдоме! Хватит с меня таких «чудес»! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='248')
    check.add_frame(game_code='zeleria_new_year', frame_num=248, content_code=1, is_demo=0,
                    text={
                        'ru': 'И тут меня осенило! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='249')
    check.add_frame(game_code='zeleria_new_year', frame_num=249, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Давай сбежим отсюда! '},
                    content='AgACAgIAAxkBAAIH4mSF3uFUDkrSqYlu7_Vg5rwOims9AAK-yjEbYVgwSITVuPd4Sz2uAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='250')
    check.add_frame(game_code='zeleria_new_year', frame_num=250, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Сбежим? '},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='251')
    check.add_frame(game_code='zeleria_new_year', frame_num=251, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Да! Прямо сейчас! Устроим себе каникулы, которые всегда бывают на Новый год в моём мире! '},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='252')
    check.add_frame(game_code='zeleria_new_year', frame_num=252, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Но куда?!  '},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='253')
    check.add_frame(game_code='zeleria_new_year', frame_num=253, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Давай наведаемся в гости к Иссе. Уверен, он будет рад нас видеть! '},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='254')
    check.add_frame(game_code='zeleria_new_year', frame_num=254, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Странный, ты, Макс. '},
                    content='AgACAgIAAxkBAAIH6mSF3-FdqBYWnBq4dvVYMf6AVLGNAALfyjEbYVgwSNtdF2MXe1gNAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='255')
    check.add_frame(game_code='zeleria_new_year', frame_num=255, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я не стал обращать на него внимания. '},
                    content='AgACAgIAAxkBAAIH6mSF3-FdqBYWnBq4dvVYMf6AVLGNAALfyjEbYVgwSNtdF2MXe1gNAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='256')
    check.add_frame(game_code='zeleria_new_year', frame_num=256, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: А как же все твои дела и обязанности? '},
                    content='AgACAgIAAxkBAAIH7GSF3_FWcJPZZkJn0q9IwLONUzkyAALgyjEbYVgwSBf2UUqW7hlAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='257')
    check.add_frame(game_code='zeleria_new_year', frame_num=257, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Подождут. Давай просто проведем время вместе. Это должен быть светлый и тихий праздник, где сбываются сокровенные мечты... А не вот это вот всё!  '},
                    content='AgACAgIAAxkBAAIH7GSF3_FWcJPZZkJn0q9IwLONUzkyAALgyjEbYVgwSBf2UUqW7hlAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='258')
    check.add_frame(game_code='zeleria_new_year', frame_num=258, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Сокровенные мечты... А что, если моя сокровенная мечта, чтобы ты женился на мне. Она исполнится сегодня, Макс? '},
                    content='AgACAgIAAxkBAAIH7GSF3_FWcJPZZkJn0q9IwLONUzkyAALgyjEbYVgwSBf2UUqW7hlAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='259')
    check.add_frame(game_code='zeleria_new_year', frame_num=259, content_code=1, is_demo=0,
                    text={
                        'ru': 'Да.'},
                    content='AgACAgIAAxkBAAIH7GSF3_FWcJPZZkJn0q9IwLONUzkyAALgyjEbYVgwSBf2UUqW7hlAAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='260')
    check.add_frame(game_code='zeleria_new_year', frame_num=260, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я повернулся и взглянул в её удивлённые глаза. И чего я раньше тянул?  '},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='261')
    check.add_frame(game_code='zeleria_new_year', frame_num=261, content_code=1, is_demo=0,
                    text={
                        'ru': 'Макс: Эйка, ты слишком странная, чтобы можно было не влюбиться в тебя. Выходи за меня замуж! '},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='262')
    check.add_frame(game_code='zeleria_new_year', frame_num=262, content_code=1, is_demo=0,
                    text={
                        'ru': 'Глаза Эйки округлились ещё больше'},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='263')
    check.add_frame(game_code='zeleria_new_year', frame_num=263, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эйка: Правда?! Можно?! Здорово! Я согласна!  '},
                    content='AgACAgIAAxkBAAIH6GSF38MHFY5yod4xpw_mFlXurYWvAALeyjEbYVgwSCYt4OHq4-XDAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='264')
    check.add_frame(game_code='zeleria_new_year', frame_num=264, content_code=1, is_demo=0,
                    text={
                        'ru': 'Я склонил голову и поцеловал Эйку.'},
                    content='AgACAgIAAxkBAAIH7mSF4DM3LWfwtkqnVnoP-5_PmCpnAALiyjEbYVgwSOa3P6K-jeqOAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='265')
    check.add_frame(game_code='zeleria_new_year', frame_num=265, content_code=1, is_demo=0,
                    text={
                        'ru': ' ... '},
                    content='',
                    variants='Продолжить', variants_frame='266')
    check.add_frame(game_code='zeleria_new_year', frame_num=266, content_code=1, is_demo=0,
                    text={
                        'ru': 'Мы стояли на балконе, слившись в страстном поцелуе. '},
                    content='AgACAgIAAxkBAAIH7mSF4DM3LWfwtkqnVnoP-5_PmCpnAALiyjEbYVgwSOa3P6K-jeqOAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='267')
    check.add_frame(game_code='zeleria_new_year', frame_num=267, content_code=1, is_demo=0,
                    text={
                        'ru': 'Мне уже не было дела до происходящего вокруг. '},
                    content='AgACAgIAAxkBAAIH7mSF4DM3LWfwtkqnVnoP-5_PmCpnAALiyjEbYVgwSOa3P6K-jeqOAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='268')
    check.add_frame(game_code='zeleria_new_year', frame_num=268, content_code=1, is_demo=0,
                    text={
                        'ru': 'В этот Новый год для нас с Эйкой началась новая жизнь. '},
                    content='AgACAgIAAxkBAAIH7mSF4DM3LWfwtkqnVnoP-5_PmCpnAALiyjEbYVgwSOa3P6K-jeqOAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='269')
    check.add_frame(game_code='zeleria_new_year', frame_num=269, content_code=1, is_demo=0,
                    text={
                        'ru': '...'},
                    content='AgACAgIAAxkBAAIH7mSF4DM3LWfwtkqnVnoP-5_PmCpnAALiyjEbYVgwSOa3P6K-jeqOAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='270')
    check.add_frame(game_code='zeleria_new_year', frame_num=270, content_code=1, is_demo=0,
                    text={
                        'ru': 'Снег, которого планета не видела миллионы лет, безмолвно падал на уже припорошённую им траву. Хамки не беспокоился о последствиях – он знал, что созданный им жар – искусственный, праздничный, он никому не мог причинить вреда – от него было просто невозможно обжечься.   '},
                    content='AgACAgIAAxkBAAIH8GSF4GfsRCtV9y41dzHBlpschC7SAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='271')
    check.add_frame(game_code='zeleria_new_year', frame_num=271, content_code=1, is_demo=0,
                    text={
                        'ru': 'И сейчас неописуемо счастливый и довольный саланганец сидел в сугробе под ёлкой и задумчиво смотрел в звездное небо. '},
                    content='AgACAgIAAxkBAAIH8GSF4GfsRCtV9y41dzHBlpschC7SAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='272')
    check.add_frame(game_code='zeleria_new_year', frame_num=272, content_code=1, is_demo=0,
                    text={
                        'ru': 'Эта ночь была волшебной и для него. То забытое чувство тепла и уюта, по которому древний зверь, к собственному удивлению, так соскучился. '},
                    content='AgACAgIAAxkBAAIH8GSF4GfsRCtV9y41dzHBlpschC7SAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='273')
    check.add_frame(game_code='zeleria_new_year', frame_num=273, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Я люблю эту планету. '},
                    content='AgACAgIAAxkBAAIH8GSF4GfsRCtV9y41dzHBlpschC7SAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='274')
    check.add_frame(game_code='zeleria_new_year', frame_num=274, content_code=1, is_demo=0,
                    text={
                        'ru': 'Он глубоко вздохнул и выпустил изо рта облачко пара. '},
                    content='AgACAgIAAxkBAAIH8GSF4GfsRCtV9y41dzHBlpschC7SAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='275')
    check.add_frame(game_code='zeleria_new_year', frame_num=275, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки: Но тебя, моя милая Хемли, я люблю больше. Мне пора домой. Следующий Новый год мы отметим вместе. На Новом Салангане! '},
                    content='AgACAgIAAxkBAAIH8GSF4GfsRCtV9y41dzHBlpschC7SAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='276')
    check.add_frame(game_code='zeleria_new_year', frame_num=276, content_code=1, is_demo=0,
                    text={
                        'ru': '... '},
                    content='AgACAgIAAxkBAAIH8GSF4GfsRCtV9y41dzHBlpschC7SAAKUyjEbYVgwSPEiHWSyT0DtAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='277')
    check.add_frame(game_code='zeleria_new_year', frame_num=277, content_code=1, is_demo=0,
                    text={
                        'ru': 'Впрочем, остальным обитателям Зелирии было не до маленьких радостей нового праздника.  '},
                    content='AgACAgIAAxkBAAIH8mSF4JD8V3J68GoIIPOSGNYtnU2_AAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='278')
    check.add_frame(game_code='zeleria_new_year', frame_num=278, content_code=1, is_demo=0,
                    text={
                        'ru': 'Бесчисленные толпы зелирийцев и умари по всей планете в панике метались во внезапно воцарившейся тьме. '},
                    content='AgACAgIAAxkBAAIH8mSF4JD8V3J68GoIIPOSGNYtnU2_AAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='279')
    check.add_frame(game_code='zeleria_new_year', frame_num=279, content_code=1, is_demo=0,
                    text={
                        'ru': 'Обжигающие красные хлопья, падающие прямо с почерневшего неба, наводили на них животный ужас. '},
                    content='AgACAgIAAxkBAAIH8mSF4JD8V3J68GoIIPOSGNYtnU2_AAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='280')
    check.add_frame(game_code='zeleria_new_year', frame_num=280, content_code=1, is_demo=0,
                    text={
                        'ru': 'Ставший горячим воздух словно звенел от отчаяния, ведь от него нельзя было укрыться, он было буквально везде! '},
                    content='AgACAgIAAxkBAAIH8mSF4JD8V3J68GoIIPOSGNYtnU2_AAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='281')
    check.add_frame(game_code='zeleria_new_year', frame_num=281, content_code=1, is_demo=0,
                    text={
                        'ru': 'Несчастные, они взывали ко всем мыслимым и немыслимым богам, лишь бы те смилостивились и не насылали на них смерть в адском пекле...'},
                    content='AgACAgIAAxkBAAIH8mSF4JD8V3J68GoIIPOSGNYtnU2_AAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='282')
    check.add_frame(game_code='zeleria_new_year', frame_num=282, content_code=1, is_demo=0,
                    text={
                        'ru': '... '},
                    content='AgACAgIAAxkBAAIH8mSF4JD8V3J68GoIIPOSGNYtnU2_AAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='283')
    check.add_frame(game_code='zeleria_new_year', frame_num=283, content_code=1, is_demo=0,
                    text={
                        'ru': 'Хамки всегда мог выполнить свои прихоти, но никогда не умел думать о других и видеть дальше собственного носа. Даже на Новый год. '},
                    content='AgACAgIAAxkBAAIH8mSF4JD8V3J68GoIIPOSGNYtnU2_AAKVyjEbYVgwSJEgiLieXkUBAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='284')
    check.add_frame(game_code='zeleria_new_year', frame_num=284, content_code=1, is_demo=0,
                    text={
                        'ru': 'Друзья! Команда Salangan Games поздравляет вас с новым годом! '},
                    content='AgACAgIAAxkBAAIH9GSF4LDSYpZmtUj2KQ1O1aeCfh4EAAKWyjEbYVgwSC6L2wPi608OAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='285')
    check.add_frame(game_code='zeleria_new_year', frame_num=285, content_code=1, is_demo=0,
                    text={
                        'ru': 'И приглашает поиграть в нашу игру «Заповедник Зелирия»: https://store.steampowered.com/app/855630/Zeliria_Sanctuary/!'},
                    content='AgACAgIAAxkBAAIH9GSF4LDSYpZmtUj2KQ1O1aeCfh4EAAKWyjEbYVgwSC6L2wPi608OAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='286')
    check.add_frame(game_code='zeleria_new_year', frame_num=286, content_code=1, is_demo=0,
                    text={
                        'ru': 'А в следующем, 2022 году, мы порадуем вас второй частью игры – «Заповедник Зелирия 2: Убежище Ксинори»: https://store.steampowered.com/app/1256330/__2/!   '},
                    content='AgACAgIAAxkBAAIH9GSF4LDSYpZmtUj2KQ1O1aeCfh4EAAKWyjEbYVgwSC6L2wPi608OAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='287')
    check.add_frame(game_code='zeleria_new_year', frame_num=287, content_code=1, is_demo=0,
                    text={
                        'ru': 'Если вам понравилось – поддержите нас! https://www.patreon.com/salangan и https://vk.com/topic-66614302_40265703 . Приятные плюшки донаторам прилагаются!   '},
                    content='AgACAgIAAxkBAAIH9GSF4LDSYpZmtUj2KQ1O1aeCfh4EAAKWyjEbYVgwSC6L2wPi608OAQADAgADeQADLwQ',
                    variants='Продолжить', variants_frame='-2')

    # check.return_genres()
    # check.add_frame(game_code='param_pam',frame_num=1,is_demo=1,content_code=0,text={'ru':'Просто проверочка'}, variants='Я\nТы', variants_frame='2\n3')
    # check.add_frame(game_code='param_pam',frame_num=2,is_demo=0,content_code=0,text={'ru':'Ты эгоист. \nБудем это знать'}, variants='Боль', variants_frame='5')
    # check.add_frame(game_code='param_pam',frame_num=3,is_demo=0,content_code=0,text={'ru':'Так ты подстилка. \nКак же славно, молодой раб'}, variants='Разочарование', variants_frame='5')


    # for i in check.return_user_library_games(483058216):
    #     print(i['game_name'])

    #
    # game_name = input('Game: ')
    # for i in check.search_game_by_name(game_name):
    #     print(i['game_name'])
    #


    # check.add_game(code='zeleria_new_year',can_buy=0, name='С новым годом зелирия', description='«С Новым годом, Зелирия!» – это новогодняя сказка и в то же время небольшой спин-офф первой части игры Zeliria Sactuary.', cover='AgACAgIAAxkBAAIEN2SFckcHPQhyoyG0wtesNe9YQDa0AALLxzEbW04xSMJeXS9r4p5pAQADAgADeAADLwQ\nAgACAgIAAxkBAAIEOWSFclnQZcYMchS4xkKqNAXWmJ75AALOxzEbW04xSM23JpSY2qdYAQADAgADeAADLwQ\nAgACAgIAAxkBAAIEO2SFcmU8qQNx24dK4DyPILWMMIOKAALPxzEbW04xSFS1YbTMyYogAQADAgADeAADLwQ\nAgACAgIAAxkBAAIEPWSFcnWR3dhJbmDBqURb9jtniCrqAALQxzEbW04xSJqkJwHCRyfkAQADAgADeAADLwQ', genre_code='adventures',genre='Приключения',creator='Salangan Games',price=0,config={}, publisher='Phoenix_co',discount=0)
    # check.add_game(code='zapovednik_zalerii',can_buy=0, name='Заповедник Зелирии', description='Осознание реальности еще не вернулось после эксперимента по телепортации. Фиолетовые хомяки, девушки с хвостами, средневековые рыцари - фантастический мир чужой планеты, по которой вы поведете спецназовца Макса', cover='AgACAgIAAxkBAAIEP2SFct88eoJDQVUCuHuj5zEo5VcfAALRxzEbW04xSO-CDVxXPZVEAQADAgADeAADLwQ\nAgACAgIAAxkBAAIEQWSFcutr8PrgkHU-s7OWSy82rKwjAALSxzEbW04xSCn7fYrwUAbzAQADAgADeQADLwQ\nAgACAgIAAxkBAAIEQ2SFcvVgjxgwObIf0ZhNdXowfI3vAALTxzEbW04xSFcy5Hmv1bVdAQADAgADeAADLwQ\nAgACAgIAAxkBAAIERWSFcv7Jm7pHAodc4HKlUT_0S4tDAALUxzEbW04xSMMyQiAbfqpaAQADAgADeAADLwQ', genre_code='adventures',genre='Приключения',creator='Salangan Games',price=339,config={}, publisher='Phoenix_co',discount=0)
    # check.add_game(code='shadows_of_lost_world',can_buy=0, name='Тени затерянного мира', description='"Тени затерянного мира"—игра в жанре пост-апокалипсис. Разгадайте тайну машины, которая предсказала дату, начала конца.', cover='AgACAgIAAxkBAAIET2SFdCIpqm01cTQpLRd39ObTluzhAALaxzEbW04xSIjUExZ6vpYeAQADAgADeQADLwQ\nAgACAgIAAxkBAAIEUWSFdC1dktH3PXxooE3juIFwjqw9AALbxzEbW04xSHyH50c51RkLAQADAgADeQADLwQ\nAgACAgIAAxkBAAIEU2SFdDtoM8Rgjg8ypPBnmT29Y_KQAALdxzEbW04xSCDncVWIf42QAQADAgADeQADLwQ\nAgACAgIAAxkBAAIEVWSFdEuiBFaxPsueJZ63If3W2OPZAALexzEbW04xSIZngn4gjazNAQADAgADeQADLwQ', genre_code='post_apocalypses',genre='Пост-Апокалипсис',creator=' BORCH Studio',price=149,config={}, publisher=' BORCH Studio ',discount=0)
    # check.add_game(code='1997',can_buy=0, name='1997', description='Визуальная новелла-детектив про тайны городка в России 90-х в стиле аниме.', cover='AgACAgIAAxkBAAIER2SFc18AAZgX9PH34LlCRLCX-Sr-agAC1scxG1tOMUglO_p9fHf1EQEAAwIAA3gAAy8E\nAgACAgIAAxkBAAIESWSFc3BrdrFcHqOe_XDAAqbZmn1qAALXxzEbW04xSMDg42E7-pr_AQADAgADeQADLwQ\nAgACAgIAAxkBAAIES2SFc34O8tePixY_kz01ZczbgDy3AALYxzEbW04xSEzHN7ZhkRlpAQADAgADeQADLwQ\nAgACAgIAAxkBAAIETWSFc43cZxrBGYgKDDUj4dysPomSAALZxzEbW04xSGxF5vAw78pRAQADAgADeQADLwQ', genre_code='detective',genre='Детектив',creator='Hit\'n\'Run Digital Studio, RUZURA Interactive',price=259,config={}, publisher='Hit\'n\'Run Digital Studio',discount=0)

    # check.add_game(code='guide_store',can_buy=0, name='Обучение правилам магазина', description='Это обучающий продукт, что расскажет вам о нашем магазине.', cover='AgACAgIAAxkBAAIDkWSFX-SFGTYUga7qaew-QGHuGya1AAKUxzEbW04xSFGbj_VtXqsJAQADAgADeAADLwQ', genre_code='off_guides',genre='Официальные инструкции',creator='Borch Store',price=0,config={}, publisher='Borch Store',discount=0)

    # check.add_game(code='silent',can_buy=0, name='Помолчим', description='Молчание', cover='AgACAgIAAxkBAAIDkWSFX-SFGTYUga7qaew-QGHuGya1AAKUxzEbW04xSFGbj_VtXqsJAQADAgADeAADLwQ', genre_code='test',genre='Проверка',creator='Test',price=0,config={}, publisher='Test',discount=0)

    #check.add_game(code='cool', name='Cool game', description='Игра, что вернула мне жизнь', cover='BAACAgIAAxkBAANgZIQNvW-Wqtz3-7B3_Aa_EfVBHfwAAowrAAJtuCFI_K_v-jdfKlQvBA\nAgACAgIAAxkBAANkZIQN0TZFoDrorfr9EumGuN_FPs0AAhnHMRttuCFIjwbJJG8er1wBAAMCAAN4AAMvBA', genre_code='kok',genre='Для любителей покрепче',creator='Ваша жизнь',price=0,config=game_config, publisher='Ваш дом',discount=0)
    # check.add_game(code='pim_pam', name='Jojo sim', description='Крутая игра для всех', cover='AgACAgIAAxkBAAMHZIOzWevS-gGso07A2fbOQtcLmEMAAkvIMRso9iFIjTr7ebImDK4BAAMCAAN5AAMvBA', genre_code='hohma',genre='Хохма',creator='Me',price=0,config=game_config, publisher='Me',discount=0)
    # check.add_game(code='param_pam', name='Bus simulator', description='Здесь просят деньги, просто уйдите', can_buy=1,cover='AgACAgIAAxkBAAIDzGSFZkltqub9IJ9up44fBZJflti4AAKgyjEbW04pSMaXeCFs5lfJAQADAgADeQADLwQ', genre_code='paid',genre='Донатный мусор',creator='Доллар',price=100,config={}, publisher='ЦБ Мира', discount=0)

    #
    # check.give_game_to_user(game_code='param_pam', user_id=483058216, is_demo=1)
    # check.give_game_to_user(game_code='pim_pam', user_id=483058216, is_demo=1)
    # check.give_game_to_user(game_code='f', user_id=483058216, is_demo=0)
    # print(check.return_user_info(483058216)['games_config'])

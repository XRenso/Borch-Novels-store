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

            elif check != 0 and is_demo == 0 and check[game_code]['is_demo'] == 1:
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
        for i in library:
            if i['game_code'] == game_code:
                return 1
        return 0


    def return_genres(self):
        return self.game.distinct('genre_code')
    def return_game_by_genre(self, genre_code):
        return self.game.find({'genre_code':genre_code})

if __name__ == '__main__':
    print('Тест')
    check = Mongo()
    check.__init__()

    # check.add_frame(game_code='param_pam',frame_num=1,is_demo=0,content_code=0,text={'ru':'Просто проверочка'}, variants='Я\nТы', variants_frame='2\n3')
    # check.add_frame(game_code='param_pam',frame_num=2,is_demo=0,content_code=0,text={'ru':'Ты эгоист. \nБудем это знать'}, variants='Боль', variants_frame='5')
    # check.add_frame(game_code='param_pam',frame_num=3,is_demo=0,content_code=0,text={'ru':'Так ты подстилка. \nКак же славно, молодой раб'}, variants='Разочарование', variants_frame='5')


    # for i in check.return_user_library_games(483058216):
    #     print(i['game_name'])

    #
    # game_name = input('Game: ')
    # for i in check.search_game_by_name(game_name):
    #     print(i['game_name'])
    #

    game_config = {
        'super_bas': ['joper'],
        'tis':5
    }

    check.add_game(code='monster',can_buy=1, name='Если бы море было водкой', description='Игра, что уничтожила здравый смысл. \nНе стоит в это играть', cover='AgACAgIAAxkBAAIClmSFLbAv9IGCpIIRJ7lw2Ud1r68pAAK4yjEbW04pSBssKYYPFrkQAQADAgADeAADLwQ', genre_code='paid',genre='Донатные помойки',creator='Борис Водка',price=300,config=game_config, publisher='Завод №297 им. Гнилой Водяры',discount=0)

    #check.add_game(code='cool', name='Cool game', description='Игра, что вернула мне жизнь', cover='BAACAgIAAxkBAANgZIQNvW-Wqtz3-7B3_Aa_EfVBHfwAAowrAAJtuCFI_K_v-jdfKlQvBA\nAgACAgIAAxkBAANkZIQN0TZFoDrorfr9EumGuN_FPs0AAhnHMRttuCFIjwbJJG8er1wBAAMCAAN4AAMvBA', genre_code='kok',genre='Для любителей покрепче',creator='Ваша жизнь',price=0,config=game_config, publisher='Ваш дом',discount=0)
    # check.add_game(code='pim_pam', name='Jojo sim', description='Крутая игра для всех', cover='AgACAgIAAxkBAAMHZIOzWevS-gGso07A2fbOQtcLmEMAAkvIMRso9iFIjTr7ebImDK4BAAMCAAN5AAMvBA', genre_code='hohma',genre='Хохма',creator='Me',price=0,config=game_config, publisher='Me',discount=0)
    check.add_game(code='param_pam', name='Bus simulator', description='Крутая игра для всех', can_buy=0,cover='AgACAgIAAxkBAAMHZIOzWevS-gGso07A2fbOQtcLmEMAAkvIMRso9iFIjTr7ebImDK4BAAMCAAN5AAMvBA', genre_code='hohma',genre='Хохма',creator='Me',price=0,config=game_config, publisher='Me', discount=0)
    #
    #
    # check.give_game_to_user(game_code='param_pam', user_id=483058216, is_demo=1)
    # check.give_game_to_user(game_code='pim_pam', user_id=483058216, is_demo=1)
    # check.give_game_to_user(game_code='f', user_id=483058216, is_demo=0)
    # print(check.return_user_info(483058216)['games_config'])

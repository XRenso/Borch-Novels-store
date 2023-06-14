import pymongo
import re
class Mongo:
    def __init__(self):
        self.connection = pymongo.MongoClient("mongodb://admin:safeKillPassword@79.143.29.191/admin")['store']
        self.user = self.connection['user']
        self.frame = self.connection['frame']
        self.game = self.connection['game']
        self.achivement = self.connection['achivement']


    def add_achivement(self,game_code:str,name:str,achivement_code:str,cover:str,description:str):

        if self.achivement.count_documents({'game_code':game_code,'achivement_code':achivement_code}) == 0:
            achivement = {
                'game_code': game_code,
                'name':name,
                'achivement_code': achivement_code,
                'cover': cover,
                'description': description
            }
            self.achivement.insert_one(achivement)
        else:
            return 0


    def give_achivement_to_user(self,game_code:str,achivement_code:str,user_id:int):
        if self.user.count_documents({'user_id':user_id, 'achivements.game_code':game_code, 'achivements.achivement_code': achivement_code}) == 0:
            achivement = {
                'game_code':game_code,
                'achivement_code':achivement_code
            }
            self.user.update_one({'user_id':user_id}, {'$push': {'achivements':achivement}})
        else:
            return 0

    def return_user_games_with_achivement(self,user_id:int):
        return self.user.distinct('achivements.game_code', {'user_id':user_id})

    def return_user_achivement_by_game_code(self,user_id:int,game_code:str):
        return self.user.distinct('achivements.achivement_code',{'user_id':user_id,'achivements.game_code':game_code})


    def return_achivement(self,game_code:str,achivement_code:str):
        if self.achivement.count_documents({'game_code':game_code, 'achivement_code':achivement_code}) == 1:
            return self.achivement.find_one({'game_code':game_code,'achivement_code':achivement_code})

        else:
            return 0
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
                'achivement': achivement # Код достижения, которое дадут при достижении этого уровня
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
            'game_config': cfg, # Конфиг игры
            'month_sales' : 0 # Продажи в месяц
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
    def update_user_game_config(self,user_id,config_value,config_key, game_code):
        user = self.return_user_info(user_id)
        if user:
            self.user.update_one({'user_id':user_id, f'games_config.{game_code}': {'$exists':True}},
                                  {'$set': {f'games_config.$.{game_code}.{config_key}' : config_value}})
        else:
            return 0

    def update_month_game_sales(self, game_code):
        game = self.return_game_info(game_code)
        try:
            self.game.update_one({'game_code':game_code, 'month_sales':{"$exists":True}}, {'$set':{'month_sales':game['month_sales']+1}})
        except:
            self.game.update_one({'game_code': game_code, 'month_sales': {"$exists": False}},
                                 {'$set': {'month_sales': 1}})

    def clear_month_sale(self):
        self.game.update_one({'month_sales':{'$exists':True}}, {'$set':{'month_sales':0}})

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

    def return_game_satistic(self, game_code):
        achivments = self.achivement.distinct('achivement_code', {'game_code':game_code})
        game = self.return_game_info(game_code)
        statistic_text = f'Статистика для игры {game["game_name"]}\n' \
                         f'Количество продаж - {self.user.count_documents({f"games_config.{game_code}.is_demo":0})}\n' \
                         f'Продажи в этом месяце - {self.game.find_one({"game_code":game_code})["month_sales"]}'
        if game['price'] > 0:
            statistic_text = f'{statistic_text}' \
                             f'Количество демо - {self.user.count_documents({f"games_config.{game_code}.is_demo":1})}\n'

        for achivment_code in achivments:
            achivement = self.return_achivement(game_code, achivment_code)

            statistic_text = f'{statistic_text}' \
                             f'{achivement["name"]} - получило {self.user.count_documents({f"achivements.game_code": achivement["game_code"], f"achivements.achivement_code":achivement["achivement_code"]})}\n'
        return statistic_text

if __name__ == '__main__':
    print('Тест')
    check = Mongo()
    check.__init__()
    check.clear_month_sale()
    # check.add_frame(game_code='guide_store',frame_num=10,is_demo=0,content_code=0,text={'ru':'1 вопрос и ты поддался сомнению, никакой из вариантов не был уникальным. Так бывает друг\nНаше обучение подошло к концу.\nПрощай'},achivement='store_guide_complete', variants='Пока', variants_frame='-1')


    # check.add_game(code='orange_world',can_buy=0, name='Мир, который никогда не оранжевый', description='Когда-то все мы были оранжевыми, а может красными, к сожалению уже не помню. Я возвёл столько строений, что забыл совсем другие науки. Однако играет ли роли? Наше общество требует худших решений. Только я задаю один и тот же вопрос: "Куда пропали все те, кого я знал и видел"', cover='AgACAgIAAxkBAAIQMmSIAAEI4HfIPAbSv-fOEoeNKTiOrwACyMwxG1xtQUjUfncYWxr8NQEAAwIAA3kAAy8E', genre_code='antiutopia',genre='Антиутопия👁',creator='Borch Store',price=0,config={}, publisher='BORCH Studio',discount=0)


    # check.add_achivement(game_code='guide_store', name='Рождён читать',achivement_code='store_guide_complete',cover='AgACAgIAAxkBAAILZGSGfvFFhTQ44UkQGYPpwbZGacbtAALwzzEbFMExSICqx1N_4NAyAQADAgADeQADLwQ', description='Вы прошли курс молодого бойца.\nВы узнали тонкости работы магазина и его особености, теперь настало время узнать остальные игры.')

    # check.return_genres()
    # check.add_frame(game_code='param_pam',frame_num=1,is_demo=1,content_code=0,text={'ru':'Просто проверочка'}, variants='Я\nТы', variants_frame='2\n3')
    # check.add_frame(game_code='param_pam',frame_num=2,is_demo=0,content_code=0,text={'ru':'Ты эгоист. \nБудем это знать'}, variants='Боль', variants_frame='5')
    # check.add_frame(game_code='guide_store',frame_num=1,is_demo=0,content_code=1,content='AgACAgIAAxkBAAIEvWSFebpYNLrGz9dHr0jqreUIh95KAAJuxTEb4e4xSFOwt15_U3lYAQADAgADeQADLwQ',text={'ru':'Добро пожаловать в наш магазин\nТелеграм позволяет делать удивительные вещи. Потому мы познакомим вас с нашим магазином\nНажми кнопку под текстом'}, variants='->Прямо сюда<-', variants_frame='2')
    # check.add_frame(game_code='guide_store',frame_num=2,is_demo=0,content_code=0,text={'ru':'Теперь ты понял как использовать кнопки. Поздравляем, но как насчёт научиться вариативности?\nОго сколько вариантов. Нажми на любой из них'}, variants='Я самый уникальный вариант\nА может это более уникальный?', variants_frame='3\n4')
    # check.add_frame(game_code='guide_store',frame_num=3,is_demo=0,content_code=0,text={'ru':'Ты нажал на самую уникальную кнопку. Молодец, теперь ты не узнаешь, что было за другой кнопкой.\nЛадно не буду тебя расстраивать, у тебя есть команда /reset_now_game . Она полностью сотрёт твоё сохранение в последней игре, которую ты играл'}, variants='Продолжим', variants_frame='5')
    # check.add_frame(game_code='guide_store',frame_num=4,is_demo=0,content_code=0,text={'ru':'Вот ты и потерял возможность узнать, что было за второй кнопкой.\nНе бойся есть команда /reset_now_game что полностью уничтожит сохранение игры, которую ты запустил последней.'}, variants='Продолжим', variants_frame='5')
    # check.add_frame(game_code='guide_store',frame_num=5,is_demo=0,content_code=1,content='AgACAgIAAxkBAAIFBmSFfZh6c-Mt6y8FNWMTxYgP4xWqAAL_xzEbW04xSKO-dJo3cTBQAQADAgADeAADLwQ',text={'ru':'Теперь же перейдём к самому магазину.\nНажав кнопку профиль вы увидите множество интересных для себя вещей.\nНу же попробуйте нажать кнопку "Профиль" в главом меню'}, variants='Далее', variants_frame='6')
    # check.add_frame(game_code='guide_store',frame_num=6,is_demo=0,content_code=1,content='AgACAgIAAxkBAAIFCmSFf4w3F2sS61_mfz0QbxpofHpNAAIEyDEbW04xSG2jVMt-KQnNAQADAgADbQADLwQ',text={'ru':'Однако самое интересное, что у тебя есть конечно же БИБЛИОТЕКА\nСколько предстоит ещё добавить нам игр в наш прекрасный магазин.\nМожешь нажать кнопку "Библиотека" и увидеть там как минимум 1 игру.\nЭтот гайд'}, variants='Вау как круто', variants_frame='7')
    # check.add_frame(game_code='guide_store',frame_num=7,is_demo=0,content_code=1,content='AgACAgIAAxkBAAIFEGSFgMNtXThxP1byv6sM7RaSDM2OAAIGyDEbW04xSPtXTEV6qsPhAQADAgADeAADLwQ',text={'ru':'Познакомимся с разделами магазина.\nНажав кнопку "Подборка" вы сможете увидеть все разделы, что есть на данный момент'}, variants='Ясно', variants_frame='8')
    # check.add_frame(game_code='guide_store',frame_num=8,is_demo=0,content_code=1,content='AgACAgIAAxkBAAIFFmSFgYea_LJKyJwAAetVLmSZz7K3XAACCMgxG1tOMUhopYwK68p9EAEAAwIAA3gAAy8E',text={'ru':'Ну и на последок - Поиск. \nКонечно найти игры вручную будет проблематично, потому существует замечательный поиск. \nСтоит только ввести начало и отправить, как бот предложит вам все подходящие варианты\nИспытайте же скорее, нажав на кнопку "Поиск"'}, variants='Борщ?Вкусно', variants_frame='9')
    # check.add_frame(game_code='guide_store',frame_num=9,is_demo=0,content_code=0,text={'ru':'Вот и подошло к концу наше обучение\nБлагодарим вас за прохождение. Чтож можете теперь идти в магазин и играть. \nВозвращайтесь, когда выйдут ещё обучающие материалы'}, variants='Пока Пока', variants_frame='10')
    #




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


    #check.add_game(code='cool', name='Cool game', description='Игра, что вернула мне жизнь', cover='BAACAgIAAxkBAANgZIQNvW-Wqtz3-7B3_Aa_EfVBHfwAAowrAAJtuCFI_K_v-jdfKlQvBA\nAgACAgIAAxkBAANkZIQN0TZFoDrorfr9EumGuN_FPs0AAhnHMRttuCFIjwbJJG8er1wBAAMCAAN4AAMvBA', genre_code='kok',genre='Для любителей покрепче',creator='Ваша жизнь',price=0,config=game_config, publisher='Ваш дом',discount=0)
    # check.add_game(code='pim_pam', name='Jojo sim', description='Крутая игра для всех', cover='AgACAgIAAxkBAAMHZIOzWevS-gGso07A2fbOQtcLmEMAAkvIMRso9iFIjTr7ebImDK4BAAMCAAN5AAMvBA', genre_code='hohma',genre='Хохма',creator='Me',price=0,config=game_config, publisher='Me',discount=0)
    # check.add_game(code='param_pam', name='Bus simulator', description='Здесь просят деньги, просто уйдите', can_buy=1,cover='AgACAgIAAxkBAAIDzGSFZkltqub9IJ9up44fBZJflti4AAKgyjEbW04pSMaXeCFs5lfJAQADAgADeQADLwQ', genre_code='paid',genre='Донатный мусор',creator='Доллар',price=100,config={}, publisher='ЦБ Мира', discount=0)

    #
    # check.give_game_to_user(game_code='param_pam', user_id=483058216, is_demo=1)
    # check.give_game_to_user(game_code='pim_pam', user_id=483058216, is_demo=1)
    # check.give_game_to_user(game_code='f', user_id=483058216, is_demo=0)
    # print(check.return_user_info(483058216)['games_config'])

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
                'is_admin': 0, #Проверка на админа
                'accept_paper':1 #Проверка на соглашение
            }
            self.user.insert_one(user)
        else:
            return 0
    def accepted_paper(self,user_id):
        self.user.update_one({'user_id':user_id},{'$set':{'accept_paper':1}})
    def add_frame(self,game_code:str, frame_num:int, is_demo:int, content_code:int, text:dict,variants:str, variants_frame:str, sound:str = None, content:str=None,  modificators:str=None, sticker:str=None, change_add_conditions:str=None,check_add_conditions:str=None, fail_condition_frame:int=None, achivement:str=None) -> 0:
        if self.frame.count_documents({'frame_num':frame_num, 'game_code':game_code}) == 0 and self.game.count_documents({'game_code':game_code}) == 1:
            frame = {
                'game_code':game_code, #Уникальный код игры
                'frame_num': frame_num, # уникальный номер кадра
                'content_code' : content_code, # Контент код, что необходимо отправить 0 - текст, 1 - фото, 2 -видео, 3 - аудио, 4 - гиф
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
                'is_demo': 1,
                'played': 0,
                'rate':0
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
            'month_sales' : 0, # Продажи в месяц
            'rating': 0, # Общая оценка
            'num_of_rates': 0 # Количество оценок
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
    def rebase(self):
        self.game.update_many({'rating':{'$exists':False}}, {'$set':{'rating':0,'num_of_rates':0}})

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
    def user_played_game(self, user_id, game_code):
        self.user.update_one({'user_id': user_id, f'games_config.{game_code}': {'$exists': True}},
                             {'$set':{f'games_config.$.{game_code}.played':1}})
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

    def rate_game(self,user_id,game_code, score):
        game_conf = self.return_game_cfg(user_id, game_code)
        game = self.return_game_info(game_code)
        rate = int(score)
        if game_conf['rate'] == 0:
            self.game.update_one({'game_code':game_code}, {'$set' : {'num_of_rates': game['num_of_rates']+1, 'rating':game['rating']+rate}})
            self.user.update_one({'user_id':user_id}, {'$set':{f'games_config.{game_code}.rate':rate}})
        else:
            self.game.update_one({'game_code':game_code}, {'$set':{'rating':game['rating']-game_conf['rate']}})
            self.user.update_one({'user_id':user_id}, {'$set':{f'games_config.{game_code}.rate':rate}})
            self.game.update_one({'game_code':game_code}, {'$set' : {'num_of_rates': game['num_of_rates']+1, 'rating':game['rating']+rate}})
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
                         f'Продажи в этом месяце - {self.game.find_one({"game_code":game_code})["month_sales"]}\n' \

        if game['price'] > 0:
            statistic_text = f'{statistic_text}' \
                             f'Количество демо - {self.user.count_documents({f"games_config.{game_code}.is_demo":1})}\n'
        statistic_text = f'{statistic_text}' \
                         f'Информация по достижениями:\n'

        for achivment_code in achivments:
            achivement = self.return_achivement(game_code, achivment_code)

            statistic_text = f'{statistic_text}' \
                             f'{achivement["name"]} - получило {self.user.count_documents({f"achivements.game_code": achivement["game_code"], f"achivements.achivement_code":achivement["achivement_code"]})}\n'
        return statistic_text



    def bot_statistic(self):
        users_of_bot = self.user.count_documents({'user_id':{'$exists':True}})
        number_of_games = self.game.count_documents({'game_code':{'$exists':True}})
        number_of_paid_games = self.game.count_documents({'price':{'$gt':0}})
        number_of_free_games = self.game.count_documents({'price':{'$lte':0}})
        percent_of_paid = int(number_of_paid_games/number_of_games * 100)
        percent_of_free = int(number_of_free_games/number_of_games * 100)

        text = f'О магазине\n' \
               f'Написать информацию\n' \
               f'Количество пользователей - {users_of_bot}\n' \
               f'Количество игр - {number_of_games}\n' \
               f'Количество платных игр - {number_of_paid_games}\n({percent_of_paid}%)\n' \
               f'Количество бесплатных игр - {number_of_free_games}({percent_of_free}%)'
        return text



if __name__ == '__main__':
    print('Тест')
    check = Mongo()
    check.__init__()



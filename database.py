import pymongo
import re
class Mongo:
    def __init__(self):
        self.connection = pymongo.MongoClient("mongodb://localhost:27017/")['store']
        self.user = self.connection['user']
        self.frame = self.connection['frame']
        self.game = self.connection['game']
    def add_user(self,user_id):
        if self.user.count_documents({'user_id':user_id}) == 0:
            user = {
                'user_id' : user_id, # Пользовательский id
                'curr_game_code': None, # Текущая игра
                'games_config': [], # Игровой конфиг
                'achivements' : None # Ачивки
            }
            self.user.insert_one(user)
        else:
            return 0
    def add_frame(self,game_code:str, frame_num:int, content_code:int, text:str, is_variants:str, content:str=None, variants:str=None, variants_frame:str=None, modificators:str=None, sticker:str=None, change_add_conditions:str=None,check_add_conditions:str=None, achivement:str=None) -> 0:
        if self.frame.count_documents({'frame_num':frame_num}) == 0 and self.game.count_documents({'game_code':game_code}) == 1:
            frame = {
                'game_code':game_code, #Уникальный код игры
                'frame_num': frame_num, # уникальный номер кадра
                'content_code' : content_code, # Контент код, что необходимо отправить 0 - текст, 1 - фото, 2 -видео, 3 - аудио
                'text' : text, # Основной текст кадра
                'is_variants' : is_variants, # Имеются ли разные варианты событий
                'content' : content, # Медиа файл, согласно контент коду
                'variants': variants, # Варианты событий, разделяются через \n
                'variants_frame': variants_frame, # Кадры в которые ведут варианты, пишутся на том же месте, что и текст вариантов. Разделяются через \n
                'sticker':sticker, # Отправит стикер вместе с вашим кадром
                'modificators':modificators, # battle - бой, все остальное - ничего
                'change_add_conditions': change_add_conditions, # Доп. условия, которые нужно изменить в условиях игры
                'check_add_conditions' : check_add_conditions, # Проверка на доп. условия из конфига игры
                'achivement': achivement # Название достижение, которое дадут на этом кадре
            }
            self.frame.insert_one(frame)
        else:
            return 0

    def add_game(self, code: str, name: str, description: str, cover: str, creator:str, publisher:str, price: int, genre_code:str, genre:str, config: dict) -> 0 or None:
        if self.game.count_documents({'game_code':code}) == 0:
            cfg = {
                'frame_num': 1
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
            'genre_code': genre_code, # Код жанра
            'genre': genre, #Жанр
            'game_config': cfg # Конфиг игры

            }
            self.game.insert_one(game)
        else:
            return 0


    def give_game_to_user(self, game_code:str, user_id:int):
        if self.user.count_documents({'user_id':user_id}) == 1:

            game_config = {
                game_code:self.return_game_info(game_code)['game_config']
            }
            if game_config not in self.return_user_info(user_id)['games_config']:
                self.user.update_one({'user_id': user_id}, {'$push': {'games_config': game_config}})
            else:
                return 0
        else:
            return 0

    def return_add_conditions_of_game(self,user_id,game_code):
        user = self.return_user_info(user_id)
        if user != 0:
            for i in user['games_config']:
                try:
                    return i[game_code]
                except:
                    pass


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
    def return_frame(self,frame_num):
        if self.frame.count_documents({'frame_num':frame_num}):
            return self.frame.find_one({'frame_num':frame_num})
        else:
            return 0
    def update_user_frame_num(self,user_id,frame_num):
        if self.user.count_documents({'user_id':user_id}):
            self.user.update_one({'user_id':user_id}, {'$set':{'frame_num':int(frame_num)}})
        else:
            return 0

    def search_game_by_name(self, search):
        return self.game.find({'game_name': re.compile(rf"(?i){search}")})
        # return self.game.find({'game_name': f"/{search}/i"})



if __name__ == '__main__':
    print('Тест')
    # check = Mongo()
    # check.__init__()
    # game_name = input('Game: ')
    # for i in check.search_game_by_name(game_name):
    #     print(i['game_name'])
    # game_config = {
    #     'super_bas': ['joper'],
    #     'tis':5
    # }
    # check.add_game(code='param_pam', name='Bus simulator', description='Крутая игра для всех', cover='AgACAgIAAxkBAAMHZIOzWevS-gGso07A2fbOQtcLmEMAAkvIMRso9iFIjTr7ebImDK4BAAMCAAN5AAMvBA', genre_code='hohma',genre='Хохма',creator='Me',price=0,config=game_config)
    # check.add_user(4810)
    # check.return_user_info(4810)

    # check.give_game_to_user(game_code='testing_game', user_id=483058216)
    # check.give_game_to_user(game_code='basta', user_id=483058216)
    # print(check.return_user_info(483058216)['games_config'])

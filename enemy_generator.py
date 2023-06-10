import random
import os.path
name = ['Урлук', 'Вельзиву', 'Батон', 'Борщ', 'Багет',
                'Монстрищее', 'Взрыватель', 'ок', 'ЕссБОЙ', 'Уничтожитель5000', 'МастерРикиРала',
        'ТОЧНО неТВОЯ МАМА', 'Дитар3', 'Пол-Жизни-3', 'Фал Спинсар', 'Джем Ройян',
        'вТелефоне', 'Интернет8000', 'МегаМэн', 'СуперЧудо', 'Рабочий', 'ПК-крыса',
        'ЛицоКнига', 'МастерСтыда', 'КиберБаг', 'Котлеты', 'Киборг-МирКоп',
        'Зибилив', 'Сраманер', 'Агент 0 киллов', 'Типичный Злодей', 'Беженка', 'Адский дрочила']

race = ['Еда', 'Эльф', 'Гном', 'Человек', 'Робот', 'Киборг',
                'Призрак', 'Насекомое', 'Животное', 'Друид', 'Демон', 'Вирус', 'Код',
        'Комплектующий', 'СуперГерой', 'Орк', 'Гоблин', 'ЧудоСредство',
        'Угнетатель', 'Буржуй', 'Пролетарий', 'Мегашевик', 'Быдло',
        'НоуНейм', 'Чувствительный', 'Тунеядец']



country = ['Евразия', 'Остазия', 'Луна', 'Бумбаза',
                   'Угинара', 'Мастараза', 'БАЗА', 'Марс', 'Земля', 'Завод', 'ПК',
           'Пендосия', 'Пельмень', 'Любимый город', 'СтрахЛяндия', 'Аэропорт',
           'Космос', 'Ад', 'Моды Стим', 'Свободные Народы', 'Скалэнд', 'Реклама туалета']




class Enemy(object):
    def __init__(self, name, age, race, hp, max_attack, country):
        self.name = name
        self.age = age
        self.chance = random.randrange(1, 101)
        self.race = race
        self.hp = hp
        self.maxHP = hp
        self.maxAttack = max_attack
        self.country = country

    def get_damage(self, damage):
        self.hp -= damage

        return f"Вы нанесли урон {self.name} в размере {damage} едениц урона. \nУ {self.name} осталось {self.hp} хп"

    # def endDIE(self, heroName):
    #     print(f"Вы победили {self.name} из {self.country}. Мои поздравления {heroName}")

    def dead(self):
        if self.hp <= 0:
            return True
        elif self.hp > 0:
            return False

    def attack(self):
        attack = random.randrange(self.maxAttack + 1)
        return attack

    def health(self):

        if self.hp < self.maxHP:
            can_u_heal = random.randrange(-5, self.chance + 1)
            if self.chance != 0:
                can_u_heal = round(can_u_heal / self.chance)
            if self.chance == 100:
                heal = random.randrange(1, self.maxHP - self.hp)
                self.hp += heal
                self.chance = 0
                return f"Вот как бывает. {self.name} увеличило свое здоровье на {heal}"

            elif self.chance > 0 and self.chance != 100 and can_u_heal >= 0.5:
                try:
                    heal = random.randrange(1, (self.maxHP - self.hp)//10)
                except:
                    heal = 3
                self.hp += heal
                self.chance = 0
                return f"Вот эта фортуна\nне для тебя..... \n{self.name} повысило хп на {heal}"
            elif can_u_heal < 0:
                damage = random.randrange(1, self.maxHP - self.hp)
                self.hp -= damage
                self.chance += random.randrange(5, 21)
                return f"О ДАААА. \n{self.name} получило чертов критический промах. \nШприц порвал его вены. \nОно получило {damage} урона"

            else:
                self.chance += random.randrange(1, 21)
                return 'Сегодня не твой день. \nЯ думаю в следущий раз повезет'

    def get_stat(self, whatUwant):
        match whatUwant:
            case 'name':
                return self.name
            case 'age':
                return self.age
            case 'country':
                return self.country
            case 'hp':
                return self.hp
            case 'race':
                return self.race
            case 'maxHP':
                return self.maxHP
            case 'maxAttack':
                return  self.maxAttack


def create_monster(difficult=0):
    random.shuffle(name)

    random.shuffle(race)
    age = random.randrange(3000)
    match difficult:
        case 0:
            hp = random.randrange(1, 100)
            monster_maxAttack = random.randrange(1, 20)
        case 1:
            hp = random.randrange(1, 100)
            monster_maxAttack = random.randrange(5, 40)
        case 2:
            hp = random.randrange(30, 150)
            monster_maxAttack = random.randrange(10, 60)
        case _:
            hp = random.randrange(1, 100)
            monster_maxAttack = random.randrange(1, 20)
    random.shuffle(country)
    random.shuffle(name)
    random.shuffle(race)
    monster = Enemy(random.choice(name), age,
                    random.choice(race), hp, monster_maxAttack, random.choice(country))

    return monster

def save_for_later(Enemy):
    count = 0
    path = 'characters/'
    if not os.path.exists(path):
        os.mkdir(path)

    name = Enemy.get_stat('name')
    race = Enemy.get_stat('race')
    age = Enemy.get_stat('age')
    attack = Enemy.get_stat('maxAttack')
    hp = Enemy.get_stat('maxHP')
    country = Enemy.get_stat('country')
    while os.path.isfile(path + 'm' + str(count) + '.txt'):
        count+=1

    with open(path + 'm' + str(count) + '.txt' , 'a', encoding='utf-8') as f:
        f.write(name)
        f.write('\n' + race)
        f.write('\n' + str(age))
        f.write('\n' + country)
        f.write('\n' + str(attack))
        f.write('\n' + str(hp))
        f.write('\n' + str(Enemy))

def read_enemy_file(enemy):
    with open(enemy) as f:
        lines = f.readlines()
        lines = list(map(lambda each:each.strip('\n'), lines))
        if len(lines) == 7:
            try:
                return Enemy(name=lines[0], age=int(lines[2]), race=lines[1], hp=int(lines[5]), max_attack=int(lines[4]), country=lines[3])
            except ValueError:
                return 'Ваш файл монстра повреждён. Не верный тип данных'
        else:
            return f'У вас поврежден файл монстра. Нет достающих типов данных'
# Borch-Novels-store
Магазин цифрового контента на основе API телеграм \
[ТГ канал проекта](https://t.me/BorchStore)
## План
1. [Описание](https://github.com/XRenso/Borch-Novels-store/edit/main/README.md#%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5)
2. [Что реализовано?](https://github.com/XRenso/Borch-Novels-store/edit/main/README.md#%D1%87%D1%82%D0%BE-%D1%80%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%BE)
3. [Как запустить?](https://github.com/XRenso/Borch-Novels-store/edit/main/README.md#%D0%BA%D0%B0%D0%BA-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D1%82%D0%B8%D1%82%D1%8C)
4. [Условия использования](https://github.com/XRenso/Borch-Novels-store/edit/main/README.md#%D1%83%D1%81%D0%BB%D0%BE%D0%B2%D0%B8%D1%8F-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)

## Описание
Открываю данный код, поскольку проект теперь не поддерживается, а все данные и ключи утратили свою действительность. Это полностью рабочий телеграм бот, который работает на оснве aiogram при помощи вебхуков.

## Что реализовано?
- Возможность запуска контента на основе *кадров*. В базу данных загружается кадр с информацией о его содержимом(текст, выборы, какой-либо медиаконтент)
- Сохранение прогресса, от текущей страницы до нужных переменных, что может потребовать продукт. Например в визуальных новеллах проверки на концовки при определенных событиях
- Система ачивок
- Система демо версий
- Inline режим, чтобы делиться играми с кем-либо в другом чате
- Режим администрирования (просмотр статистики продуктов, тех. режим)
- Группировка продуктов по пользовательским папкам (как в Steam)
- Система оценок продукта по 5-и бальной шкале
- Профиль пользователя, который отображает достижения, количество продуктов и последняя запущенная игра
- Есть возможность массовой рассылки пользователям (только для администраторов)
- Разбиение товаров на категории
- В случае большого количества товаров есть слайдер, который переключает страницы
- Возможность переходить на страницы (только для книг)

Указал вроде весь функционал, который находится в этом боте, мог упустить что-то незначительное.


## Как запустить?
Вам необходимо будет создать файл `.env` в папке с проектом. Внутри него указать следующие переменные
- `TOKEN` - API токен вашего бота в телеграме
- `KASSA` - API ключ для ваше электронной кассы, которая принимает оплату
- `NGROK_URL` - Тут уже адрес, куда будет обращаться телеграм, чтобы достучаться во время какого-либо события. Я использовал первое время NGROK, потому такое название. Не обязательно нужно использовать NGROK
- `HOST` - Адрес хоста для вебхука

## Условия использования
Данный проект и какие-либо части его кода запрещенно использовать в коммерческих проектах, без создателя (меня - XRenso). Доступ открыт в качестве pet проекта, а также интереса иных лиц, которые хотят увидеть и научиться писать телеграм ботов.

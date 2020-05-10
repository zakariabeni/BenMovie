import telebot
import ast
from preprocess_data import read_predata
from input_suggestion import title_suggestion
from cosine_similarity import recommendations

token = "1268385140:AAEuiAil9oFfR-kntdc1O4V_clrQz0SUznk"
bot = telebot.TeleBot(token)
save_one = []


@bot.message_handler(commands=['start'])
def send_welcome(message):
    opening = str("Hi! This is *BenMovie Bot*. It is a content-based movie recommender.\n\n")
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(telebot.types.InlineKeyboardButton("Search", callback_data="search"),
               telebot.types.InlineKeyboardButton("Data Info", callback_data="info"))
    bot.send_message(message.chat.id, opening, parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data == "search")
def query_handler_1(query):
    answer = 'Type your favorite movie!'
    msg = bot.send_message(query.message.chat.id, answer)
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id)
    bot.register_next_step_handler(msg, query_search)


@bot.callback_query_handler(lambda query: query.data == "info")
def query_handler_2(query):
    bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id)
    answer = "Final Project Advanced Information Retrieval \n\n"\
             "project *'BenMovie Telegram Bot'* \n\n"\
             "_Note_: \n"\
             "Movie datasets were obtained from IMDb with a Metascore flag, a total vote of more than 15000, " \
             "and were released at least after 1990s."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(telebot.types.InlineKeyboardButton("Back", callback_data="back"))
    bot.edit_message_text(answer, query.message.chat.id, query.message.message_id, parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data == "back")
def query_handler_3(query):
    opening = str("Hi! This is *BenMovie Bot*. It is a content-based movie recommender.\n\n")
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(telebot.types.InlineKeyboardButton("Search", callback_data="search"),
               telebot.types.InlineKeyboardButton("Data Info", callback_data="info"))
    bot.edit_message_text(opening, query.message.chat.id, query.message.message_id, parse_mode="Markdown", reply_markup=markup)


def query_search(message):
    title_suggest = (title_suggestion(message.text))
    options = telebot.types.InlineKeyboardMarkup()
    save_one.clear()
    if title_suggest != 0:
        for title in title_suggest:
            options.add(telebot.types.InlineKeyboardButton(text=title, callback_data=str('*' + title)))
        reply = str("Pick your input title! \nOr try another input query!")
        options.add(telebot.types.InlineKeyboardButton(text="<<Try Again>>", callback_data="back"))
        bot.send_message(message.chat.id, reply, reply_markup=options)

    else:
        options.add(telebot.types.InlineKeyboardButton(text="<<Try Again>>", callback_data="back"))
        reply = str("Sorry, nothing to suggest! \nTry another input query!")
        bot.send_message(message.chat.id, reply, reply_markup=options)


@bot.callback_query_handler(func=lambda query: True)
def title_handler(query):
    data = query.data
    movie_name = data.replace('*', '')
    # print('up', movie_name)
    result = recommendations(movie_name)
    one = result.pop(0)
    save_one.append(one)
    # print(len(save_one))
    # print(save_one)
    if data.startswith('*'):
        markups = telebot.types.InlineKeyboardMarkup()
        for idx in result:
            # print(i, title)
            markups.add(telebot.types.InlineKeyboardButton(text='{} ({})'.format(read_predata()['movie'].values[idx], read_predata()['year'].values[idx]),
                                                           callback_data=str(read_predata()['movie'].values[idx])))
        reply = str("Top 5 recommended movies to *{}* are:".format(movie_name))
        markups.add(telebot.types.InlineKeyboardButton(text="<<Try Again>>", callback_data="back"))
        bot.edit_message_text(reply, query.message.chat.id, query.message.message_id, parse_mode="Markdown", reply_markup=markups)
    else:
        markups = telebot.types.InlineKeyboardMarkup()
        stars = ', '.join(read_predata()['stars'].values[one])
        reply = "*{} ({})*".format(movie_name, read_predata()['year'].values[one]) + "\n" \
                "{} | {}".format(read_predata()['certificate'].values[one], read_predata()['duration'].values[one]) + "\n" \
                "IMDB Rating: *{}*".format(read_predata()['imdb'].values[one]) + "\n\n" \
                "*Director*: {}".format(read_predata()['director'].values[one].replace("'", "")) + "\n" \
                "*Stars*: {}".format(stars.replace("'", "")) + "\n" \
                "*Genre*: {}".format('[' + ', '.join(read_predata()['genre'].values[one]) + ']') + "\n\n" \
                "*Description*: _{}_".format(read_predata()['description'].values[one]) + "\n" \
                "[Movie Poster]({})".format(read_predata()['movie_img'].values[one])
        # print('down', read_predata()['movie'].values[save_one[0]])
        markups.add(telebot.types.InlineKeyboardButton(text="<<Back>>", callback_data=str(
            '*' + read_predata()['movie'].values[save_one[0]])))
        bot.edit_message_text(reply, query.message.chat.id, query.message.message_id, parse_mode="Markdown", reply_markup=markups)


bot.polling(none_stop=False, timeout=50)

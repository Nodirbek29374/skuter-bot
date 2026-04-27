const TelegramBot = require('node-telegram-bot-api');

const token = '8658604129:AAHU5bJ8ixuR_vPQqEGxhMUhnmwrvMjyPwE';

const bot = new TelegramBot(token, { polling: true });

bot.on('message', (msg) => {
  const chatId = msg.chat.id;

  if (msg.text === '/start') {
    bot.sendMessage(chatId, 'Salom! Skuter botga xush kelibsiz!');
  }
});

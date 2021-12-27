def sample_responses(input_text):
    user_message = str(input_text).lower()

    if user_message in ('hello', 'hi', 'salam'):
        return "Алейкум Ассалам!"

    if user_message in ('ты кто?', 'кто ты?'):
        return "Я - бот который будет помогать вам вести учет долгов магазина!"       
    
    return 'Я твоя не понимать( Введи /help чтоле'
    

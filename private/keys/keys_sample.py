def bot_config(bot_mode):
    if bot_mode == 'live_mode':
        return {
            'bot_name': '',
            'bot_token': '',
            'bot_prefix': [],
            'version': ''
            }
    elif bot_mode == 'dev_mode':
        return {
            'bot_name': '',
            'bot_token': '',
            'bot_prefix': [],
            'version': '',
            }
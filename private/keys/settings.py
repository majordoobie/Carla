import private.keys.keys as keys
def bot_config(bot_mode):
    if bot_mode == 'live_mode':
        return {
            'bot_name': 'Carla',
            'bot_token': f'{keys.live["bot_token"]}',
            'bot_prefix': ['carla.', 'Carla.', 'c.', 'C.'],
            'version': 'Carla Version: 4.0.0',
            }
    elif bot_mode == 'dev_mode':
        return {
            'bot_name': 'Carla [Dev Shell]',
            'bot_token': f'{keys.dev["bot_token"]}',
            'bot_prefix': ['dev.', 'd.', 'D.'],
            'version': 'Carla [BETA] 4.0.0',
            }

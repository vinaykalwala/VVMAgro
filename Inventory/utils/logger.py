# Inventory/utils/logger.py

import logging

logger = logging.getLogger('app_logger')

def log_action(user, action, model_name, object_id=None, extra_info=None):
    logger.info(f'User: {user} | Action: {action} | Model: {model_name} | Object ID: {object_id} | Info: {extra_info}')

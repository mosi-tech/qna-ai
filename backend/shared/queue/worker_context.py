import contextvars
from shared.services.progress_service import send_progress_event as _send_progress_event

this_context = contextvars.ContextVar('this_context', default={})

def set_context(**kwargs):
    current = this_context.get({})
    this_context.set({**current, **kwargs})

def get_context_value(key, default=None):
    return this_context.get({}).get(key, default)

def get_session_id():
    return get_context_value('session_id')

def get_message_id():
    return get_context_value('message_id')

def get_user_id():
    return get_context_value('user_id')

        

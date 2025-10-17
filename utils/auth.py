import os
import streamlit as st
from typing import Tuple

def is_user_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_user_auth() -> Tuple[bool, str, str]:
    """Get user authentication status and role using Windows login."""
    username = os.getlogin()
    is_admin = is_user_admin()
    role = 'admin' if is_admin else 'user'
    return True, role, username

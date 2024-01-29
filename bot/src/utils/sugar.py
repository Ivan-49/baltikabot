#-*- coding: utf-8 -*-
import time


def datetime(sec: bool = True) -> str:
    return time.strftime(f'%d.%m.%Y, %H:%M{":%S" if sec else ""}')

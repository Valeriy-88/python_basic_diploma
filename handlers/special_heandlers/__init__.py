# Когда ввожу любую команду программа начинает выполняться с первого найденного файла, а не с той команды которую я ввел
# к примеру я ввожу команду /high но код будет выполняться команды custom т.к. она стоит выше команды high так же и с /low
# не понимаю как это исправить
from . import history
from . import custom
from . import high
from . import low

__all__ = ['history', 'custom', 'high', 'low']
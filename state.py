import configparser

config = configparser.ConfigParser(interpolation=configparser.BasicInterpolation())
config.read("config.ini")

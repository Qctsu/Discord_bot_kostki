import socket


def get_database_path():
    server_hostname = "Ponyville"
    current_hostname = socket.gethostname()

    if current_hostname == server_hostname:
        return "/home/kucu/Discord/DB_kostki/DataBase/discord_bot_kostki.db"
    else:
        return "C:\\Users\\Kucu\\IdeaProjects\\DB_kostki\\DataBase\\discord_bot_kostki.db"

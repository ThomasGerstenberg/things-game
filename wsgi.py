from things_game.server import app, socketio


if __name__ == '__main__':
    socketio.run(app)

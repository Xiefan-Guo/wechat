import server
import util


def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower()
    c = server.database.get_cursor()
    r = c.execute('SELECT * from users where username=?', [parameters[0]])
    rows = r.fetchall()
    if len(rows) > 0:
        util.send_message(sc,util.message.MessageType.username_taken)
        return

    c = server.database.get_cursor()
    c.execute('INSERT into users (username,password,nickname) values (?,?,?)',
              [parameters[0], util.md5(parameters[1]), parameters[2]])
    util.send_message(sc,util.message.MessageType.register_successful, c.lastrowid)
    #sc.send(MessageType.register_successful, c.lastrowid)

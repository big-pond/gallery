import sqlite3

try:
    sqlite_connection = sqlite3.connect('gallery1.db')
    cursor = sqlite_connection.cursor()
    print("Подключен к SQLite")

    select_query = "SELECT id, image FROM photo"
    cursor.execute(select_query)
    photos = cursor.fetchall()
    for photo in photos:
        file_name = photo[1][7:]  # Оставляем только имя файла
        print(photo[0], file_name)
        cursor.execute('UPDATE photo SET image = ? WHERE id = ?', (file_name, photo[0]))

    sqlite_connection.commit()
    print("Поля image успешно изменены")

except sqlite3.Error as error:
    print("Ошибка при работе с SQLite", error)
finally:
    if sqlite_connection:
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")

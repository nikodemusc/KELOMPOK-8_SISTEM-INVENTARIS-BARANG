class ItemModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_items(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM barang")
        return cur.fetchall()

    def add_item(self, nama_barang, jumlah, harga):
        cur = self.mysql.connection.cursor()
        cur.execute("INSERT INTO barang (nama_barang, jumlah, harga) VALUES (%s, %s, %s)",
                    (nama_barang, jumlah, harga))
        self.mysql.connection.commit()

    def update_item(self, item_id, nama_barang, jumlah, harga):
        cur = self.mysql.connection.cursor()
        cur.execute("UPDATE barang SET nama_barang = %s, jumlah = %s, harga = %s WHERE id = %s",
                    (nama_barang, jumlah, harga, item_id))
        self.mysql.connection.commit()

    def delete_item(self, item_id):
        cur = self.mysql.connection.cursor()
        cur.execute("DELETE FROM barang WHERE id = %s", (item_id,))
        self.mysql.connection.commit()

    def get_item_by_id(self, item_id):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT * FROM barang WHERE id = %s", (item_id,))
        return cur.fetchone()

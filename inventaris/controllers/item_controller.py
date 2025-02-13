from flask import render_template, request, redirect, url_for
from models.item_model import ItemModel

class ItemController:
    def __init__(self, mysql):
        self.model = ItemModel(mysql)

    def show_items(self):
        items = self.model.get_items()
        return render_template('dashboard.html', items=items)

    def add_item(self):
        if request.method == 'POST':
            nama_barang = request.form['nama_barang']
            jumlah = request.form['jumlah']
            harga = request.form['harga']
            self.model.add_item(nama_barang, jumlah, harga)
            return redirect(url_for('dashboard'))
        return render_template('add_item.html')

    def update_item(self, item_id):
        if request.method == 'POST':
            nama_barang = request.form['nama_barang']
            jumlah = request.form['jumlah']
            harga = request.form['harga']
            self.model.update_item(item_id, nama_barang, jumlah, harga)
            return redirect(url_for('dashboard'))
        item = self.model.get_item_by_id(item_id)
        return render_template('edit_item.html', item=item)

    def delete_item(self, item_id):
        self.model.delete_item(item_id)
        return redirect(url_for('dashboard'))

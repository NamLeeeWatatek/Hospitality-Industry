import csv
import io
from odoo import models, fields, api, tools
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    longphung_id = fields.Integer(string='Long Phung ID')

    @api.model
    def import_data(self):
        try:
            file_path = 'custom_import_data/csv/San_Pham.csv'
            vals_list = []
            
            try:
                csv_file = tools.file_open(file_path, mode='rb')
                content = csv_file.read().decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(content))
                self._process_csv_reader(reader, vals_list)
                csv_file.close()
            except FileNotFoundError:
                raise UserError(f"File not found: {file_path}")
            except Exception as e:
                raise UserError(f"Error processing file: {str(e)}")
            
            self._bulk_create_or_update(vals_list)
            return True
            
        except Exception as e:
            raise UserError(f"Error importing products: {str(e)}")

    def _process_csv_reader(self, reader, vals_list):
        for row in reader:
            name = row.get('Name', '').strip()
            product_vals = self._prepare_product_vals(row, name)
            vals_list.append(product_vals)

    def _prepare_product_vals(self, row, name):
        product_vals = {
            'name': name or f"Product_{row.get('Id', 'Unknown')}",
            'default_code': row.get('Code', '').strip() or False,
            'active': bool(int(row.get('Status', 1))),
            'longphung_id': int(row.get('Id', 0)),
            'tracking': 'lot',  # Theo dõi theo lô
            'uom_id': 12,  # Đơn vị tính mặc định
            'uom_po_id': 12,  # Đơn vị tính mua hàng mặc định
            'is_storable': True,
            'default_code': "",
            'barcode': int(row.get('Id', 0)),
        }
        
        return product_vals

    def _bulk_create_or_update(self, vals_list):
        if not vals_list:
            return
        
        longphung_ids = [vals['longphung_id'] for vals in vals_list if vals.get('longphung_id')]
        if not longphung_ids:
            self.create(vals_list)
            return
        
        existing_records = self.search([('longphung_id', 'in', longphung_ids)])
        existing_longphung_ids = set(existing_records.mapped('longphung_id'))
        
        create_vals = []
        update_vals = {}
        
        for vals in vals_list:
            longphung_id = vals.get('longphung_id')
            if not longphung_id or longphung_id not in existing_longphung_ids:
                create_vals.append(vals)
            else:
                matching_record = existing_records.filtered(lambda r: r.longphung_id == longphung_id)
                if matching_record:
                    update_vals[matching_record[0].id] = vals
        
        if create_vals:
            self.create(create_vals)
        
        if update_vals:
            for product_id, vals in update_vals.items():
                self.browse(product_id).write(vals)

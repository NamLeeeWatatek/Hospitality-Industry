import csv
import io
import logging
from odoo import models, fields, api, tools
from odoo.exceptions import UserError
import re

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    longphung_id = fields.Integer(string='Long Phung ID')
    is_khach_hang = fields.Boolean(string='Is Khach Hang')
    is_don_vi_ban = fields.Boolean(string='Is Don Vi Ban')
    is_don_vi_mua = fields.Boolean(string='Is Don Vi Mua')

    @api.model
    def import_data(self):
        try:
            file_configs = [
                {'path': 'custom_import_data/csv/Khach_Hang.csv', 'flag': 'is_khach_hang'},
                {'path': 'custom_import_data/csv/Don_Vi_Ban.csv', 'flag': 'is_don_vi_ban'},
                {'path': 'custom_import_data/csv/Don_Vi_Mua.csv', 'flag': 'is_don_vi_mua'},
            ]
            
            default_phone = '01234567890'
            vals_list = []
            
            _logger.info("Starting import process")
            for config in file_configs:
                try:
                    csv_file = tools.file_open(config['path'])
                    _logger.info(f"Processing file: {config['path']}")
                    with csv_file as f:
                        reader = csv.DictReader(f)
                        self._process_csv_reader(reader, default_phone, config['flag'], vals_list)
                except FileNotFoundError:
                    _logger.warning(f"File not found: {config['path']}, skipping...")
                    continue
                except Exception as e:
                    _logger.error(f"Error processing file {config['path']}: {str(e)}")
                    continue
            
            _logger.info(f"Collected {len(vals_list)} records to process")
            self._bulk_create_or_update(vals_list)
            _logger.info("Import process completed")
            
            return True
            
        except Exception as e:
            _logger.error(f"Import failed: {str(e)}")
            raise UserError(f"Error importing partners: {str(e)}")

    def _process_csv_reader(self, reader, default_phone, flag, vals_list):
        for row in reader:
            _logger.info(f"Processing row: {row}")
            
            name = (row.get('Ten', '') or row.get('Name', '')).strip()
            phone, mobile = self._extract_phone_from_name(name)
            if phone:
                name = self._clean_name(name)
            
            phone_column = row.get('SoDienThoai', '').strip()
            phone, mobile = self._process_phone_column(phone_column, phone, mobile)
            
            if not phone:
                phone = default_phone
            
            partner_vals = self._prepare_partner_vals(row, name, phone, mobile, flag)
            vals_list.append(partner_vals)
            _logger.info(f"Added to vals_list: {partner_vals}")

    def _is_valid_phone(self, number):
        if not number:
            return False
        cleaned_number = re.sub(r'[^0-9+]', '', number)
        return bool(re.match(r'^(0|\+)[0-9]{8,15}$', cleaned_number))

    def _extract_phone_from_name(self, name):
        if not name or not any(char.isdigit() for char in name):
            return None, None
            
        parts = [part.strip() for part in name.split('-')]
        phone_numbers = []
        
        for part in parts:
            if self._is_valid_phone(part):
                phone_numbers.append(part)
        
        return (phone_numbers[0] if phone_numbers else None,
                phone_numbers[1] if len(phone_numbers) > 1 else None)

    def _clean_name(self, name):
        parts = [part.strip() for part in name.split('-')]
        return ' '.join([part for part in parts if not self._is_valid_phone(part)])

    def _process_phone_column(self, phone_column, existing_phone, existing_mobile):
        if not phone_column:
            return existing_phone, existing_mobile
            
        if '-' in phone_column:
            numbers = [n.strip() for n in phone_column.split('-') if n.strip()]
            valid_numbers = [n for n in numbers if self._is_valid_phone(n)]
            if valid_numbers:
                phone = valid_numbers[0] if not existing_phone else existing_phone
                mobile = valid_numbers[1] if len(valid_numbers) > 1 and not existing_mobile else existing_mobile
                return phone, mobile
                
        if self._is_valid_phone(phone_column) and not existing_phone:
            return phone_column, existing_mobile
        return existing_phone, existing_mobile

    def _prepare_partner_vals(self, row, name, phone, mobile, flag):
        partner_vals = {
            'name': name or f"Partner_{row.get('Id', 'Unknown')}",
            'phone': phone,
            'mobile': mobile,
            'street': row.get('DiaChi', '').strip(),
            'active': bool(int(row.get('Status', 1))),
            'is_company': False,
            'longphung_id': int(row.get('Id', 0)),
            'is_khach_hang': flag == 'is_khach_hang',
            'is_don_vi_ban': flag == 'is_don_vi_ban',
            'is_don_vi_mua': flag == 'is_don_vi_mua',
        }
        
        if not partner_vals['street']:
            partner_vals.pop('street')
            
        return partner_vals

    def _bulk_create_or_update(self, vals_list):
        if not vals_list:
            _logger.info("No records to process")
            return
        
        longphung_ids = [vals['longphung_id'] for vals in vals_list]
        existing_records = self.search([('longphung_id', 'in', longphung_ids)])
        
        create_vals = []
        update_vals = {}
        
        for vals in vals_list:
            longphung_id = vals['longphung_id']
            flag = 'is_khach_hang' if vals['is_khach_hang'] else 'is_don_vi_ban' if vals['is_don_vi_ban'] else 'is_don_vi_mua'
            
            matching_record = existing_records.filtered(lambda r: r.longphung_id == longphung_id and 
                                                       ((flag == 'is_khach_hang' and r.is_khach_hang) or 
                                                        (flag == 'is_don_vi_ban' and r.is_don_vi_ban) or 
                                                        (flag == 'is_don_vi_mua' and r.is_don_vi_mua)))
            
            if matching_record:
                update_vals[matching_record[0].id] = vals
            else:
                create_vals.append(vals)
        
        if create_vals:
            _logger.info(f"Creating {len(create_vals)} new partners")
            self.create(create_vals)
        
        if update_vals:
            _logger.info(f"Updating {len(update_vals)} existing partners")
            for partner_id, vals in update_vals.items():
                self.browse(partner_id).write(vals)
import io
import base64
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = 'Stock Report Wizard'

    location_id = fields.Many2one('stock.location', string='Location')
    date_from = fields.Datetime(string='From Date')
    date_to = fields.Datetime(string='To Date')
    

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise UserError(
                    "The 'From Date' cannot be later than the 'To Date'. Please select a valid date range")
            if self.date_from > datetime.now():
                raise UserError(
                    "The 'From Date' cannot be later than today. Please select a valid date range")

    # Add a actions needed to generate an Excel report
    def action_genarate_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Báo cáo NXT kho")
        
        # Set column width
        sheet.set_column('A:A', 5)   
        sheet.set_column('B:B', 10)  
        sheet.set_column('C:C', 20)  
        sheet.set_column('D:D', 11)  
        sheet.set_column('E:E', 10)  
        sheet.set_column('F:G', 14) 
        sheet.set_column('H:I', 14)   
        sheet.set_column('J:K', 14)   
        sheet.set_column('L:M', 14)   
        
        # Format font
        title_format = workbook.add_format({
            'font_name': 'Calibri', 
            'font_size': 16, 
            'bold': True})
        second_format = workbook.add_format({
            'font_name': 'Times New Roman', 
            'font_size': 15, 
            'bold': True})
        header_format = workbook.add_format({
            'font_name': 'Times New Roman', 
            'font_size': 12, 
            'bold': True,
            'border': 1, 
            'indent': 1, 
            'align': 'center'})
        cell_format = workbook.add_format({
            'font_name': 'Times New Roman', 
            'font_size': 11,
            'border': 1, 
            'align': 'right', 
            'indent': 1})
        
        # Write format data to Excel file
        sheet.write(
            'A1', 
            f'Công ty: {str(self.location_id.company_id.name).upper()}', 
            second_format)
        sheet.write(
            'A4', 
            'BÁO CÁO NHẬP XUẤT TỒN KHO HÀNG HÓA', 
            title_format)
        sheet.write(
            'A5', 
            f'Từ ngày: {self.date_from} - Đến ngày: {self.date_to}', 
            second_format)
        sheet.merge_range('A7:A8', 'STT', header_format)
        sheet.merge_range('B7:B8', 'Mã hàng', header_format)
        sheet.merge_range('C7:C8', 'Tên hàng', header_format)
        sheet.merge_range('D7:D8', 'Nhóm hàng', header_format)
        sheet.merge_range('E7:E8', 'ĐVT', header_format)
        sheet.merge_range('F7:G7', 'Số tồn đầu', header_format)
        sheet.write('F8', 'Số lượng', header_format)
        sheet.write('G8', 'Giá trị', header_format)
        sheet.merge_range('H7:I7', 'Nhập trong kỳ', header_format)
        sheet.write('H8', 'Số lượng', header_format)
        sheet.write('I8', 'Giá trị', header_format)
        sheet.merge_range('J7:K7', 'Xuất trong kỳ', header_format)
        sheet.write('J8', 'Số lượng', header_format)
        sheet.write('K8', 'Giá trị', header_format)
        sheet.merge_range('L7:M7', 'Số tồn cuối', header_format)
        sheet.write('L8', 'Số lượng', header_format)
        sheet.write('M8', 'Giá trị', header_format)
        sheet.write('A9', 'A', header_format)
        sheet.write('B9', 'B', header_format)
        sheet.write('C9', 'C', header_format)
        sheet.write('D9', 'D', header_format)
        sheet.write('E9', 'E', header_format)
        sheet.write('F9', '(1)', header_format)
        sheet.write('G9', '(2)', header_format)
        sheet.write('H9', '(3)', header_format)
        sheet.write('I9', '(4)', header_format)
        sheet.write('J9', '(5)', header_format)
        sheet.write('K9', '(6)', header_format)
        sheet.write('L9', '(7)=(1)+(3)-(5)', header_format)
        sheet.write('M9', '(8)=(2)+4-(6)', header_format)
        sheet.write('A10', str(self.location_id.complete_name), header_format)
        
        
        final_state = self.action_fetch_final_state(
            self.location_id.id, self.date_to)
        import_export_data = self.compute_import_export(
            self.location_id.id, self.date_from, self.date_to)
        merged_data = {}
        
        # Merge final state and import/export data
        for product_id, final_data in final_state.items():
            import_data = import_export_data.get(product_id, {
                'import_qty': 0,
                'import_value': 0,
                'export_qty': 0,
                'export_value': 0,
            })

            merged_data[product_id] = {
                'final_quantity': final_data['quantity'],
                'final_value': final_data['value'],
                'import_qty': import_data['import_qty'],
                'import_value': import_data['import_value'],
                'export_qty': import_data['export_qty'],
                'export_value': import_data['export_value'],
            }
            
        row = 10
        stt = 1
        total_final_quantity = 0
        total_final_value = 0
        total_import_quantity = 0
        total_import_value = 0
        total_export_quantity = 0
        total_export_value = 0
        
        # Write data that are processed to Excel file
        for product_id, data in merged_data.items():
            product = self.env['product.product'].browse(product_id)
            
            final_quantity = data['final_quantity']
            final_value = data['final_value']
            import_quantity = data['import_qty']
            import_value = data['import_value']
            export_quantity = data['export_qty']
            export_value = data['export_value']
            initial_quantity = final_quantity - import_quantity + export_quantity
            initial_value = final_value - import_value + export_value
            
            total_final_quantity += final_quantity
            total_final_value += final_value
            total_import_quantity += import_quantity
            total_import_value += import_value
            total_export_quantity += export_quantity
            total_export_value += export_value
            
            sheet.write(row, 0, stt, cell_format)
            sheet.write(row, 1, product.default_code, cell_format)  
            sheet.write(row, 2, product.name, cell_format)          
            sheet.write(row, 3, product.categ_id.name, cell_format) 
            sheet.write(row, 4, product.uom_id.name, cell_format)  
            sheet.write(row, 5, initial_quantity if initial_quantity != 0 else '-  ', cell_format)          
            sheet.write(row, 6, initial_value if initial_value != 0 else '-  ', cell_format)        
            sheet.write(row, 7, import_quantity if import_quantity !=0 else '-  ', cell_format)            
            sheet.write(row, 8, import_value if import_value !=0 else '-  ', cell_format)            
            sheet.write(row, 9, export_quantity if export_quantity !=0 else '-  ', cell_format)             
            sheet.write(row, 10, export_value if export_value !=0 else '-  ', cell_format)         
            sheet.write(row, 11, final_quantity if final_quantity !=0 else '-  ', cell_format)           
            sheet.write(row, 12, final_value if final_value !=0 else '-  ', cell_format)           
            row += 1
            stt += 1
        
        total_initial_quantity = total_final_quantity - total_import_quantity + total_export_quantity
        total_initial_value = total_final_value - total_import_value + total_export_value
        
        
        # Write total data at final line to Excel file
        sheet.write(
            'F10', 
            total_initial_quantity if total_initial_quantity !=0 else '-  ', 
            header_format)
        sheet.write(
            'G10', 
            total_import_value if total_initial_value !=0 else '-  ', 
            header_format)
        sheet.write(
            'H10', 
            total_import_quantity if total_import_quantity !=0 else '-  ', 
            header_format)
        sheet.write(
            'I10', 
            total_import_value if total_import_value !=0 else '-  ', 
            header_format)
        sheet.write(
            'J10', 
            total_export_quantity if total_export_quantity !=0 else '-  ', 
            header_format)
        sheet.write(
            'K10', 
            total_export_value if total_export_value !=0 else '-  ', 
            header_format)
        sheet.write(
            'L10', 
            total_final_quantity if total_final_quantity !=0 else '-  ', 
            header_format)
        sheet.write(
            'M10', 
            total_final_value if total_final_value !=0 else '-  ', 
            header_format)
        
        workbook.close()
        output.seek(0)
        excel_file = base64.b64encode(output.read())
        output.close()
        
        attachment = self.env['ir.attachment'].create({
            'name': f'Báo cáo NXT kho.xlsx',
            'type': 'binary',
            'datas': excel_file,
            'store_fname': f'Báo cáo NXT kho.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    
    # Add a method to fetch the final state of the stock
    def action_fetch_final_state(self, location_id, to_date):
        final_state = {}
        stock_quants = self.env['stock.quant'].search([('location_id', '=', location_id)])
        for quant in stock_quants:
            product_id = quant.product_id.id
            cost = quant.product_id.standard_price
            final_state[product_id] = {
                'quantity': quant.quantity,
                'value': quant.quantity * cost,  
            }

        # Fetch adjustments to get data at the end of the period
        self.env.cr.execute("""
            SELECT
                sml.product_id,
                SUM(CASE WHEN sml.location_dest_id = %s THEN sml.quantity ELSE 0 END) -
                SUM(CASE WHEN sml.location_id = %s THEN sml.quantity ELSE 0 END) AS net_quantity,
                SUM(CASE WHEN sml.location_dest_id = %s THEN svl.value ELSE 0 END) -
                SUM(CASE WHEN sml.location_id = %s THEN svl.value ELSE 0 END) AS net_value
            FROM stock_move_line sml
            LEFT JOIN stock_valuation_layer svl ON sml.move_id = svl.stock_move_id
            WHERE sml.date > %s
            AND sml.state = 'done'
            AND (sml.location_id = %s OR sml.location_dest_id = %s)
            GROUP BY sml.product_id
        """, 
        (location_id, location_id, location_id, location_id, to_date, location_id, location_id))

        adjustments = self.env.cr.fetchall()
        
        # Update the final state array with the adjustments
        for row in adjustments:
            product_id = row[0]
            adjustment_qty = row[1] or 0
            adjustment_value = row[2] or 0

            if product_id in final_state:
                final_state[product_id]['quantity'] -= adjustment_qty
                final_state[product_id]['value'] -= adjustment_value
            else:
                final_state[product_id] = {
                    'quantity': -adjustment_qty,
                    'value': -adjustment_value,
                }

        return final_state

    
    # Add a method to compute the import and export movements
    def compute_import_export(self, location_id, from_date, to_date):
        # Fetch movements between the specified dates
        self.env.cr.execute("""
            SELECT
                sml.product_id,
                SUM(CASE WHEN sml.location_dest_id = %s THEN sml.quantity ELSE 0 END) AS total_import_qty,
                SUM(CASE WHEN sml.location_dest_id = %s THEN svl.value ELSE 0 END) AS total_import_value,
                SUM(CASE WHEN sml.location_id = %s THEN sml.quantity ELSE 0 END) AS total_export_qty,
                SUM(CASE WHEN sml.location_id = %s THEN svl.value ELSE 0 END) AS total_export_value
            FROM stock_move_line sml
            LEFT JOIN stock_valuation_layer svl ON sml.move_id = svl.stock_move_id
            WHERE sml.date >= %s AND sml.date <= %s
            AND sml.state = 'done'
            AND (sml.location_id = %s OR sml.location_dest_id = %s)
            GROUP BY sml.product_id
        """, 
        (location_id, location_id, location_id, location_id, from_date, to_date, location_id, location_id))

        movements = self.env.cr.fetchall()

        return {
            row[0]: {
                'import_qty': row[1] or 0,
                'import_value': row[2] or 0,
                'export_qty': row[3] or 0,
                'export_value': -row[4] or 0,
            } for row in movements
        }

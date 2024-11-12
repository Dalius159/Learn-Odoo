from odoo import models, fields

class UniversitySchool(models.Model):
    _name = 'university.school'
    _description = 'University School'
    
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    class_ids = fields.One2many("university.class", "school_id", string="class")
    student_ids = fields.One2many("university.student", "school_id", string="Student")
    
    #SQL CONSTRAINS
    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'This code has exsist!')
    ]
from odoo import models, fields


class UniversityClass(models.Model):
    _name = 'university.class'
    _description = 'University School Class'
    
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    school_id = fields.Many2one("university.school", string="School Id") 
    student_ids = fields.One2many("university.student", "class_id", string="Student Id")
    school_name = fields.Char(string="School", related='school_id.name', store=True)
    
    #SQL CONSTRAINT
    _sql_constraints = [
        ('unique_code_school', 
            'UNIQUE(code, school_id)', 
            'The class code must be unique within the same school!')
    ]
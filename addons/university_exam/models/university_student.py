from odoo import api, models, fields


class UniversityStudent(models.Model):
    _name = "university.student"
    _description = "University Student"
    
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    school_id = fields.Many2one("university.school", string="School Id")
    class_id = fields.Many2one("university.class", string="Class Id")
    math_score = fields.Float(string="Math Score")
    physics_score = fields.Float(string="Physics Score")
    chemistry_score = fields.Float(string="Chemistry Score")
    rank_in_class = fields.Integer(string="Rank in class", readonly=True)
    rank_in_school = fields.Integer(string="Rank in school", readonly=True)
    total_score = fields.Float(
        string="Total Score", 
        readonly=True, 
        compute="_compute_total", 
        store=True)
    avarage_score = fields.Float(
        string="Avarage Score", 
        readonly=True, 
        compute="_compute_avarage", 
        store=True)
    
    
    # Related fields    
    school_name = fields.Char(string="School", related='school_id.name', store=True)
    class_name = fields.Char(string="Class", related='class_id.name', store=True)
    
    #SQL CONSTRAINS
    _sql_constraints = [
        ('positive_physics_score', 
            'CHECK(physics_score >= 0 AND physics_score <= 10)', 
            'Physics score must be between 0 and 10!'),
        ('positive_chemistry_score', 
            'CHECK(chemistry_score >= 0 AND chemistry_score <= 10)', 
            'Chemistry score must be between 0 and 10!'),
        ('positive_math_score', 
            'CHECK(math_score >= 0 AND math_score <= 10)', 
            'Math score must be between 0 and 10!'),
        ('unique_code_student', 
            'UNIQUE(code, school_id)', 
            'The student code must be unique within the same school!')
    ]
    
    
    @api.depends("math_score", "physics_score", "chemistry_score")
    def _compute_total(self):
        for record in self:
            record.total_score = record.math_score + record.physics_score + record.chemistry_score
        
        
    @api.depends("total_score")
    def _compute_avarage(self):
        for record in self:
            record.avarage_score = record.total_score / 3
            
            
    @api.depends("total_score")
    def compute_rank_in_class(self):
        for record in self:
            if record.class_id:
                students_in_class = self.search(
                    [('class_id', '=', record.class_id.id)], order="total_score desc")
                rank = 1
                for student in students_in_class:
                    student.rank_in_class = rank
                    rank += 1


    @api.depends("total_score")
    def compute_rank_in_school(self):
        for record in self:
            if record.school_id:              
                students_in_school = self.search(
                    [('school_id', '=', record.school_id.id)], order="total_score desc")
                rank = 1
                for student in students_in_school:
                    student.rank_in_school = rank
                    rank += 1

    
    # Automatically compute the rank in class and rank in school 
    # when a student is created
    @api.model
    def create(self, vals):
        student = super(UniversityStudent, self).create(vals)
        student.compute_rank_in_class()
        student.compute_rank_in_school()
        return student
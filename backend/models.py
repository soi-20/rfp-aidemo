from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Site(db.Model):
    __tablename__ = 'site'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    site_id = db.Column(db.String(128))
    drive_id = db.Column(db.String(128))
    workbook_id = db.Column(db.String(128))
    worksheet_id = db.Column(db.String(128))

class Links(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    comp_name = db.Column(db.String(128))
    doc_name = db.Column(db.String(128))
    link = db.Column(db.String(256))
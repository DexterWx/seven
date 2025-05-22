from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    phone = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    commission_rate = db.Column(db.Float, default=0)     # 分成比例
    superior_name = db.Column(db.String(100))              # 上级名字
    superior_phone = db.Column(db.String(20), db.ForeignKey('users.phone'), nullable=True)
    unwithdrawn_amount = db.Column(db.Float, default=0)  # 未体现金额
    withdrawn_amount = db.Column(db.Float, default=0)    # 已提现金额
    yesterday_income = db.Column(db.Float, default=0)    # 昨日收益
    month_income = db.Column(db.Float, default=0)        # 本月收益
    team_yesterday_income = db.Column(db.Float, default=0)  # 团队昨日收益
    team_month_income = db.Column(db.Float, default=0)  # 团队本月收益
    
    password = db.Column(db.String(100), nullable=False)
    first_level_count = db.Column(db.Integer, default=0)   # 一级下线数量
    
    # 添加设备关系
    devices = db.relationship('Device', backref='user', lazy='dynamic')

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.String(50), primary_key=True)
    phone = db.Column(db.String(20), db.ForeignKey('users.phone'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float)                           # 设备金额
    is_returned = db.Column(db.Boolean, default=False)     # 是否返现
    is_paid = db.Column(db.Boolean, default=False)         # 是否打款
    remark = db.Column(db.Text)                            # 备注
    commission_rate = db.Column(db.Integer, default=0)     # 分成比例 
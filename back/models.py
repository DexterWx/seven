from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    phone = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    min_commission_rate = db.Column(db.Float, default=0)     # 最小分成比例
    max_commission_rate = db.Column(db.Float, default=0)     # 最大分成比例
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
    phone = db.Column(db.String(20), db.ForeignKey('users.phone'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float)                           # 设备金额
    is_returned = db.Column(db.Boolean, default=False)     # 是否返现
    is_paid = db.Column(db.Boolean, default=False)         # 是否打款
    remark = db.Column(db.Text)                            # 备注
    commission_rate = db.Column(db.Integer, default=0.1)     # 分成比例 
    first_commission_rate = db.Column(db.Integer, default=0.1)     # 一级分成比例 
    
    yesterday_income = db.Column(db.Float, default=0)    # 昨日收益

class PlatformStats(db.Model):
    __tablename__ = 'platform_stats'
    id = db.Column(db.Integer, primary_key=True)
    withdrawn = db.Column(db.Float, default=0)          # 已提现金额
    unwithdrawn = db.Column(db.Float, default=0)        # 未提现金额
    total = db.Column(db.Float, default=0)              # 总额
    commission_total = db.Column(db.Float, default=0)   # 抽成总额
    device_total = db.Column(db.Float, default=0)       # 设备金额总和
    return_total = db.Column(db.Float, default=0)       # 返现总额
    paid_return = db.Column(db.Float, default=0)        # 已打款返现金额
    unpaid_return = db.Column(db.Float, default=0)      # 未打款返现金额
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
